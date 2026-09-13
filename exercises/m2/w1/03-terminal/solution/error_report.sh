#!/usr/bin/env bash
# Reference solution.
set -euo pipefail

LOG_FILE="${1:?Usage: error_report.sh LOG_FILE}"

if [[ ! -f "$LOG_FILE" ]]; then
  echo "Error: file not found: $LOG_FILE" >&2
  exit 1
fi

# The level is the 2nd field. `|| true` because awk/grep finding nothing is not an error here.
errors=$(awk '$2 == "ERROR"' "$LOG_FILE" | wc -l | tr -d ' ')
echo "Errors: $errors"
echo "Top failing endpoints:"

awk '$2 == "ERROR" {print $3, $4}' "$LOG_FILE" \
  | sort | uniq -c \
  | sort -k1,1nr -k2,2 -k3,3 \
  | head -n 3 \
  | awk '{print $1, $2, $3}' || true
