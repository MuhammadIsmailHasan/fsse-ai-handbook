variable "region" {
  description = "Region for the dev box. Closer region = lower latency on every query."
  type        = string
  default     = "ap-southeast-3" # Jakarta
}

variable "allowed_cidr" {
  description = <<-EOT
    The ONLY source allowed to reach Postgres, Redis and SSH, as a CIDR.
    Put your own address here: "$(curl -s https://checkip.amazonaws.com)/32".
    A home connection usually changes address every few days, so expect to run
    `terraform apply` again when you cannot connect.
  EOT
  type        = string

  validation {
    condition     = var.allowed_cidr != "0.0.0.0/0"
    error_message = "Refusing 0.0.0.0/0: that opens your practice database to the whole internet."
  }

  validation {
    condition     = can(cidrhost(var.allowed_cidr, 0))
    error_message = "allowed_cidr must be a CIDR block, e.g. 203.0.113.9/32."
  }
}

variable "instance_type" {
  description = <<-EOT
    t4g.small (ARM, 2 GB) runs Postgres + Redis for exercises comfortably.
    t4g.micro (1 GB) also works and is cheaper; t4g.medium if you later add
    Langfuse or more services.
  EOT
  type        = string
  default     = "t4g.small"
}

variable "ssh_public_key_path" {
  description = <<-EOT
    Path to the public key allowed to SSH in, e.g. "~/.ssh/id_ed25519.pub".
    Leave empty to skip SSH entirely and use `aws ssm start-session` instead —
    no open port 22, no key to lose.
  EOT
  type        = string
  default     = ""
}

variable "data_volume_gb" {
  description = "Separate disk for Postgres data, so rebuilding the box keeps your databases."
  type        = number
  default     = 10
}
