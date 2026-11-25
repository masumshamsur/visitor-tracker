terraform {
  required_version = ">= 1.10"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  # Where Terraform keeps its state file: the S3 bucket you created in bootstrap/.
  # Variables are not allowed here, so type your real bucket name.
  backend "s3" {
    bucket       = "visitor-tracker-tfstate-842190336606"
    key          = "visitor-tracker/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true # S3 locking: stops two "terraform apply" runs at the same time
  }
}