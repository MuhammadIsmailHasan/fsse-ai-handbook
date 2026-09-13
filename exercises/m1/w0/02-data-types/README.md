# M1 · W0 · 02 — Convert Raw Form Input

> 🚫🤖 **No-AI** · ⏱️ ~30 min · Lesson: *Data Containers: Variables & Data Types*

A sign-up form sends every field as **text**. Complete the functions in `form_data.py` so the rest of the app gets clean, correctly typed values.

| Function | Input example | Output |
|---|---|---|
| `parse_age(text)` | `" 25 "` | `25` |
| `parse_height_m(text)` | `"172"` (centimeters) | `1.72` |
| `parse_newsletter(text)` | `" YES "` | `True` |
| `describe_user(name, age)` | `"Ana", 20` | `"Ana (20 years old)"` |

`parse_newsletter` returns `True` only for `yes`, `y` or `true` (any capitalization, surrounding spaces allowed). Everything else is `False`.

## Run the checks

```bash
cd exercises
uv run pytest m1/w0/02-data-types
```

## Stretch 🏆

Add `parse_price_idr(text)`: `"Rp 15.000"` → `15000`, `"15000"` → `15000`.
