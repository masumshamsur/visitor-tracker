variable "project" {
  description = "Name prefix for every resource"
  type        = string
  default     = "visitor-tracker"
}

variable "region" {
  description = "AWS region to build in"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "IP address range for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "kubernetes_version" {
  description = "EKS Kubernetes version. Use one in standard support (check the EKS console)."
  type        = string
  default     = "1.35"
}

variable "node_instance_type" {
  description = "EC2 instance type for the worker nodes"
  type        = string
  default     = "t3.medium"
}

variable "github_repo" {
  description = "Your GitHub repository as owner/name, e.g. masumshamsur/visitor-tracker"
  type        = string
}

variable "github_sub_prefix" {
  description = "GitHub's immutable OIDC subject prefix (owner and repo with IDs)"
  type        = string
  default     = "repo:masumshamsur@128269966/visitor-tracker@1462309980"
}