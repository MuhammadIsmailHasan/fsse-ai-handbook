# M2 · W2 · 01 — Your First PostgreSQL Table

> 🚫🤖 **No-AI** · ⏱️ ~40 min · needs the exercise database: `cd exercises && docker compose up -d`

Write `study_log.sql` that creates this table and inserts **3 rows**:

| Column | Rules |
|---|---|
| `id` | `bigint`, identity, primary key |
| `topic` | text, required |
| `minutes` | integer, required, between **1 and 600** |
| `studied_on` | date, required, defaults to today |
| `mood` | text, optional, only `'great'`, `'ok'` or `'tired'` |
| `created_at` | `timestamptz`, required, defaults to now |

Insert 3 rows **without** specifying `id`, `studied_on` or `created_at` (let the defaults work).

```bash
cd exercises
uv run pytest m2/w2/01-postgres-setup
```
