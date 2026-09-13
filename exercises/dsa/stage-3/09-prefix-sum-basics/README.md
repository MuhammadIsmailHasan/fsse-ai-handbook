# DSA · Stage 3 · Prefix Sum Basics

> 🟢 Easy set · 🚫🤖 No-AI

| Function | Example | Result | Target |
|---|---|---|---|
| `running_totals(nums)` | `[3, 1, 4]` | `[3, 4, 8]` | O(n) |
| `range_sums(nums, queries)` | `[2, 4, 1, 5], [(0, 1), (1, 3), (2, 2)]` | `[6, 10, 1]` — sum of `nums[i..j]` **inclusive** | O(n + q) |
| `pivot_index(nums)` | `[1, 7, 3, 6, 5, 6]` | `3` — the **leftmost** index where the sum left of it equals the sum right of it; `-1` if none | O(n) |

```bash
cd exercises
uv run pytest dsa/stage-3/09-prefix-sum-basics
```
