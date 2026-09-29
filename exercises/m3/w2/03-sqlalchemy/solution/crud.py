"""Module 3 · W2 — SQLAlchemy 2.0 CRUD (solution)."""

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
    user = User(name=name, email=email)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)


def list_users_by_domain(session: Session, domain: str) -> list[User]:
    stmt = select(User).where(User.email.endswith(domain)).order_by(User.id)
    return list(session.scalars(stmt).all())
