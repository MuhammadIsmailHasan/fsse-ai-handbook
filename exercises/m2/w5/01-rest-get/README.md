# M2 · W5 · 01 — Filter, Sort and Paginate Job Listings

> 🚫🤖 **No-AI** · ⏱️ ~90 min · needs the exercise database (`docker compose up -d`)

Provided: `app.py` (factory + JSON error handler for `ApiError`), `models.py` (`Job`), `seed.py` (60 fictional jobs). Implement `jobs.py` (blueprint `jobs`, prefix `/api/v1/jobs`).

## `GET /api/v1/jobs`

| Param | Rules |
|---|---|
| `city` | optional, case-insensitive exact match |
| `remote` | optional, `true`/`false` |
| `min_salary` | optional integer ≥ 0 → jobs with `salary_max >= min_salary` |
| `sort` | optional, default `-posted_on`; comma-separated fields from `posted_on`, `salary_max`, `title`, optional `-` prefix; tie-breaker `id` in the direction of the **last** field |
| `page` | integer ≥ 1, default 1 |
| `per_page` | integer 1–100, default 20 |

Invalid/unknown value for **any** param → raise `ApiError(422, "invalid_query", message, fields)` with a field → message dict. Unknown **param names** → `422` too (field name → `"unknown parameter"`).

Response:
```json
{
  "data": [{"id": 1, "title": "...", "company": "...", "city": "...", "remote": true, "salary_max": 14000000, "posted_on": "2026-09-01"}],
  "meta": {"page": 1, "per_page": 20, "total": 60, "total_pages": 3},
  "links": {"self": "/api/v1/jobs?page=1&per_page=20", "next": "/api/v1/jobs?page=2&per_page=20", "prev": null}
}
```
Links keep the other query parameters (in the order: filters, sort, page, per_page — only those the client sent plus page/per_page).

`salary_max` sorting: `NULL`s last in both directions.

## `GET /api/v1/jobs/feed` — keyset pagination
Always ordered newest first (`posted_on DESC, id DESC`). Params: `limit` (1–100, default 20), `cursor` (optional, opaque). Response: `{"data": [...], "meta": {"limit": 20, "next_cursor": "…" | null}}`. Invalid cursor → `422`.

## `GET /api/v1/jobs/<int:job_id>`
`{"data": job}`; missing → `ApiError(404, "job_not_found", ...)`.

```bash
cd exercises
uv run pytest m2/w5/01-rest-get
```
