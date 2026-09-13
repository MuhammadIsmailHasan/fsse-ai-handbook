#!/usr/bin/env bash
# Creates ./conflict-lab: a repo with a merge conflict in progress. Safe to run again.
set -euo pipefail
cd "$(dirname "$0")"

rm -rf conflict-lab
mkdir conflict-lab
cd conflict-lab

git init -q -b main
git config user.name "Conflict Lab"
git config user.email "lab@example.com"

cat > pricing.py <<'PY'
def final_price(price: int, is_member: bool) -> int:
    return price
PY
printf "# Changelog\n" > CHANGELOG.md
git add . && git commit -qm "feat: add final_price"

git switch -qc feature/discount
cat > pricing.py <<'PY'
def final_price(price: int, is_member: bool) -> int:
    if is_member:
        price = price * 90 // 100
    return price
PY
printf "# Changelog\n- Members get a 10%% discount\n" > CHANGELOG.md
git commit -qam "feat(pricing): add member discount"

git switch -q main
cat > pricing.py <<'PY'
def final_price(price: int, is_member: bool) -> int:
    return price * 111 // 100
PY
printf "# Changelog\n- Prices include 11%% tax\n" > CHANGELOG.md
git commit -qam "feat(pricing): include tax"

git merge feature/discount >/dev/null 2>&1 || true
echo "conflict-lab ready. Next: cd conflict-lab && git status"
