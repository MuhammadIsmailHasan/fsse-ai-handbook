# M2 · W3 · 02 — Statuses, Commands and Events

> 🚫🤖 **No-AI** · ⏱️ ~50 min

## Status transitions

| From | Allowed next |
|---|---|
| `wishlist` | `applied`, `withdrawn` |
| `applied` | `interview`, `rejected`, `withdrawn` |
| `interview` | `interview`, `offer`, `rejected`, `withdrawn` |
| `offer` | `offer_accepted`, `offer_declined` |
| `rejected`, `withdrawn`, `offer_accepted`, `offer_declined` | — (terminal) |

- `next_status(current, target)` → `target`, or raise `InvalidTransition` (also for unknown statuses)
- `allowed_next(current)` → sorted list; unknown status raises `InvalidTransition`

## `parse_command(text)` — use `match`

| Input | Returns |
|---|---|
| `"add Kopi Data Analyst"` | `{"action": "add", "company": "Kopi", "role": "Data Analyst"}` *(first word = company)* |
| `"move 12 interview"` | `{"action": "move", "id": 12, "status": "interview"}` |
| `"list"` | `{"action": "list", "status": None}` |
| `"list offer"` | `{"action": "list", "status": "offer"}` |
| `"help"` | `{"action": "help"}` |
| anything else, `"add Kopi"` (no role), `"move x interview"` | raise `ValueError` |

Extra spaces are ignored; the command word is case-insensitive (`"MOVE 3 offer"` works).

## `describe_event(event)` — use mapping patterns

| Event | Returns |
|---|---|
| `{"type": "application.created", "company": "Kopi Data", …}` | `"New application at Kopi Data"` |
| `{"type": "status.changed", "to": "offer"}` or `"offer_accepted"` | `"🎉 Offer!"` |
| `{"type": "status.changed", "to": "<other>"}` | `"Status changed to <other>"` |
| `{"type": "<other string>"}` | `"Ignored event <other string>"` |
| anything else | raise `ValueError` |

```bash
cd exercises
uv run pytest m2/w3/02-control-flow
```
