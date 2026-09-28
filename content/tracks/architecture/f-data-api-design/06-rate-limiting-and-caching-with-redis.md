---
title: "Rate Limiting & Caching with Redis"
summary: Two jobs Redis does well — rate limiting to protect your API from overload, and caching hot reads so the database isn't asked the same question repeatedly — with token-bucket and cache-aside built by hand.
type: lesson
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: core }
durationMinutes: 130
tags: [architecture, redis, rate-limiting, caching, performance, api]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Why an API needs **rate limiting**, and the **token-bucket** idea
- Why **caching** hot reads protects your database
- The **cache-aside** pattern and what **TTL** means
- **Cache invalidation**: the hard part, and how to handle stale data
- Why Redis is the usual home for both
- How this connects to RevoShop (Module 5 already added Redis)

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Rate limit** | A cap on how many requests someone may make | Batas jumlah request |
| **Token bucket** | A bucket of tokens that refills over time; each request spends one | Ember token yang terisi ulang |
| **Cache** | A fast store of answers you computed recently | Simpanan jawaban cepat |
| **Cache-aside** | Check cache first; on a miss, load from DB and store it | Cek cache dulu, baru DB |
| **TTL** | Time to live — how long a cached value stays valid | Umur data di cache |
| **Cache hit / miss** | The answer was / wasn't already in the cache | Ada / tidak ada di cache |
| **Invalidation** | Removing stale cache entries when data changes | Membuang cache basi |
| **Redis** | A fast in-memory key-value store used for both jobs | Penyimpan cepat di memori |

## 🧠 The big idea

- **Rate limiting** is the **turnstile at a stadium**: it lets people in at a safe pace so the stands don't get crushed. One person can't shove through 10,000 times a second.
- **Caching** is a **notepad by the phone**: the first time someone asks "what are today's hours?", you look it up and jot it down; the next hundred callers get the answer from the notepad, not another trip to check.

Both keep your slow, precious resource (the database) from being hammered.

## ❓ Why it matters

Without rate limiting, one buggy client or one attacker can flood your API and take the whole site down for everyone — and if your API costs money per call (an AI model), it can also drain your budget in minutes.

Without caching, your database answers the exact same popular query thousands of times a second. It becomes the bottleneck, and everything slows down. Caching turns "ask the database every time" into "ask once, reuse the answer".

## 📖 Step by step

### 1. Rate limiting with a token bucket

Give each user a **bucket** that holds up to N **tokens** and refills at a steady rate. Every request spends one token. Empty bucket → request is rejected (HTTP `429 Too Many Requests`).

```python
class TokenBucket:
    def __init__(self, capacity, refill_per_sec):
        self.capacity = capacity
        self.refill_per_sec = refill_per_sec
        self.tokens = capacity
        self.last = 0.0

    def allow(self, now, cost=1):
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.refill_per_sec)
        self.last = now
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False        # 429: slow down
```

Why a bucket and not a plain counter? It allows short **bursts** (spend saved tokens) while still capping the long-run rate — friendlier than a hard "N per minute" wall.

### 2. Where the limit lives: Redis

In real apps you run many server copies, so the count can't live in one server's memory. It lives in **Redis**, which all servers share, and Redis is fast enough to check on every request.

### 3. Caching: don't ask the same question twice

Reading a popular product page hits the database every time. Put the answer in a cache (Redis) so repeat reads are near-instant.

### 4. The cache-aside pattern

The most common caching pattern:

```python
def get_product(cache, db, product_id, now, ttl=60):
    hit = cache.get(product_id)
    if hit and hit["expires"] > now:
        return hit["value"], "hit"          # fast path
    value = db.load(product_id)             # miss: go to the slow source
    cache[product_id] = {"value": value, "expires": now + ttl}
    return value, "miss"
```

- **Hit**: the value was in the cache and still fresh → return it fast.
- **Miss**: not there (or expired) → load from the database, store it with a **TTL**, return it.

The `ttl` (time to live) is your safety net: even if you forget to remove a stale entry, it expires on its own after a while.

### 5. The hard part: invalidation

> "There are only two hard things in Computer Science: cache invalidation and naming things." — Phil Karlton

If a product's price changes but the cache still holds the old price, users see the wrong number. Two common fixes:

| Strategy | How | Trade-off |
|---|---|---|
| **TTL only** | Let entries expire after N seconds | Simple; users may see stale data up to N seconds |
| **Write-through / delete-on-write** | When you update the DB, also delete/update the cache key | Fresh immediately; more code, must not miss a write path |

A common combo: delete the cache key on write **and** keep a short TTL as a backstop.

### Choosing what and how to cache

| Situation | Do this |
|---|---|
| Read often, changes rarely (product catalog) | Cache with a longer TTL |
| Read often, changes often (stock count) | Short TTL, or don't cache the volatile field |
| Must always be exact (account balance) | Don't cache; read the source |
| Public API open to the internet | Rate limit per user/IP |
| Expensive/paid downstream (AI calls) | Rate limit **and** cache results |

- ✅ Cache hot, rarely-changing reads; give every entry a TTL.
- ✅ Delete or update the cache key when the underlying data changes.
- ✅ Rate limit public and expensive endpoints; return `429` with a `Retry-After`.
- 🚫 Don't cache data that must be exact right now (balances, live stock for checkout).

## ⚠️ Common mistakes

- Caching with no TTL, so stale data lives forever after a missed invalidation.
- Forgetting to clear the cache on one of the write paths, so some updates never show.
- Rate limiting in a single server's memory, so it resets/varies across server copies.
- Caching per-user private data under a shared key, leaking one user's data to another.
- No rate limit on an endpoint that calls a paid API — one loop drains the budget.

:::revoshop
Module 5 already added Redis to RevoShop. (1) Which reads are hot and rarely change — the product catalog? Product detail? Give a TTL and say how you'd invalidate on a price/stock update. (2) Which data must **not** be cached at checkout (live stock, the buyer's cart total) and why? (3) Where would a rate limit protect RevoShop — login attempts, the payment endpoint, or a public search? What would you return when the limit is hit?
:::

## 🏆 Best practices

- [ ] Rate limit public, auth, and paid-downstream endpoints; respond `429` with `Retry-After`.
- [ ] Keep rate-limit state in Redis so it's shared across all server copies.
- [ ] Cache hot, slow, rarely-changing reads; always set a TTL as a backstop.
- [ ] Invalidate (delete/update the key) on every write path that changes the cached data.
- [ ] Namespace cache keys and never share a key across users for private data.
- [ ] Never cache data that must be exact at that instant (balances, checkout stock).

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain rate limiting with the stadium-turnstile analogy and caching with the notepad-by-the-phone analogy. Then explain why cache invalidation is famously hard: what goes wrong when the data changes but the notepad still shows the old answer.

## 📐 Design it

CareerPilot has an AI endpoint `POST /suggestions` that calls a paid LLM (slow and costs money per call), and a `GET /companies/:id` endpoint hit constantly by list pages. Design: (a) a rate limit for the AI endpoint and what you return when it's exceeded; (b) a cache for the companies endpoint including TTL and how you invalidate when a company's info is edited; (c) which of the two you would cache results for and why.

:::quiz
Show a possible design

- **(a) AI endpoint rate limit**: token bucket per user in Redis, e.g. capacity 5, refill 1 token / 12s (≈5/min with small bursts). On empty bucket return `429` with `Retry-After: <seconds>` so the client knows when to try again. This protects both the LLM budget and the service.
- **(b) Companies cache (cache-aside)**: on `GET`, check Redis (`company:<id>`); hit → return; miss → load from DB, store with TTL 300s. On an edit to a company, **delete** `company:<id>` (delete-on-write) so the next read repopulates it; the TTL is a backstop if a write path is missed.
- **(c) Cache which?** Cache the **companies** reads (same answer, read constantly, changes rarely). For AI **suggestions**, cache only if the same input reliably gives the same output (e.g. hash the prompt) — otherwise rate limiting is the main protection, not caching.

**Rule shown:** rate limit expensive/public endpoints; cache hot rarely-changing reads with a TTL and delete-on-write invalidation.
:::

### 📝 Self-review checklist

- [ ] Rate limit placed on expensive/public endpoints with a `429` + `Retry-After`
- [ ] Cache has a TTL and a clear invalidation on write
- [ ] Shared state (limits, cache) lives in Redis, not one server's memory
- [ ] Nothing that must be exact is cached; no private data under shared keys

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/architecture/f-data-api-design/06-ratelimit-cache" ai="no-ai" title="Token-bucket limiter and cache-aside"}
Implement a token-bucket rate limiter (refills over time, allows short bursts, rejects when empty) and a cache-aside `get` (hit returns fast; miss loads from a source, stores with a TTL, and expires). The tests prove the limiter refills after waiting and that the loader runs only on misses.
:::

:::hints
- Pass `now` (a float seconds value) into every call so tests are deterministic — don't read the real clock.
- Bucket refill: `tokens = min(capacity, tokens + (now - last) * refill_per_sec)`, update `last = now`, then spend if enough.
- Cache-aside: treat an entry as a miss if it's absent **or** `entry["expires"] <= now`; count loader calls to prove misses vs hits.
:::

## ✅ Quick check

:::quiz
Why keep rate-limit counts and caches in Redis instead of in each server's memory?

Because real apps run many server copies. In-memory state would differ per server (a limit that resets when a request hits a different server, or caches that don't share). Redis is a shared, fast store all servers use, so the limit and cache are consistent everywhere.
:::

:::quiz
What is cache invalidation, and why is it hard?

It's removing or updating cached entries when the underlying data changes. It's hard because you must catch *every* write path that affects the cached value; miss one and users keep seeing stale data — which is why a TTL is kept as a backstop.
:::

## 📚 Keep learning

- [Redis: caching patterns](https://redis.io/learn/howtos/solutions/caching-architecture/write-through)
- [Cloudflare: what is rate limiting?](https://www.cloudflare.com/learning/bots/what-is-rate-limiting/)
- [Token bucket algorithm](https://en.wikipedia.org/wiki/Token_bucket)
