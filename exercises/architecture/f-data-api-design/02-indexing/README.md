# Architecture · F · Build a Tiny Index

> 🚫🤖 **No-AI** · ⏱️ ~30 min

Feel why an index matters. A linear search reads **every** row; an index jumps straight to the matches. A composite `(user_id, status)` index serves a query on `user_id` alone — but not on `status` alone.

| Function | Does |
|---|---|
| `linear_search(rows, field, value)` | Scan all rows → `(matches, scanned)`; `scanned == len(rows)` always |
| `build_index(rows, field)` | `{value: [rows]}` for one column |
| `indexed_search(index, value)` | O(1) lookup; `[]` if absent |
| `build_composite_index(rows, a, b)` | `{(a, b): [rows]}` |
| `search_composite_by_first(index, a)` | Serve a query on the first column by scanning the composite keys |

The tests show a composite index has no key for the *second* column alone — mirroring a phone book sorted by (last, first) that can't find a first name by itself.

```bash
cd exercises
uv run pytest architecture/f-data-api-design/02-indexing
```
