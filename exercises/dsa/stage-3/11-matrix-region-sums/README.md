# DSA · Stage 3 · Heatmap Region Totals

> 🟡 Medium · 🚫🤖 No-AI · Target: O(rows × cols) preprocessing, **O(1) per query**

A job-map heatmap stores applications per grid cell. Users drag rectangles and want totals instantly.

`RegionSums(grid)` precomputes; `total(r1, c1, r2, c2)` returns the sum of the rectangle with corners `(r1, c1)` and `(r2, c2)`, **inclusive**, where `r1 <= r2` and `c1 <= c2`.

```python
grid = [[3, 0, 1, 4],
        [5, 6, 3, 2],
        [1, 2, 0, 1]]
sums = RegionSums(grid)
sums.total(0, 0, 1, 1)   # 14  (3 + 0 + 5 + 6)
sums.total(1, 1, 2, 3)   # 14  (6 + 3 + 2 + 2 + 0 + 1)
```

Build `prefix[r + 1][c + 1]` = sum of the rectangle from `(0, 0)` to `(r, c)`, then use inclusion–exclusion.

```bash
cd exercises
uv run pytest dsa/stage-3/11-matrix-region-sums
```
