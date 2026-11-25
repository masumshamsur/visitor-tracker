# Resume bullets

For your resume and LinkedIn, not the public README.

- Designed and provisioned AWS infrastructure (VPC, EKS, ECR, IAM) with Terraform modules and remote state locking.
- Built a GitHub Actions CI/CD pipeline with automated tests, container vulnerability scanning (Trivy), manual approval gates, and automatic rollback on failed rollouts.
- Eliminated static cloud credentials in CI by federating GitHub Actions to AWS with OIDC and least-privilege IAM.
- Deployed a horizontally autoscaled service on Kubernetes with zero-downtime rolling updates, PDBs, and health probes.
- Implemented observability with Prometheus, Grafana, and alerting rules for availability and resource saturation.

- Debugged real deployment failures end to end: GitHub OIDC immutable subject claims, Free Tier instance restrictions, a Trivy-blocked image (Starlette CVEs), Kubernetes service-link env var collisions, and stuck load balancer resources during teardown.
