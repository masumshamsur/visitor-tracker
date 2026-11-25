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

- **Attempt:** 2 (Terraform). Console build (Steps 4-31) skipped by choice on 2026-11-18; Phase 0 (Steps 1-3) done
- **Phase:** Terraform setup
- **Last step completed:** Step 3 (2026-11-18)
- **Last Terraform step completed:** T16 (2026-11-25). Attempt 2 complete; everything destroyed
- **Next step:** none. Optional: rebuild later for Steps 27-29 (Grafana, autoscaling, rollback, screenshots)

## 3. Roadmap: Attempt 1 (Console)

| #  | Phase                | Step                                                        | Status      |
|----|----------------------|-------------------------------------------------------------|-------------|
| 1  | 0 Prepare            | Install and check local tools (kubectl, helm)               | Done        |
| 2  | 0 Prepare            | Create a budget alert                                       | Done        |
| 3  | 0 Prepare            | Confirm AWS identity, set shell variables                   | Done        |
| 4  | 1 Network            | Create the VPC (VPC and more wizard)                        | Skipped     |
| 5  | 1 Network            | Tag subnets for load balancers                              | Skipped     |
| 6  | 2 Registry           | Create the ECR repository                                   | Skipped     |
| 7  | 2 Registry           | Build (linux/amd64) and push the first image by hand        | Skipped     |
| 8  | 3 IAM                | EKS cluster role                                            | Skipped     |
| 9  | 3 IAM                | Node role                                                   | Skipped     |
| 10 | 4 EKS                | Create the EKS cluster (custom config, no Auto Mode)        | Skipped     |
| 11 | 4 EKS                | Create the node group                                       | Skipped     |
| 12 | 4 EKS                | Check the add-ons                                           | Skipped     |
| 13 | 4 EKS                | Connect kubectl                                             | Skipped     |
| 14 | 5 Cluster add-ons    | IAM policy and role for the Load Balancer Controller        | Skipped     |
| 15 | 5 Cluster add-ons    | Pod Identity association                                    | Skipped     |
| 16 | 5 Cluster add-ons    | Install the AWS Load Balancer Controller (Helm)             | Skipped     |
| 17 | 5 Cluster add-ons    | Install Prometheus and Grafana (Helm)                       | Skipped     |
| 18 | 6 First deploy       | Deploy the app with kubectl                                 | Skipped     |
| 19 | 6 First deploy       | Open the app in the browser via the ALB                     | Skipped     |
| 20 | 7 CI/CD              | Create the GitHub repository                                | Skipped     |
| 21 | 7 CI/CD              | GitHub OIDC identity provider in IAM                        | Skipped     |
| 22 | 7 CI/CD              | GitHub Actions IAM role (trust + inline policy)             | Skipped     |
| 23 | 7 CI/CD              | EKS access entry for the CI role                            | Skipped     |
| 24 | 7 CI/CD              | GitHub secret and production environment                    | Skipped     |
| 25 | 7 CI/CD              | Push code and run the pipeline                              | Skipped     |
| 26 | 7 CI/CD              | Ship a change through the pipeline                          | Skipped     |
| 27 | 8 Prove it           | Prometheus and Grafana                                      | Skipped     |
| 28 | 8 Prove it           | Autoscaling and automatic rollback tests                    | Skipped     |
| 29 | 8 Prove it           | Portfolio screenshots                                       | Skipped     |
| 30 | 9 Teardown           | Delete everything in order                                  | Skipped     |
| 31 | 9 Teardown           | Prepare for attempt 2 (Terraform)                           | Skipped     |

## 4. Roadmap: Attempt 2 (Terraform)

Steps T1–T16 in `docs/console-deploy-guide.md`. You write the Terraform code yourself from the guide.

| #   | Phase        | Step                                                      | Status      |
|-----|--------------|-----------------------------------------------------------|-------------|
| T1  | TF setup     | Clean account, tool versions, check Kubernetes version     | Done        |
| T2  | TF setup     | Folder structure                                           | Done        |
| T3  | TF setup     | Bootstrap remote state bucket (S3, versioned, encrypted)   | Done        |
| T4  | TF setup     | `versions.tf` backend + `providers.tf`; `terraform init`   | Done        |
| T5  | TF code      | `variables.tf`, `terraform.tfvars`                         | Done        |
| T6  | TF code      | `vpc.tf`                                                   | Done        |
| T7  | TF code      | `ecr.tf`                                                   | Done        |
| T8  | TF code      | `eks.tf`                                                   | Done        |
| T9  | TF code      | `iam-github.tf`                                            | Done        |
| T10 | TF code      | `iam-lbc.tf` + policy JSON                                 | Done        |
| T11 | TF code      | `outputs.tf`                                               | Done        |
| T12 | Build        | fmt, validate, `plan -out=tfplan`                          | Done        |
| T13 | Build        | `apply tfplan`                                             | Done        |
| T14 | Build        | kubectl + `monitoring/install.sh`                          | Done        |
| T15 | Deploy       | Update secret, deploy through pipeline                     | Done        |
| T16 | Destroy      | App, Helm, `terraform destroy`, bootstrap destroy          | Done        |

## 5. Completed steps (with evidence)

### Phase 0 (Steps 1-3) - 2026-11-18

| Check                    | Result | Evidence |
|--------------------------|--------|----------|
| Helm installed           | Pass   | `helm version` -> `v4.1.3` (guide's `helm repo add` / `helm install` commands work unchanged in Helm 4) |
| kubectl installed        | Pass   | `kubectl version --client` -> `v1.34.1`, Kustomize `v5.7.1` (Docker Desktop's copy at `/usr/local/bin/kubectl`). Kept as is: Step 10 will use Kubernetes 1.35, within kubectl's one-minor-version support range |
| Docker, Git, AWS CLI     | Pass   | Installed and verified in the 2048 project; app ran locally with Docker Compose |
| Budget alerts            | Pass   | Existing budgets reused instead of a new one: "My Monthly Cost Budget" ($10, OK, $1.49 used MTD) and "My Zero-Spend Budget" ($1, OK). Cost Anomaly Detection is also on |
| Terminal identity        | Pass   | `aws sts get-caller-identity` -> IAM user `shams-terraform001`, account ending `6606` |
| Console identity         | Pass   | Console signed in as `shams-terraform001`, same account; so Step 13 needs no extra access entry |
| Shell variables          | Pass   | `echo` printed account ID and `....dkr.ecr.us-east-1.amazonaws.com/visitor-tracker` |

### Step T1 - 2026-11-18

| Check                       | Result | Evidence |
|-----------------------------|--------|----------|
| Terraform version           | Pass   | `Terraform v1.16.3` on darwin_arm64 (1.17.2 available; not needed, 1.10+ required) |
| AWS identity                | Pass   | IAM user `shams-terraform001`, account ending `6606` |
| kubectl / Helm              | Pass   | kubectl `v1.34.1`, Helm `v4.1.3` |
| Kubernetes version          | Pass   | EKS console offers 1.35 with standard support until 2027-03-26 (1.37 is newest; 1.33 and older are extended support only). Using 1.35 |
| GitHub identity provider    | Found  | `token.actions.githubusercontent.com` already exists (created about a month ago for another project). Terraform code changed to look it up (`data` block) instead of creating it, so destroy leaves it in place |

### Steps T2-T3 - 2026-11-19

| Check                      | Result | Evidence |
|----------------------------|--------|----------|
| Folder structure           | Pass   | `terraform/bootstrap/` and `terraform/policies/` created |
| Bootstrap code             | Pass   | `bootstrap/main.tf` (1 data source, 4 resources) and `bootstrap/outputs.tf` written by hand |
| Bootstrap apply            | Pass   | `Apply complete! Resources: 4 added`; output `state_bucket_name = "visitor-tracker-tfstate-<account ID>"` |
| State contents             | Pass   | `terraform state list`: `aws_s3_bucket.tfstate`, versioning, encryption, public access block, plus the account lookup |
| Git ignores state          | Pass   | `bootstrap/.terraform/` and `terraform.tfstate` not tracked; `.terraform.lock.hcl`, `main.tf`, `outputs.tf` show as new files to commit |

### Step T4 - 2026-11-19

| Check                 | Result | Evidence |
|-----------------------|--------|----------|
| Backend configured    | Pass   | `terraform init` -> `Successfully configured the backend "s3"!` |
| Backend settings      | Pass   | `versions.tf`: bucket `visitor-tracker-tfstate-<account ID>`, key `visitor-tracker/terraform.tfstate`, `use_lockfile = true` |
| Provider locked       | Pass   | `terraform/.terraform.lock.hcl` pins `hashicorp/aws` `6.73.0` (constraint `~> 6.0`) |

### Step T5 - 2026-11-19

| Check            | Result | Evidence |
|------------------|--------|----------|
| Variables        | Pass   | `variables.tf` with 6 variables, `kubernetes_version = "1.35"` |
| tfvars           | Pass   | `terraform.tfvars`: `github_repo = "masumshamsur/visitor-tracker"`; not tracked by Git |
| Validate         | Pass   | `terraform validate` -> `Success!` |

### Steps T6-T12 - 2026-11-22

| Check            | Result | Evidence |
|------------------|--------|----------|
| Code files       | Pass   | `vpc.tf`, `ecr.tf`, `eks.tf`, `iam-github.tf`, `iam-lbc.tf`, `outputs.tf` written by hand |
| Plan             | Pass   | `terraform plan -out=tfplan` -> `Plan: 63 to add, 0 to change, 0 to destroy` |
| Outputs          | Pass   | `cluster_name = "visitor-tracker-eks"`, `kubeconfig_command` for us-east-1; ECR URL, CI role ARN, VPC ID known after apply |
| Plan file        | Fixed  | `tfplan` added to `.gitignore` (it can hold sensitive values) |

### Step T13 - 2026-11-24

| Check            | Result | Evidence |
|------------------|--------|----------|
| First apply      | Failed | Node group `CREATE_FAILED` (t3.medium not Free Tier eligible); see Problems |
| Second apply     | Pass   | `node_instance_type = "m7i-flex.large"` -> `Apply complete! Resources: 4 added, 0 changed, 1 destroyed` (new node group + add-ons, failed node group removed) |
| Outputs          | Pass   | `cluster_name`, `ecr_repository_url` (`....dkr.ecr.us-east-1.amazonaws.com/visitor-tracker`), `github_ci_role_arn` (`role/visitor-tracker-github-ci`), `kubeconfig_command`, `vpc_id` |

### Step T14 - 2026-11-24

| Check                 | Result | Evidence |
|-----------------------|--------|----------|
| kubectl connected     | Pass   | `update-kubeconfig` added context `...:cluster/visitor-tracker-eks` (first try from the project root did nothing; it must run from `terraform/`) |
| Nodes                 | Pass   | 2 nodes `Ready`, `v1.35.9-eks`, in `10.0.10.x` and `10.0.11.x` (one per private subnet) |
| Install script        | Pass   | Helm installed `monitoring` and `aws-load-balancer-controller`; created namespace `visitor-tracker` and `prometheusrule/api-alerts` |
| Load Balancer Ctrl    | Pass   | `aws-load-balancer-controller` `2/2` READY |
| Monitoring pods       | Pass   | Alertmanager, Grafana, operator, kube-state-metrics, 2 node-exporters, Prometheus all `Running`, 0 restarts |

### Step T15 - 2026-11-25

| Check                 | Result | Evidence |
|-----------------------|--------|----------|
| Secret + environment  | Pass   | `AWS_CI_ROLE_ARN` added; `production` environment with required reviewer `masumshamsur` |
| Pipeline              | Pass   | Run #10 "Fix REDIS_PORT clash with Kubernetes service links": preflight, test, terraform-check, build-scan-push, deploy all green (2m 8s), after fixes for runs #6-#9 (see Problems) |
| Pods                  | Pass   | 2 `api` pods and 1 `redis` pod `1/1 Running`, 0 restarts |
| Ingress               | Pass   | ALB address `k8s-visitort-api-....us-east-1.elb.amazonaws.com` |
| App in browser        | Pass   | ALB page loads, status `Ready`, version `7b87d86` (commit SHA); Send 10 requests -> 13 visits, alternating between 2 pods (`api-5489dbc7fd-r2fcg`, `api-5489dbc7fd-n7469`); counter shared through Redis |

### Step T16 - 2026-11-25

| Check                 | Result | Evidence |
|-----------------------|--------|----------|
| App deleted           | Pass   | `kubectl delete` removed all 9 objects; ALB deleted |
| Controller leftovers  | Fixed  | Target group `k8s-visitort-api-...` stuck with `ResourceInUse` for 15+ min although no load balancer used it; the 2 `k8s-` security groups were free (no ENIs, no rules), so deleted by hand before destroy (see Problems) |
| Main destroy          | Pass   | `terraform destroy` -> `Destroy complete! Resources: 67 destroyed` |
| Bootstrap destroy     | Pass   | `Destroy complete! Resources: 4 destroyed` |
| AWS check             | Pass   | us-east-1: no EKS clusters, only the default VPC, no instances, Elastic IPs, NAT Gateways, load balancers, target groups, ECR repos, available volumes, `/aws/eks/visitor*` log groups, `visitor-tracker*` IAM roles or state bucket |

## 6. Problems hit and fixes

- **Teardown: target group stuck "in use" (2026-11-25):** after deleting the app, the ALB went away but its target group couldn't be deleted (`ResourceInUse`, "in use by a listener or a rule", console showed "None associated"). The Load Balancer Controller kept retrying and so didn't delete its 2 security groups, which would have blocked VPC deletion. Fix: checked that the security groups had no ENIs or referencing rules, deleted them by hand, then uninstalled Helm and ran `terraform destroy`. The target group was gone by the end of the destroy.


- **Pipeline: api pods crash on EKS (2026-11-25):** `deploy` timed out waiting for rollout; pods in `CrashLoopBackOff`. Logs: `ValueError: invalid literal for int() with base 10: 'tcp://172.20.143.233:6379'` at `REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))`. Kubernetes adds environment variables for every Service in the namespace; the Service named `redis` creates `REDIS_PORT=tcp://<IP>:6379`, which overrides the app's default. (Docker Compose doesn't do this, so it worked locally.) Fix in `k8s/api.yaml`: `enableServiceLinks: false` and an explicit `REDIS_PORT: "6379"`. The automatic rollback also failed with `no rollout history found`, because this was the first deploy and there was no earlier version to go back to.

- **Pipeline: deploy failed in kustomize (2026-11-25):** `kubectl apply -k k8s` -> `file '.../monitoring/servicemonitor.yaml' is not in or below '.../k8s'`. Kustomize refuses files outside the folder it builds, for security. Fix: moved the file to `k8s/servicemonitor.yaml` and listed it as `servicemonitor.yaml` in `k8s/kustomization.yaml`. `kubectl kustomize k8s` now renders all 9 objects, including the ServiceMonitor.

- **Pipeline: Trivy blocked the image (2026-11-25):** after the OIDC fix, AWS login worked, but the scan found 3 HIGH vulnerabilities in `starlette 0.41.3` (CVE-2025-62727, CVE-2026-48818, CVE-2026-54283; fixed in 1.3.1). Starlette comes with FastAPI. Fix: `app/requirements.txt` `fastapi==0.115.6` -> `fastapi==0.165.0` (pulls in starlette 1.10.0). All 6 tests pass with the new version. The scan gate worked as designed: the vulnerable image was never pushed.

- **Pipeline: could not assume the CI role (2026-11-25):** `build-scan-push` failed at "Configure AWS credentials" with `Not authorized to perform sts:AssumeRoleWithWebIdentity`. The secret, OIDC provider (audience `sts.amazonaws.com`) and trust policy were all correct, but the repo uses GitHub's immutable subject format: `gh api repos/masumshamsur/visitor-tracker/actions/oidc/customization/sub` -> `sub_claim_prefix: repo:masumshamsur@128269966/visitor-tracker@1462309980`. The trust policy only allowed `repo:masumshamsur/visitor-tracker:...`. Fix: add the two immutable-format subjects in `iam-github.tf`, apply, rerun the failed jobs.

- **Pipeline: Trivy action not found (2026-11-25):** run 45547467136 failed in `build-scan-push` at "Set up job": `Unable to resolve action aquasecurity/trivy-action@0.28.0`. The action's tags now start with `v` (`v0.28.0` ... `v0.36.0`). Fix: workflow uses `aquasecurity/trivy-action@v0.36.0`. (`test`, `preflight` and `terraform-check` passed in that run.)

- **No Pod Identity association after apply (2026-11-24):** the EKS console showed 0 Pod Identity associations. `terraform/iam-lbc.tf` was empty (0 bytes, likely never saved), so the Load Balancer Controller's policy, role and association were never planned; the policy JSON in `policies/` was fine. Fix: paste the Step T10 code into `iam-lbc.tf`, save, then plan and apply again. Result: association `aws-load-balancer-controller` in `kube-system` with role `visitor-tracker-lbc-role` shows in the console; all 5 add-ons Active.

- **Node group failed: instance type not Free Tier eligible (2026-11-24):** `terraform apply` failed after 33 minutes with `AsgInstanceLaunchFailures ... The specified instance type is not eligible for Free Tier`. The account is on the AWS Free plan, which only launches Free Tier instance types, and `t3.medium` isn't one. Fix: set `node_instance_type = "m7i-flex.large"` (2 vCPU, 8 GiB, Free Tier eligible) in `terraform.tfvars`, then plan and apply again.

- **GitHub OIDC provider already exists (2026-11-18):** an account can only have one provider per URL, so creating it in Terraform would fail. Fix: `iam-github.tf` uses `data "aws_iam_openid_connect_provider" "github"` to look up the existing one.

- **Cost anomalies before starting (2026-11-18):** Cost Anomaly Detection flagged Amazon RDS ($0.39, 2026-11-09) and Elastic Load Balancing ($0.05, 2026-11-10), likely leftovers from earlier labs. Checked 2026-11-18: `aws elbv2 describe-load-balancers` and `aws rds describe-db-instances` both returned nothing in us-east-1, so nothing is still running there.
