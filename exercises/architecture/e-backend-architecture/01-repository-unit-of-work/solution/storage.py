"""Repository and Unit of Work — reference solution."""

import copy
from dataclasses import dataclass, field
from typing import Protocol

from sqlalchemy import Column, Integer, MetaData, String, Table, delete, insert, select, update
from sqlalchemy.engine import Connection, Engine


@dataclass
class Application:
    """Domain object: plain Python, no database knowledge."""

    user_id: int
    company: str
    role: str
    status: str = "saved"
    id: int | None = None


metadata = MetaData()
applications_table = Table(
    "applications",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, nullable=False, index=True),
    Column("company", String(200), nullable=False),
    Column("role", String(200), nullable=False),
    Column("status", String(20), nullable=False),
)


@dataclass
class InMemoryDatabase:
    """Pretend database for the fake unit of work."""

    rows: dict[int, Application] = field(default_factory=dict)
    next_id: int = 1


class ApplicationRepository(Protocol):
    def add(self, application: Application) -> int: ...
    def get(self, application_id: int) -> Application | None: ...
    def list_for_user(self, user_id: int) -> list[Application]: ...
    def update(self, application: Application) -> None: ...
    def remove(self, application_id: int) -> None: ...


class UnitOfWork(Protocol):
    applications: ApplicationRepository

    def __enter__(self) -> "UnitOfWork": ...
    def __exit__(self, *exc_info) -> None: ...
    def commit(self) -> None: ...


# ---------- Repositories ----------


class InMemoryApplicationRepository:
    def __init__(self, database: InMemoryDatabase):
        self._db = database

    def add(self, application: Application) -> int:
        application.id = self._db.next_id
        self._db.next_id += 1
        self._db.rows[application.id] = copy.copy(application)
        return application.id

    def get(self, application_id: int) -> Application | None:
        row = self._db.rows.get(application_id)
        return copy.copy(row) if row else None

    def list_for_user(self, user_id: int) -> list[Application]:
        return [copy.copy(a) for _, a in sorted(self._db.rows.items()) if a.user_id == user_id]

    def update(self, application: Application) -> None:
        if application.id not in self._db.rows:
            raise LookupError(f"application {application.id} not found")
        self._db.rows[application.id] = copy.copy(application)

    def remove(self, application_id: int) -> None:
        if self._db.rows.pop(application_id, None) is None:
            raise LookupError(f"application {application_id} not found")


def _to_domain(row) -> Application:
    return Application(user_id=row.user_id, company=row.company, role=row.role, status=row.status, id=row.id)


class SqlApplicationRepository:
    def __init__(self, connection: Connection):
        self._conn = connection

    def add(self, application: Application) -> int:
        new_id = self._conn.execute(
            insert(applications_table)
            .values(user_id=application.user_id, company=application.company, role=application.role, status=application.status)
            .returning(applications_table.c.id)
        ).scalar_one()
        application.id = new_id
        return new_id

    def get(self, application_id: int) -> Application | None:
        row = self._conn.execute(select(applications_table).where(applications_table.c.id == application_id)).first()
        return _to_domain(row) if row else None

    def list_for_user(self, user_id: int) -> list[Application]:
        rows = self._conn.execute(
            select(applications_table).where(applications_table.c.user_id == user_id).order_by(applications_table.c.id)
        )
        return [_to_domain(row) for row in rows]

    def update(self, application: Application) -> None:
        result = self._conn.execute(
            update(applications_table)
            .where(applications_table.c.id == application.id)
            .values(user_id=application.user_id, company=application.company, role=application.role, status=application.status)
        )
        if result.rowcount == 0:
            raise LookupError(f"application {application.id} not found")

    def remove(self, application_id: int) -> None:
        result = self._conn.execute(delete(applications_table).where(applications_table.c.id == application_id))
        if result.rowcount == 0:
            raise LookupError(f"application {application_id} not found")


# ---------- Units of work ----------


class InMemoryUnitOfWork:
    def __init__(self, database: InMemoryDatabase):
        self._database = database

    def __enter__(self) -> "InMemoryUnitOfWork":
        self._working = copy.deepcopy(self._database)  # uncommitted changes live only here
        self.applications = InMemoryApplicationRepository(self._working)
        return self

    def commit(self) -> None:
        self._database.rows = copy.deepcopy(self._working.rows)
        self._database.next_id = self._working.next_id

    def __exit__(self, *exc_info) -> None:
        self._working = None  # type: ignore[assignment]  # discard anything not committed


class SqlUnitOfWork:
    def __init__(self, engine: Engine):
        self._engine = engine

    def __enter__(self) -> "SqlUnitOfWork":
        self._connection = self._engine.connect()
        self._transaction = self._connection.begin()
        self.applications = SqlApplicationRepository(self._connection)
        return self

    def commit(self) -> None:
        self._transaction.commit()
        self._transaction = self._connection.begin()

    def __exit__(self, *exc_info) -> None:
        try:
            if self._transaction.is_active:
                self._transaction.rollback()
        finally:
            self._connection.close()
