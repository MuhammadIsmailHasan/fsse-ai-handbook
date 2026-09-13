"""Provided: the domain model. Pure Python — no Flask, no database."""

from dataclasses import dataclass
from datetime import datetime

TRANSITIONS = {
    "saved": {"applied", "withdrawn"},
    "applied": {"interview", "rejected", "withdrawn"},
    "interview": {"offer", "rejected", "withdrawn"},
    "offer": {"accepted", "rejected", "withdrawn"},
}
FINAL = {"accepted", "rejected", "withdrawn"}


class InvalidTransition(Exception):
    def __init__(self, current: str, target: str):
        super().__init__(f"cannot move from {current} to {target}")
        self.current, self.target = current, target


@dataclass
class Application:
    user_id: int
    company: str
    role: str
    created_at: datetime
    updated_at: datetime
    status: str = "saved"
    id: int | None = None

    @property
    def is_active(self) -> bool:
        return self.status not in FINAL

    def move_to(self, new_status: str) -> None:
        if new_status not in TRANSITIONS.get(self.status, set()):
            raise InvalidTransition(self.status, new_status)
        self.status = new_status
