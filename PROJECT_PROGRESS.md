# Project Progress: visitor-tracker

This file and the actual repository files are the source of truth when resuming. A step is marked complete only when its verification evidence is recorded here.

## 1. Objective and architecture

Deploy a containerized FastAPI web app (visit counter with a browser dashboard, backed by Redis) to Amazon EKS behind an internet-facing Application Load Balancer. A push to `main` on GitHub triggers GitHub Actions: tests, `terraform validate`, Docker build, Trivy scan, push to ECR (tagged with the short commit SHA), manual approval, then `kubectl apply` with automatic rollback. Prometheus and Grafana monitor the app.

```
GitHub (main) -> GitHub Actions (OIDC to AWS, no stored keys)
   -> test + terraform validate
   -> docker build -> Trivy scan -> push to ECR
   -> manual approval (production environment)
   -> kubectl apply -k k8s -> rollout check / undo
Users -> ALB (public subnets) -> api pods (private subnets, EKS) -> redis
Prometheus scrapes /metrics -> Grafana
```

Networking: one VPC (`10.0.0.0/16`), two public and two private subnets in two AZs, one NAT Gateway. Nodes run in the private subnets.

The project is done twice:

- **Attempt 1: AWS Console.** Every AWS resource is created by hand. Guide: `docs/console-deploy-guide.md` (interactive version: `docs/console-deploy-guide.html`, published at https://claude.ai/artifact/Kxs5jFdw5gJGLuBcZSaYuN).
- **Attempt 2: Terraform.** The same infrastructure from `terraform/`.

## 2. Current position

- **Attempt:** 1 (Console)
- **Phase:** 0 - Prepare
- **Last step completed:** none
- **Next step:** Step 1 - Install and check your local tools

## 3. Roadmap: Attempt 1 (Console)

| #  | Phase                | Step                                                        | Status      |
|----|----------------------|-------------------------------------------------------------|-------------|
| 1  | 0 Prepare            | Install and check local tools (kubectl, helm)               | Next        |
| 2  | 0 Prepare            | Create a budget alert                                       | Not started |
| 3  | 0 Prepare            | Confirm AWS identity, set shell variables                   | Not started |
| 4  | 1 Network            | Create the VPC (VPC and more wizard)                        | Not started |
| 5  | 1 Network            | Tag subnets for load balancers                              | Not started |
| 6  | 2 Registry           | Create the ECR repository                                   | Not started |
| 7  | 2 Registry           | Build (linux/amd64) and push the first image by hand        | Not started |
| 8  | 3 IAM                | EKS cluster role                                            | Not started |
| 9  | 3 IAM                | Node role                                                   | Not started |
| 10 | 4 EKS                | Create the EKS cluster (custom config, no Auto Mode)        | Not started |
| 11 | 4 EKS                | Create the node group                                       | Not started |
| 12 | 4 EKS                | Check the add-ons                                           | Not started |
| 13 | 4 EKS                | Connect kubectl                                             | Not started |
| 14 | 5 Cluster add-ons    | IAM policy and role for the Load Balancer Controller        | Not started |
| 15 | 5 Cluster add-ons    | Pod Identity association                                    | Not started |
| 16 | 5 Cluster add-ons    | Install the AWS Load Balancer Controller (Helm)             | Not started |
| 17 | 5 Cluster add-ons    | Install Prometheus and Grafana (Helm)                       | Not started |
| 18 | 6 First deploy       | Deploy the app with kubectl                                 | Not started |
| 19 | 6 First deploy       | Open the app in the browser via the ALB                     | Not started |
| 20 | 7 CI/CD              | Create the GitHub repository                                | Not started |
| 21 | 7 CI/CD              | GitHub OIDC identity provider in IAM                        | Not started |
| 22 | 7 CI/CD              | GitHub Actions IAM role (trust + inline policy)             | Not started |
| 23 | 7 CI/CD              | EKS access entry for the CI role                            | Not started |
| 24 | 7 CI/CD              | GitHub secret and production environment                    | Not started |
| 25 | 7 CI/CD              | Push code and run the pipeline                              | Not started |
| 26 | 7 CI/CD              | Ship a change through the pipeline                          | Not started |
| 27 | 8 Prove it           | Prometheus and Grafana                                      | Not started |
| 28 | 8 Prove it           | Autoscaling and automatic rollback tests                    | Not started |
| 29 | 8 Prove it           | Portfolio screenshots                                       | Not started |
| 30 | 9 Teardown           | Delete everything in order                                  | Not started |
| 31 | 9 Teardown           | Prepare for attempt 2 (Terraform)                           | Not started |

## 4. Roadmap: Attempt 2 (Terraform)

Steps T1–T16 in `docs/console-deploy-guide.md`. You write the Terraform code yourself from the guide.

| #   | Phase        | Step                                                      | Status      |
|-----|--------------|-----------------------------------------------------------|-------------|
| T1  | TF setup     | Clean account, tool versions, check Kubernetes version     | Not started |
| T2  | TF setup     | Folder structure (move old draft to `terraform-old/`)      | Not started |
| T3  | TF setup     | Bootstrap remote state bucket (S3, versioned, encrypted)   | Not started |
| T4  | TF setup     | `versions.tf` backend + `providers.tf`; `terraform init`   | Not started |
| T5  | TF code      | `variables.tf`, `terraform.tfvars`                         | Not started |
| T6  | TF code      | `vpc.tf`                                                   | Not started |
| T7  | TF code      | `ecr.tf`                                                   | Not started |
| T8  | TF code      | `eks.tf`                                                   | Not started |
| T9  | TF code      | `iam-github.tf`                                            | Not started |
| T10 | TF code      | `iam-lbc.tf` + policy JSON                                 | Not started |
| T11 | TF code      | `outputs.tf`                                               | Not started |
| T12 | Build        | fmt, validate, `plan -out=tfplan`                          | Not started |
| T13 | Build        | `apply tfplan`                                             | Not started |
| T14 | Build        | kubectl + `monitoring/install.sh`                          | Not started |
| T15 | Deploy       | Update secret, deploy through pipeline                     | Not started |
| T16 | Destroy      | App, Helm, `terraform destroy`, bootstrap destroy          | Not started |

## 5. Completed steps (with evidence)

None yet. Record each step like this:

### Step N - YYYY-MM-DD

| Check | Result | Evidence |
|-------|--------|----------|
|       |        |          |

## 6. Problems hit and fixes

None yet.
