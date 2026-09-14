# M5 · W1 · 04 — Redis patterns: cache, stampede lock, rate limit, reliable queue, idempotency

> 🚫🤖 **No-AI** · ⏱️ ~2.5 h

Implement five production patterns in `redis_patterns.py` against a **real Redis** (port **6391**). Every function receives a `redis.Redis` client created with `decode_responses=True`.

```bash
cd exercises
docker compose up -d redis
uv run pytest m5/w1/04-redis-patterns
```

## 1. Cache-aside with TTL jitter
`cache_aside(r, key, ttl, loader, *, jitter=0.1, rng=random.random)`
- cache hit → return the JSON-decoded value (don't call `loader`)
- miss → `value = loader()`; if `value is None` return `None` **without caching**; else store `json.dumps(value)` with an expiry of `ttl + int(ttl * jitter * rng())` seconds and return it

`invalidate(r, *keys) -> int` deletes keys and returns how many existed.

## 2. Stampede protection
`cache_with_lock(r, key, ttl, loader, *, lock_ttl_ms=5000, poll_interval=0.02, max_wait=2.0)`
- hit → return it
- miss → try to take `lock:<key>` with `SET NX PX` and a **random token**
  - got the lock → re-check the cache (someone may have just filled it), otherwise call `loader`, cache it with `ttl` (no jitter), then **release the lock only if you still own it** (compare the token atomically with a Lua script)
  - didn't get it → poll the cache every `poll_interval`; if a value appears return it; after `max_wait` call `loader` yourself (don't cache) — never wait forever
- 20 threads asking for the same missing key → `loader` runs **once**

## 3. Sliding-window rate limiter
`SlidingWindowRateLimiter(r, *, limit, window_seconds, prefix="ratelimit", clock=time.time)` with `allow(identity) -> tuple[bool, float]`
- sorted set `"{prefix}:{identity}"`; scores are timestamps
- remove entries older than `now - window_seconds`; if fewer than `limit` remain, add `now` (with a unique member) and return `(True, 0.0)`
- otherwise return `(False, retry_after)` where `retry_after = oldest_score + window_seconds - now` (rounded to 3 decimals) and **don't** record the denied request
- set the key's expiry to `ceil(window_seconds)`
- must be **atomic** (one Lua script) so concurrent requests can't exceed the limit

## 4. Reliable queue
`ReliableQueue(r, name, *, clock=time.time)`
- `enqueue(payload: dict) -> str` — job id (`uuid4().hex`), pushes `{"id", "payload"}` as JSON; FIFO
- `reserve(timeout: float = 1.0) -> Job | None` — atomically moves one job from `"{name}:ready"` to `"{name}:processing"` (`BLMOVE`), records the reservation time in hash `"{name}:reserved_at"`; returns `Job(id, payload, raw)` or `None` after `timeout`
- `ack(job) -> None` — removes it from processing and from the hash
- `requeue_stale(older_than: float) -> int` — jobs reserved more than `older_than` seconds ago go back to the **front** of ready (they're next); returns how many
- `ready_count()` / `processing_count()`

## 5. Idempotency
`run_once(r, key, ttl, action)` for duplicate webhooks and double-clicked "Pay" buttons:
- `SET key "__pending__" NX EX ttl`; if acquired: `result = action()`, store `json.dumps(result)` keeping the TTL, return `(result, True)`
- if `action` raises → delete the key (so a retry can run) and re-raise
- key exists with a stored result → `(json.loads(result), False)` without calling `action`
- key exists but still pending → raise `InProgressError`
