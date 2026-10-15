# DSA · Stage 5 · N-Queens

> 🔴 Hard · 🚫🤖 No-AI · Target: O(n!) branches, O(1) conflict checks

The classic. Place `n` queens on an `n × n` board so none attacks another — along rows, columns or either diagonal.

Two decisions turn this from hopeless into easy:

**1. One queen per row.** You never *choose* a row, you only choose a column for row 0, then row 1, and so on. Row clashes become impossible by construction instead of by checking.

**2. Three sets instead of a board scan.** Every cell on the same diagonal shares a number:

```text
row + col  (↗ rising)          row - col  (↘ falling)
  0 1 2 3                        0 -1 -2 -3
  1 2 3 4                        1  0 -1 -2
  2 3 4 5                        2  1  0 -1
  3 4 5 6                        3  2  1  0
```

So a cell is attacked when `col in columns or row + col in rising or row - col in falling` — three set lookups, O(1), instead of walking the board. This is the difference between `n=9` finishing instantly and timing out.

| Function | Does |
|---|---|
| `count_queen_placements(n)` | how many complete solutions exist |
| `first_queen_board(n)` | one board as strings, or `None`; try columns left to right |

Known counts: `1 → 1`, `2 → 0`, `3 → 0`, `4 → 2`, `5 → 10`, `6 → 4`, `7 → 40`, `8 → 92`, `9 → 352`.

```bash
cd exercises
uv run pytest dsa/stage-5/04-n-queens
```
