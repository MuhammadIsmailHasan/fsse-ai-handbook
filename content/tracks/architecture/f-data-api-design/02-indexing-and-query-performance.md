---
title: "Indexing & Query Performance"
summary: Why the same query can be instant or painfully slow — how a database index works like the index of a book, when a composite index helps, the write cost of every index, and how to read EXPLAIN to prove it.
type: lesson
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: recommended }
durationMinutes: 120
tags: [architecture, database, index, performance, postgresql, explain]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What an index is and why it makes lookups fast
- The default kind (B-tree) and what it is good at
- **Composite** indexes and why column order matters
- The hidden cost: indexes slow down writes and use space
- How to read `EXPLAIN` to see if an index is actually used
- Which columns to index in a real app like RevoShop

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Index** | A sorted shortcut the database keeps so it can find rows fast | Jalan pintas pencarian |
| **Full table scan** | Reading every row to find matches (slow on big tables) | Membaca semua baris |
| **B-tree** | The default index shape; keeps keys sorted for fast lookup and ranges | Struktur index terurut |
| **Composite index** | One index over several columns together | Index gabungan beberapa kolom |
| **Selectivity** | How well a column narrows results (unique = high) | Seberapa menyaring sebuah kolom |
| **EXPLAIN** | A command that shows the plan the database will use | Perintah lihat rencana query |
| **Covering index** | An index that already holds every column the query needs | Index yang memuat semua kolom query |

## 🧠 The big idea

An index is the **index at the back of a book**. Without it, finding every mention of "Redis" means reading all 400 pages (a **full table scan**). With it, you flip to the index, see "Redis … 88, 210", and jump straight there.

Same book, same words — the index just lets you skip the pages that cannot match.

## ❓ Why it matters

On 100 rows, everything is fast, so beginners never notice. On 5 million rows, a query with no index reads all 5 million rows *every time*, and your app grinds to a halt exactly when it finally has users.

Indexes turn "read everything" into "jump to the right place". But they are not free, so knowing *which* columns to index — and proving it with `EXPLAIN` — is a core backend skill.

## 📖 Step by step

### 1. The problem: a full table scan

```sql
SELECT * FROM orders WHERE user_id = 42;
```

With no index, the database checks **every** row to see if `user_id = 42`. On a big `orders` table that is millions of comparisons for one query.

### 2. The fix: an index

```sql
CREATE INDEX idx_orders_user_id ON orders (user_id);
```

Now the database keeps `user_id` values **sorted** (a **B-tree**). To find `42` it does a fast search — like finding a word in a dictionary — instead of reading everything. A B-tree is also great for **ranges** (`created_at > '2026-01-01'`) and **sorting**, because the values are already in order.

### 3. Composite indexes — order matters

A **composite index** covers several columns at once:

```sql
CREATE INDEX idx_orders_user_status ON orders (user_id, status);
```

Think of a phone book sorted by **(last name, first name)**. It helps you find "Hasan, Ismail" and all "Hasan"s — but it does **not** help you find everyone named "Ismail", because first name is the *second* sort key.

Rule: a composite index on `(a, b)` helps queries that filter on `a`, or on `a` **and** `b` — but not on `b` alone. Put the column you always filter by **first**.

### 4. The hidden cost: writes get slower

Every index must be kept up to date. On every `INSERT`, `UPDATE` or `DELETE`, the database also updates each index and uses extra disk space.

| More indexes | Effect |
|---|---|
| Reads matching the index | ⚡ much faster |
| Writes (insert/update/delete) | 🐢 a bit slower each time |
| Disk usage | 📈 grows |

So you do **not** index every column "just in case". You index the columns you actually search, join, or sort by.

### 5. Prove it with EXPLAIN

Never guess whether an index is used — ask:

```sql
EXPLAIN SELECT * FROM orders WHERE user_id = 42;
```

- `Seq Scan` → a full table scan (no index used). Bad on big tables.
- `Index Scan using idx_orders_user_id` → the index is working. 

If you added an index and still see `Seq Scan`, something is off (wrong column order, a function wrapping the column, or the table is so small the planner skips the index on purpose).

### 6. A quick win: covering indexes

If an index already contains every column a query needs, the database can answer from the index alone, never touching the table:

```sql
-- This index can answer "statuses for a user" without reading the table rows
CREATE INDEX idx_orders_user_status ON orders (user_id, status);
SELECT status FROM orders WHERE user_id = 42;   -- covered
```

### Choosing what to index

| Situation | Index it? |
|---|---|
| Column in `WHERE`, `JOIN`, or `ORDER BY` on a big table | ✅ yes |
| Foreign keys (`user_id`, `product_id`) | ✅ usually yes |
| Column with few distinct values (e.g. `is_active` true/false) | ⚠️ rarely helps — low selectivity |
| A write-heavy table with rarely-read columns | 🚫 don't over-index |
| A tiny lookup table | 🚫 not needed |

- ✅ Index high-**selectivity** columns you filter/join/sort on.
- ✅ For multi-column filters, use a composite index with the most-filtered column first.
- 🚫 Don't add indexes you cannot justify with a real query.

## ⚠️ Common mistakes

- Adding an index and never checking `EXPLAIN` to see if it is used.
- Wrong column order in a composite index, so the query still scans.
- Wrapping the column in a function (`WHERE lower(email) = ...`) so a plain index on `email` can't be used.
- Indexing everything, then wondering why writes got slow and disk filled up.
- Indexing a boolean/low-variety column and expecting a big speedup.

:::revoshop
Open RevoShop's models/migrations. (1) Which columns does it query most — `orders.user_id`, `order_items.order_id`, `products.category`? Are those indexed? (2) The "my orders" page filters by `user_id` and sorts by `created_at`. Would a composite index `(user_id, created_at)` help more than two single-column indexes? Why? (3) If you run `EXPLAIN` on the orders-by-user query, do you see `Index Scan` or `Seq Scan`?
:::

## 🏆 Best practices

- [ ] Index foreign keys and the columns you filter, join, and sort on.
- [ ] Prove every index with `EXPLAIN` on a realistic amount of data — don't guess.
- [ ] For multi-column filters, choose composite-index column order by what you filter on first.
- [ ] Remember writes pay for indexes; keep only the ones a real query needs.
- [ ] Avoid functions on indexed columns in `WHERE`, or add a matching expression index.
- [ ] Re-check indexes when query patterns change; drop ones no query uses.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a friend, using the book-index analogy, why adding an index makes reads faster but writes slower. Then explain why a composite index on `(last_name, first_name)` does not help a search by first name alone.

## 📐 Design it

CareerPilot's `applications` table has millions of rows. The three hottest queries are: (a) all applications for one user, newest first; (b) all applications with `status = 'interviewing'` for one user; (c) a global daily count of applications created per day. Design the indexes you would add, name the columns and their order, and say which query each index serves. Note any query where an index would *not* help much.

:::quiz
Show a possible design

- (a) *user's applications, newest first* → **composite** `(user_id, created_at DESC)`. Filters by `user_id` and gives the sort order for free — a covering-ish index for the list.
- (b) *user + status* → the same `(user_id, created_at)` index already narrows by user; add `status` only if status filtering is common: `(user_id, status, created_at)`. Column order: the always-filtered `user_id` first.
- (c) *daily global counts* → an index on `created_at` helps range/group by day, but a full daily aggregate over *all* rows may still scan a lot; a summary table or materialized view is often better than an index here.

**Rule shown:** design indexes from the actual hot queries and their filter+sort shape, not column by column. Some analytics queries want a summary table, not an index.
:::

### 📝 Self-review checklist

- [ ] Each index maps to a real, named query
- [ ] Composite column order matches the filter (most-filtered first)
- [ ] Write cost acknowledged (not indexing everything)
- [ ] Cases where an index won't help are identified

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/architecture/f-data-api-design/02-indexing" ai="no-ai" title="Build a tiny index and count the work"}
Implement a linear search that scans every row (and counts how many it touched) and an equality index (a dict from value → rows) that answers the same query touching far fewer rows. Then build a composite `(a, b)` index and show it can serve a query on `a` alone but not on `b` alone.
:::

:::hints
- `linear_search` returns `(matches, scanned)` where `scanned == len(rows)` every time.
- `build_index(rows, field)`: a dict mapping each value to the list of rows with it.
- Composite key: use the tuple `(row[a], row[b])`; to serve "a alone", also keep the first-column grouping (or iterate keys whose first element matches).
:::

## ✅ Quick check

:::quiz
Why does adding indexes make writes slower?

Because every insert, update, or delete must also update each index (and it uses extra disk). Indexes speed up reads at the cost of write speed and space, so you add only the ones a real query needs.
:::

:::quiz
A composite index is on `(user_id, status)`. Which of these does it help: filter by `user_id`; filter by `status` alone; filter by both?

It helps filtering by `user_id`, and by `user_id` **and** `status` together, but not `status` alone — because `status` is the second sort key, like first name in a phone book sorted by last name first.
:::

## 📚 Keep learning

- [Use The Index, Luke — how indexes work](https://use-the-index-luke.com/)
- [PostgreSQL: Using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)
- [PostgreSQL: Indexes](https://www.postgresql.org/docs/current/indexes.html)
