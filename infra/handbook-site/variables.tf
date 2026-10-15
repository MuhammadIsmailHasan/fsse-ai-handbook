variable "region" {
  description = <<-EOT
    Region for the S3 bucket. CloudFront serves readers from its own edge
    locations, so this only affects uploads, not reading speed.
    Singapore is enabled in every account; Jakarta (ap-southeast-3) is an
    "opt-in" region you must switch on in Account settings first.
  EOT
  type        = string
  default     = "ap-southeast-1" # Singapore
}

variable "bucket_name" {
  description = <<-EOT
    Globally unique S3 bucket name for the built site, e.g.
    "fsse-handbook-ismail-2026". The bucket is private: only CloudFront reads it.
  EOT
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$", var.bucket_name))
    error_message = "Bucket names must be 3-63 chars, lowercase letters, numbers, dots and hyphens."
  }
}

variable "basic_auth_user" {
  description = <<-EOT
    Username for the browser password prompt. Leave both auth variables empty to
    publish the handbook openly. The handbook is your own study material, so the
    default is to lock it.
  EOT
  type        = string
  default     = "learner"
}

variable "basic_auth_password" {
  description = <<-EOT
    Password for the browser prompt. Set it in terraform.tfvars (gitignored).
    NOTE: this value is stored in plain text in the Terraform state file and in
    the deployed CloudFront Function, so treat it as a gate, not a secret.
    Empty string = no password prompt at all.
  EOT
  type        = string
  default     = ""
  sensitive   = true
}

variable "price_class" {
  description = "PriceClass_200 includes Southeast Asia edges; _100 is US/EU only and cheapest."
  type        = string
  default     = "PriceClass_200"
}
