output "cluster_name" {
  value = module.eks.cluster_name
}

output "vpc_id" {
  value = module.vpc.vpc_id
}

output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}

output "github_ci_role_arn" {
  description = "Put this in the GitHub secret AWS_CI_ROLE_ARN"
  value       = aws_iam_role.github_ci.arn
}

output "kubeconfig_command" {
  description = "Run this to connect kubectl"
  value       = "aws eks update-kubeconfig --region ${var.region} --name ${module.eks.cluster_name}"
}