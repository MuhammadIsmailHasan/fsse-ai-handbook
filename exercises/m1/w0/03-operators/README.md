# M1 · W0 · 03 — Checkout Rules

> 🚫🤖 **No-AI** · ⏱️ ~30 min · Lesson: *Operators*

Implement the functions in `checkout.py`.

| Function | Example | Result |
|---|---|---|
| `split_bill(total, people)` | `split_bill(100_000, 3)` | `(33333, 1)` |
| `page_count(total_items, per_page)` | `page_count(10, 3)` | `4` |
| `is_even(n)` | `is_even(7)` | `False` |
| `gets_free_shipping(cart_total, is_member, is_oversized)` | `(500_000, True, False)` | `True` |

Free shipping: members with a cart **of at least Rp 500.000**, never for oversized items.

```bash
cd exercises
uv run pytest m1/w0/03-operators
```

Stretch 🏆: `shipping_fee(weight_kg)` — see the lesson.
