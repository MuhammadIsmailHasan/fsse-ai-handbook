"""M2 · W4 · 02 — Implement these with SQLAlchemy 2.0 style queries."""

from sqlalchemy import func, select  # noqa: F401
from sqlalchemy.exc import IntegrityError  # noqa: F401

from models import Application, Company, db  # noqa: F401


class DuplicateApplication(Exception):
    pass


def get_for_user(application_id: int, user_id: int) -> Application | None:
    # YOUR CODE HERE
    return None


def list_applications(
    user_id: int, statuses: list[str] | None = None, page: int = 1, per_page: int = 20
) -> tuple[list[Application], int]:
    # YOUR CODE HERE
    return [], 0


def count_by_status(user_id: int) -> dict[str, int]:
    # YOUR CODE HERE
    return {}


def create_application_with_company(user_id: int, company_name: str, role_title: str) -> Application:
    # YOUR CODE HERE
    raise NotImplementedError
