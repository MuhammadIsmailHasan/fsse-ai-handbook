"""M2 · W4 · 05 — The dashboard query."""

from datetime import datetime

from sqlalchemy import select  # noqa: F401
from sqlalchemy.orm import joinedload, selectinload  # noqa: F401

from models import Application, db  # noqa: F401


def dashboard(user_id: int, now: datetime) -> list[dict]:
    # YOUR CODE HERE
    return []
