# M1 · W1 · 01 — Counting Toolkit

> 🚫🤖 **No-AI** · ⏱️ ~45 min · Lesson: *Counting & Frequency Algorithms*

Implement the functions in `counting.py` **without** `collections.Counter`.

| Function | Example | Result |
|---|---|---|
| `count_items(items)` | `["a", "b", "a"]` | `{"a": 2, "b": 1}` |
| `most_frequent(items)` | `["b", "a", "b", "a", "c"]` | `["a", "b"]` |
| `first_duplicate(items)` | `["x", "y", "z", "y", "x"]` | `"y"` |
| `count_skills(skill_strings)` | `["Python, SQL", "python"]` | `{"python": 2, "sql": 1}` |
| `top_skills(skill_strings, n)` | `(…, 1)` | `[("python", 2)]` |

```bash
cd exercises
uv run pytest m1/w1/01-counting
```
