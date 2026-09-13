# M2 · W3 · 01 — Make It Pythonic

> 🚫🤖 **No-AI** · ⏱️ ~40 min

`legacy.py` works but isn't Pythonic. Write the **same four functions** in `pythonic.py`:

| Function | Behavior (same as legacy) |
|---|---|
| `numbered_titles(jobs)` | `["1. Backend Dev", "2. QA", …]` for jobs that are remote **and** have a salary |
| `pair_scores(names, scores)` | dict name → score; raise `ValueError` if lengths differ |
| `initials(full_name)` | `"ana putri"` → `"AP"`; extra spaces ignored |
| `count_lines_with(path, word)` | number of lines in a UTF-8 text file containing `word` (case-insensitive) |

Style rules checked: no `range(len(…))`, no `== None` / `!= None` / `== True` / `== False`, no variables named `list`, `dict`, `str`, `id`, `type`, `input`, `sum`, `max`, `min`; file reads with `with` and `encoding="utf-8"`.

```bash
cd exercises
uv run pytest m2/w3/01-pythonic-syntax
```
