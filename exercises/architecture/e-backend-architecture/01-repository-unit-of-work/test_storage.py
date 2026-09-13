"""Contract tests: the SAME tests run against the fake and the real unit of work. Don't edit."""

import pytest
from sqlalchemy import create_engine, func, select

import storage as st


@pytest.fixture(params=["memory", "sql"])
def make_uow(request):
    if request.param == "memory":
        database = st.InMemoryDatabase()
        yield lambda: st.InMemoryUnitOfWork(database)
        return
    pg_url = request.getfixturevalue("pg_url")
    engine = create_engine(pg_url)
    st.metadata.create_all(engine)
    try:
        yield lambda: st.SqlUnitOfWork(engine)
    finally:
        engine.dispose()


def new_app(user_id=1, company="Kopi Data", role="Backend Engineer"):
    return st.Application(user_id=user_id, company=company, role=role)


def test_add_commit_and_read_back(make_uow):
    with make_uow() as uow:
        first = new_app()
        first_id = uow.applications.add(first)
        second_id = uow.applications.add(new_app(company="Awan Cloud"))
        assert first.id == first_id and second_id > first_id
        uow.commit()
    with make_uow() as uow:
        loaded = uow.applications.get(first_id)
        assert loaded == st.Application(1, "Kopi Data", "Backend Engineer", "saved", first_id)
        assert uow.applications.get(999_999) is None


def test_without_commit_nothing_is_saved(make_uow):
    with make_uow() as uow:
        uow.applications.add(new_app())
    with make_uow() as uow:
        assert uow.applications.list_for_user(1) == []


def test_exception_rolls_back_and_propagates(make_uow):
    with make_uow() as uow:
        kept_id = uow.applications.add(new_app(company="Kept"))
        uow.commit()
    with pytest.raises(RuntimeError):
        with make_uow() as uow:
            uow.applications.add(new_app(company="Lost"))
            app = uow.applications.get(kept_id)
            app.status = "applied"
            uow.applications.update(app)
            raise RuntimeError("something failed halfway")
    with make_uow() as uow:
        assert [a.company for a in uow.applications.list_for_user(1)] == ["Kept"]
        assert uow.applications.get(kept_id).status == "saved"


def test_commit_then_more_work_in_same_block(make_uow):
    with make_uow() as uow:
        first_id = uow.applications.add(new_app(company="First"))
        uow.commit()
        uow.applications.add(new_app(company="Second, not committed"))
    with make_uow() as uow:
        assert [a.id for a in uow.applications.list_for_user(1)] == [first_id]


def test_list_update_remove(make_uow):
    with make_uow() as uow:
        ids = [uow.applications.add(new_app(user_id=u, company=c)) for u, c in [(1, "A"), (2, "B"), (1, "C")]]
        uow.commit()
    with make_uow() as uow:
        assert [a.company for a in uow.applications.list_for_user(1)] == ["A", "C"]
        app = uow.applications.get(ids[0])
        app.status = "interview"
        app.role = "Senior Backend Engineer"
        assert uow.applications.get(ids[0]).status == "saved", "get returns an independent object"
        uow.applications.update(app)
        uow.applications.remove(ids[1])
        uow.commit()
    with make_uow() as uow:
        assert uow.applications.get(ids[0]).role == "Senior Backend Engineer"
        assert uow.applications.get(ids[1]) is None
        with pytest.raises(LookupError):
            uow.applications.remove(ids[1])
        with pytest.raises(LookupError):
            uow.applications.update(st.Application(9, "X", "Y", id=987_654))


def test_sql_unit_of_work_closes_connections(pg_url):
    engine = create_engine(pg_url, pool_size=1, max_overflow=0, pool_timeout=2)
    st.metadata.create_all(engine)
    try:
        for _ in range(5):  # would time out if connections leaked from the pool of 1
            with st.SqlUnitOfWork(engine) as uow:
                uow.applications.add(new_app())
                uow.commit()
        with engine.connect() as connection:
            assert connection.execute(select(func.count()).select_from(st.applications_table)).scalar_one() == 5
    finally:
        engine.dispose()
