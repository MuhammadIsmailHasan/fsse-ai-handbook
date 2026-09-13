"""Reference solution."""

from typing import Literal, Protocol, TypedDict

type Status = Literal["applied", "interview", "offer", "rejected"]


class ApplicationData(TypedDict):
    id: int
    company: str
    status: Status
    salary: int | None


class ApplicationRepository(Protocol):
    def get(self, application_id: int) -> ApplicationData | None: ...

    def save(self, application: ApplicationData) -> None: ...


def first_or_none[T](items: list[T]) -> T | None:
    return items[0] if items else None


def format_rupiah(amount: int) -> str:
    return "Rp " + f"{amount:,}".replace(",", ".")


def _require(repo: ApplicationRepository, application_id: int) -> ApplicationData:
    application = repo.get(application_id)
    if application is None:  # bug 1 & 2: repo.get can return None
        raise LookupError(f"Application {application_id} not found")
    return application


def salary_label(repo: ApplicationRepository, application_id: int) -> str:
    salary = _require(repo, application_id)["salary"]
    if salary is None:  # salary can be None too
        return "Not disclosed"
    return format_rupiah(salary)


def advance(repo: ApplicationRepository, application_id: int, status: Status) -> ApplicationData:
    application = _require(repo, application_id)
    updated: ApplicationData = {**application, "status": status}
    repo.save(updated)
    return updated
