---
title: "Models: Defining Database Tables as Python Classes"
summary: Write typed SQLAlchemy 2.0 models — columns, nullability, defaults, constraints, indexes, timestamps and enums — so Python and PostgreSQL agree on the rules.
type: lesson
source: core
roles: { be: core, fe: none, fs: core, ai: recommended, ops: optional }
durationMinutes: 150
tags: [flask, sqlalchemy, models, orm, constraints]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Declarative models with **`Mapped[...]`** and **`mapped_column()`** (SQLAlchemy 2.0)
- How Python type hints decide **nullability**
- Python-side defaults vs **server defaults**; `created_at` / `updated_at`
- Constraints and indexes in models: `unique`, `CheckConstraint`, `UniqueConstraint`, `Index`, **naming conventions**
- Enums for statuses, money columns, and `__repr__`
- Keeping models focused: what belongs in a model and what doesn't

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Model** | A Python class that describes one table | Kelas penggambar tabel |
| **`Mapped[...]` / `mapped_column()`** | The modern way to declare a column and its type | Cara mendeklarasikan kolom |
| **Nullable** | Whether the column may be empty | Boleh kosong atau tidak |
| **Python default** | A value your code fills in when creating the row | Nilai bawaan dari kode |
| **Server default** | A value the database fills in (`now()`) | Nilai bawaan dari database |
| **Constraint** | A rule the database enforces (`UNIQUE`, `CHECK`) | Aturan yang dipaksakan database |
| **Naming convention** | Predictable names for constraints and indexes | Pola penamaan |
| **Enum** | A fixed set of allowed values (statuses) | Kumpulan nilai yang diizinkan |
| **`__repr__`** | A readable text form of the object, for logs and debugging | Bentuk teks objek |

## 🧠 The big idea

A model is a **contract written twice at once**: once in Python, so your code knows the shape of the data, and once in the database, so the rules are actually enforced. SQLAlchemy lets you write it **once** as a class and generates the table — and later the migrations — from it.

The table you wrote by hand in SQL in Week 2 becomes:

```python
class Application(db.Model):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    role_title: Mapped[str] = mapped_column(String(200))
    salary_expectation: Mapped[int | None]
```

## ❓ Why it matters

Your app needs Python objects with attributes; the database needs tables with columns and constraints. Keeping the two in step by hand drifts over time — and models are also the input for **migrations** (lesson 04), **relationships** (lesson 05) and type checking in your services.

Careless models cause quiet damage:

```python
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String)          # any text, nullable, no rule
    salary = db.Column(db.Float)           # money as float 😬
    created_at = db.Column(db.DateTime, default=datetime.now())   # evaluated ONCE at import time!
```

- `status` accepts `NULL` and `"aplied"`.
- Money gets rounding errors.
- `default=datetime.now()` — with the parentheses — freezes the time the app started, so every row gets the same timestamp.
- Unnamed constraints produce unreadable migrations and error messages.

## 📖 Step by step

### 1. The base and a first model

```python
from datetime import datetime
from sqlalchemy import MetaData, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)

db = SQLAlchemy(model_class=Base)
```

A **naming convention** gives every constraint a predictable name — essential for migrations that drop or alter constraints later.

### 2. Typed columns

```python
class Company(db.Model):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    website: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
```

| Python annotation | Database |
|---|---|
| `Mapped[str]` | `NOT NULL` |
| `Mapped[str \| None]` | nullable |
| `Mapped[int]` | `INTEGER NOT NULL` (use `BigInteger` explicitly for very large ids/amounts) |
| `Mapped[bool]` | `BOOLEAN NOT NULL` |
| `Mapped[datetime]` | `TIMESTAMP NOT NULL` — add `DateTime(timezone=True)` for `timestamptz` |
| `Mapped[Decimal]` | `NUMERIC` — specify precision: `Numeric(12, 2)` |

The type hint is the **single source of truth** for nullability — and your type checker understands it too.

### 3. Defaults: Python side vs server side

Remember the difference by who fills the form: a Python default is filled by your app before sending it; a server default is filled by the database when the row arrives — including for rows inserted by scripts or other services.

```python
from sqlalchemy import DateTime, func

class Application(db.Model):
    status: Mapped[str] = mapped_column(String(30), default="applied", server_default="applied")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
```

| Option | Who sets the value | Applies to |
|---|---|---|
| `default=` | SQLAlchemy, when inserting through the ORM | ORM inserts only |
| `server_default=` | the **database** (`DEFAULT` in the table) | every insert, including raw SQL and other apps |
| `onupdate=` | SQLAlchemy on ORM updates | ORM updates only |

Pass **functions**, not results: `default=datetime.now` or `func.now()` — never `datetime.now()`.

### 4. Constraints and indexes

```python
from sqlalchemy import CheckConstraint, Index, UniqueConstraint

class Application(db.Model):
    __tablename__ = "applications"
    __table_args__ = (
        CheckConstraint("salary_expectation >= 0", name="salary_non_negative"),
        CheckConstraint("length(trim(role_title)) > 0", name="role_title_not_blank"),
        UniqueConstraint("user_id", "company_id", "role_title", name="uq_applications_user_company_role"),
        Index("ix_applications_user_created", "user_id", "created_at"),
    )
```

The Week 2 rules move into the model: checks, composite uniqueness, composite indexes (lesson 06 of Week 2).

### 5. Enums for statuses

```python
import enum
from sqlalchemy import Enum

class ApplicationStatus(enum.StrEnum):
    WISHLIST = "wishlist"
    APPLIED = "applied"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"

status: Mapped[ApplicationStatus] = mapped_column(
    Enum(
        ApplicationStatus,
        native_enum=False,          # store as VARCHAR instead of a PostgreSQL ENUM type
        create_constraint=True,     # add a CHECK constraint with the allowed values
        length=30,
        values_callable=lambda e: [m.value for m in e],
    ),
    default=ApplicationStatus.APPLIED,
)
```

`native_enum=False` stores a `VARCHAR`, which is easier to change later than a PostgreSQL `ENUM` type. `values_callable` stores the lowercase **values** instead of member names.

:::warning[The CHECK constraint is opt-in]
Since SQLAlchemy 1.4, a non-native `Enum` does **not** create a `CHECK` constraint unless you pass `create_constraint=True`. Without it, Python validates values, but the database accepts any text — raw SQL, scripts and other services can insert `'hired'`. Always verify with an invalid insert.
:::

### 6. `__repr__` and small domain methods

```python
    def __repr__(self) -> str:
        return f"<Application id={self.id} {self.role_title!r} status={self.status}>"

    @property
    def is_active(self) -> bool:
        return self.status in {ApplicationStatus.APPLIED, ApplicationStatus.INTERVIEW}
```

### 7. What belongs in a model?

Keep a model close to the table: fields, rules and tiny helpers. Business processes that touch several tables belong in a service (lesson 06), or the model becomes a second, hidden application.

| ✅ In the model | ❌ Not in the model |
|---|---|
| columns, constraints, relationships | HTTP request/response handling |
| simple derived properties (`is_active`) | sending emails, calling external APIs |
| small invariants about its own fields | queries across many tables (→ repositories) |
| | JSON serialization for a specific endpoint (→ schemas) |

Models that grow `to_dict_for_admin_page()`, `send_welcome_email()` and 30 query helpers become hard to change.

### Choosing your setup

Every option here is a trade-off:

| Choice | ✅ | ❌ |
|---|---|---|
| Typed `Mapped[...]` style | type checking, clear nullability, modern docs | different from older tutorials (`db.Column`) |
| Legacy `db.Column(...)` | common in existing code | nullable by default (easy to forget `nullable=False`), no typing |
| `server_default` | enforced for every writer | value not visible on the Python object until refreshed |
| Python `default` | immediate in Python | raw SQL inserts skip it |
| Non-native enum (VARCHAR + CHECK via `create_constraint=True`) | easy to evolve | slightly larger storage; remember the opt-in flag |
| Native PostgreSQL ENUM | compact | altering values needs special migrations |

- ✅ Declare **every** rule that must always hold in the model/table (nullability, uniqueness, checks).
- ✅ Use `server_default` for timestamps and important defaults.
- 🚫 Don't use `db.create_all()` to manage production schemas — use migrations (lesson 04).
- 🚫 Don't put business workflows or presentation logic in models.

## ⚠️ Common mistakes

- `default=datetime.now()` (evaluated once).
- Forgetting timezone-aware timestamps.
- `Float` for money.
- Missing `nullable=False` in legacy `db.Column` style.
- Unnamed constraints that migrations can't reference.

:::revoshop
Open `app/models/products.py` in RevoShop. It uses the legacy `db.Column` style: `price = db.Column(db.Numeric(11, 2), nullable=False)` (good — Numeric for money), a **named** check constraint `ck_products_price_non_negative`, foreign keys with `ondelete='SET NULL'` and `index=True`, `is_active` for soft deletes, and `created_at = db.Column(db.DateTime, default=utcnow)`. Answer: (1) Is `created_at` timezone-aware? (2) Which columns are nullable only because `nullable=False` was omitted? (3) Rewrite the model in the typed `Mapped` style — what changes? (4) `to_dict()` lives on the model: what are the pros and cons compared with a marshmallow schema?
:::

## 🏆 Best practices

- [ ] Use **SQLAlchemy 2.0 typed models** (`Mapped`, `mapped_column`) for new code.
- [ ] Configure a **naming convention** on the metadata before the first migration.
- [ ] Let `Mapped[X | None]` define nullability — and allow `None` only when it's meaningful.
- [ ] Timestamps: `DateTime(timezone=True)` with `server_default=func.now()`; `updated_at` with `onupdate`.
- [ ] Money: `Numeric(precision, scale)` or integer smallest units — never `Float`.
- [ ] Statuses as `StrEnum` (non-native **with `create_constraint=True`**) or an explicit `CHECK` — never free text.
- [ ] Add `__table_args__` constraints and composite indexes that match real queries.
- [ ] Give models a helpful `__repr__`; keep them small.
- [ ] Pass callables to defaults (`func.now()`, `datetime.now`), never evaluated values.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a non-programmer why a database rule (like "salary can't be negative") should exist both in the Python model and in the database table, even though it feels like writing it twice.

## 📐 Design it

Write the typed SQLAlchemy model (fields, types, nullability, defaults, constraints, indexes) for a CareerPilot **`Interview`**: belongs to an application; type (`hr`, `technical`, `system_design`, `final`); scheduled start and end (timezone-aware; end after start); optional meeting URL; outcome (`pending`, `passed`, `failed`) defaulting to pending; optional notes; timestamps. Frequent query: "upcoming interviews for a user's applications, ordered by start time".

:::quiz
Show a possible model

```python
class InterviewType(enum.StrEnum):
    HR = "hr"; TECHNICAL = "technical"; SYSTEM_DESIGN = "system_design"; FINAL = "final"

class InterviewOutcome(enum.StrEnum):
    PENDING = "pending"; PASSED = "passed"; FAILED = "failed"

def str_enum(e):
    return Enum(e, native_enum=False, create_constraint=True, length=30, values_callable=lambda m: [x.value for x in m])

class Interview(db.Model):
    __tablename__ = "interviews"
    __table_args__ = (
        CheckConstraint("ends_at > starts_at", name="ends_after_starts"),
        Index("ix_interviews_application_starts", "application_id", "starts_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"))
    type: Mapped[InterviewType] = mapped_column(str_enum(InterviewType))
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    meeting_url: Mapped[str | None] = mapped_column(String(500))
    outcome: Mapped[InterviewOutcome] = mapped_column(
        str_enum(InterviewOutcome), default=InterviewOutcome.PENDING, server_default="pending"
    )
    notes: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

The composite index `(application_id, starts_at)` serves "interviews of these applications ordered by time".
:::

### 📝 Self-review checklist

- [ ] Nullability matches the requirements exactly
- [ ] Timestamps are timezone-aware with server defaults
- [ ] Enums/checks restrict statuses and the time window
- [ ] The index matches the frequent query

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m2/w4/03-models" ai="no-ai" title="Typed models that enforce the rules"}
Write `models.py` with a naming convention, `User`, `Company` and `Application` models in SQLAlchemy 2.0 typed style. The tests create the tables in a fresh PostgreSQL schema, **inspect** the real columns and constraints, and try inserting invalid data — so the rules must exist in the database, not only in Python.
:::

:::hints
- Nullable = `Mapped[X | None]`; everything else is `NOT NULL`.
- Timezone-aware: `mapped_column(DateTime(timezone=True), server_default=func.now())`.
- Case-insensitive unique email: `Index("ix_users_email_lower", func.lower(email), unique=True)` inside `__table_args__` (reference the column after it's defined, or use `text("lower(email)")`).
- For the status enum, use `native_enum=False`, `create_constraint=True` and `values_callable` — then check that inserting `'hired'` really fails.
:::

### 🏆 Stretch goal

Add a `to_summary()` method… then move it into a separate `serializers.py` and explain in your notes why that's the better home.

## ✅ Quick check

:::quiz
How does SQLAlchemy 2.0 decide whether a column is nullable?

From the `Mapped[...]` annotation: `Mapped[str]` is `NOT NULL`, `Mapped[str | None]` is nullable (unless overridden with `nullable=`).
:::

:::quiz
What's wrong with `default=datetime.now()`?

The function is called once when the module loads, so every row gets that same fixed timestamp. Pass the callable (`datetime.now`) or use `server_default=func.now()`.
:::

:::quiz
Why configure a naming convention for constraints?

So every constraint and index gets a predictable name, which migrations need to alter or drop them and which makes errors readable.
:::


## 📚 Keep learning

- [SQLAlchemy: Declarative mapping with mapped_column](https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html)
- [SQLAlchemy: Configuring constraint naming conventions](https://docs.sqlalchemy.org/en/20/core/constraints.html#configuring-constraint-naming-conventions)
- [Flask-SQLAlchemy: Models and tables](https://flask-sqlalchemy.readthedocs.io/en/stable/models/)
