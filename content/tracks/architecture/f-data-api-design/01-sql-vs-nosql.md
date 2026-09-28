---
title: "SQL vs NoSQL"
summary: Pick the right database for the job — how relational and document/key-value stores really differ, what each is good and bad at, and why "start with PostgreSQL" is the safe default for most apps.
type: lesson
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: recommended }
durationMinutes: 120
tags: [architecture, database, sql, nosql, postgresql, data-modeling]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What "SQL" (relational) and "NoSQL" databases actually mean
- The main NoSQL families: document, key-value, wide-column, graph
- What relational databases are good at, and where they struggle
- What NoSQL buys you, and what it costs
- A simple rule for choosing — and why PostgreSQL is the safe default
- How this connects to RevoShop's data (users, products, orders)

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Relational (SQL)** | Data kept in tables with rows and columns, with strict shape | Basis data tabel |
| **Schema** | The agreed shape of your data (which columns, which types) | Bentuk data yang disepakati |
| **NoSQL** | Any database that is not table-and-row relational | Basis data non-tabel |
| **Document store** | Saves whole objects (like JSON) instead of rows | Penyimpan dokumen |
| **Key-value store** | A giant dictionary: one key → one value | Penyimpan kunci-nilai |
| **JOIN** | Combining rows from two tables by a shared key | Menggabungkan tabel |
| **Transaction** | A group of changes that all happen, or none do | Transaksi (semua atau tidak) |
| **Denormalize** | Copy the same data into several places to read it faster | Menggandakan data agar cepat dibaca |

## 🧠 The big idea

A **relational database** is a **spreadsheet with rules**: every row in the "orders" sheet has exactly the same columns, and the database refuses a row that breaks the rules. It is strict, and that strictness protects your data.

A **document database** is a **folder of forms**: each form (document) is a whole object, and two forms in the same folder can look a little different. It is flexible, and that flexibility lets you move fast — until you need the rules back.

## ❓ Why it matters

Choosing a database is one of the hardest decisions to undo. Your whole app is shaped by it. If you pick wrong, you do not fix it with a small change — you migrate data, rewrite queries, and re-test everything.

The good news: for most apps the honest answer is **PostgreSQL** (relational). Beginners often reach for NoSQL because it sounds modern or "web scale", then hit painful problems that relational databases solved decades ago — like keeping an order and its payment consistent. Knowing what each tool is really for saves you that pain.

## 📖 Step by step

### 1. What relational (SQL) databases are

Data lives in **tables**. Each table has a fixed **schema** (columns and types). You link tables with keys and combine them with **JOIN**. Examples: **PostgreSQL**, MySQL, SQLite.

```sql
-- Two tables, linked by user_id
SELECT users.name, orders.total
FROM orders
JOIN users ON users.id = orders.user_id
WHERE orders.status = 'paid';
```

Their superpower is **consistency**: strict shape, relationships enforced by the database, and **transactions** — "create the order AND reduce stock, or do neither". You met these in Module 2 Week 2.

### 2. What NoSQL databases are

"NoSQL" just means "not the classic table-and-row model". It is a family, not one thing:

| Family | Stores | Good for | Example |
|---|---|---|---|
| **Document** | Whole objects (JSON-like) | Data that travels together, flexible shape | MongoDB |
| **Key-value** | key → value (a giant dictionary) | Caches, sessions, very fast lookups | Redis |
| **Wide-column** | Rows with huge, sparse column sets | Massive write volume, time-series | Cassandra |
| **Graph** | Nodes and connections | "Friends of friends", recommendations | Neo4j |

A document store lets you save an order as one object, no JOIN needed:

```javascript
// One document = the whole order, read in a single lookup
{
  "_id": "order_123",
  "user": { "id": 7, "name": "Ismail" },
  "items": [ { "product": "Mug", "qty": 2, "price": 50000 } ],
  "status": "paid"
}
```

### 3. The real trade-off: strict shape vs flexible shape

This is the heart of the choice.

| | Relational (SQL) | Document (NoSQL) |
|---|---|---|
| Shape of data | Fixed schema, enforced | Flexible, per-document |
| Relationships | JOINs across tables | Often copied into the document (**denormalize**) |
| Strong transactions | ✅ built for it | ⚠️ limited (better in newer versions) |
| Change a field's type | Migration needed | Just write the new shape |
| Duplicated data | Avoided | Common (and can drift out of sync) |

Denormalizing (copying `user.name` into every order) makes reads fast, but now a name change must be updated in many places. Relational databases avoid that by keeping one source of truth and JOINing.

### 4. What each is genuinely good at

**Relational shines when:**
- Data has clear relationships (users → orders → items).
- You need transactions ("all or nothing").
- You run varied queries you cannot predict yet (reports, filters, JOINs).

**NoSQL shines when:**
- Data is read and written as one blob (a document, a cache entry, an event).
- The shape changes often or differs per record.
- You need one specific thing at extreme scale (millions of key-value reads/sec → Redis; huge write streams → Cassandra).

### 5. Modern reality: the line is blurry

PostgreSQL has a `JSONB` column type — you can store a flexible document *inside* a relational table and query into it. So you often get NoSQL-style flexibility without leaving the safety of a relational database:

```sql
-- Flexible attributes in a JSONB column, still inside PostgreSQL
SELECT name FROM products WHERE attributes->>'color' = 'red';
```

This is why "just use PostgreSQL" covers so many cases: it does the strict part *and* a good chunk of the flexible part.

### Choosing your database

| Your situation | Good choice |
|---|---|
| A normal web/mobile app (users, orders, content) | **PostgreSQL** — start here |
| Cache, session store, rate-limit counters | **Redis** (key-value) — *alongside* your main DB |
| One flexible sub-part inside a relational app | PostgreSQL **`JSONB`** |
| Truly huge write volume / time-series | Cassandra or a time-series DB |
| Data that is mostly connections (social graph) | A graph DB |

- ✅ Default to relational (PostgreSQL) unless you have a concrete reason not to.
- ✅ It is normal to use **two** stores: PostgreSQL for the source of truth, Redis for caching.
- 🚫 Don't pick NoSQL for "scale" you don't have yet — most apps never reach it.
- 🚫 Don't spread your source of truth across many databases early; that multiplies bugs.

## ⚠️ Common mistakes

- Choosing NoSQL to "avoid schemas", then rebuilding schema rules by hand in app code (badly).
- Storing money or orders in a store without strong transactions, then getting inconsistent totals.
- Denormalizing everywhere, then chasing the same value across dozens of documents when it changes.
- Treating Redis as the source of truth — it is a fast helper, not your safe long-term store.

:::revoshop
RevoShop uses PostgreSQL. (1) List its main tables and the relationships between them (users, products, orders, order items). Why is a transaction important when creating an order that also reduces product stock? (2) Which part of RevoShop would fit a key-value store like Redis well — for example a cart or a rate-limit counter — and why keep it *separate* from the source-of-truth tables? (3) Could product `attributes` (size, color) live in a `JSONB` column instead of many nullable columns? What would you gain and lose?
:::

## 🏆 Best practices

- [ ] Start with a relational database (PostgreSQL) and a clear schema; move away only for a proven reason.
- [ ] Keep **one source of truth**; add other stores (like Redis) as helpers, not replacements.
- [ ] Use transactions for anything that must be "all or nothing" (money, stock, multi-step writes).
- [ ] Reach for `JSONB` when a few fields are flexible — before reaching for a whole second database.
- [ ] When you denormalize, write down where the copies live and how they stay in sync.
- [ ] Match the store to the access pattern: source of truth → relational; cache/counter → key-value.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a non-programmer why an online shop keeps its orders in a "strict" database (relational) but might keep its shopping carts in a "fast, simple" one (key-value). Use the spreadsheet-with-rules vs folder-of-forms analogy.

## 📐 Design it

CareerPilot stores: user profiles, saved job applications (with status), and a log of every AI suggestion it ever made (millions of small, write-once records). Decide which store each of the three belongs in and why. For the profiles-and-applications part, sketch the relational tables; for the AI-suggestion log, argue whether relational is still fine or whether a different store earns its place.

:::quiz
Show a possible design

**Profiles + applications → PostgreSQL (relational).** They have clear relationships (`user` → `application` → `status_history`) and need transactions (change status *and* record the change together). Varied future queries ("all applications interviewing this month") are easy with SQL.

**AI-suggestion log → still PostgreSQL to start.** It is write-once and high-volume, which *sounds* like a NoSQL job, but modern PostgreSQL handles millions of rows fine with an index on `(user_id, created_at)`. Keeping it in one database means one backup, one place to query, and transactions when a suggestion links to an application. Only move it to a wide-column/time-series store if measurements later show PostgreSQL struggling.

**Rule shown:** don't split stores on a guess. Start relational, measure, and split a specific table only when it proves it needs a specialized store.
:::

### 📝 Self-review checklist

- [ ] Each store choice is justified by access pattern and consistency needs, not by hype
- [ ] Transactions identified where "all or nothing" matters
- [ ] A single source of truth is clear
- [ ] Any denormalization/duplication is called out with a sync plan

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/architecture/f-data-api-design/01-sql-vs-nosql" ai="no-ai" title="Model the same data two ways"}
Given a small orders dataset, implement two tiny in-memory "stores": a relational one (normalized tables + a join) and a document one (denormalized objects). The same tests check that both return the right order totals and user names — and that updating a user's name is one write in the relational model but many in the document model.
:::

:::hints
- Relational: keep `users` and `orders` as separate dicts keyed by id; `join_orders` looks up the user by `user_id`.
- Document: each order embeds a copy of the user's name; `rename_user` must scan every order to update it.
- The point of the tests is to *show* the trade-off, not to make one model "win".
:::

## ✅ Quick check

:::quiz
Why is "just use PostgreSQL" a reasonable default for most apps?

Because most apps have related data, need transactions, and run varied queries — exactly what relational databases do best — and PostgreSQL also offers `JSONB` for the flexible parts, so you rarely need a second kind of database early on.
:::

:::quiz
What is the main risk of denormalizing (copying data into many documents)?

The copies can drift out of sync. When the original value changes, you must update every copy, and missing one leaves your data inconsistent.
:::

## 📚 Keep learning

- [PostgreSQL: JSON types](https://www.postgresql.org/docs/current/datatype-json.html)
- [MongoDB: data modeling introduction](https://www.mongodb.com/docs/manual/core/data-modeling-introduction/)
- [Martin Kleppmann, *Designing Data-Intensive Applications*, Ch. 2 (data models)](https://dataintensive.net/)
