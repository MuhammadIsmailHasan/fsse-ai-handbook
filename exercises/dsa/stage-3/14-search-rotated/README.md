# DSA · Stage 3 · Search a Rotated Schedule

> 🟡 Medium · 🚫🤖 No-AI · Target: O(log n)

A list of **distinct**, sorted meeting times was rotated at an unknown point (e.g. a week view starting on Thursday):
`[13, 15, 18, 2, 5, 9, 11]`.

`search_rotated(nums, target)` → the index of `target`, or `-1`.

```python
search_rotated([13, 15, 18, 2, 5, 9, 11], 5)    # 4
search_rotated([13, 15, 18, 2, 5, 9, 11], 14)   # -1
search_rotated([1, 3], 3)                       # 1  (a rotation of 0 is allowed)
```

At every `mid`, **one half is sorted**. Check whether the target lies inside that sorted half; if yes search there, otherwise search the other half.

```bash
cd exercises
uv run pytest dsa/stage-3/14-search-rotated
```
