# Provider and version pins. Pinning means `terraform init` tomorrow installs
# the same versions as today, so a provider update cannot change your infra.
terraform {
  required_version = ">= 1.9"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  # State lives next to this file (infra/handbook-site/terraform.tfstate) and is
  # gitignored. It is a small, single-user setup, so there is no remote backend.
  # Module 5 W7 teaches S3 remote state when you want the real-team version.
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project   = "fsse-handbook"
      Component = "handbook-site"
      ManagedBy = "terraform"
    }
  }
}
