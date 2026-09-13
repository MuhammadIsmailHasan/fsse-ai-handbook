---
title: "Week 2 Placement Check"
summary: Can you design tables, write queries with joins and aggregates, and explain indexes and transactions? Find out in 25 minutes.
type: placement-check
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: recommended }
durationMinutes: 25
tags: [placement, sql, postgresql]
---

::::placement{id="modules/m2/w2"}
Write SQL on paper or in a scratch file — no running it until you've answered.

:::quiz
1 · Design tables for: users can save many job listings, and a job listing can be saved by many users, remembering **when** it was saved.

Three tables: `users(id PK, …)`, `jobs(id PK, …)`, and a junction table `saved_jobs(user_id FK → users, job_id FK → jobs, saved_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY (user_id, job_id))`. The composite primary key prevents saving the same job twice.
:::

:::quiz
2 · Write a query: number of applications per status for user 7, most common status first.

```sql
SELECT status, COUNT(*) AS total
FROM applications
WHERE user_id = 7
GROUP BY status
ORDER BY total DESC;
```
:::

:::quiz
3 · List every company with its number of applications — **including companies with zero**.

```sql
SELECT c.name, COUNT(a.id) AS applications
FROM companies c
LEFT JOIN applications a ON a.company_id = c.id
GROUP BY c.id, c.name
ORDER BY applications DESC;
```

`LEFT JOIN` keeps companies without matches, and `COUNT(a.id)` counts only real rows (0 for none). `COUNT(*)` would wrongly give 1.
:::

:::quiz
4 · What's the difference between `WHERE` and `HAVING`?

`WHERE` filters **rows before** grouping; `HAVING` filters **groups after** aggregation (e.g. `HAVING COUNT(*) > 5`).
:::

:::quiz
5 · A query filtering `applications` by `user_id` is slow on 10 million rows. What's the first thing to check, and what might fix it?

Run `EXPLAIN ANALYZE` to see the plan. If it's a sequential scan, add an index: `CREATE INDEX ON applications (user_id);` (foreign key columns aren't indexed automatically in PostgreSQL).
:::

:::quiz
6 · Why must "create order + decrease stock + record payment" run in a transaction?

So it's **atomic**: either all steps succeed (`COMMIT`) or none do (`ROLLBACK`). Without it, a failure halfway leaves inconsistent data, like stock decreased for an order that doesn't exist.
:::
::::

:::tip[Scoring yourself]
Pass with **5 of 6**. Question 3 is the classic trap — if you used `INNER JOIN` or `COUNT(*)`, study lesson 05.
:::
