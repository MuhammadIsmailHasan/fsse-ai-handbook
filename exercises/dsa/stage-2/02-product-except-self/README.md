# DSA · Stage 2 · Product of Everything Else

> 🟡 Medium · 🚫🤖 No-AI · Target: O(n) time, **no division**

A dashboard shows, for each team, the product of all **other** teams' growth factors.

`product_except_self(nums)` → a list where `result[i]` is the product of every element except `nums[i]`.

```python
product_except_self([2, 3, 4, 5])   # [60, 40, 30, 24]
product_except_self([1, 0, 3])      # [0, 3, 0]
```

- `len(nums) >= 2`; values can be negative or zero
- Don't use `/` or `//` (a test checks) — think "product of everything to my left × everything to my right"

```bash
cd exercises
uv run pytest dsa/stage-2/02-product-except-self
```
