# DSA · Stage 3 · Binary Search Basics

> 🟢 Easy set · 🚫🤖 No-AI · Target: O(log n) each · `bisect` is not allowed (a test checks)

| Function | Example | Result |
|---|---|---|
| `find_index(sorted_nums, target)` | `[2, 5, 8, 12, 16], 12` | `3`; `-1` if absent (any matching index if there are duplicates) |
| `first_at_least(sorted_nums, x)` | `[10, 20, 20, 30], 20` | `1` — the first index whose value is `>= x`; `len(nums)` if none (a.k.a. *lower bound*) |
| `integer_sqrt(n)` | `27` | `5` — the largest integer `r` with `r * r <= n`, for `n >= 0`; no `math.isqrt`, `**0.5` or `sqrt` |

```bash
cd exercises
uv run pytest dsa/stage-3/13-binary-search-basics
```
