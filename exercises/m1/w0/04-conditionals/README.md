# M1 · W0 · 04 — Grades, Status Codes and Shipping

> 🚫🤖 **No-AI** · ⏱️ ~40 min · Lesson: *Conditionals*

Implement the functions in `rules.py`:

| Function | Rules |
|---|---|
| `letter_grade(score)` | A 90–100 · B 80–89 · C 70–79 · D 60–69 · E 0–59 · `ValueError` outside 0–100 |
| `status_category(code)` | 1xx informational · 2xx success · 3xx redirect · 4xx client error · 5xx server error · else unknown |
| `shipping_cost(weight_kg, express, member)` | `None` if weight ≤ 0 · express: 15.000 member / 25.000 non-member · regular: 0 member / 10.000 non-member |

```bash
cd exercises
uv run pytest m1/w0/04-conditionals
```
