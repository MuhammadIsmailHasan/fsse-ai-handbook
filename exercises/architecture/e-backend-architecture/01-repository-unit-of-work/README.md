# Architecture · E · Repository & Unit of Work (fake and real)

> 🚫🤖 **No-AI** · ⏱️ ~90 min · needs the exercise database (`docker compose up -d`)

Provided in `storage.py`: the domain dataclass `Application` (no ORM!), the SQLAlchemy **Core** table `applications_table`, the `InMemoryDatabase` holder, and the protocols. Implement:

| Class | Contract |
|---|---|
| `InMemoryApplicationRepository(rows, next_id)` | works on the dict it's given |
| `SqlApplicationRepository(connection)` | uses SQLAlchemy Core (`insert(...).returning(...)`, `select`, `update`, `delete`) on the given connection |
| `InMemoryUnitOfWork(database)` | on enter: work on a **copy** of `database.rows`; `commit()` writes the copy back; leaving without commit discards changes |
| `SqlUnitOfWork(engine)` | on enter: open a connection and begin a transaction; `commit()` commits (further work goes in a new transaction); on exit: roll back anything uncommitted, close the connection |

Repository contract (both implementations):
- `add(application)` → stores it, sets `application.id` (1, 2, 3… for in-memory; database id for SQL) and returns the id
- `get(application_id)` → an `Application` or `None` (a **new** object; changing it does nothing until `update`)
- `list_for_user(user_id)` → that user's applications ordered by id
- `update(application)` → saves changed fields; unknown id → `LookupError`
- `remove(application_id)` → deletes; unknown id → `LookupError`

Unit of work contract:
- `with uow:` gives `uow.applications` (a repository)
- exceptions inside the block → rollback, and the exception still propagates
- no `commit()` → nothing is saved

The **same contract tests** run against the fake and the real implementation. That's how you know the fake is trustworthy.

```bash
cd exercises
uv run pytest architecture/e-backend-architecture/01-repository-unit-of-work
```
