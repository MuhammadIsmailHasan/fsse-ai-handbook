---
title: "Repository & Unit of Work"
summary: Separate business logic from persistence — repositories as collection-like interfaces, units of work as transaction boundaries, fakes you can trust through contract tests, and when an ORM session already does the job.
type: lesson
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: optional }
durationMinutes: 150
tags: [architecture, repository, unit-of-work, transactions, testing, sqlalchemy]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- The **Repository** pattern: a collection-like interface over storage
- The **Unit of Work** pattern: one atomic business operation = one transaction
- Mapping between **domain objects** and database rows
- Fake implementations and **contract tests** that keep fakes honest
- How SQLAlchemy's `Session` already implements both patterns — and when adding your own layer is worth it
- Building on Module 2 Week 4 (layered architecture) and Week 2 (transactions)

## 🧠 The big idea

A **repository** is a **librarian**: you ask "give me application 42" or "shelve this one", and you don't care whether the books live on shelves, in a warehouse or in a digital archive.

A **unit of work** is a **shopping cart at checkout**: you put several items in, and payment happens **all at once** — either everything is bought or nothing is. You never end up having paid for half the cart.

## ❓ Why does this exist?

In Week 4 you saw routes full of `db.session` calls and moved them into repositories. Two problems remain in many codebases:

1. **Business logic tied to the database** → slow tests that need PostgreSQL for every rule.
2. **Unclear transaction boundaries** → some functions commit, others don't; a failure halfway leaves half-saved data.

The repository hides *how* data is stored; the unit of work decides *when* a batch of changes becomes permanent.

## 💥 What happens if we DON'T?

```python
def withdraw_all(user_id):
    for app in Application.query.filter_by(user_id=user_id):
        app.status = "withdrawn"
        db.session.commit()          # commits inside the loop
        send_withdrawal_email(app)   # fails on the 3rd application…
```

Two applications are withdrawn, the rest aren't, and emails went out for some. And testing the rule "only active applications can be withdrawn" requires a real database.

## 📖 How it works, step by step

### 1. The repository interface

```python
class ApplicationRepository(Protocol):
    def add(self, application: Application) -> int: ...
    def get(self, application_id: int) -> Application | None: ...
    def list_for_user(self, user_id: int) -> list[Application]: ...
    def update(self, application: Application) -> None: ...
    def remove(self, application_id: int) -> None: ...
```

Design rules:
- Speak the **domain's language** (`list_for_user`, `find_due_follow_ups`), not SQL (`select_where`).
- Return **domain objects** or `None`, never raw rows or ORM query objects that leak persistence.
- **No commit inside repository methods** — that's the unit of work's job.

### 2. Real implementation: mapping rows ↔ domain objects

```python
class SqlApplicationRepository:
    def __init__(self, connection):
        self._conn = connection

    def get(self, application_id):
        row = self._conn.execute(select(applications_table).where(applications_table.c.id == application_id)).first()
        return Application(user_id=row.user_id, company=row.company, role=row.role, status=row.status, id=row.id) if row else None
```

Here the domain `Application` is a plain dataclass; the repository does the mapping. (With SQLAlchemy ORM models you can also map classes directly — simpler, but then the domain class depends on SQLAlchemy.)

### 3. Unit of Work as a context manager

```python
class SqlUnitOfWork:
    def __init__(self, engine):
        self._engine = engine

    def __enter__(self):
        self._connection = self._engine.connect()
        self._transaction = self._connection.begin()
        self.applications = SqlApplicationRepository(self._connection)
        return self

    def commit(self):
        self._transaction.commit()
        self._transaction = self._connection.begin()

    def __exit__(self, *exc_info):
        if self._transaction.is_active:
            self._transaction.rollback()      # no commit or an exception → nothing saved
        self._connection.close()
```

```python
def withdraw_all(uow, user_id):
    with uow:
        for app in uow.applications.list_for_user(user_id):
            if app.is_active:
                app.status = "withdrawn"
                uow.applications.update(app)
        uow.commit()                          # one atomic change
    # send emails AFTER commit (or publish an event → worker)
```

**Explicit commit** is a deliberate choice: forgetting to commit loses changes safely, rather than auto-committing half-finished work.

### 4. Fakes

```python
class InMemoryUnitOfWork:
    def __enter__(self):
        self._working = copy.deepcopy(self._database)   # uncommitted changes live in a copy
        self.applications = InMemoryApplicationRepository(self._working)
        return self

    def commit(self):
        self._database.rows = copy.deepcopy(self._working.rows)
```

Service tests run in milliseconds with `InMemoryUnitOfWork` — hundreds of business-rule tests without Docker.

### 5. Contract tests: one test suite, two implementations

```python
@pytest.fixture(params=["memory", "sql"])
def make_uow(request): ...

def test_without_commit_nothing_is_saved(make_uow):
    with make_uow() as uow:
        uow.applications.add(new_app())
    with make_uow() as uow:
        assert uow.applications.list_for_user(1) == []
```

A fake that behaves differently from production is worse than no fake. Running the **same** tests against both proves they agree on the contract (ids, ordering, "not found" errors, rollback).

### 6. "Doesn't SQLAlchemy already do this?"

Yes:
- `Session` **is** a unit of work (tracks changes, flushes, `commit()`/`rollback()`),
- `session.get(Application, id)` / `session.scalars(select(...))` is repository-like.

| Situation | Recommendation |
|---|---|
| Small CRUD API, logic mostly in queries | use the `Session` directly in services (Week 4 style), test with PostgreSQL |
| Rich business rules, many unit tests, possible storage changes | add repository + UoW interfaces over SQLAlchemy |
| Several data sources in one use case (DB + external API + cache) | a UoW coordinating them is especially valuable |

## ⚖️ Trade-offs

| Choice | ✅ | ❌ |
|---|---|---|
| Repository interface | testable logic, persistence details in one place | extra layer; risk of reinventing the ORM |
| Generic repository (`get/add/remove` for all models) | little code | ends up leaking queries; weak domain language |
| Specific repositories | expressive (`find_due_follow_ups`) | more methods to maintain |
| Explicit UoW commit | clear, safe transaction boundaries | must remember to commit |
| Fakes + contract tests | fast tests you can trust | contract tests must be maintained with the interface |
| Domain dataclasses + mapping | domain independent of ORM | mapping code |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ Services with meaningful business rules you want to unit test.
- ✅ Operations touching several aggregates that must succeed or fail together.
- ✅ When storage might change (SQL → document store, or an external API as source of truth).
- 🚫 Thin CRUD endpoints with no logic — the extra layer adds nothing.
- 🚫 Complex reporting queries — use dedicated read-model queries (SQL views, query services) instead of forcing them through repositories.

## 🏆 Best practices

- [ ] Name repository methods in domain language; return domain objects or DTOs, never ORM queries.
- [ ] **Never commit inside repositories**; one use case = one unit of work = one commit.
- [ ] Roll back automatically on exceptions or missing commit; always close connections.
- [ ] Trigger side effects (emails, events) **after** commit.
- [ ] Keep fakes behind the same protocol and run **contract tests** against fake and real implementations.
- [ ] Don't create a repository per table by reflex — group by aggregate/use case.
- [ ] Use the ORM session directly when the extra abstraction wouldn't pay for itself — and say so in a design note.

## 🏭 How it's used in industry

- Domain-driven design teams (and the *Architecture Patterns with Python* / "Cosmic Python" book) use repository + UoW for complex domains like logistics and finance.
- Many successful Django/Flask apps skip the pattern and use the ORM directly — the right choice for CRUD-heavy products.
- Contract tests are common for adapters to external systems (payment gateways, message brokers), not only databases.

## ⚠️ Common mistakes

- `repository.save()` that commits — composing two saves loses atomicity.
- Returning SQLAlchemy `Query` objects from repositories so callers keep building SQL.
- Fakes that auto-assign ids differently, ignore rollback, or return shared mutable objects.
- Sending emails inside the transaction, before commit.

:::revoshop
RevoShop has `app/repositories/*`. (1) Open `order_repository.py`: does `OrderRepository.create` call `db.session.commit()`? What happens if you want to create an order **and** a payment record in one atomic operation from a service? (2) Do repository methods return model instances, dicts or queries? (3) The unit tests mock repositories (`tests/unit/test_order_service.py`) — what would a contract test between a fake repository and the real one catch that mocks don't?
:::

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain the unit of work to a non-programmer with the shopping cart analogy, then say what goes wrong in a checkout system that "pays for each item separately" when the card declines on the third item.

## 📐 Design it

CareerPilot's "Import from job board" use case: fetch 50 jobs from a partner API, create or update `Company` rows, create `Application` rows (status `saved`) for the ones the user selected, record an `ImportRun` (counts, errors), and send one summary notification. Design the repositories, the unit-of-work boundary(ies), what happens when the 30th job has invalid data, and how you'd test it quickly.

:::quiz
Show a possible design

**Repositories** (via one UoW): `companies` (`get_by_normalized_name`, `add`), `applications` (`add`, `exists_for_job(user_id, external_job_id)`), `import_runs` (`add`, `update`).

**Flow**
1. **Outside any transaction**: fetch the 50 jobs from the partner API (network calls shouldn't hold DB transactions open).
2. Validate/normalize each job in memory → split into `valid` and `rejected` (with reasons). Invalid job #30 is **rejected, not fatal**.
3. **UoW #1** (`with uow:`): upsert companies, add applications for selected valid jobs (skip ones already imported), add `ImportRun(counts, rejected_reasons)`, `commit()` — all or nothing for the database state.
4. **After commit**: publish `import_completed {run_id}` → worker sends the summary notification (retries independent of the import).

If an unexpected exception happens inside step 3 (e.g. database error), everything rolls back and the `ImportRun` can be recorded as failed in a **separate small UoW** so the user sees what happened.

**Testing**: service tests with `FakeUnitOfWork` + `FakeJobBoardClient` cover validation, duplicates and counts in milliseconds; contract tests prove fake and SQL repositories agree; one integration test runs the real UoW on PostgreSQL.
:::

### 📝 Self-review checklist

- [ ] Network I/O outside the transaction
- [ ] Clear rule for partial invalid data vs fatal errors
- [ ] Notification after commit
- [ ] Fast tests with fakes, plus contract/integration coverage

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/architecture/e-backend-architecture/01-repository-unit-of-work" ai="no-ai" title="Repositories and units of work — fake and PostgreSQL"}
Implement in-memory and SQLAlchemy Core repositories plus matching units of work. The same contract tests run against both: ids, independent objects, update/remove errors, no commit = no save, rollback on exceptions, and no leaked connections.
:::

:::hints
- SQL add: `insert(table).values(...).returning(table.c.id)` then `.scalar_one()`.
- SQL update/remove: check `result.rowcount == 0` to raise `LookupError`.
- `SqlUnitOfWork.__exit__`: roll back if `self._transaction.is_active`, then close in a `finally`.
- In-memory: `copy.deepcopy` the database on enter; copy objects on `get` so callers can't mutate stored rows.
:::

## ✅ Quick check

:::quiz
Why shouldn't repository methods commit?

Because a use case often changes several things that must succeed or fail together; commits inside repositories break that atomicity. The unit of work owns the transaction boundary.
:::

:::quiz
What does a contract test protect you from?

A fake implementation drifting from the real one, so tests pass with the fake while production behaves differently.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Repository | Repositori — antarmuka seperti koleksi untuk data |
| Unit of Work | Satuan kerja — satu transaksi untuk satu operasi bisnis |
| Atomic | Atomik — semua berhasil atau semua batal |
| Mapping | Pemetaan (baris database ↔ objek domain) |
| Fake | Implementasi tiruan yang berfungsi |
| Contract test | Tes kontrak — tes yang sama untuk beberapa implementasi |

## 📚 Keep learning

- [Cosmic Python — Repository pattern](https://www.cosmicpython.com/book/chapter_02_repository.html)
- [Cosmic Python — Unit of Work pattern](https://www.cosmicpython.com/book/chapter_06_uow.html)
- [SQLAlchemy docs: Session basics (the ORM's unit of work)](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
