# DSA · Stage 5 · Combination Sum & Equal Groups

> 🟡 Medium · 🚫🤖 No-AI · Target: pruned backtracking

Three questions that look alike but differ in one rule each:

| Function | The rule | The trick |
|---|---|---|
| `combination_sum(candidates, target)` | a candidate may be **reused** | recurse with the **same** index |
| `combination_sum_once(candidates, target)` | each element used **once**, no duplicate results | sort, then `if i > start and a[i] == a[i-1]: continue` |
| `can_split_into_equal_groups(nums, k)` | split everything into k equal sums | pruning, pruning, pruning |

Two prunings carry the first two functions:

```python
if ordered[i] > remaining:
    break          # sorted, so every later candidate is too big too
```

The third function is where backtracking stops being a template and starts being thinking. A plain search over 16 numbers and 4 groups is billions of branches; the same search with four cheap checks answers instantly:

- the total must divide by `k`, and the biggest number must fit in one group
- sort **big to small**, so hopeless branches die at the top of the tree
- never try two groups that currently hold the **same** amount
- if a number fails in an **empty** group, no other empty group will help — stop

```bash
cd exercises
uv run pytest dsa/stage-5/02-combination-sum
```
