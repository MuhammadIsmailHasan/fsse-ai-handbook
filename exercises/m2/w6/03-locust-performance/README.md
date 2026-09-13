# M2 · W6 · 03 — Load Testing with Locust

> 🤖✅ **AI-allowed** (explain every line) · ⏱️ ~75 min · no database needed

Provided: `target_app.py` — an in-memory job board (read its docstring) — and `sample_stats.csv`, a Locust results file from a bigger run.

## Part 1 — `analyze.py` (results → decisions)
- `load_stats(path)` → `EndpointStats` rows from a Locust `*_stats.csv`. Skip the `Aggregated` row and rows with 0 requests. `p95_ms` comes from the `95%` column; `N/A` means `0`.
- `EndpointStats.failure_rate` → `failures / requests` (0.0 when there are no requests).
- `slo_violations(stats, max_p95_ms, max_failure_rate)` → messages sorted by endpoint name; for each endpoint, the p95 message comes before the failure message:
  - `"GET /api/v1/jobs/search: p95 1480ms > 500ms"`
  - `"GET /api/v1/jobs: failure rate 10.0% > 1.0%"`
- `slowest(stats, n=3)` → endpoint names by p95, highest first (ties: by name).

## Part 2 — `locustfile.py` (a realistic user)
A `JobSeeker(HttpUser)` with think time `between(1, 3)`:
| Behavior | Requirement |
|---|---|
| `on_start` | log in **once** (`POST /api/v1/login` with any email/password), keep the token |
| browse (weight **5**) | `GET /api/v1/jobs` — use `catch_response=True` and mark the **degraded** 200 responses (no `data` key) as failures |
| view (weight **3**) | `GET /api/v1/jobs/<random 1..50>` |
| save (weight **1**) | `POST /api/v1/jobs/<random 1..50>/save` with `Authorization: Bearer <token>` |
| names | group with `name=`: `POST /api/v1/login`, `GET /api/v1/jobs`, `GET /api/v1/jobs/[id]`, `POST /api/v1/jobs/[id]/save` |

The tests start `target_app.py`, run **your** user for 3 seconds (with think time shortened), and inspect the CSV.

```bash
cd exercises
uv run pytest m2/w6/03-locust-performance

# Try it yourself with the web UI (two terminals):
uv run python m2/w6/03-locust-performance/target_app.py --port 5092
uv run locust -f m2/w6/03-locust-performance/locustfile.py --host http://127.0.0.1:5092 --web-port 8191
# open http://localhost:8191
```
