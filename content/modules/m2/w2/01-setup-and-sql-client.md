---
title: "PostgreSQL Setup & SQL Client"
summary: What a relational database is, running PostgreSQL locally with Docker, connecting with psql and a GUI client, and choosing the right column types.
type: lesson
source: core
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: recommended }
durationMinutes: 150
tags: [postgresql, sql, database, docker, psql]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What a **relational database** is and why apps don't just use files
- Why **PostgreSQL** is a strong default choice
- Running PostgreSQL locally with **Docker Compose**
- Connecting with **psql** and a **GUI client**; reading a **connection string**
- Creating your first table with the right **data types** and **defaults**

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Relational database** | Data kept in strict tables that can be linked together | Basis data bertabel |
| **Table / row / column** | A sheet / one record / one field with a fixed type | Tabel / baris / kolom |
| **PostgreSQL** | A popular, reliable open-source database server | Server basis data populer |
| **SQL** | The language you use to ask the database questions | Bahasa bertanya ke database |
| **Connection string** | One line with user, password, host, port and database name | Alamat koneksi database |
| **psql** | PostgreSQL's command-line client | Klien database di terminal |
| **Data type** | What a column may hold (`text`, `integer`, `numeric`, `timestamptz`) | Jenis isi kolom |
| **Default value** | What the database puts in when you don't provide one | Nilai bawaan |
| **`numeric`** | The exact number type used for money (never `float`) | Angka presisi untuk uang |

## 🧠 The big idea

A :term[relational database]{bahasa="basis data relasional — menyimpan data dalam tabel (baris & kolom) yang saling terhubung"} is a set of **very strict spreadsheets** with a **guard** standing in front of them.

- Each **table** is a sheet (`users`, `applications`), each **row** is a record, each **column** is a field with a fixed **type**.
- The guard — the database server — **enforces the rules** (no missing email, no negative salary), lets many people read and write **at the same time** safely, and answers questions written in **SQL**.

Files have no guard: anyone can write anything, and two people writing at once ruin the page.

## ❓ Why it matters

Keeping app data in JSON or CSV files works until:

- two requests write the same file at the same moment → broken data,
- you need "all applications for user 7 with status interview" across millions of rows → you must read whole files,
- the server crashes mid-write → half a file,
- you need a rule like "every application must belong to a user that exists".

Databases solve exactly these four problems: many users at once, fast questions, surviving crashes, and keeping data valid.

Picking the wrong column types brings its own pain:

- `applications.json` grows to 2 GB, and every page load reads all of it.
- Salary stored as text: `'9000000'` sorts before `'10000000'`, and `'9 juta'` sneaks in.
- Dates stored as `'13/09/2026'` strings: sorting and date maths break.
- Money stored as `float`: rounding errors in invoices.

## 📖 Step by step

### 1. Why PostgreSQL

| Strength | Why it matters |
|---|---|
| Open source, very mature | free, huge community, used from startups to banks |
| Strict and standards-friendly | catches bad data early |
| Rich types (`jsonb`, arrays, `uuid`, ranges) | flexible when you need it |
| Extensions (**pgvector**, PostGIS) | vector search for AI (Module 7), maps |
| Offered by every cloud (AWS RDS, Supabase, Neon) | easy to deploy |

Other databases you'll hear about: MySQL/MariaDB (also relational), SQLite (a file-based database — great for tests and small apps), MongoDB (document database), Redis (in-memory key-value).

### 2. Run PostgreSQL with Docker

The handbook's `exercises/compose.yaml` already defines a database on port **5491**:

```bash
cd exercises
docker compose up -d        # start in the background
docker compose ps           # should show "healthy"
docker compose logs -f db   # watch logs (Ctrl+C to stop watching)
docker compose down         # stop (data stays in the volume)
```

### 3. Connection strings

Read it like a postal address: who you are, the secret, which building, which door, and which room — `postgresql://user:password@host:port/database`.

Apps connect with a URL:

```text
postgresql://fsse:fsse@localhost:5491/fsse
└── scheme ─┘ └user┘└pwd┘ └─ host ─┘└port┘└db┘
```

In real projects this lives in an environment variable (`DATABASE_URL`), never in code.

### 4. psql: the command-line client

```bash
docker compose exec db psql -U fsse -d fsse
```

| Command | Does |
|---|---|
| `\l` | list databases |
| `\dt` | list tables |
| `\d applications` | describe a table (columns, types, constraints, indexes) |
| `\dn` | list schemas |
| `\x` | toggle expanded display for wide rows |
| `\timing` | show how long queries take |
| `\i file.sql` | run a SQL file |
| `\q` | quit |

SQL statements end with `;`. Backslash commands don't.

### 5. GUI clients

| Client | Notes |
|---|---|
| **DBeaver** | free, supports every database |
| **TablePlus** | fast, clean (free tier) |
| **pgAdmin** | official PostgreSQL tool |
| VS Code **PostgreSQL** extensions | query from your editor |

Connect with host `localhost`, port `5491`, user `fsse`, password `fsse`, database `fsse`. GUIs are great for **exploring**; keep real schema changes in **SQL files / migrations** so they're versioned (Week 4).

### 6. PostgreSQL data types you'll use most

Choosing a type is like choosing a container in the kitchen: the right shape stops you storing soup in a paper bag. Money always goes in `numeric`, times always in `timestamptz`.

| Use for | Type | Notes |
|---|---|---|
| Ids | `bigint GENERATED ALWAYS AS IDENTITY` | auto-incrementing primary key (modern replacement for `serial`) |
| Public/unguessable ids | `uuid` | e.g. `gen_random_uuid()` |
| Counts, small numbers | `integer` | ±2.1 billion |
| Money | `bigint` (smallest unit) or `numeric(12,2)` | **never** `real`/`double precision` |
| Text | `text` | no practical difference from `varchar(n)` in PostgreSQL; add a `CHECK` if you need a max length |
| Yes/no | `boolean` | |
| Calendar dates | `date` | |
| Moments in time | `timestamptz` | stores an absolute instant — use this, not `timestamp` without time zone |
| Flexible documents | `jsonb` | for truly variable data; don't use it to avoid designing tables |

### 7. Your first table

```sql
CREATE TABLE study_sessions (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    topic       text        NOT NULL,
    minutes     integer     NOT NULL CHECK (minutes > 0),
    studied_on  date        NOT NULL DEFAULT CURRENT_DATE,
    created_at  timestamptz NOT NULL DEFAULT now()
);

INSERT INTO study_sessions (topic, minutes) VALUES ('Git basics', 90)
RETURNING id, studied_on;

SELECT * FROM study_sessions;
```

- `PRIMARY KEY` = unique, not null identifier for each row.
- `NOT NULL`, `CHECK` and `DEFAULT` are **rules the database enforces** — no matter which app or script writes the data.
- `RETURNING` gives you back generated values without a second query.

### Choosing your setup

Every option here is a trade-off:

| Choice | ✅ | ❌ |
|---|---|---|
| PostgreSQL | powerful, strict, extensible | a server to run and operate |
| SQLite | zero setup, one file | limited concurrent writes; fewer features |
| MongoDB (documents) | flexible shapes | weaker relations/joins; integrity rules live in app code |
| Database in Docker locally | identical setup for everyone | Docker required |
| Managed cloud database in production | backups, failover, patches handled | cost; less control |

- ✅ PostgreSQL as the default for web apps with related data: users, orders, applications.
- ✅ Constraints in the database for rules that must **always** hold.
- 🚫 Don't use a relational database as a cache or message queue at high volume (Redis/queues exist for that).
- 🚫 Don't store large files (CVs, images) in tables — store them in object storage and save the **path/URL**.

## ⚠️ Common mistakes

- Forgetting the `;` in psql and wondering why nothing happens (the prompt changes to `fsse-#`).
- Connecting to `5432` when the container is published on `5491`.
- Using `timestamp` instead of `timestamptz`.
- Naming a table `user` or `order` (reserved words → quoting headaches).
- Losing data with `docker compose down -v` (the `-v` deletes volumes).

:::revoshop
Open `queries/schema.sql` in RevoShop. Find: the primary keys, the `NOT NULL UNIQUE` on `users.username` and `users.email`, and the `CHECK (price > 0)` on products. Which types did you use for money (`price`, `total_amount`) and timestamps? Compare them with the table in section 6 — would you change any type today, and why? Also check `docker-compose.yml`: which PostgreSQL version does RevoShop pin?
:::

## 🏆 Best practices

- [ ] Run the **same major PostgreSQL version** locally as in production (pin the Docker image tag).
- [ ] Keep connection details in **`DATABASE_URL`** / environment variables; commit only `.env.example`.
- [ ] Use `bigint ... GENERATED ALWAYS AS IDENTITY` (or `uuid`) for primary keys.
- [ ] Use **`timestamptz`** for points in time; store in UTC and convert for display.
- [ ] Never use floating point for money.
- [ ] Add `NOT NULL` by default; allow `NULL` only when "unknown/not applicable" is a real state.
- [ ] Put schema changes in **versioned SQL files or migrations**, not only clicks in a GUI.
- [ ] Use a **least-privilege** database user for the app (not the superuser) in real environments.
- [ ] Use `snake_case` names; avoid reserved words (`user`, `order`) as table names — prefer `users`, `orders`.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a non-programmer why an app with thousands of users stores data in a database server instead of a big spreadsheet file. Mention at least two problems a database solves.

## 📐 Design it

Choose a PostgreSQL type, nullability, and default (if any) for each column of a CareerPilot `job_listings` table:

`id`, `title`, `company_name`, `city`, `is_remote`, `salary_min`, `salary_max`, `currency`, `posted_on`, `source_url`, `raw_description`, `imported_at`, `extra_metadata` (varies a lot between job boards)

:::quiz
Show a possible design

| Column | Type | Null? | Default / rule |
|---|---|---|---|
| `id` | `bigint GENERATED ALWAYS AS IDENTITY` | no | primary key |
| `title` | `text` | no | `CHECK (length(title) BETWEEN 1 AND 200)` |
| `company_name` | `text` | no | |
| `city` | `text` | yes | remote jobs may not have one |
| `is_remote` | `boolean` | no | `DEFAULT false` |
| `salary_min`, `salary_max` | `bigint` | yes | `CHECK (salary_min <= salary_max)` |
| `currency` | `text` | no | `DEFAULT 'IDR'`, `CHECK (currency ~ '^[A-Z]{3}$')` |
| `posted_on` | `date` | yes | |
| `source_url` | `text` | no | `UNIQUE` (prevents duplicate imports) |
| `raw_description` | `text` | no | |
| `imported_at` | `timestamptz` | no | `DEFAULT now()` |
| `extra_metadata` | `jsonb` | no | `DEFAULT '{}'` — varies per source |
:::

### 📝 Self-review checklist

- [ ] Money is `bigint`/`numeric`, never floating point
- [ ] Moments in time use `timestamptz`
- [ ] `NULL` is allowed only where "unknown" is real
- [ ] I used `UNIQUE`/`CHECK` to protect data quality

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m2/w2/01-postgres-setup" ai="no-ai" title="Your first PostgreSQL table"}
1. Start the database: `cd exercises && docker compose up -d`
2. Connect with psql (`docker compose exec db psql -U fsse -d fsse`) **and** with a GUI client of your choice. Run `SELECT version();` in both.
3. Write `study_log.sql` (spec in the folder README): a `study_log` table with the right types, constraints and defaults, plus 3 inserted rows.

The tests run your file in a fresh schema and inspect the result.
:::

:::hints
- `bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY`
- `CHECK (minutes BETWEEN 1 AND 600)`
- `DEFAULT CURRENT_DATE` for dates, `DEFAULT now()` for timestamps
- Don't include `CREATE SCHEMA` or `SET search_path` — the tests handle that.
:::

### 🏆 Stretch goal

In psql, run `\d study_log`, then try to insert a row with `minutes = 0` and read the error message. Which constraint name does PostgreSQL report? Give your constraint a clear name: `CONSTRAINT study_log_minutes_range CHECK (…)`.

## ✅ Quick check

:::quiz
Why use `timestamptz` instead of `timestamp`?

`timestamptz` stores an absolute point in time (normalized to UTC) and converts correctly between time zones. `timestamp` has no time zone, so the same value can mean different moments on different servers.
:::

:::quiz
What does `RETURNING` do in an `INSERT`?

It returns columns of the inserted rows — such as the generated `id` and defaults — in the same statement.
:::

:::quiz
Where should the connection string for your app live?

In an environment variable (e.g. `DATABASE_URL`), loaded from a git-ignored `.env` locally and from the platform's secret settings in production.
:::


## 📚 Keep learning

- [PostgreSQL docs: Data Types](https://www.postgresql.org/docs/current/datatype.html)
- [PostgreSQL wiki: Don't Do This](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
- [psql reference](https://www.postgresql.org/docs/current/app-psql.html)
