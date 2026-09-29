import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from crud import Base, create_user, get_user, list_users_by_domain


@pytest.fixture
def session():
    # In-memory SQLite — no external database needed.
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


def test_create_and_get(session):
    user = create_user(session, "Ismail", "ismail@example.com")
    assert user.id is not None  # id assigned after commit/refresh
    again = get_user(session, user.id)
    assert again is not None
    assert again.name == "Ismail"
    assert again.email == "ismail@example.com"


def test_get_missing_returns_none(session):
    assert get_user(session, 999) is None


def test_list_by_domain(session):
    create_user(session, "A", "a@example.com")
    create_user(session, "B", "b@other.com")
    create_user(session, "C", "c@example.com")
    results = list_users_by_domain(session, "@example.com")
    assert [u.name for u in results] == ["A", "C"]  # ordered by id, filtered by domain
