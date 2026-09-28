# Architecture · H · Saga Runner

> 🚫🤖 **No-AI** · ⏱️ ~30 min

Implement the saga pattern: run a chain of local steps, and if one fails, undo the completed ones with their compensations — in reverse order.

Each step is `{"name", "action", "compensate"}`; a failing `action` raises.

`run_saga(steps, ctx)` returns:
- success → `{"status": "committed", "committed": [...], "compensated": [], "failed_at": None}`
- failure → `{"status": "aborted", "committed": [...], "compensated": [undo order], "failed_at": name}`

The tests drive a booking saga (reserve stock → charge payment → create shipment) to full success and to a mid-way failure that must roll back the earlier steps newest-first.

```bash
cd exercises
uv run pytest architecture/h-distributed-systems/04-saga
```
