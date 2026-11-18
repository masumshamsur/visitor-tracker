# Docker and Docker Compose in visitor-tracker

This guide explains, in simple words, how this project uses Docker and Docker Compose. It also has hands-on practice steps. Run every command yourself from the project folder:

```bash
cd ~/Documents/aws/aws-labs/visitor-tracker
```

## 1. The basic ideas

| Word | Simple meaning |
|---|---|
| **Image** | A packaged copy of the app: the code, Python, and every library it needs. Like a template. |
| **Container** | A running copy of an image. You can start many containers from one image. |
| **Dockerfile** | The recipe that tells Docker how to build the image. |
| **Build context** | The folder Docker is allowed to read files from while building. |
| **Registry** | A place to store images online. This project uses Docker Hub (for Redis) and Amazon ECR (for our app). |
| **Docker Compose** | A tool that starts several containers together from one file, `docker-compose.yml`. |

Why use Docker at all? The app runs the same way on your Mac, in GitHub Actions and on EKS, because the image contains everything it needs.

## 2. Where the Docker files are

```
visitor-tracker/
├── Dockerfile           Recipe for the app image
├── .dockerignore        Files Docker must NOT send into the build
├── docker-compose.yml   Starts the app + Redis together on your laptop
└── app/                 The app code that goes into the image
    ├── main.py
    ├── static/index.html
    └── requirements.txt
```

The Dockerfile is at the project root, so **always build from the project root**. Running `docker build` inside `app/` fails, because Docker can't find the `app/...` paths.

## 3. The Dockerfile, line by line

The Dockerfile has two **stages**. The first stage installs the Python packages. The second stage copies only what the app needs, so the final image stays small and has no build tools in it.

The comments on the right are only here to explain each line. Docker only allows comments on their own line, so the real file doesn't have them.

```dockerfile
# ---- build stage ----
FROM python:3.12-slim AS build          # Start from a small official Python image. Call this stage "build".
WORKDIR /app                            # Work inside the /app folder.
COPY app/requirements.txt .             # Copy the list of Python libraries.
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
                                        # Install the libraries into /install.

# ---- runtime stage ----
FROM python:3.12-slim                   # Start again from a clean Python image.
RUN useradd --uid 10001 --create-home appuser
                                        # Create a normal user, so the app does not run as root.
WORKDIR /app
COPY --from=build /install /usr/local   # Take only the installed libraries from the build stage.
COPY app/main.py .                      # Copy the app code.
COPY app/static/ static/                # Copy the web page.
USER 10001                              # From here on, run as the normal user.
EXPOSE 8000                             # Note that the app listens on port 8000.
HEALTHCHECK --interval=30s CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8000/healthz')"
                                        # Every 30 seconds, Docker checks the app is still healthy.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
                                        # The command that starts the app.
```

**Why copy `requirements.txt` before the code?** Docker saves (caches) each step. If you only change `main.py`, Docker reuses the slow "install libraries" step and rebuilds in seconds.

## 4. The .dockerignore file

The build context is the whole project, including `terraform/`, `docs/` and `.git/`. You don't want those in the image. `.dockerignore` blocks everything, then allows only the three things the app needs:

```
*                      # ignore everything...
!app/requirements.txt  # ...except these
!app/main.py
!app/static/
```

(As with the Dockerfile, the comments are only here to explain; the real file puts its comment on a separate line.)

Result: a smaller, faster, safer build with no secrets or Terraform files inside.

## 5. Practice: build and run the image yourself

### Step 1: Clean up old images

```bash
docker compose down
```

```bash
docker rmi visitor-tracker-api visitor-tracker:local
```

"No such image" is fine. It just means there was nothing to delete.

### Step 2: Build the image

```bash
docker build -t visitor-tracker:local .
```

- `-t visitor-tracker:local` gives the image a **name** (`visitor-tracker`) and a **tag** (`local`).
- The `.` at the end is the **build context** (the current folder).

You should see the two stages run. The last line says `naming to docker.io/library/visitor-tracker:local`.

### Step 3: Look inside the image

```bash
docker images visitor-tracker
```

Shows the image and its size (about 150–200 MB).

```bash
docker history visitor-tracker:local
```

Shows each layer and the Dockerfile line that made it.

```bash
docker run --rm visitor-tracker:local ls -R /app
```

Lists the files in the image. You should see only `main.py` and `static/index.html`.

### Step 4: Run the container on its own

```bash
docker run --rm -p 8000:8000 --name api visitor-tracker:local
```

- `-p 8000:8000` connects port 8000 on your Mac to port 8000 in the container.
- `--rm` deletes the container when it stops.
- `--name api` gives the container a name you can use in other commands.

Open http://localhost:8000. There is no Redis, so the badge says **Redis unavailable** and the count says **Redis down**. The app keeps working instead of crashing. Press **Ctrl+C** to stop.

### Step 5: Run everything with Compose

```bash
docker compose up --build
```

Open http://localhost:8000. Now the badge is green (**Ready**) and the count goes up. Press **Ctrl+C**, then:

```bash
docker compose down
```

### Check yourself

- [ ] `docker images` shows `visitor-tracker:local`
- [ ] The image contains only `main.py` and `static/`
- [ ] Without Redis, the page shows "Redis unavailable"
- [ ] With Compose, the page shows "Ready" and the count goes up

## 6. How Docker Compose knows which image to run

When you run `docker compose up --build`, Compose reads `docker-compose.yml` **in the current folder**. That's why you `cd` into the project first.

```yaml
services:
  api:
    build: .                  # Build an image from ./Dockerfile
    ports: ["8000:8000"]
    environment:
      REDIS_HOST: redis       # Find Redis by its service name
      APP_VERSION: local
    depends_on: [redis]       # Start Redis first
  redis:
    image: redis:7.4-alpine   # Use a ready-made image from Docker Hub
    ports: ["6379:6379"]
```

Each service either **builds** an image or **uses** an existing one:

| Service | Line | What Compose does |
|---|---|---|
| `api` | `build: .` | Builds an image from `./Dockerfile` |
| `redis` | `image: redis:7.4-alpine` | Downloads the image from Docker Hub (only the first time) |

**The image name.** The `api` service has no `image:` name, so Compose makes one: `<project>-<service>`. The project name is the folder name, so the image is called **`visitor-tracker-api`**.

**The `--build` flag.**

| Command | What happens |
|---|---|
| `docker compose up --build` | Always rebuilds the app image, so your latest code goes in |
| `docker compose up` | Reuses `visitor-tracker-api` if it exists, and builds only if it's missing. You might run old code. |

**How the containers find each other.** Compose creates a private network. On it, each container can reach the others by **service name**. That's why `REDIS_HOST: redis` works.

**Your `docker build` image vs the Compose image.** `visitor-tracker:local` (built by hand) and `visitor-tracker-api` (built by Compose) are **two different images**. Compose ignores yours unless you name it in the file:

```yaml
  api:
    build: .
    image: visitor-tracker:local   # Build from the Dockerfile and use this name
```

**Useful commands** (after `docker compose up -d`, where `-d` runs it in the background):

```bash
docker compose ps
```

Shows the running containers, such as `visitor-tracker-api-1`.

```bash
docker compose images
```

Shows which image each service uses.

```bash
docker compose logs -f api
```

Follows the app's logs. Press Ctrl+C to stop following.

```bash
docker compose config
```

Prints the full settings Compose is using.

## 7. Docker Compose vs Kubernetes

Both describe which containers to run and how they connect, but they're used in different places.

| | Docker Compose | Kubernetes (EKS) |
|---|---|---|
| Where | One machine (your laptop) | A cluster of machines in AWS |
| Used for | Fast local development | Running in production |
| App image | Built from the Dockerfile on the spot | Pulled from ECR (built by GitHub Actions) |
| Copies of the app | 1 | 2 to 10 (autoscaling) |
| If a container crashes | Stays down unless you add a restart rule | Restarted automatically |
| Updates | Stop old, start new | Rolling update with no downtime |
| File | `docker-compose.yml` | `k8s/*.yaml` |

The same image runs in both places. Compose is for your laptop; Kubernetes is for AWS.

## 8. Building for AWS (Apple Silicon Macs)

Your Mac uses an **arm64** chip. The EKS nodes (t3.medium) use **x86** (`amd64`). An image built normally on your Mac **won't run** on those nodes; the pods fail with `exec format error`.

So when you build for AWS (console guide, Step 7), tell Docker which platform to build for:

```bash
docker buildx build --platform linux/amd64 -t $REPO_URI:manual-1 --push .
```

- `buildx` is Docker's newer builder, which can build for other chip types.
- `--platform linux/amd64` builds for x86.
- `--push` uploads the image to ECR straight after building.

GitHub Actions runs on x86 machines, so the pipeline doesn't need this flag.

## 9. Does the app need a database?

The app already uses one: **Redis**, which stores the visit count.

Redis keeps its data **in memory**, and this project doesn't give it a disk. So the count goes back to 0 when:

- you run `docker compose down` (the Redis container is deleted), or
- the Redis pod restarts on EKS.

That's fine for this demo. The project is about infrastructure and CI/CD, not data.

If you want the data to stay, here are your options:

| Goal | Option | Effort |
|---|---|---|
| Keep the count after `docker compose down` | Add a Docker **volume** for Redis | Small |
| Keep it when the pod restarts on EKS | Redis persistence + a **PersistentVolumeClaim** on EBS (needs the EBS CSI driver add-on) | Medium |
| Let AWS run Redis for you | **Amazon ElastiCache**: point `REDIS_HOST` at it | Medium, about $0.40+/day |
| Store real data (users, messages) | **Amazon RDS (PostgreSQL)** + a new feature, such as a guestbook | Larger, about $0.50+/day |

**Recommendation:** finish the console guide first without a database. Afterwards, adding ElastiCache or RDS makes a strong portfolio extension.

## 10. Common problems

| Problem | Cause | Fix |
|---|---|---|
| `failed to compute cache key: "/app/main.py" not found` | You ran `docker build` inside `app/` | Run it from the project root |
| `port is already allocated` | Something else uses port 8000 | Stop it, or use `-p 8080:8000` and open http://localhost:8080 |
| Page shows "Redis down" with Compose | The Redis container isn't running | Check `docker compose ps` and `docker compose logs redis` |
| Code change doesn't show up | Compose reused the old image | Run `docker compose up --build` |
| `Cannot connect to the Docker daemon` | Docker Desktop isn't running | Start Docker Desktop and try again |
| Pods on EKS fail with `exec format error` | Image built for arm64 | Rebuild with `--platform linux/amd64` |
