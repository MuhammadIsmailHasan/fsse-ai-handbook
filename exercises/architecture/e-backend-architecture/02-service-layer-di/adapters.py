"""Provided: simple adapters used as defaults by bootstrap()."""

import copy
import logging
from datetime import UTC, datetime

from domain import Application


class InMemoryRepository:
    def __init__(self, rows: dict[int, Application]):
        self.rows = rows

    def add(self, application: Application) -> int:
        application.id = max(self.rows, default=0) + 1
        self.rows[application.id] = application
        return application.id

    def get(self, application_id: int) -> Application | None:
        return self.rows.get(application_id)

    def list_for_user(self, user_id: int) -> list[Application]:
        return [a for _, a in sorted(self.rows.items()) if a.user_id == user_id]


class InMemoryUnitOfWork:
    def __init__(self) -> None:
        self.committed_rows: dict[int, Application] = {}
        self.commits = 0

    def __enter__(self):
        self.applications = InMemoryRepository(copy.deepcopy(self.committed_rows))
        return self

    def __exit__(self, *exc_info) -> None:
        pass  # uncommitted changes are simply dropped

    def commit(self) -> None:
        self.committed_rows = copy.deepcopy(self.applications.rows)
        self.commits += 1


class LoggingPublisher:
    def publish(self, name: str, payload: dict) -> None:
        logging.getLogger("events").info(name, extra={"payload": payload})


def system_clock() -> datetime:
    return datetime.now(UTC)
