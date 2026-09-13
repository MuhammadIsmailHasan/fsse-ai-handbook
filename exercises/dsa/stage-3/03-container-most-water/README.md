# DSA · Stage 3 · Biggest Billboard Frame

> 🟡 Medium · 🚫🤖 No-AI · Target: O(n)

Poles of different heights stand in a row, 1 metre apart. A banner hangs between **two** poles; its height is limited by the **shorter** pole and its width is the distance between them.

`max_banner_area(heights)` → the largest possible area (`min(h[i], h[j]) * (j - i)`), or `0` with fewer than two poles.

```python
max_banner_area([1, 8, 6, 2, 5, 4, 8, 3, 7])   # 49  (poles 1 and 8: min(8, 7) * 7)
```

Start with the widest pair. Which pointer should move inward, and why can moving the taller one never help?

```bash
cd exercises
uv run pytest dsa/stage-3/03-container-most-water
```
