# DSA · Stage 2 · Spiral Seat Map

> 🔴 Stretch · 🚫🤖 No-AI · Target: O(rows × cols)

An interview room assigns seats in a spiral starting top-left, going right. Return the values in spiral order.

```python
spiral_order([[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9]])        # [1, 2, 3, 6, 9, 8, 7, 4, 5]

spiral_order([[1, 2, 3, 4],
              [5, 6, 7, 8]])     # [1, 2, 3, 4, 8, 7, 6, 5]
```

- The matrix is rectangular; it may be empty (`[]`) or have empty rows (`[[]]`)
- Don't modify the input
- Hint: keep four boundaries — `top`, `bottom`, `left`, `right` — and shrink them after each side

```bash
cd exercises
uv run pytest dsa/stage-2/04-spiral-order
```
