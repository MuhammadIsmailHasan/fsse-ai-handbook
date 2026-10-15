---
title: "SQLAlchemy: Connecting Flask to PostgreSQL"
summary: How an ORM talks to your database — engines, connection pools, sessions and transactions, SQLAlchemy 2.0 select() queries, and wiring it into a Flask app safely.
type: lesson
source: core
roles: { be: core, fe: none, fs: core, ai: recommended, ops: optional }
durationMinutes: 180
tags: [flask, sqlalchemy, orm, postgresql, sessions]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What an **ORM** is, and what it does and doesn't hide
- SQLAlchemy's layers: **engine**, **connection pool**, **session**
- The **unit of work**: `add`, `flush`, `commit`, `rollback`
- SQLAlchemy **2.0-style** queries with `select()`, `scalars()`, `get()`
- Wiring **Flask-SQLAlchemy** into an application factory
- Session lifetime per request, and seeing the SQL that runs

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **ORM** | A translator between Python objects and database tables | Penerjemah objek ke tabel |
| **Engine** | The object that knows how to talk to your database | Penghubung ke database |
| **Connection pool** | A small set of reused connections instead of new ones each time | Kumpulan koneksi siap pakai |
| **Session** | Your workspace for one request: it tracks changes and saves them together | Ruang kerja satu request |
| **Unit of work** | The pattern: collect changes, then commit them as one transaction | Kumpulkan lalu simpan sekali |
| **`flush` vs `commit`** | Send SQL now but stay in the transaction / finish the transaction | Kirim SQL / selesaikan transaksi |
| **`rollback`** | Undo everything in this session's transaction | Batalkan perubahan |
| **`select()`** | The modern SQLAlchemy way to write a query | Cara menulis kueri modern |
| **N+1 query** | One query per row in a loop, instead of one query for all | Kueri berulang per baris |

## 🧠 The big idea

An :term[ORM]{bahasa="Object-Relational Mapper — penerjemah antara objek Python dan tabel database"} is an **interpreter** between two languages: your Python objects, and the database's tables and SQL. You say "save this `Application` object" and it writes the `INSERT`; you ask for "user 7's applications" and it writes the `SELECT` and hands back objects.

An interpreter makes the conversation easy — but you still need to know what is being said. Good ORM users **read the SQL** it generates.

## ❓ Why it matters

Writing raw SQL for everything means repetitive mapping code (rows → dicts → objects), handling parameters by hand, and SQL strings scattered across files. An ORM gives you Python classes for tables (lesson 03), queries you can build up in pieces, a **session** that tracks your changes and commits them in one transaction, and mostly-portable code.

The danger is treating it as magic:

- A new connection opened on **every request** with no pool → the database hits its connection limit under load.
- Forgetting `commit()` → "it saved in my tests but not in the database".
- An exception in the middle of a request leaves the session broken → every later request fails until a restart.
- A loop that quietly runs hundreds of queries (the N+1 problem, lesson 05).

## 📖 Step by step

### 1. The layers

```mermaid
flowchart LR
    Code[Your code<br/>models & queries] --> Session[Session<br/>unit of work, tracks objects]
    Session --> Engine[Engine<br/>dialect + connection pool]
    Engine --> Pool[(Pool of open<br/>DB connections)]
    Pool --> PG[(PostgreSQL)]
```

| Layer | Job |
|---|---|
| **Engine** | knows *how* to talk to PostgreSQL (dialect + driver) and manages a **pool** of connections |
| **Connection pool** | reuses a few open connections instead of opening a new one per query (opening is slow) |
| **Session** | your workspace: loads objects, tracks changes, sends them in a transaction |

### 2. The database URL

```text
postgresql+psycopg://careerpilot:secret@localhost:5491/careerpilot
└─ dialect ─┘└driver┘
```

`+psycopg` selects the psycopg 3 driver you used in Week 2. The URL comes from `DATABASE_URL`, never from code.

### 3. Core SQLAlchemy (without Flask)

```python
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session

engine = create_engine(DATABASE_URL, pool_pre_ping=True)   # create ONCE per process

with Session(engine) as session:                            # short-lived
    total = session.scalar(text("SELECT count(*) FROM applications"))
```

`pool_pre_ping=True` checks a pooled connection is still alive before using it (databases and proxies drop idle connections).

### 4. The unit of work

Think of a shopping trolley: `add` puts items in, `flush` shows them to the cashier, and `commit` pays. Until you pay, nothing is final — and `rollback` empties the trolley.

```python
with Session(engine) as session:
    company = Company(name="Kopi Data")
    session.add(company)          # pending: nothing sent yet
    session.flush()               # sends INSERT, company.id is now set — still inside the transaction
    session.add(Application(company_id=company.id, role_title="Analyst"))
    session.commit()              # COMMIT: both rows saved together
```

| Method | What happens |
|---|---|
| `add(obj)` | start tracking a new object |
| `flush()` | send pending SQL to the database **within** the current transaction |
| `commit()` | flush + COMMIT |
| `rollback()` | discard everything since the last commit |
| `close()` | release the connection back to the pool |

On error: `rollback()`. The `with Session(...)` block closes the session for you.

### 5. SQLAlchemy 2.0 queries

```python
from sqlalchemy import select, func

# one object by primary key
application = session.get(Application, 42)            # None if missing

# many objects
stmt = (
    select(Application)
    .where(Application.user_id == user_id, Application.status == "interview")
    .order_by(Application.created_at.desc())
    .limit(20)
)
applications = session.scalars(stmt).all()

# one or none
company = session.scalars(select(Company).where(Company.name == "Kopi Data")).one_or_none()

# aggregates
counts = session.execute(
    select(Application.status, func.count()).where(Application.user_id == user_id).group_by(Application.status)
).all()                                               # list of (status, count) rows
```

- `scalars(...)` returns the first column of each row — perfect when selecting whole objects.
- `execute(...)` returns rows with several columns.
- Values like `user_id` are sent as **bound parameters** — SQL injection safe.

:::note[Old style you'll see in existing code]
`Application.query.filter_by(user_id=7).all()` is the legacy Flask-SQLAlchemy query API. It still works, but new code and docs use `db.session.scalars(select(...))`.
:::

### 6. Flask-SQLAlchemy in a factory

```python
# extensions.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)          # created WITHOUT an app

# __init__.py
def create_app(config_object=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_object)   # includes SQLALCHEMY_DATABASE_URI
    db.init_app(app)                         # attach to THIS app
    ...
    return app
```

Flask-SQLAlchemy gives you `db.session`, a **scoped session per request/app context**, and **removes it at the end of every request** — so each request starts clean.

### 7. Session per request

```python
@applications_bp.post("")
def create_application():
    data = parse(request.get_json())
    application = Application(**data, user_id=current_user_id())
    db.session.add(application)
    db.session.commit()
    return {"data": serialize(application)}, 201
```

If anything raises before `commit()`, nothing is saved. In services that do several steps, commit **once** at the end of the unit of work (lesson 06).

### 8. See the SQL

Turn this on while learning. Every surprise in an ORM becomes obvious the moment you can see the query it actually sent.

```python
app.config["SQLALCHEMY_ECHO"] = True        # logs every SQL statement (development only!)
print(select(Application).where(Application.user_id == 7))   # shows the SQL of a statement
```

### 9. Pool settings (production preview)

| Setting | Meaning |
|---|---|
| `pool_size` | connections kept open per process (default 5) |
| `max_overflow` | extra temporary connections under load |
| `pool_pre_ping` | test connections before use |
| `pool_recycle` | reopen connections older than N seconds |

Gunicorn with 4 workers × (5 + 10 overflow) can open up to **60** connections — check that fits your database's `max_connections` (Week 6 / Module 5).

### Choosing your setup

Every option here is a trade-off:

| Choice | ✅ | ❌ |
|---|---|---|
| ORM | less boilerplate, objects, safe parameters, migrations integration | hidden queries, learning curve, can produce inefficient SQL |
| Raw SQL (psycopg) | full control, easy to optimize | manual mapping, repetitive, scattered SQL |
| SQLAlchemy Core (`select`, tables, no objects) | SQL-like, composable | less convenient than objects |
| Hybrid: ORM + raw SQL for hard reports | best of both | two styles in one codebase |
| Long-lived sessions | fewer objects created | stale data, memory growth, locks |

- ✅ The ORM for typical CRUD and business logic.
- ✅ `text()` or Core for complex reports, bulk operations, or database-specific features.
- 🚫 Don't create engines per request.
- 🚫 Don't share one session across threads or keep a session open for minutes.

## ⚠️ Common mistakes

- Forgetting to commit.
- Catching an exception but not rolling back → `PendingRollbackError` on the next query.
- Accessing an object's attributes after the session closed (`DetachedInstanceError`).
- Leaving `SQLALCHEMY_ECHO=True` in production (noisy, may log sensitive data).
- Mixing legacy `.query` and 2.0 `select()` styles randomly.

:::revoshop
RevoShop's `app/extensions.py` creates `db = SQLAlchemy()` without an app, and `create_app()` calls `db.init_app(flask_app)`. `config/base.py` reads `SQLALCHEMY_DATABASE_URI` from `DATABASE_URL`, and `config/development.py` sets `SQLALCHEMY_ECHO = True`. Open one repository (e.g. `app/repositories/product_repository.py`): is it using the legacy `Model.query` API or 2.0-style `select()`? Where are `commit()` calls — in repositories, services or routes? Is there any path where an exception after `add()` could leave a half-done unit of work committed?
:::

## 🏆 Best practices

- [ ] **One engine per process** (Flask-SQLAlchemy handles it); connection URL from `DATABASE_URL`.
- [ ] Use **short-lived sessions** — one per request or unit of work.
- [ ] Commit **once per unit of work**; roll back on errors (Flask-SQLAlchemy cleans up at request end).
- [ ] Use **SQLAlchemy 2.0 style** (`select()`, `scalars()`, `session.get()`) in new code.
- [ ] Turn on `SQLALCHEMY_ECHO` locally and **read the SQL** for important endpoints.
- [ ] Set `pool_pre_ping=True` (via `SQLALCHEMY_ENGINE_OPTIONS`) and size pools against the database's connection limit.
- [ ] Never build SQL with string formatting; use bound parameters (ORM expressions or `text(":param")`).
- [ ] Keep database access out of route functions — use repositories/services (lesson 06).

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain a connection pool to a non-programmer using taxis waiting at an airport versus calling a new taxi for every passenger. Then explain `flush` vs `commit` in one sentence each.

## 📐 Design it

For CareerPilot, write the SQLAlchemy 2.0 statements (Python, not SQL) for:
1. Get application 42 only if it belongs to user 7
2. List user 7's applications with status in `interview`/`offer`, newest first, page 2 (20 per page), plus the total count
3. Count applications per status for user 7
4. Create a company if no company with that name (case-insensitive) exists, then create an application for it — in **one** transaction

:::quiz
Show possible code

```python
# 1
application = db.session.scalars(
    select(Application).where(Application.id == 42, Application.user_id == 7)
).one_or_none()

# 2
base = select(Application).where(Application.user_id == 7, Application.status.in_(["interview", "offer"]))
items = db.session.scalars(base.order_by(Application.created_at.desc(), Application.id.desc()).limit(20).offset(20)).all()
total = db.session.scalar(select(func.count()).select_from(base.subquery()))

# 3
rows = db.session.execute(
    select(Application.status, func.count()).where(Application.user_id == 7).group_by(Application.status)
).all()

# 4
company = db.session.scalars(select(Company).where(func.lower(Company.name) == name.lower())).one_or_none()
if company is None:
    company = Company(name=name)
    db.session.add(company)
    db.session.flush()                      # get company.id without committing
db.session.add(Application(user_id=7, company_id=company.id, role_title=role))
db.session.commit()                         # both inserts, one transaction
```

For #4 under concurrency, also keep a unique index on `lower(name)` and handle `IntegrityError` (two requests can create the same company at the same moment).
:::

### 📝 Self-review checklist

- [ ] Ownership filter in #1
- [ ] Stable ordering and a separate total count in #2
- [ ] `flush` before using a generated id; one `commit` in #4
- [ ] I considered the race in #4

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m2/w4/02-sqlalchemy" ai="no-ai" title="Queries and units of work with SQLAlchemy 2.0"}
`models.py` (provided) defines `Company` and `Application` with Flask-SQLAlchemy. Implement `repository.py` functions using **2.0-style** queries against real PostgreSQL: get-for-user, paginated listing with a total, counts per status, and `create_application_with_company` that creates both rows in **one** transaction and rolls back cleanly on failure. The tests also count how many SQL statements your functions run.
:::

:::hints
- `db.session.scalars(select(Model).where(...)).one_or_none()`
- Total count: `select(func.count()).select_from(stmt.subquery())`
- Use `flush()` to get `company.id`, then `commit()` once.
- On `IntegrityError`, call `db.session.rollback()` before re-raising your own error.
:::

### 🏆 Stretch goal

Turn on `SQLALCHEMY_ECHO` in the test app and read the SQL generated for `list_applications`. Is the count query efficient?

## ✅ Quick check

:::quiz
What's the difference between the engine and the session?

The engine is created once per process and manages how to connect (dialect, driver, connection pool). The session is short-lived: it tracks objects and runs a unit of work in a transaction.
:::

:::quiz
Why call `flush()` before `commit()` sometimes?

To send pending inserts so the database generates values (like primary keys) you need for the next step — while keeping everything in the same, still-uncommitted transaction.
:::

:::quiz
What must you do after catching a database error inside a session?

Call `session.rollback()`; otherwise the session stays in a failed transaction state and further queries fail.
:::


## 📚 Keep learning

- [SQLAlchemy 2.0 Unified Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [SQLAlchemy: Session basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [Flask-SQLAlchemy: Quick start](https://flask-sqlalchemy.readthedocs.io/en/stable/quickstart/)
