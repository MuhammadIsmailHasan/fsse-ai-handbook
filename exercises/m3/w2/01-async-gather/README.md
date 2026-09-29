# Module 3 · W2 · Sequential vs Concurrent I/O

> 🚫🤖 **No-AI** · ⏱️ ~25 min

Implement two async functions that call a fake `fetch` for several ids:

- `fetch_all_sequential` — await them one-by-one.
- `fetch_all_concurrent` — run them all at once with `asyncio.gather`.

A shared `Tracker` counts calls "in flight". The tests prove — with no timing, fully deterministic — that the sequential version never exceeds **1** in flight, while the concurrent version reaches **all** of them at once.

```bash
cd exercises
uv run pytest m3/w2/01-async-gather
```
