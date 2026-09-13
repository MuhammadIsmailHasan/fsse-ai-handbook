"""Reference solution."""

import functools
from datetime import date


class InvalidTransition(Exception):
    pass


class SalaryRange:
    __slots__ = ("_minimum", "_maximum")

    def __init__(self, minimum: int, maximum: int):
        if minimum < 0 or maximum < minimum:
            raise ValueError(f"invalid salary range: {minimum}–{maximum}")
        self._minimum = minimum
        self._maximum = maximum

    @property
    def minimum(self) -> int:
        return self._minimum

    @property
    def maximum(self) -> int:
        return self._maximum

    @property
    def midpoint(self) -> int:
        return (self._minimum + self._maximum) // 2

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SalaryRange):
            return NotImplemented
        return (self._minimum, self._maximum) == (other._minimum, other._maximum)

    def __hash__(self) -> int:
        return hash((self._minimum, self._maximum))

    def __repr__(self) -> str:
        return f"SalaryRange({self._minimum}, {self._maximum})"


@functools.total_ordering
class Application:
    TRANSITIONS: dict[str, frozenset[str]] = {
        "applied": frozenset({"interview", "rejected", "withdrawn"}),
        "interview": frozenset({"interview", "offer", "rejected", "withdrawn"}),
        "offer": frozenset({"accepted", "declined"}),
    }
    ACTIVE = frozenset({"applied", "interview"})

    def __init__(self, company: str, role: str, applied_on: date, salary: SalaryRange | None = None):
        self.company = company
        self.role = role
        self.applied_on = applied_on
        self.salary = salary
        self._status = "applied"
        self._history: list[tuple[str, date]] = [("applied", applied_on)]

    @property
    def status(self) -> str:
        return self._status

    @property
    def history(self) -> list[tuple[str, date]]:
        return list(self._history)  # a copy: callers can't change internal state

    @property
    def is_active(self) -> bool:
        return self._status in self.ACTIVE

    @property
    def last_changed_on(self) -> date:
        return self._history[-1][1]

    def move_to(self, status: str, on: date) -> None:
        if status not in self.TRANSITIONS.get(self._status, frozenset()):
            raise InvalidTransition(f"{self._status!r} → {status!r}")
        self._status = status
        self._history.append((status, on))

    def __lt__(self, other: "Application") -> bool:
        if not isinstance(other, Application):
            return NotImplemented
        return self.applied_on < other.applied_on

    def __eq__(self, other: object) -> bool:
        return self is other

    __hash__ = object.__hash__

    def __repr__(self) -> str:
        return f"Application({self.company!r}, {self.role!r}, status={self._status!r})"


class ReminderService:
    def __init__(self, notifier):
        self._notifier = notifier  # composition: injected dependency

    def send_follow_ups(self, applications, today: date, after_days: int = 14) -> int:
        due = [
            application
            for application in applications
            if application.is_active and (today - application.last_changed_on).days > after_days
        ]
        for application in due:
            self._notifier.send(f"Follow up with {application.company} ({application.role})")
        return len(due)
