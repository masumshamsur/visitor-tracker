module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.0"

  name               = "${var.project}-eks"
  kubernetes_version = var.kubernetes_version

  # Reach the Kubernetes API from your laptop and from GitHub Actions.
  endpoint_public_access = true

  # Make the identity running "terraform apply" a cluster admin (console Step 10).
  enable_cluster_creator_admin_permissions = true

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # The same five add-ons as console Step 10.
  addons = {
    vpc-cni = {
      before_compute = true # networking must exist before nodes start
    }
    eks-pod-identity-agent = {
      before_compute = true
    }
    kube-proxy     = {}
    coredns        = {}
    metrics-server = {}
  }

  # Two worker nodes in the private subnets (console Step 11).
  eks_managed_node_groups = {
    default = {
      name           = "${var.project}-nodes"
      ami_type       = "AL2023_x86_64_STANDARD"
      instance_types = [var.node_instance_type]
      min_size       = 2
      max_size       = 4
      desired_size   = 2
    }
  }

  # Let the GitHub Actions role run kubectl (console Step 23).
  access_entries = {
    github_ci = {
      principal_arn = aws_iam_role.github_ci.arn
      policy_associations = {
        admin = {
          policy_arn = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
          access_scope = {
            type = "cluster"
          }
        }
      }
    }
  }
}