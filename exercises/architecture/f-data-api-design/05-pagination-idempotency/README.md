# Architecture · F · Pagination & Idempotency

> 🚫🤖 **No-AI** · ⏱️ ~35 min

Three production API habits, in code.

| Function | Does |
|---|---|
| `offset_page(items, offset, limit)` | Classic "skip N, take M" |
| `cursor_page(items, after_id, limit)` | "Next M after this id" → `(page, next_cursor)` |
| `create_payment(store, key, amount)` | Idempotent create — charges **once** per key |

The tests show the point:
- **Cursor** paging stays stable when a new row is inserted; **offset** can serve the same row twice.
- A retried payment with the **same idempotency key** returns the first result and never double-charges.

```bash
cd exercises
uv run pytest architecture/f-data-api-design/05-pagination-idempotency
```
