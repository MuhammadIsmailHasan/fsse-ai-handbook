# Architecture · B · Latency and Capacity Calculator

> 🚫🤖 **No-AI** · ⏱️ ~30 min

| Function | Example | Result |
|---|---|---|
| `percentile(samples_ms, p)` | `[10..100 step 10], 90` | `90` — nearest-rank method |
| `sequential_latency(calls_ms)` | `[80, 400, 60]` | `540` |
| `parallel_latency(calls_ms)` | `[80, 400, 60]` | `400` (`0` for none) |
| `average_rps(daily_users, requests_per_user)` | `100_000, 20` | `23.148…` |
| `peak_rps(daily_users, requests_per_user, peak_factor)` | `100_000, 20, 10` | `231.48…` |
| `max_throughput(concurrency, latency_ms)` | `10, 50` | `200.0` |

**Nearest-rank percentile:** sort the samples, take the item at position `ceil(p / 100 × n)` counting from 1. `percentile([], p)` raises `ValueError`.

```bash
cd exercises
uv run pytest architecture/b-system-design-basics/01-latency-budget
```
