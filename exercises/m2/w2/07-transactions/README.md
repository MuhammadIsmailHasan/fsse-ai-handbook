# M2 · W2 · 07 — All-or-Nothing Checkout

> 🚫🤖 **No-AI** · ⏱️ ~60 min · needs the exercise database (`docker compose up -d`)

`shop_schema.sql` (provided) creates `products`, `orders` and `order_items`. Implement `place_order(conn, user_id, items)` in `checkout.py` with **psycopg 3**:

- `items` is a list of `(product_id, quantity)` tuples
- In **one transaction**:
  1. for each item, decrease `stock` — but only if enough stock exists
  2. create one `orders` row with the correct `total`
  3. create one `order_items` row per item with the **current price** as `unit_price`
- Return the new order id
- If **any** product doesn't exist or has insufficient stock, raise `OutOfStock(product_id)` and leave the database **completely unchanged**
- Raise `ValueError` for an empty `items` list or a quantity ≤ 0 (before touching the database)
- Two customers buying the **last unit at the same time**: exactly one succeeds

`conn` is a psycopg connection in autocommit mode; use `with conn.transaction():` to group statements.

```bash
cd exercises
uv run pytest m2/w2/07-transactions
```
