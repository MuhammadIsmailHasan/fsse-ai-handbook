"""Strategy, Observer and Command — reference solution."""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from typing import Callable, Protocol


@dataclass
class Board:
    """Provided: the receiver that commands act on."""

    statuses: dict[int, str] = field(default_factory=dict)
    notes: dict[int, list[str]] = field(default_factory=dict)


# ---------- Strategy ----------


class ScoringStrategy(Protocol):
    def score(self, job: dict) -> float: ...


class BySalary:
    def score(self, job: dict) -> float:
        return job["salary_max"] or 0


class ByRecency:
    def __init__(self, today: date):
        self.today = today

    def score(self, job: dict) -> float:
        return -(self.today - job["posted_on"]).days


class BySkillMatch:
    def __init__(self, my_skills: list[str]):
        self.my_skills = {skill.lower() for skill in my_skills}

    def score(self, job: dict) -> float:
        wanted = {skill.lower() for skill in job["skills"]}
        return len(wanted & self.my_skills) / len(wanted) if wanted else 0.0


def rank_jobs(jobs: list[dict], strategy: ScoringStrategy) -> list[dict]:
    return sorted(jobs, key=lambda job: (-strategy.score(job), job["id"]))


# ---------- Observer ----------


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable[[dict], None]]] = defaultdict(list)
        self._logger = logging.getLogger("events")

    def subscribe(self, event_type: str, handler: Callable[[dict], None]) -> Callable[[], None]:
        self._handlers[event_type].append(handler)

        def unsubscribe() -> None:
            if handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)

        return unsubscribe

    def publish(self, event_type: str, payload: dict) -> list[Exception]:
        errors: list[Exception] = []
        for handler in list(self._handlers[event_type]):  # copy: handlers may unsubscribe while running
            try:
                handler(payload)
            except Exception as error:
                self._logger.exception("handler %r failed for %s", getattr(handler, "__name__", handler), event_type)
                errors.append(error)
        return errors


# ---------- Command ----------


class Command(Protocol):
    def execute(self) -> None: ...
    def undo(self) -> None: ...


class ChangeStatus:
    def __init__(self, board: Board, application_id: int, new_status: str):
        self.board, self.application_id, self.new_status = board, application_id, new_status
        self._previous: str | None = None

    def execute(self) -> None:
        self._previous = self.board.statuses.get(self.application_id)
        self.board.statuses[self.application_id] = self.new_status

    def undo(self) -> None:
        if self._previous is None:
            self.board.statuses.pop(self.application_id, None)
        else:
            self.board.statuses[self.application_id] = self._previous


class AddNote:
    def __init__(self, board: Board, application_id: int, text: str):
        self.board, self.application_id, self.text = board, application_id, text

    def execute(self) -> None:
        self.board.notes.setdefault(self.application_id, []).append(self.text)

    def undo(self) -> None:
        notes = self.board.notes[self.application_id]
        del notes[len(notes) - 1 - notes[::-1].index(self.text)]  # remove the last matching note


class History:
    def __init__(self) -> None:
        self._done: list[Command] = []
        self._undone: list[Command] = []

    def run(self, command: Command) -> None:
        command.execute()
        self._done.append(command)
        self._undone.clear()

    def undo(self) -> bool:
        if not self._done:
            return False
        command = self._done.pop()
        command.undo()
        self._undone.append(command)
        return True

    def redo(self) -> bool:
        if not self._undone:
            return False
        command = self._undone.pop()
        command.execute()
        self._done.append(command)
        return True
