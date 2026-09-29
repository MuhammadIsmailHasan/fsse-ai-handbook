---
title: "Database with SQLAlchemy 2.0"
summary: Connecting FastAPI to a database the modern way — SQLAlchemy 2.0 typed models, the select() query style, a Session as a unit of work, and wiring it all through a get_db dependency (with a note on SQLModel).
type: lesson
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: optional }
durationMinutes: 120
tags: [fastapi, sqlalchemy, database, orm, sqlmodel]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Defining tables as **typed models** in SQLAlchemy 2.0
- The modern **`select()`** query style (not the old `Query` API)
- The **`Session`** as a unit of work: add, commit, refresh
- Wiring the DB into FastAPI via a **`get_db`** dependency
- What **SQLModel** is and when it's handy

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **ORM** | Maps Python objects to database rows | Objek ↔ baris database |
| **Model** | A class that maps to a table | Kelas untuk sebuah tabel |
| **Session** | A unit of work batching DB changes | Unit kerja perubahan DB |
| **select()** | The 2.0 way to build a query | Cara membangun query 2.0 |
| **scalars** | Get model objects from a result | Ambil objek dari hasil |
| **commit** | Save the session's changes | Menyimpan perubahan |
| **SQLModel** | Pydantic + SQLAlchemy combined | Gabungan Pydantic + SQLAlchemy |

## 🧠 The big idea

An ORM is a **translator between two languages**: your code speaks Python objects, the database speaks rows and SQL. SQLAlchemy translates both ways so you work with `User` objects instead of writing raw SQL by hand. The **Session** is the translator's **notepad**: you jot down changes (add this user, update that one) and, on `commit`, it sends them all to the database in one transaction.

## ❓ Why it matters

You used SQLAlchemy with Flask in Module 2. FastAPI uses the *same* SQLAlchemy, but the modern **2.0 style** is more typed and explicit (the `select()` API), and you wire the session through a **dependency** instead of Flask's global `db`. Getting this pattern right gives you clean, testable data access with autocomplete and type-checking — and it's the exact setup real FastAPI projects use.

## 📖 Step by step

### 1. Typed models (2.0 style)

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
```

`Mapped[int]` / `mapped_column(...)` give typed columns — your editor knows `user.email` is a `str`.

### 2. Engine and Session

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql+psycopg://...")   # or sqlite:///./app.db
SessionLocal = sessionmaker(bind=engine)
```

The **engine** manages the connection pool; **`SessionLocal()`** creates a session (unit of work) per request.

### 3. Querying with select()

The 2.0 style builds a statement and executes it:

```python
from sqlalchemy import select

# one by primary key
user = session.get(User, 7)

# a query
stmt = select(User).where(User.email == "i@x.com")
user = session.scalars(stmt).first()

# a list
users = session.scalars(select(User).order_by(User.name)).all()
```

`scalars(...)` returns model objects (not rows). This replaces the old `session.query(User)` API.

### 4. Writing: add, commit, refresh

```python
user = User(name="Ismail", email="i@x.com")
session.add(user)
session.commit()          # sends the INSERT in a transaction
session.refresh(user)     # loads DB-generated fields (like id)
```

Everything between commits is one transaction — all-or-nothing, exactly as in Module 2.

### 5. Wire it into FastAPI with get_db

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users", response_model=UserOut, status_code=201)
def create_user(body: UserIn, db: Session = Depends(get_db)):
    user = User(name=body.name, email=body.email)
    db.add(user); db.commit(); db.refresh(user)
    return user
```

The `yield` dependency (last lesson) gives each request a fresh session that's always closed.

### 6. SQLModel (optional)

**SQLModel** (by FastAPI's author) merges Pydantic and SQLAlchemy: one class is *both* your table model *and* your API schema. It's convenient for small apps, but for complex cases many teams keep SQLAlchemy models and Pydantic schemas separate for clarity. Know it exists; either is fine.

### Choosing your data setup

| Situation | Do this |
|---|---|
| Query by primary key | `session.get(Model, id)` |
| Filter/sort query | `select(Model).where(...).order_by(...)` + `scalars` |
| Per-request session | a `get_db` yield dependency |
| Small app, want less boilerplate | consider SQLModel |
| Complex domain / clear layers | separate SQLAlchemy models + Pydantic schemas |

- ✅ Use the 2.0 `select()` style and typed `Mapped` columns.
- ✅ One session per request via a `get_db` dependency; commit in the handler/service.
- 🚫 Don't share one global session across requests; don't use the legacy `Query` API.

## ⚠️ Common mistakes

- Using the old `session.query(...)` API instead of `select()` (2.0 style).
- Sharing a single session across requests (causes threading and stale-data bugs).
- Forgetting to `commit()`, so changes are silently lost.
- Not closing the session (fixed by the `get_db` yield dependency).
- Returning ORM objects directly without a `response_model`, leaking columns.

:::revoshop
RevoShop uses Flask-SQLAlchemy (a Flask wrapper). (1) Its models map to the same tables — rewrite one model in plain SQLAlchemy 2.0 (`Mapped`, `mapped_column`). (2) Convert one `Model.query.filter_by(...)` call to the `select(...).where(...)` style. (3) In FastAPI you'd replace Flask's global `db.session` with a `get_db` dependency — where would that change RevoShop's route code?
:::

## 🏆 Best practices

- [ ] Define typed models with `Mapped`/`mapped_column`; use `select()` for queries.
- [ ] Give each request its own session via a `get_db` yield dependency.
- [ ] Commit deliberately; refresh to load generated fields like ids.
- [ ] Keep transactions clear — a use case is one commit (as in Module 2).
- [ ] Return via `response_model`, not raw ORM objects.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain the ORM with the translator analogy and the Session with the notepad analogy. Then show, in one line each, how to fetch a user by id and how to fetch by email in SQLAlchemy 2.0.

## 📐 Design it

Design the data layer for CareerPilot's `Application` model and its endpoints: a typed model (`id, user_id, company, role, status`), a `get_db` dependency, a create endpoint, and a "list my applications filtered by status" endpoint using `select()`. Note where the transaction boundary is.

:::quiz
Show a possible design

```python
class Application(Base):
    __tablename__ = "applications"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(index=True)
    company: Mapped[str]
    role: Mapped[str]
    status: Mapped[str] = mapped_column(default="saved")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.post("/users/{user_id}/applications", response_model=ApplicationOut, status_code=201)
def create(user_id: int, body: ApplicationIn, db: Session = Depends(get_db)):
    app_row = Application(user_id=user_id, company=body.company, role=body.role, status=body.status)
    db.add(app_row); db.commit(); db.refresh(app_row)   # ← one transaction
    return app_row

@app.get("/users/{user_id}/applications", response_model=list[ApplicationOut])
def list_apps(user_id: int, status: str | None = None, db: Session = Depends(get_db)):
    stmt = select(Application).where(Application.user_id == user_id)
    if status:
        stmt = stmt.where(Application.status == status)
    return db.scalars(stmt.order_by(Application.id)).all()
```

- Typed model with an index on `user_id` (the filter column, per Stage F indexing).
- `get_db` gives a per-request session; the **transaction boundary** is the create's `add`+`commit`.
- The list uses `select().where()` and builds the filter conditionally.

**Rule shown:** 2.0 typed models + `select()`, one session per request via `get_db`, and a clear one-commit transaction per write.
:::

### 📝 Self-review checklist

- [ ] Model uses `Mapped`/`mapped_column`; hot filter column indexed
- [ ] `get_db` yield dependency for the session
- [ ] Queries use `select()` + `scalars`
- [ ] Transaction boundary (one commit per use case) is clear

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m3/w2/03-sqlalchemy" ai="no-ai" title="SQLAlchemy 2.0 CRUD (SQLite)"}
Using SQLAlchemy 2.0 against an in-memory SQLite database (no server needed), define a `User` model and implement `create_user`, `get_user`, and `list_users_by_domain` (email ends with a domain) using `session.add/commit`, `session.get`, and `select().where()`. The tests create a session, insert users, and check queries.
:::

:::hints
- `Base(DeclarativeBase)`, `User` with `id` (pk), `name`, `email`.
- `create_user(session, name, email)`: build, `add`, `commit`, `refresh`, return it.
- `get_user(session, user_id)`: `session.get(User, user_id)`.
- `list_users_by_domain(session, domain)`: `select(User).where(User.email.endswith(domain))` then `scalars(...).all()`.
:::

## ✅ Quick check

:::quiz
In SQLAlchemy 2.0, how do you fetch one row by primary key vs. run a filtered query?

By primary key: `session.get(Model, id)`. For a filtered query, build a statement with `select(Model).where(...)` and execute it with `session.scalars(stmt).first()` (one) or `.all()` (many). The 2.0 style favors `select()` over the legacy `session.query(...)`.
:::

:::quiz
Why give each request its own Session via `get_db` instead of one global session?

A Session is a per-unit-of-work object and isn't safe to share across concurrent requests — a global one causes threading issues and stale data. A `get_db` yield dependency creates a fresh session per request and always closes it, keeping transactions isolated and clean.
:::

## 📚 Keep learning

- [SQLAlchemy 2.0: ORM quickstart](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
- [FastAPI: SQL databases](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [SQLModel documentation](https://sqlmodel.tiangolo.com/)
