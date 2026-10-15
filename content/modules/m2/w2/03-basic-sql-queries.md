---
title: "Basic SQL Queries: INSERT, SELECT, UPDATE, DELETE"
summary: Create, read, update and delete data safely — filtering, sorting, NULL handling, aggregates with GROUP BY and HAVING, and parameterized queries.
type: lesson
source: core
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: recommended }
durationMinutes: 180
tags: [sql, postgresql, crud, aggregates]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- The four operations behind almost every app: **C**reate, **R**ead, **U**pdate, **D**elete
- Filtering (`WHERE`, `LIKE/ILIKE`, `IN`, `BETWEEN`) and sorting (`ORDER BY`, `LIMIT`, `OFFSET`)
- Why `NULL` is special
- Summarizing data with `COUNT`, `SUM`, `AVG`, `GROUP BY` and `HAVING`
- Making `UPDATE`/`DELETE` safe, and why **parameterized queries** prevent SQL injection

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **CRUD** | The four basic actions: create, read, update, delete | Empat operasi dasar data |
| **Declarative** | You say *what* you want; the database decides *how* | Menyatakan hasil, bukan caranya |
| **`WHERE`** | The filter that picks which rows | Penyaring baris |
| **`NULL`** | "Unknown" — not zero, and not equal to anything, even itself | Nilai tidak diketahui |
| **Aggregate** | A function that summarises many rows (`COUNT`, `SUM`, `AVG`) | Fungsi peringkas |
| **`GROUP BY`** | Making one result row per group | Mengelompokkan hasil |
| **`HAVING`** | A filter applied *after* grouping | Penyaring setelah pengelompokan |
| **Pagination** | Showing results page by page (`LIMIT` / `OFFSET`) | Membagi hasil per halaman |
| **Parameterized query** | Passing values separately so they can never become SQL code | Kueri dengan nilai terpisah |
| **SQL injection** | An attack where user text becomes part of your SQL | Penyisipan perintah SQL |

## 🧠 The big idea

SQL is **declarative**: you describe **what** you want, and the database works out **how** to get it.

> "Give me the titles of open remote jobs, sorted by title."

```sql
SELECT title FROM job_listings WHERE status = 'open' AND is_remote ORDER BY title;
```

You wrote no loop, no index lookup and no sorting algorithm. It's like ordering *nasi goreng* instead of explaining every step of cooking it — you did the cooking yourself in Module 1; now the database does it, very efficiently.

## ❓ Why it matters

Every screen in an app is a query: a list page is `SELECT … ORDER BY … LIMIT`, a submitted form is `INSERT`, an edit is `UPDATE`, a remove button is `DELETE`, a dashboard is `GROUP BY`. SQL has been the standard language for this for decades, and works almost the same in PostgreSQL, MySQL, SQLite and data warehouses.

Used carelessly, it's also the fastest way to destroy data:

```sql
UPDATE job_listings SET status = 'closed';          -- forgot WHERE: closed ALL jobs
DELETE FROM applications WHERE user_id = user_id;   -- always true: deleted everything
SELECT * FROM job_listings WHERE salary_max = NULL; -- returns nothing, silently
```

And in application code:

```python
# 🚨 SQL injection: a "search term" like  ' OR '1'='1  returns every row
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

## 📖 Step by step

### 1. INSERT

```sql
INSERT INTO job_listings (title, company, city, posted_on)
VALUES ('Data Analyst', 'Kopi Data', 'Bandung', '2026-09-13')
RETURNING id, status;

-- several rows at once
INSERT INTO job_listings (title, company, posted_on) VALUES
    ('QA Engineer', 'Awan Cloud', '2026-09-13'),
    ('ML Engineer', 'Lintas AI',  '2026-09-13');
```

Always **list the columns** — the statement keeps working when a column is added later.

### 2. SELECT: choose columns and rows

```sql
SELECT title, company, salary_max
FROM job_listings
WHERE city = 'Jakarta'
  AND salary_max >= 15000000
ORDER BY salary_max DESC, title
LIMIT 10;
```

Logical order of evaluation (not the written order):

```mermaid
flowchart LR
    F[FROM] --> W[WHERE] --> G[GROUP BY] --> H[HAVING] --> S[SELECT] --> O[ORDER BY] --> L[LIMIT / OFFSET]
```

That's why you can't use a `SELECT` alias inside `WHERE`, but you can in `ORDER BY`.

### 3. Filtering toolkit

| Need | SQL |
|---|---|
| exact match | `city = 'Jakarta'` |
| not equal | `status <> 'closed'` |
| one of several | `city IN ('Jakarta', 'Bandung')` |
| range (inclusive) | `salary_max BETWEEN 10000000 AND 20000000` |
| pattern, case-sensitive | `title LIKE 'Junior%'` (`%` = any characters, `_` = one) |
| pattern, case-insensitive (PostgreSQL) | `title ILIKE '%engineer%'` |
| missing value | `salary_max IS NULL` / `IS NOT NULL` |
| combine | `AND`, `OR`, `NOT` — use parentheses when mixing |

### 4. NULL means "unknown"

`NULL` behaves like a sealed envelope: you can't compare two sealed envelopes and say they're equal, so use `IS NULL` instead of `= NULL`.

`NULL` isn't zero or empty text — it's **unknown**. Any comparison with unknown is unknown, so:

- `salary_max = NULL` → never true. Use `IS NULL`.
- `salary_max <> 10000000` does **not** return rows where `salary_max` is `NULL`.
- `COUNT(salary_max)` skips NULLs; `COUNT(*)` counts rows.
- `COALESCE(city, 'Remote')` replaces NULL with a fallback.

### 5. Aggregates, GROUP BY, HAVING

```sql
SELECT city,
       COUNT(*)                 AS total_jobs,
       ROUND(AVG(salary_max))   AS avg_max_salary,
       MAX(salary_max)          AS highest
FROM job_listings
WHERE status = 'open'            -- filter ROWS first
GROUP BY city
HAVING COUNT(*) >= 2             -- then filter GROUPS
ORDER BY total_jobs DESC;
```

Rule: every selected column must either be **in `GROUP BY`** or be **inside an aggregate**.

### 6. Pagination

```sql
SELECT id, title FROM job_listings ORDER BY posted_on DESC, id DESC LIMIT 20 OFFSET 40;  -- page 3
```

`OFFSET` gets slow on deep pages and can skip/duplicate rows when data changes; large apps use **keyset pagination** (`WHERE (posted_on, id) < (:last_date, :last_id)`) — you'll build it in Week 5. Always include a unique column (like `id`) in `ORDER BY` for a stable order.

### 7. UPDATE and DELETE — safely

```sql
UPDATE applications
SET status = 'interview', updated_at = now()
WHERE id = 42 AND user_id = 7          -- the ownership check matters!
RETURNING id, status;

DELETE FROM job_listings
WHERE status = 'closed' AND posted_on < '2026-01-01'
RETURNING id;
```

A safe routine for manual changes:

1. Write the `WHERE` as a `SELECT` first and check the rows.
2. Run the change inside a transaction: `BEGIN;` → `UPDATE …` → check → `COMMIT;` (or `ROLLBACK;`).
3. Use `RETURNING` to see exactly what changed.

**Soft delete** instead of `DELETE` when you need history: `UPDATE … SET deleted_at = now()` and filter `WHERE deleted_at IS NULL` everywhere.

### 8. Parameterized queries (from Python)

A parameterized query keeps the **question** and the **answer slot** separate, like a form with blank fields. Text typed into a blank field can never become a new instruction.

```python
# ✅ The driver sends the value separately — it can never become SQL
conn.execute("SELECT id, full_name FROM users WHERE email = %s", (email,))

# ❌ Never build SQL with f-strings / concatenation from user input
conn.execute(f"SELECT id FROM users WHERE email = '{email}'")
```

ORMs like SQLAlchemy (Week 4) parameterize automatically — but the moment you write raw SQL, this rule is yours.

### Choosing your setup

Every option here is a trade-off:

| Choice | ✅ | ❌ |
|---|---|---|
| `SELECT *` | quick for exploring | fragile in apps, sends unneeded data, breaks when columns change |
| Explicit column lists | stable, efficient | a bit more typing |
| `OFFSET` pagination | simple | slow for deep pages, unstable with inserts |
| Keyset pagination | fast, stable | can't jump to "page 37" directly |
| Hard `DELETE` | simple, saves space | no history or undo |
| Soft delete | recoverable, auditable | every query must remember the filter |
| Filtering in SQL | uses indexes, less data transferred | logic split between SQL and app |
| Filtering in Python | flexible | loads too much data |

- ✅ Filter, sort, aggregate and paginate **in the database**, not after loading everything into Python.
- ✅ Use `RETURNING` to avoid a second query after insert/update/delete.
- 🚫 Don't run `UPDATE`/`DELETE` without a `WHERE` you've tested with a `SELECT`.
- 🚫 Don't concatenate user input into SQL. Ever.

## ⚠️ Common mistakes

- `= NULL` instead of `IS NULL`.
- Selecting a non-aggregated column not in `GROUP BY`.
- Using `WHERE` to filter aggregates (use `HAVING`).
- Relying on insertion order without `ORDER BY`.
- `LIKE '%engineer%'` missing "Engineer" (case) — use `ILIKE` or `lower()`.

:::revoshop
Open `queries/queries.sql` and `queries/tests.sql` in RevoShop. For each query, identify: is it C, R, U or D? Does it filter with `WHERE`, sort, aggregate? Then open one repository file, e.g. `app/repositories/order_repository.py`: find a place where a query filters by the **current user** (an ownership check). Could any endpoint let user A read or update user B's order? Write down how you verified it.
:::

## 🏆 Best practices

- [ ] **Parameterize every query** that includes external input.
- [ ] List columns explicitly in `SELECT` and `INSERT` in application code.
- [ ] Always `ORDER BY` when order matters (without it, row order is **not guaranteed**), with a unique tie-breaker for pagination.
- [ ] Test `WHERE` clauses with `SELECT` before `UPDATE`/`DELETE`; wrap manual changes in a transaction.
- [ ] Include **ownership checks** (`AND user_id = :current_user`) in queries on user data.
- [ ] Handle `NULL` deliberately (`IS NULL`, `COALESCE`, `COUNT(column)` vs `COUNT(*)`).
- [ ] Use `RETURNING` instead of re-selecting.
- [ ] Format SQL for humans: one clause per line, uppercase keywords, meaningful aliases.
- [ ] Never run ad-hoc writes on production without a backup/review process.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain the difference between `WHERE` and `HAVING` using a real-life example (e.g. counting students per class, then keeping only big classes). Then explain SQL injection to a non-programmer.

## 📐 Design it

Write the SQL (on paper) that CareerPilot's API would run for each endpoint. Use `:name` placeholders for parameters:

1. `GET /applications?status=interview&page=2` — the current user's applications with that status, newest first, 20 per page
2. `GET /stats` — the current user's application count per status
3. `PATCH /applications/:id` — change the notes of one application (only if it belongs to the current user); return the updated row
4. `DELETE /applications/:id` — soft delete

:::quiz
Show possible SQL

```sql
-- 1
SELECT id, company_id, role_title, status, applied_on
FROM applications
WHERE user_id = :user_id AND status = :status AND deleted_at IS NULL
ORDER BY created_at DESC, id DESC
LIMIT 20 OFFSET 20;

-- 2
SELECT status, COUNT(*) AS total
FROM applications
WHERE user_id = :user_id AND deleted_at IS NULL
GROUP BY status
ORDER BY total DESC;

-- 3
UPDATE applications
SET notes = :notes, updated_at = now()
WHERE id = :id AND user_id = :user_id AND deleted_at IS NULL
RETURNING id, role_title, status, notes, updated_at;
-- 0 rows returned → respond 404

-- 4
UPDATE applications
SET deleted_at = now()
WHERE id = :id AND user_id = :user_id AND deleted_at IS NULL
RETURNING id;
```
:::

### 📝 Self-review checklist

- [ ] Every query filters by `user_id` (ownership)
- [ ] Pagination has a stable order with a unique tie-breaker
- [ ] Parameters are placeholders, never concatenated values
- [ ] I know what the API returns when 0 rows are affected

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m2/w2/03-crud-queries" ai="no-ai" title="Ten queries on job listings"}
Write 10 small SQL files — filtering, NULLs, aggregates, `HAVING`, `LIMIT`, `INSERT … RETURNING`, a safe `UPDATE` and a `DELETE`. The tests load fictional seed data into a fresh schema and compare your results exactly (columns, values and order).
:::

:::hints
- Run your query in psql or a GUI against the seed data before running the tests.
- For "contains engineer in any capitalization", think `ILIKE`.
- `ROUND(AVG(…))` rounds to a whole number.
- q06: filter rows *with a salary* in `WHERE`, then count per city in `HAVING`.
:::

### 🏆 Stretch goal

Write `q11_salary_bands.sql`: count jobs per band — `'< 10 juta'`, `'10–20 juta'`, `'> 20 juta'`, `'unknown'` — using `CASE WHEN … END` inside `GROUP BY`.

## ✅ Quick check

:::quiz
Why does `WHERE salary_max <> 10000000` not return rows where `salary_max` is NULL?

Comparisons with NULL produce "unknown", and `WHERE` keeps only rows where the condition is true. Add `OR salary_max IS NULL` if you want them.
:::

:::quiz
What's the difference between `COUNT(*)` and `COUNT(salary_max)`?

`COUNT(*)` counts rows; `COUNT(salary_max)` counts only rows where `salary_max` is not NULL.
:::

:::quiz
How do parameterized queries prevent SQL injection?

The SQL text and the values are sent separately; the database treats values strictly as data, so input can't change the query's structure.
:::


## 📚 Keep learning

- [PostgreSQL tutorial: Querying a table](https://www.postgresql.org/docs/current/tutorial-select.html)
- [PostgreSQL docs: Aggregate functions](https://www.postgresql.org/docs/current/functions-aggregate.html)
- [OWASP: SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
