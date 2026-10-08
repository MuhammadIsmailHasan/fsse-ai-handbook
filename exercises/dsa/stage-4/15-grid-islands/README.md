# DSA · Stage 4 · Grids Are Graphs: Islands and Flood Fill

> 🟡 Medium · 🚫🤖 No-AI · Target: O(rows × cols)

A map, a photo, a game board: a **grid** is a graph where every cell is a node and its neighbours are the cells **up, down, left and right**. You do not build the graph; you just compute the neighbours:

```python
for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
    if 0 <= nx < rows and 0 <= ny < cols:
        ...
```

```text
1 1 0 0 0
1 1 0 0 0        3 islands (up/down/left/right only), the biggest has 4 cells
0 0 1 0 0
0 0 0 1 1
```

| Function | Does |
|---|---|
| `count_islands(grid)` | for every land cell not yet seen, count +1 and **flood** its whole island |
| `max_island_area(grid)` | the same flood, but count the cells |
| `flood_fill(image, row, col, color)` | the paint-bucket tool; return a **new** image |

The big test is a 500 × 500 grid that is all land: one island of 250,000 cells. Recursion would crash, so flood with your own **stack** (or a queue). Mark cells as seen **when you push them**, not when you pop them, or the same cell enters many times.

```bash
cd exercises
uv run pytest dsa/stage-4/15-grid-islands
```
