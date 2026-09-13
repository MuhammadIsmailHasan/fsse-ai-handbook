# DSA · Stage 2 · Longest Streak

> 🟡 Medium · 🚫🤖 No-AI · Target: **O(n)** — sorting is not allowed

A learner's study log lists the day numbers they studied (unsorted, with duplicates). Find their longest streak of consecutive days.

```python
longest_streak([100, 4, 200, 1, 3, 2])   # 4  (1, 2, 3, 4)
longest_streak([0, 3, 7, 2, 5, 8, 4, 6, 0, 1])  # 9
longest_streak([])                         # 0
```

Hint: put everything in a set. A number starts a streak only if `n - 1` is **not** in the set — only then count upward.

```bash
cd exercises
uv run pytest dsa/stage-2/07-longest-consecutive
```
