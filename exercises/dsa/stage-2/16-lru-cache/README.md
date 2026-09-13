# DSA · Stage 2 · LRU Cache

> 🔴 Stretch · 🚫🤖 No-AI · Target: `get` and `put` in **O(1)**

Cache CareerPilot's expensive company lookups. When the cache is full, evict the **least recently used** entry.

```python
cache = LRUCache(capacity=2)
cache.put("kopi", 1)
cache.put("awan", 2)
cache.get("kopi")      # 1   ("kopi" is now most recently used)
cache.put("batik", 3)  # evicts "awan"
cache.get("awan")      # None
len(cache)             # 2
```

- `get(key)` → value or `None`; a successful `get` makes the key most recently used
- `put(key, value)` inserts or updates (an update also makes it most recently used)
- `len(cache)` → number of entries; `capacity >= 1`
- **Build it yourself**: a dict for key → node plus a **doubly linked list** for recency order. `OrderedDict` and `functools.lru_cache` are not allowed (a test checks).

```bash
cd exercises
uv run pytest dsa/stage-2/16-lru-cache
```
