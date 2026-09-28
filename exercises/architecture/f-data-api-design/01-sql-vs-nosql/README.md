# Architecture · F · Model the Same Data Two Ways

> 🚫🤖 **No-AI** · ⏱️ ~30 min

Model the same orders as a **relational** store (users and orders kept separate) and as a **document** store (each order embeds a copy of the user's name). Then feel the trade-off when a user changes their name.

| Function | Model | Does |
|---|---|---|
| `order_total(order)` | both | Sum `qty * price` over items |
| `join_orders(orders, users)` | relational | Look up each order's user by id → `{order_id, user_name, total}` |
| `rename_user_relational(users, id, name)` | relational | Rename in **one** place; return `1` |
| `rename_user_document(orders, id, name)` | document | Rename in **every** order that copied the name; return how many changed |

The tests show the point: the relational rename is a single write, while the document rename must touch one record per order — the cost of denormalizing.

```bash
cd exercises
uv run pytest architecture/f-data-api-design/01-sql-vs-nosql
```
