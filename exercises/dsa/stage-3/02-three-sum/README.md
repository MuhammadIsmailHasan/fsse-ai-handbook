# DSA · Stage 3 · Three Budgets That Balance

> 🟡 Medium · 🚫🤖 No-AI · Target: O(n²)

A finance team wants every combination of **three** budget adjustments that cancel out to zero.

`three_sum_zero(nums)` → all **unique** triplets `[a, b, c]` with `a + b + c == 0`:
- each triplet sorted ascending (`a <= b <= c`)
- the list of triplets sorted ascending
- no duplicate triplets, even if the input has duplicates

```python
three_sum_zero([-1, 0, 1, 2, -1, -4])   # [[-1, -1, 2], [-1, 0, 1]]
three_sum_zero([0, 0, 0, 0])            # [[0, 0, 0]]
```

Sort first, fix the first number, then use two pointers for the other two. Skip duplicates instead of using a set of results.

```bash
cd exercises
uv run pytest dsa/stage-3/02-three-sum
```
