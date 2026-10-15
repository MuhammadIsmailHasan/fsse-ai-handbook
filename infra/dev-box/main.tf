# ─────────────────────────────────────────────────────────────────────────────
# Dev box: one small ARM instance running the Postgres + Redis that
# exercises/compose.yaml runs locally, so a learning session needs no Docker
# Desktop on the Mac.
#
# Shape and cost: a t4g.small plus a 10 GB data disk, in the default VPC, with
# an Elastic IP so the address survives stop/start. Postgres and Redis are
# reachable only from `allowed_cidr` (your own address).
#
# Managed RDS + ElastiCache would be the production answer, and roughly 5x the
# price for practice data. Module 5 W7 covers that version.
# ─────────────────────────────────────────────────────────────────────────────

locals {
  # Same non-default ports as the rest of the repo, so only the HOST changes in
  # your .env when you switch between local Docker and this box.
  postgres_port = 5491
  redis_port    = 6391

  use_ssh = var.ssh_public_key_path != ""
}

# ── Passwords ───────────────────────────────────────────────────────────────
# Generated once and kept in Terraform state. Practice data only — never reuse
# these anywhere real.

resource "random_password" "postgres" {
  length  = 24
  special = false # keeps DATABASE_URL copy-pasteable without escaping
}

resource "random_password" "redis" {
  length  = 24
  special = false
}

# ── Network ─────────────────────────────────────────────────────────────────

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_security_group" "dev_box" {
  name        = "fsse-dev-box"
  description = "FSSE exercise services, reachable only from the learner's address"
  vpc_id      = data.aws_vpc.default.id
}

resource "aws_vpc_security_group_ingress_rule" "postgres" {
  security_group_id = aws_security_group.dev_box.id
  description       = "Postgres from the learner only"
  cidr_ipv4         = var.allowed_cidr
  from_port         = local.postgres_port
  to_port           = local.postgres_port
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "redis" {
  security_group_id = aws_security_group.dev_box.id
  description       = "Redis from the learner only"
  cidr_ipv4         = var.allowed_cidr
  from_port         = local.redis_port
  to_port           = local.redis_port
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "ssh" {
  count             = local.use_ssh ? 1 : 0
  security_group_id = aws_security_group.dev_box.id
  description       = "SSH from the learner only"
  cidr_ipv4         = var.allowed_cidr
  from_port         = 22
  to_port           = 22
  ip_protocol       = "tcp"
}

# Outbound stays open: the box needs to pull Docker images and talk to SSM.
resource "aws_vpc_security_group_egress_rule" "all" {
  security_group_id = aws_security_group.dev_box.id
  description       = "Docker pulls, package updates, SSM"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

# ── Access without SSH ──────────────────────────────────────────────────────
# Session Manager gives a shell through the AWS API, so there is no key file to
# lose and port 22 can stay shut.

data "aws_iam_policy_document" "assume_ec2" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "dev_box" {
  name               = "fsse-dev-box"
  assume_role_policy = data.aws_iam_policy_document.assume_ec2.json
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.dev_box.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "dev_box" {
  name = "fsse-dev-box"
  role = aws_iam_role.dev_box.name
}

resource "aws_key_pair" "learner" {
  count      = local.use_ssh ? 1 : 0
  key_name   = "fsse-dev-box"
  public_key = file(pathexpand(var.ssh_public_key_path))
}

# ── The instance ────────────────────────────────────────────────────────────

data "aws_ssm_parameter" "al2023_arm64" {
  # AWS publishes the current Amazon Linux 2023 image id here, so a rebuild
  # picks up the patched image instead of a hardcoded stale one.
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-arm64"
}

resource "aws_instance" "dev_box" {
  ami                         = data.aws_ssm_parameter.al2023_arm64.value
  instance_type               = var.instance_type
  subnet_id                   = data.aws_subnets.default.ids[0]
  vpc_security_group_ids      = [aws_security_group.dev_box.id]
  iam_instance_profile        = aws_iam_instance_profile.dev_box.name
  key_name                    = local.use_ssh ? aws_key_pair.learner[0].key_name : null
  associate_public_ip_address = true

  user_data = templatefile("${path.module}/cloud-init.yaml.tftpl", {
    postgres_password = random_password.postgres.result
    redis_password    = random_password.redis.result
    postgres_port     = local.postgres_port
    redis_port        = local.redis_port
  })

  # Replacing the instance must not wipe the databases: they live on the
  # separate volume below, which is never part of this resource.
  user_data_replace_on_change = true

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = true
  }

  metadata_options {
    http_tokens = "required" # IMDSv2 only
  }

  tags = { Name = "fsse-dev-box" }
}

resource "aws_ebs_volume" "data" {
  availability_zone = aws_instance.dev_box.availability_zone
  size              = var.data_volume_gb
  type              = "gp3"
  encrypted         = true

  tags = { Name = "fsse-dev-box-data" }

  lifecycle {
    prevent_destroy = true # your databases; `terraform destroy` must not take them
  }
}

resource "aws_volume_attachment" "data" {
  device_name = "/dev/sdf"
  volume_id   = aws_ebs_volume.data.id
  instance_id = aws_instance.dev_box.id
}

# An Elastic IP is free while it is attached to a running instance, and it keeps
# the address stable so stopping the box overnight does not change your .env.
resource "aws_eip" "dev_box" {
  instance = aws_instance.dev_box.id
  domain   = "vpc"

  tags = { Name = "fsse-dev-box" }
}
