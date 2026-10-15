#!/usr/bin/env bash
# Start, stop and inspect the AWS dev box that runs Postgres + Redis.
#
#   ./scripts/devbox.sh start     # before a learning session
#   ./scripts/devbox.sh stop      # after  — a stopped box costs only its disks
#   ./scripts/devbox.sh status
#   ./scripts/devbox.sh env       # the DATABASE_URL / REDIS_URL to paste into .env
#   ./scripts/devbox.sh shell     # shell on the box via Session Manager
#   ./scripts/devbox.sh logs      # docker compose logs for the services
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tf="terraform -chdir=$repo_root/infra/dev-box"

instance_id="${DEVBOX_INSTANCE_ID:-$($tf output -raw instance_id 2>/dev/null || true)}"
region="$($tf output -raw region 2>/dev/null || echo "${AWS_REGION:-ap-southeast-3}")"

if [[ -z "$instance_id" ]]; then
  echo "No dev box found. Run \`terraform apply\` in infra/dev-box first." >&2
  exit 1
fi

case "${1:-status}" in
  start)
    aws ec2 start-instances --region "$region" --instance-ids "$instance_id" >/dev/null
    echo "Starting $instance_id ..."
    aws ec2 wait instance-running --region "$region" --instance-ids "$instance_id"
    echo "Running at $($tf output -raw public_ip). Postgres and Redis come up a few seconds later."
    ;;
  stop)
    aws ec2 stop-instances --region "$region" --instance-ids "$instance_id" >/dev/null
    echo "Stopping $instance_id. The Elastic IP and your data are kept."
    ;;
  status)
    aws ec2 describe-instances --region "$region" --instance-ids "$instance_id" \
      --query 'Reservations[0].Instances[0].{state:State.Name,type:InstanceType,ip:PublicIpAddress}' \
      --output table
    ;;
  env)
    $tf output -raw env_block
    echo
    ;;
  shell)
    exec aws ssm start-session --region "$region" --target "$instance_id"
    ;;
  logs)
    aws ssm start-session --region "$region" --target "$instance_id" \
      --document-name AWS-StartInteractiveCommand \
      --parameters 'command=["sudo docker compose -f /etc/fsse/compose.yaml logs --tail=50"]'
    ;;
  *)
    echo "usage: $0 {start|stop|status|env|shell|logs}" >&2
    exit 2
    ;;
esac
