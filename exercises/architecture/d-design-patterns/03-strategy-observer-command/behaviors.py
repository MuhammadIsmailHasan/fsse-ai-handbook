"""Strategy, Observer and Command. See README.md."""

import logging
from dataclasses import dataclass, field
from datetime import date


@dataclass
class Board:
    """Provided: the receiver that commands act on."""

    statuses: dict[int, str] = field(default_factory=dict)
    notes: dict[int, list[str]] = field(default_factory=dict)


# TODO: BySalary, ByRecency, BySkillMatch, rank_jobs
# TODO: EventBus
# TODO: ChangeStatus, AddNote, History
