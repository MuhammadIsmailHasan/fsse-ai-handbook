# Architecture · B · Build a TTL Cache

> 🚫🤖 **No-AI** · ⏱️ ~45 min

Implement in `ttl_cache.py`:

**`TTLCache(ttl_seconds, clock=time.monotonic)`**
- `set(key, value)` — stores the value; it expires `ttl_seconds` after being set
- `get(key, default=None)` — returns the value, or `default` if missing/expired (expired entries are removed)
- `delete(key)` — removes the key if present (no error if missing)
- `hits`, `misses` — counters updated by `get`

**`cached_fetch(cache, key, fetch)`** — cache-aside: return the cached value, or call `fetch()`, store the result, and return it. A fetched value of `None` is **not** cached.

```bash
cd exercises
uv run pytest architecture/b-system-design-basics/03-ttl-cache
```
