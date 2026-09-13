# DSA · Stage 3 · Periods With an Exact Net Change

> 🟡 Medium · 🚫🤖 No-AI · Target: O(n)

A wallet app records daily net changes (positive **and negative**). How many periods of consecutive days have a net change of exactly `k`?

`count_periods(changes, k)` → the number of contiguous subarrays whose sum is exactly `k`.

```python
count_periods([1, 1, 1], 2)        # 2
count_periods([3, 4, -7, 7, 0], 7) # 5   ([3, 4], [3, 4, -7, 7], [3, 4, -7, 7, 0], [7], [7, 0])
count_periods([], 0)               # 0
```

A sliding window doesn't work with negative numbers. Instead: `sum(i..j) == k` ⇔ `prefix[j + 1] - prefix[i] == k`. Count how many earlier prefix sums equal `current - k` with a dict.

```bash
cd exercises
uv run pytest dsa/stage-3/10-subarray-sum-equals-k
```
