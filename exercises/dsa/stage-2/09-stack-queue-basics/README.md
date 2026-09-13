# DSA · Stage 2 · Stack & Queue Basics

> 🟢 Easy set · 🚫🤖 No-AI

| Task | Example | Result | Target |
|---|---|---|---|
| `is_balanced(text)` | `"fn(a[i]) { return {x: 1}; }"` | `True` — every `()[]{}` closes in the right order; other characters are ignored | O(n) |
| `apply_backspaces(text)` | `"ab#c##d"` | `"d"` — `#` deletes the previous kept character (nothing if none) | O(n) |
| `MinStack` | `push(5); push(2); push(7); get_min()` | `2` | `push`, `pop`, `top`, `get_min` all **O(1)** |

`MinStack.pop()`, `top()` and `get_min()` on an empty stack raise `IndexError`. `pop()` returns the removed value.

```bash
cd exercises
uv run pytest dsa/stage-2/09-stack-queue-basics
```
