# DSA · Stage 3 · Minimum Daily Review Capacity

> 🟡 Medium · 🚫🤖 No-AI · Target: O(n log(sum))

A hiring team must review applications **in order**, each with a size (pages). They review whole applications only, and must finish within `days`. What's the smallest daily page capacity that makes it possible?

`min_daily_capacity(sizes, days)`:

```python
min_daily_capacity([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5)   # 15
min_daily_capacity([3, 2, 2, 4, 1, 4], 3)                # 6
min_daily_capacity([1, 2, 3, 1, 1], 4)                   # 3
```

- `sizes` non-empty, positive; `1 <= days <= len(sizes)`
- **Binary search on the answer**: capacity `c` works → any bigger `c` works too. Search between `max(sizes)` and `sum(sizes)` with a greedy `can_finish(c)` check.

```bash
cd exercises
uv run pytest dsa/stage-3/15-min-daily-capacity
```
