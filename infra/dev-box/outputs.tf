output "instance_id" {
  description = "Used by scripts/devbox.sh to start and stop the box."
  value       = aws_instance.dev_box.id
}

output "public_ip" {
  description = "Stable address of the dev box."
  value       = aws_eip.dev_box.public_ip
}

output "ssh_command" {
  description = "Empty when ssh_public_key_path is unset; use ssm_command instead."
  value       = var.ssh_public_key_path != "" ? "ssh ec2-user@${aws_eip.dev_box.public_ip}" : ""
}

output "ssm_command" {
  description = "Shell on the box with no open SSH port (needs the Session Manager plugin)."
  value       = "aws ssm start-session --region ${var.region} --target ${aws_instance.dev_box.id}"
}

output "env_block" {
  description = "Paste into .env to point the exercises at the dev box instead of local Docker."
  sensitive   = true
  value = join("\n", [
    "# FSSE dev box (AWS) — practice credentials only",
    "DEVBOX_INSTANCE_ID=${aws_instance.dev_box.id}",
    "DEVBOX_HOST=${aws_eip.dev_box.public_ip}",
    "DATABASE_URL=postgresql://fsse:${random_password.postgres.result}@${aws_eip.dev_box.public_ip}:5491/fsse",
    "REDIS_URL=redis://:${random_password.redis.result}@${aws_eip.dev_box.public_ip}:6391/0",
  ])
}

output "region" {
  description = "Used by scripts/devbox.sh so it does not need AWS_REGION set."
  value       = var.region
}
