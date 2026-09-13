# M1 · W0 · 05 — Loop It

> 🚫🤖 **No-AI** · ⏱️ ~45 min · Lesson: *Lists and Loops*

Implement the functions in `loops.py` **with your own loops** — no `sum`, `max`, `min` or list comprehensions this time. (A test checks for it!)

| Function | Example | Result |
|---|---|---|
| `cart_total(prices)` | `[10, 20, 30]` | `60` |
| `count_expensive(prices, limit)` | `[10, 50, 60], 40` | `2` |
| `highest_price(prices)` | `[]` | `None` |
| `first_over(prices, limit)` | `[10, 50, 60], 40` | `50` |
| `longest_streak(steps, goal)` | `[12000, 11000, 2000, 10000], 10000` | `2` |

```bash
cd exercises
uv run pytest m1/w0/05-lists-and-loops
```
