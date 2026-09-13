# DSA · Stage 3 · Longest Streak Under Budget

> 🟡 Medium · 🚫🤖 No-AI · Target: O(n)

A bootcamp student has daily course costs (all **positive**). What is the longest run of **consecutive** days they can afford with a fixed budget?

`longest_affordable(costs, budget)` → the maximum number of consecutive days whose total cost is `<= budget` (`0` if no single day fits).

```python
longest_affordable([3, 1, 2, 7, 4, 2, 1, 1, 5], 8)   # 4  (4 + 2 + 1 + 1)
longest_affordable([10, 20], 5)                     # 0
```

Because costs are positive, adding a day never lowers the total — so when the window is over budget, shrinking from the left is always right. (Why does this break with negative numbers? The lesson explains.)

```bash
cd exercises
uv run pytest dsa/stage-3/07-longest-under-budget
```
