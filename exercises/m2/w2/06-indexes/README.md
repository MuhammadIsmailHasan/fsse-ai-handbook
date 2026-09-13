# M2 · W2 · 06 — Make Slow Queries Fast

> 🚫🤖 **No-AI** · ⏱️ ~60 min · needs the exercise database (`docker compose up -d`)

`seed.sql` creates `users` (5,000 rows) and `applications` (60,000 rows). `queries.sql` shows four queries the app runs constantly.

1. Load the seed into a practice schema and run each query with `EXPLAIN ANALYZE`. Note the plan (`Seq Scan`?) and time.
2. Write `indexes.sql` with **at most 4** `CREATE INDEX` statements so that **none** of the four queries uses a sequential scan.
3. Re-run `EXPLAIN ANALYZE` and compare.

Rules checked by the tests:
- no `Seq Scan` on `applications` or `users` for Q1–Q4
- at most **4** new indexes in total (indexes cost disk space and slow down writes)
- Q3's index must be **partial** (only active applications) — it's smaller and cheaper to maintain

```bash
cd exercises
uv run pytest m2/w2/06-indexes
```
