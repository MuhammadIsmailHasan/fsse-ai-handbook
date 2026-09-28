# Architecture · H · Queue, Idempotent Consumer & Dead-Letter

> 🚫🤖 **No-AI** · ⏱️ ~30 min

Build the moving parts behind async messaging.

| Piece | Does |
|---|---|
| `Queue` | FIFO: `enqueue`, `dequeue` (oldest first, `None` when empty), `len()` |
| `consume_idempotently(processed, handler, msg)` | Run each message id at most once → `"processed"` / `"duplicate"` |
| `process_with_retries(handler, msg, max_attempts)` | Retry a failing handler → `("done", n)` or `("dead-letter", n)` |

The tests replay a **duplicate** message (proving the consumer doesn't double-send) and a **permanently failing** one (proving it dead-letters instead of retrying forever).

```bash
cd exercises
uv run pytest architecture/h-distributed-systems/02-queue-consumer
```
