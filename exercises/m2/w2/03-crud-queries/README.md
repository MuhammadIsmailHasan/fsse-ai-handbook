# M2 · W2 · 03 — CRUD Query Practice

> 🚫🤖 **No-AI** · ⏱️ ~60 min · needs the exercise database (`docker compose up -d`)

The tests load `seed.sql` (15 fictional job listings) into a fresh schema, then run **your** SQL files.
Explore the data first:

```bash
docker compose exec -T db psql -U fsse -d fsse -c "CREATE SCHEMA IF NOT EXISTS play"
docker compose exec -T db psql -U fsse -d fsse -c "SET search_path TO play" -f - < m2/w2/03-crud-queries/seed.sql
```

Or just paste `seed.sql` into your GUI client.

Write **one statement per file**. Column names and order must match exactly.

| File | Task |
|---|---|
| `q01_open_remote.sql` | `title, company` of **open, remote** jobs, ordered by `title` A→Z |
| `q02_salary_range.sql` | `title, salary_max` of jobs with `salary_max` **between 13.000.000 and 21.000.000** (inclusive), highest first, then `title` A→Z |
| `q03_engineer_titles.sql` | `title` of jobs whose title contains **"engineer"** in any capitalization, A→Z |
| `q04_missing_salary.sql` | `title` of jobs **without** salary information, A→Z |
| `q05_count_per_city.sql` | `city, total` — number of jobs per city (ignore rows with no city), most first, then city A→Z |
| `q06_avg_salary_busy_cities.sql` | `city, avg_max` — average `salary_max` **rounded to a whole number**, only cities with **at least 3 jobs that have a salary**, highest average first |
| `q07_latest_three.sql` | `title, posted_on` — the 3 most recently posted **open** jobs |
| `q08_insert.sql` | insert `('Platform Engineer', 'Garuda Pay', 'Jakarta', false, 17000000, 26000000, '2026-09-13')` and return `id, title, status` |
| `q09_close_old.sql` | close every **open** job posted **before 2026-08-29**; return `title` of the updated rows |
| `q10_delete_closed_without_salary.sql` | delete **closed** jobs with **no** `salary_max`; return `title` |

```bash
cd exercises
uv run pytest m2/w2/03-crud-queries
```
