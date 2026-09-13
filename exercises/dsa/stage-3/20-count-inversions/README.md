# DSA · Stage 3 · How Different Are Two Rankings?

> 🔴 Stretch · 🚫🤖 No-AI · Target: O(n log n)

CareerPilot compares its job ranking with a user's own ranking. A simple measure is the number of **inversions**: pairs `(i, j)` with `i < j` but `nums[i] > nums[j]`. 0 means identical order; `n(n-1)/2` means fully reversed.

`count_inversions(nums)` → the number of inversions. Don't modify `nums`.

```python
count_inversions([2, 4, 1, 3, 5])   # 3  → (2,1), (4,1), (4,3)
count_inversions([1, 2, 3])         # 0
count_inversions([3, 2, 1])         # 3
```

Brute force is O(n²). Modify **merge sort**: while merging, when you take an item from the right half, every item still waiting in the left half is bigger — count them all at once.

```bash
cd exercises
uv run pytest dsa/stage-3/20-count-inversions
```
