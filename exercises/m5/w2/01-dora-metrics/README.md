# M5 · W2 · 01 — Measure delivery performance (DORA metrics)

> 🚫🤖 **No-AI** · ⏱️ ~75 min

You can't improve a pipeline you don't measure. The DORA research program uses four key metrics. Compute them from a team's deployment and incident records in `dora.py`.

## Data
```python
Deployment(id: str, environment: str, deployed_at: datetime, commits: list[datetime], outcome: str)
    # outcome: "success" | "failed" | "rolled_back"
Incident(id: str, deployment_id: str, started_at: datetime, resolved_at: datetime | None)
```
Only `environment == "production"` counts for every metric.

## Functions
1. `deployment_frequency(deployments, start, end) -> float` — production deployments with outcome `"success"` in `[start, end)` **per week** (`count / (days / 7)`), rounded to 2 decimals.
2. `lead_time_hours(deployments) -> float | None` — for **successful** production deployments, every commit's `deployed_at - commit_time` in hours; return the **median** of all those durations (rounded to 1 decimal), `None` if there are none.
3. `change_failure_rate(deployments, incidents) -> float | None` — a production deployment is a *failure* if its outcome is `"failed"` or `"rolled_back"` **or** any incident points to it; rate = failures / production deployments, rounded to 3 decimals; `None` if no production deployments.
4. `recovery_time_hours(incidents, deployments) -> float | None` — median `resolved_at - started_at` in hours (1 decimal) for **resolved** incidents linked to **production** deployments.
5. `classify(frequency_per_week, lead_time_hours, failure_rate, recovery_hours) -> str` — `"elite"`, `"high"`, `"medium"` or `"low"` using the handbook's simplified thresholds; a team gets the **lowest** level any metric reaches. `None` values are ignored.

| Level | Frequency (per week) | Lead time | Change failure rate | Recovery |
|---|---|---|---|---|
| elite | ≥ 7 | < 24 h | ≤ 0.05 | < 1 h |
| high | ≥ 1 | < 168 h | ≤ 0.10 | < 24 h |
| medium | ≥ 0.25 | < 720 h | ≤ 0.15 | < 168 h |
| low | anything else | | | |

```bash
cd exercises
uv run pytest m5/w2/01-dora-metrics
```
