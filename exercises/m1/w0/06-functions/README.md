# M1 · W0 · 06 — From Copy-Paste to Functions

> 🚫🤖 **No-AI** · ⏱️ ~45 min · Lesson: *Functions*

`pricing.py` starts as a copy-pasted script (read it — spot the duplication and the bug!). Replace it with these functions:

| Function | Example | Result |
|---|---|---|
| `format_rupiah(amount)` | `1500000` | `"Rp 1.500.000"` |
| `apply_discount(price, percent=10)` | `199_999` | `179_999` |
| `line_total(price, qty)` | `25_000, 3` | `75_000` |
| `cart_total(items)` | `[(25_000, 3), (10_000, 1)]` | `85_000` |
| `receipt(items, discount_percent=0)` | see below | string |

`receipt([(25_000, 3), (10_000, 1)], discount_percent=10)` returns exactly:

```text
25.000 x 3 = Rp 75.000
10.000 x 1 = Rp 10.000
Subtotal: Rp 85.000
Discount (10%): -Rp 8.500
Total: Rp 76.500
```

When `discount_percent` is `0`, leave out the `Discount` line.
Unit prices on item lines have **no** `Rp` prefix; amounts after `=` do.

```bash
cd exercises
uv run pytest m1/w0/06-functions
```
