#!/usr/bin/env bash
# Build the handbook and publish it to S3 + CloudFront.
#
#   ./scripts/deploy-handbook.sh
#
# Reads HANDBOOK_BUCKET / HANDBOOK_DISTRIBUTION_ID / HANDBOOK_REGION from the
# environment or .env; falls back to `terraform output` in infra/handbook-site.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if [[ -f .env ]]; then
  # shellcheck disable=SC1091
  set -a && source .env && set +a
fi

tf_output() {
  terraform -chdir=infra/handbook-site output -raw "$1" 2>/dev/null || true
}

bucket="${HANDBOOK_BUCKET:-$(tf_output bucket_name)}"
distribution="${HANDBOOK_DISTRIBUTION_ID:-$(tf_output distribution_id)}"
region="${HANDBOOK_REGION:-ap-southeast-1}"

if [[ -z "$bucket" || -z "$distribution" ]]; then
  cat >&2 <<'MSG'
Missing bucket or distribution id.
Run `terraform apply` in infra/handbook-site first, then either:
  - add HANDBOOK_BUCKET and HANDBOOK_DISTRIBUTION_ID to .env, or
  - run this script from the repo root so it can read terraform output.
MSG
  exit 1
fi

echo "==> Checking content before publishing"
npm run -s content:check

echo "==> Building"
npm run -s build

echo "==> Uploading hashed assets (cache for a year — the filename changes when the file does)"
aws s3 sync dist/ "s3://$bucket/" \
  --region "$region" \
  --delete \
  --exclude "index.html" \
  --size-only \
  --cache-control "public,max-age=31536000,immutable"

echo "==> Uploading index.html (never cached, so a deploy is visible immediately)"
aws s3 cp dist/index.html "s3://$bucket/index.html" \
  --region "$region" \
  --cache-control "no-cache,must-revalidate" \
  --content-type "text/html; charset=utf-8"

echo "==> Invalidating the CloudFront cache"
invalidation_id=$(aws cloudfront create-invalidation \
  --distribution-id "$distribution" \
  --paths "/index.html" "/" \
  --query 'Invalidation.Id' --output text)

echo "    invalidation $invalidation_id created (usually live within a minute)"
echo
echo "Done: https://$(aws cloudfront get-distribution --id "$distribution" --query 'Distribution.DomainName' --output text)"
