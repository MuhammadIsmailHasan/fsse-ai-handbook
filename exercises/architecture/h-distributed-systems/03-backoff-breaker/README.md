# Architecture · H · Backoff & Circuit Breaker

> 🚫🤖 **No-AI** · ⏱️ ~35 min

Two resilience tools for a flaky dependency.

| Piece | Does |
|---|---|
| `backoff_delay(attempt, base, cap)` | `base * 2**attempt`, capped — wait longer each retry |
| `CircuitBreaker(threshold, cooldown)` | `closed → open → half-open` state machine |

The tests check the doubling-and-cap of the delays, then drive the breaker through a failure streak (→ open), the cooldown (→ half-open trial), recovery (→ closed), and a failed trial (→ open again).

The breaker takes an explicit `now` (float seconds) so tests are deterministic — never read the real clock.

```bash
cd exercises
uv run pytest architecture/h-distributed-systems/03-backoff-breaker
```
