# DSA · Stage 3 · Sorting Basics

> 🟢 Easy set · 🚫🤖 No-AI

| Function | What | Target |
|---|---|---|
| `rank_jobs(jobs)` | Return a **new** list of job dicts ordered by: `salary_max` high → low (`None` **last**), then `posted_on` newest first (`"YYYY-MM-DD"` strings), then `title` A → Z | O(n log n), one `sorted` call with a key |
| `merge_intervals(intervals)` | Merge overlapping `[start, end]` ranges (touching ranges like `[1, 3]` and `[3, 5]` **do** merge); return them sorted by start | O(n log n) |
| `kth_largest(nums, k)` | The k-th largest value (`k = 1` is the maximum; duplicates count) with `1 <= k <= len(nums)` | O(n log k) with `heapq` |

```python
merge_intervals([[8, 10], [1, 3], [2, 6], [15, 18]])   # [[1, 6], [8, 10], [15, 18]]
kth_largest([3, 2, 1, 5, 6, 4], 2)                     # 5
```

```bash
cd exercises
uv run pytest dsa/stage-3/17-sorting-basics
```
