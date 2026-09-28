# Architecture · F · Rate Limiter & Cache-Aside

> 🚫🤖 **No-AI** · ⏱️ ~35 min

Build the two things Redis is famous for.

**`TokenBucket`** — allows short bursts up to `capacity`, refills `refill_per_sec` tokens/second, rejects when empty (your API would return HTTP 429).

**`CacheAside`** — `get` returns fast on a hit; on a miss it runs the loader, stores the value with a TTL, and expires it. `invalidate` drops a key on write.

Both take an explicit `now` (float seconds) so tests are deterministic — never read the real clock.

The tests prove the bucket refills after waiting (but never exceeds capacity) and that the loader runs **only** on misses.

```bash
cd exercises
uv run pytest architecture/f-data-api-design/06-ratelimit-cache
```
