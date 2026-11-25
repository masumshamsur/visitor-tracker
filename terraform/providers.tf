provider "aws" {
  region = var.region

  # Every AWS resource Terraform creates gets these tags automatically.
  default_tags {
    tags = {
      Project   = var.project
      ManagedBy = "terraform"
    }
  }
}