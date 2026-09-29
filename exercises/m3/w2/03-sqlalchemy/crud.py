"""Module 3 · W2 — SQLAlchemy 2.0 CRUD (SQLite, no server needed).

Define a User model and three functions using the 2.0 API:
- create_user(session, name, email) -> User      (add + commit + refresh)
- get_user(session, user_id) -> User | None       (session.get)
- list_users_by_domain(session, domain) -> list   (select().where(...))
"""

from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)


def create_user(session: Session, name: str, email: str) -> User:
    # YOUR CODE HERE
    ...


def get_user(session: Session, user_id: int) -> User | None:
    # YOUR CODE HERE
    ...


def list_users_by_domain(session: Session, domain: str) -> list[User]:
    """Return users whose email ends with `domain` (e.g. '@example.com'), ordered by id."""
    # YOUR CODE HERE
    ...
