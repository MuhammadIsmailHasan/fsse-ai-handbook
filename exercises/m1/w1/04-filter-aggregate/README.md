# M1 · W1 · 04 — Job Market Insights

> 🚫🤖 **No-AI** · ⏱️ ~50 min · Lesson: *Filtering, Aggregation & Combining*

| Function | Result |
|---|---|
| `remote_titles(jobs, min_salary)` | titles of remote jobs with salary ≥ min, original order |
| `group_by_city(jobs)` | `{city: [jobs]}` |
| `city_summary(jobs)` | `{city: {"count", "average_salary", "remote_share"}}` (whole numbers, rounded down) |
| `attach_company(jobs, companies)` | new dicts with `"company"` name or `None`; inputs unchanged |
| `unique_emails(emails)` | case-insensitive de-dup, first spelling kept, order kept |

```bash
cd exercises
uv run pytest m1/w1/04-filter-aggregate
```
