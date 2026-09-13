"""Provided: what the service layer needs from the outside world (owned by the application, implemented by adapters)."""

from datetime import datetime
from typing import Callable, Protocol

from domain import Application

Clock = Callable[[], datetime]


class ApplicationRepository(Protocol):
    def add(self, application: Application) -> int: ...
    def get(self, application_id: int) -> Application | None: ...
    def list_for_user(self, user_id: int) -> list[Application]: ...


class UnitOfWork(Protocol):
    applications: ApplicationRepository

    def __enter__(self) -> "UnitOfWork": ...
    def __exit__(self, *exc_info) -> None: ...
    def commit(self) -> None: ...


class EventPublisher(Protocol):
    def publish(self, name: str, payload: dict) -> None: ...
