#!/usr/bin/env bash
# check-web-exercises.sh — verify every JavaScript/TypeScript exercise in exercises/web:
#   1. the STARTER code fails its tests
#   2. the SOLUTION passes the same tests
#
# Usage (from the project root):  bash scripts/check-web-exercises.sh [folder-filter]
set -uo pipefail

cd "$(dirname "$0")/../exercises/web"
[[ -d node_modules ]] || npm install --silent
filter="${1:-}"
status=0
tmp_root="$(pwd)/.check-tmp"
rm -rf "$tmp_root" && mkdir -p "$tmp_root"
trap 'rm -rf "$tmp_root"' EXIT

while IFS= read -r solution_dir; do
  exercise_dir="$(dirname "$solution_dir")"
  [[ -n "$filter" && "$exercise_dir" != *"$filter"* ]] && continue

  if npx vitest run "$exercise_dir" --reporter=dot >/dev/null 2>&1; then
    echo "⚠️  starter already passes: $exercise_dir"
    status=1
  fi

  tmp="$tmp_root/$(echo "$exercise_dir" | tr '/' '_')"
  mkdir -p "$tmp"
  cp -R "$exercise_dir"/. "$tmp"/
  rm -rf "$tmp/solution"
  cp -R "$solution_dir"/. "$tmp"/
  if npx vitest run "$tmp" --reporter=dot >/dev/null 2>&1; then
    echo "✅ $exercise_dir"
  else
    echo "❌ solution fails: $exercise_dir"
    npx vitest run "$tmp" 2>&1 | tail -30
    status=1
  fi
done < <(find . -type d -name solution -not -path "./node_modules/*" -not -path "./.check-tmp/*" | sort)

exit $status
