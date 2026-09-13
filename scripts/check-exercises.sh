#!/usr/bin/env bash
# check-exercises.sh — verify every exercise is set up correctly:
#   1. the STARTER code fails its tests (so the exercise is not already solved)
#   2. the SOLUTION passes the same tests
#
# Usage (from the project root):  bash scripts/check-exercises.sh [folder-filter]
set -uo pipefail

cd "$(dirname "$0")/../exercises"
filter="${1:-}"
status=0
tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

while IFS= read -r solution_dir; do
  exercise_dir="$(dirname "$solution_dir")"
  [[ -n "$filter" && "$exercise_dir" != *"$filter"* ]] && continue

  # Starter must FAIL
  if uv run pytest "$exercise_dir" -q -p no:cacheprovider >/dev/null 2>&1; then
    echo "⚠️  starter already passes: $exercise_dir"
    status=1
  fi

  # Solution must PASS: copy tests + solution files into a temp folder
  tmp="$tmp_root/$(echo "$exercise_dir" | tr '/' '_')"
  mkdir -p "$tmp"
  cp "$exercise_dir"/test_*.py "$tmp"/
  [[ -d "$exercise_dir/data" ]] && cp -R "$exercise_dir/data" "$tmp"/
  cp -R "$solution_dir"/. "$tmp"/
  if uv run pytest "$tmp" -q -p no:cacheprovider >/dev/null 2>&1; then
    echo "✅ $exercise_dir"
  else
    echo "❌ solution fails: $exercise_dir"
    uv run pytest "$tmp" -q -p no:cacheprovider 2>&1 | tail -15
    status=1
  fi
done < <(find . -type d -name solution -not -path "./.venv/*" | sort)

exit $status
