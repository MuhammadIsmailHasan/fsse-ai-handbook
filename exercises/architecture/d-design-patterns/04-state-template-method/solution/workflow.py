"""State and Template Method — reference solution."""

from abc import ABC, abstractmethod


class InvalidAction(Exception):
    pass


# ---------- State ----------


class State:
    """Default: every action is invalid. Each concrete state overrides only what it allows."""

    name = "?"

    def _invalid(self, workflow: "ApplicationWorkflow", action: str) -> None:
        raise InvalidAction(f"cannot {action} when {self.name}")

    def apply(self, workflow):
        self._invalid(workflow, "apply")

    def schedule_interview(self, workflow):
        self._invalid(workflow, "schedule_interview")

    def make_offer(self, workflow, amount):
        self._invalid(workflow, "make_offer")

    def accept(self, workflow):
        self._invalid(workflow, "accept")

    def reject(self, workflow):
        self._invalid(workflow, "reject")

    def withdraw(self, workflow):
        self._invalid(workflow, "withdraw")


class Open(State):
    """Shared by every non-final state after saved: can be withdrawn or rejected."""

    def reject(self, workflow):
        workflow._move_to(Rejected())

    def withdraw(self, workflow):
        workflow._move_to(Withdrawn())


class Saved(State):
    name = "saved"

    def apply(self, workflow):
        workflow._move_to(Applied())

    def withdraw(self, workflow):
        workflow._move_to(Withdrawn())


class Applied(Open):
    name = "applied"

    def schedule_interview(self, workflow):
        workflow.interview_rounds += 1
        workflow._move_to(Interviewing())


class Interviewing(Open):
    name = "interviewing"

    def schedule_interview(self, workflow):
        workflow.interview_rounds += 1
        workflow._move_to(Interviewing())

    def make_offer(self, workflow, amount):
        workflow.offer_amount = amount
        workflow._move_to(Offered())


class Offered(Open):
    name = "offered"

    def accept(self, workflow):
        workflow._move_to(Accepted())


class Accepted(State):
    name = "accepted"


class Rejected(State):
    name = "rejected"


class Withdrawn(State):
    name = "withdrawn"


class ApplicationWorkflow:
    def __init__(self) -> None:
        self._state: State = Saved()
        self.interview_rounds = 0
        self.offer_amount: int | None = None
        self.history = [self._state.name]

    @property
    def status(self) -> str:
        return self._state.name

    def _move_to(self, state: State) -> None:
        self._state = state
        self.history.append(state.name)

    def apply(self):
        self._state.apply(self)

    def schedule_interview(self):
        self._state.schedule_interview(self)

    def make_offer(self, amount: int):
        self._state.make_offer(self, amount)

    def accept(self):
        self._state.accept(self)

    def reject(self):
        self._state.reject(self)

    def withdraw(self):
        self._state.withdraw(self)


# ---------- Template Method ----------


class ApplicationReport(ABC):
    title = "Applications"

    def generate(self, applications: list[dict]) -> str:
        """The template: fixed order of steps; subclasses fill in the steps."""
        lines = [self.header()]
        lines.extend(self.row(app) for app in applications)
        lines.append(self.footer(applications))
        return "\n".join(lines)

    @abstractmethod
    def header(self) -> str: ...

    @abstractmethod
    def row(self, app: dict) -> str: ...

    def footer(self, applications: list[dict]) -> str:
        return f"Total: {len(applications)}"


class PlainTextReport(ApplicationReport):
    def header(self) -> str:
        return f"== {self.title} =="

    def row(self, app: dict) -> str:
        return f"- {app['company']}: {app['role']} ({app['status']})"


class MarkdownReport(ApplicationReport):
    title = "Job Hunt"

    def header(self) -> str:
        return f"# {self.title}\n\n| Company | Role | Status |\n|---|---|---|"

    def row(self, app: dict) -> str:
        return f"| {app['company']} | {app['role']} | {app['status']} |"

    def footer(self, applications: list[dict]) -> str:
        return f"\n_Total: {len(applications)} applications_"
