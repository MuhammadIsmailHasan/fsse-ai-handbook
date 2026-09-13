# DSA · Stage 3 · Fair Sprint Split

> 🔴 Stretch · 🚫🤖 No-AI · Target: O(n log(sum))

A backlog of tasks (story points, in priority order) must be split into **exactly `k` consecutive, non-empty sprints**. Minimize the points of the **heaviest** sprint.

`min_heaviest_sprint(points, k)` → that minimal maximum.

```python
min_heaviest_sprint([7, 2, 5, 10, 8], 2)   # 18  ([7, 2, 5] | [10, 8])
min_heaviest_sprint([1, 2, 3, 4, 5], 2)    # 9   ([1, 2, 3] | [4, 5])
min_heaviest_sprint([1, 4, 4], 3)          # 4
```

- `points` non-empty, non-negative; `1 <= k <= len(points)`
- Why can "at most k sprints" be checked greedily, and why is that enough for "exactly k"? Explain it in a comment.

```bash
cd exercises
uv run pytest dsa/stage-3/16-split-largest-sum
```
