"""Reference solution: business rules only — no Flask, no SQLAlchemy."""

from collections.abc import Callable
from datetime import datetime
from typing import Protocol

from .errors import ApplicationNotFound, InvalidTransition, ValidationFailed
from .models import Application

TRANSITIONS: dict[str, frozenset[str]] = {
    "applied": frozenset({"interview", "rejected"}),
    "interview": frozenset({"offer", "rejected"}),
    "offer": frozenset({"accepted", "declined"}),
}


class ApplicationRepository(Protocol):
    def get_for_user(self, application_id: int, user_id: int) -> Application | None: ...
    def list_for_user(self, user_id: int) -> list[Application]: ...
    def add(self, application: Application) -> None: ...
    def commit(self) -> None: ...


class ApplicationService:
    def __init__(self, repository: ApplicationRepository, clock: Callable[[], datetime]):
        self._repository = repository
        self._clock = clock

    def create(self, user_id: int, data: dict) -> Application:
        cleaned, errors = {}, {}
        for field in ("company", "role_title"):
            value = data.get(field)
            if isinstance(value, str) and value.strip():
                cleaned[field] = value.strip()
            else:
                errors[field] = "required"
        if errors:
            raise ValidationFailed(errors)

        now = self._clock()
        application = Application(user_id=user_id, status="applied", created_at=now, updated_at=now, **cleaned)
        self._repository.add(application)
        self._repository.commit()  # one unit of work, one commit
        return application

    def list(self, user_id: int) -> list[Application]:
        return self._repository.list_for_user(user_id)

    def change_status(self, user_id: int, application_id: int, status: str) -> Application:
        application = self._repository.get_for_user(application_id, user_id)
        if application is None:
            raise ApplicationNotFound(application_id)
        if status not in TRANSITIONS.get(application.status, frozenset()):
            raise InvalidTransition(f"can't move from {application.status} to {status}")
        application.status = status
        application.updated_at = self._clock()
        self._repository.commit()
        return application
