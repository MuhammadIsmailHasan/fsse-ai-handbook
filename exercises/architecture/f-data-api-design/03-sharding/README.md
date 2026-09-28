# Architecture · F · Shard Router & Resharding Cost

> 🚫🤖 **No-AI** · ⏱️ ~30 min

Build the routing logic behind replication and sharding, then measure why resharding hurts.

| Function | Does |
|---|---|
| `shard_for(key, n)` | Pick a shard `[0, n)` with a **stable** hash (same every run) |
| `route(operation)` | Writes → `"primary"`, reads → `"replica"` |
| `keys_moved_on_resize(keys, old_n, new_n)` | Count keys that change shard when resizing |

The last test shows naive `hash % n` sharding moves **most** keys when you add one shard — the reason production systems use consistent hashing.

```bash
cd exercises
uv run pytest architecture/f-data-api-design/03-sharding
```
