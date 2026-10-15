output "url" {
  description = "Open this in a browser to read the handbook."
  value       = "https://${aws_cloudfront_distribution.site.domain_name}"
}

output "bucket_name" {
  description = "Pass to scripts/deploy-handbook.sh as HANDBOOK_BUCKET."
  value       = aws_s3_bucket.site.id
}

output "distribution_id" {
  description = "Pass to scripts/deploy-handbook.sh as HANDBOOK_DISTRIBUTION_ID."
  value       = aws_cloudfront_distribution.site.id
}

output "deploy_env" {
  description = "Copy-paste block for your shell or .env file."
  value = join("\n", [
    "HANDBOOK_BUCKET=${aws_s3_bucket.site.id}",
    "HANDBOOK_DISTRIBUTION_ID=${aws_cloudfront_distribution.site.id}",
    "HANDBOOK_REGION=${var.region}",
  ])
}
