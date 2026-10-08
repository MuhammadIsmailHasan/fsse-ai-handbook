# DSA · Stage 4 · Shortest Paths on Grids (BFS)

> 🔴 Hard · 🚫🤖 No-AI · Target: O(rows × cols)

BFS gives the shortest path when every move costs the same. Two ideas make these problems fast:

1. **Distance by level.** Process the queue one *round* at a time. After round `k`, you have reached everything that is `k` moves away. The number of rounds is the answer.
2. **Multi-source BFS.** If many cells can be the start (all rotten oranges, all zeros), put them **all** in the queue at the beginning. One BFS then finds each cell's distance to its *nearest* start. Running a BFS from every cell would be far too slow.

```text
oranges (2 = rotten):          minute 0   minute 1   minute 2 ...
 2 1 1                           2 1 1      2 2 1      2 2 2
 1 1 0       → 4 minutes         1 1 0      2 1 0      2 2 0
 0 1 1                           0 1 1      0 1 1      0 2 1
```

| Function | Does |
|---|---|
| `maze_steps(maze, start, end)` | fewest moves through `.` cells avoiding `#`, or `-1` |
| `rotting_oranges(grid)` | minutes until nothing fresh is left, or `-1` |
| `nearest_zero(matrix)` | distance to the nearest `0` for every cell |

```bash
cd exercises
uv run pytest dsa/stage-4/16-grid-shortest
```
