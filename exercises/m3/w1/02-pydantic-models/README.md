# Module 3 · W1 · Validate & Clean with Pydantic v2

> 🚫🤖 **No-AI** · ⏱️ ~30 min

Build two models in `models.py`:

- **`Product`** — `name` (1–50 chars), `price` (> 0), `stock` (≥ 0, default 0), using `Field` constraints.
- **`Signup`** — `email` (a `field_validator` requiring `@`, stored lowercase), `password` (≥ 8 chars).

The tests parse valid data (including a numeric string coerced to a number), assert `ValidationError` on each broken rule, and check the email is lowercased.

```bash
cd exercises
uv run pytest m3/w1/02-pydantic-models
```
