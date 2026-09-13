# DSA · Stage 2 · Sliding-Window Rate Limiter

> 🔴 Stretch · 🚫🤖 No-AI · Target: amortized O(1) per request

Protect CareerPilot's login endpoint: each user may make at most `limit` requests in any `window` seconds.

```python
limiter = RateLimiter(limit=3, window=10)
limiter.allow("siti", now=0)    # True
limiter.allow("siti", now=1)    # True
limiter.allow("siti", now=2)    # True
limiter.allow("siti", now=3)    # False  (3 requests in the last 10 s)
limiter.allow("budi", now=3)    # True   (separate user)
limiter.allow("siti", now=10)   # True   (the request at t=0 is now outside the window)
```

Rules:
- A previous request at time `t` counts while `now - t < window`
- **Rejected** requests are not recorded
- `now` never goes backwards (per the caller's clock)
- `limit >= 1`, `window > 0`

Keep a `collections.deque` of timestamps per user: evict old ones from the **left**, append new ones on the **right**. A test sends 300,000 requests to check it stays fast.

```bash
cd exercises
uv run pytest dsa/stage-2/12-rate-limiter
```
