# M2 · W1 · 05 — Merge Conflict Lab

> 🚫🤖 **No-AI** · ⏱️ ~30 min

```bash
cd exercises/m2/w1/05-git-collaboration
bash make_conflict.sh          # (re)creates conflict-lab/ with a conflicting merge in progress
cd conflict-lab
git status
```

## What each branch wanted

`pricing.py` has `final_price(price, is_member)`.

- **`main`** added **tax**: the result must include 11% tax, rounded down: `price * 111 // 100`.
- **`feature/discount`** added a **member discount**: members pay 10% less, rounded down, applied **before** tax.

The correct merged behavior keeps **both**:

| price | is_member | result |
|---|---|---|
| 100_000 | False | 111_000 |
| 100_000 | True | 99_900 |

Both branches also added a line to `CHANGELOG.md` — keep **both** lines.

## Finish

1. Edit the conflicted files: combine both intentions, remove all conflict markers.
2. `git add pricing.py CHANGELOG.md`
3. `git commit --no-edit`
4. From `exercises/`: `uv run pytest m2/w1/05-git-collaboration`
