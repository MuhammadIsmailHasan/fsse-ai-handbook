"""Repository and Unit of Work. See README.md."""

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


# TODO: InMemoryApplicationRepository, SqlApplicationRepository, InMemoryUnitOfWork, SqlUnitOfWork
