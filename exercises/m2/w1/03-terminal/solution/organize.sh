#!/usr/bin/env bash
# Reference solution.
set -euo pipefail
shopt -s nullglob   # a pattern with no matches expands to nothing, not the literal "*.log"

DIR="${1:?Usage: organize.sh DIR}"

if [[ ! -d "$DIR" ]]; then
  echo "Error: not a directory: $DIR" >&2
  exit 1
fi

moved=0

move_into() {
  local target="$1"
  shift
  for file in "$@"; do
    mkdir -p "$DIR/$target"
    mv "$file" "$DIR/$target/"
    moved=$((moved + 1))
  done
}

move_into logs "$DIR"/*.log
move_into data "$DIR"/*.csv "$DIR"/*.json
move_into images "$DIR"/*.png "$DIR"/*.jpg

echo "Moved $moved file(s)"
