"""API tests on PostgreSQL. Expectations are computed from seed.py in Python. Don't edit this file."""

from datetime import date

import pytest

from app import create_app
from models import Job, db
from seed import seed_jobs


@pytest.fixture
def client(pg_url):
    app = create_app(pg_url)
    with app.app_context():
        db.create_all()
        db.session.add_all([Job(**job) for job in seed_jobs()])
        db.session.commit()
        yield app.test_client()
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def all_jobs(client):
    return client.get("/api/v1/jobs?per_page=100").get_json()["data"]


def test_default_listing_and_meta(client):
    body = client.get("/api/v1/jobs").get_json()
    assert body["meta"] == {"page": 1, "per_page": 20, "total": 60, "total_pages": 3}
    assert body["links"] == {"self": "/api/v1/jobs?page=1&per_page=20", "next": "/api/v1/jobs?page=2&per_page=20", "prev": None}
    posted = [(j["posted_on"], j["id"]) for j in body["data"]]
    assert posted == sorted(posted, reverse=True)
    assert set(body["data"][0]) == {"id", "title", "company", "city", "remote", "salary_max", "posted_on"}


def test_pages_cover_everything_exactly_once(client):
    seen = []
    for page in (1, 2, 3):
        seen += [j["id"] for j in client.get(f"/api/v1/jobs?page={page}&per_page=20").get_json()["data"]]
    assert sorted(seen) == list(range(1, 61))
    last = client.get("/api/v1/jobs?page=3&per_page=20").get_json()
    assert last["links"]["next"] is None and last["links"]["prev"] == "/api/v1/jobs?page=2&per_page=20"


def test_filters(client):
    expected = [j for j in seed_jobs() if (j["city"] or "").lower() == "jakarta" and j["remote"] and (j["salary_max"] or -1) >= 10_000_000]
    body = client.get("/api/v1/jobs?city=JAKARTA&remote=true&min_salary=10000000&per_page=100").get_json()
    assert body["meta"]["total"] == len(expected) > 0
    assert all(j["city"] == "Jakarta" and j["remote"] and j["salary_max"] >= 10_000_000 for j in body["data"])
    assert body["links"]["self"] == "/api/v1/jobs?city=JAKARTA&remote=true&min_salary=10000000&page=1&per_page=100"


def test_multi_sort_with_nulls_last(client):
    data = client.get("/api/v1/jobs?sort=-salary_max,title&per_page=100").get_json()["data"]
    with_salary = [j for j in data if j["salary_max"] is not None]
    assert data[len(with_salary):] == [j for j in data if j["salary_max"] is None], "NULL salaries must come last"
    keys = [(-j["salary_max"], j["title"]) for j in with_salary]
    assert keys == sorted(keys)

    ascending = client.get("/api/v1/jobs?sort=salary_max&per_page=100").get_json()["data"]
    assert ascending[-1]["salary_max"] is None


@pytest.mark.parametrize(
    ("query", "field"),
    [
        ("remote=maybe", "remote"),
        ("min_salary=-5", "min_salary"),
        ("min_salary=abc", "min_salary"),
        ("sort=password", "sort"),
        ("sort=posted_on;DROP TABLE jobs", "sort"),
        ("page=0", "page"),
        ("per_page=101", "per_page"),
        ("reomte=true", "reomte"),
    ],
)
def test_invalid_query(client, query, field):
    response = client.get(f"/api/v1/jobs?{query}")
    assert response.status_code == 422
    error = response.get_json()["error"]
    assert error["code"] == "invalid_query" and field in error["fields"]


def test_detail_and_404(client):
    assert client.get("/api/v1/jobs/5").get_json()["data"]["id"] == 5
    missing = client.get("/api/v1/jobs/999")
    assert missing.status_code == 404 and missing.get_json()["error"]["code"] == "job_not_found"


def test_keyset_feed_walks_everything_in_order(client):
    ids, cursor, requests = [], None, 0
    while True:
        url = "/api/v1/jobs/feed?limit=25" + (f"&cursor={cursor}" if cursor else "")
        body = client.get(url).get_json()
        ids += [(j["posted_on"], j["id"]) for j in body["data"]]
        cursor = body["meta"]["next_cursor"]
        requests += 1
        if not cursor:
            break
    assert requests == 3
    assert ids == sorted(ids, reverse=True) and len(ids) == 60


def test_keyset_is_stable_when_new_rows_arrive(client):
    first = client.get("/api/v1/jobs/feed?limit=10").get_json()
    with client.application.app_context():
        db.session.add(Job(title="Brand new", company="X", city=None, remote=False, salary_max=None, posted_on=date(2026, 9, 14)))
        db.session.commit()
    second = client.get(f"/api/v1/jobs/feed?limit=10&cursor={first['meta']['next_cursor']}").get_json()
    first_ids = {j["id"] for j in first["data"]}
    assert not first_ids & {j["id"] for j in second["data"]}, "keyset pages must not repeat rows"


def test_invalid_cursor(client):
    assert client.get("/api/v1/jobs/feed?cursor=not-a-cursor").status_code == 422
    assert client.get("/api/v1/jobs/feed?limit=0").status_code == 422
