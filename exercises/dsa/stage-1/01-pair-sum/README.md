# DSA · Stage 1 · Pair With Target Sum

> 🟢 Easy · Target: O(n) time

`has_pair_with_sum(nums, target)` → `True` if two **different positions** add up to `target`.

```python
has_pair_with_sum([3, 9, 4, 7], 11)  # True (4 + 7)
has_pair_with_sum([5], 10)           # False (can't use the same position twice)
has_pair_with_sum([5, 5], 10)        # True
```

```bash
cd exercises
uv run pytest dsa/stage-1/01-pair-sum
```

Write your complexity (time + space) as a comment above the function.
