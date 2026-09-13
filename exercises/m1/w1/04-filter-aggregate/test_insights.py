"""Automatic checks. Don't edit — make them pass by editing insights.py."""

import copy

from insights import attach_company, city_summary, group_by_city, remote_titles, unique_emails

JOBS = [
    {"title": "Backend Dev", "city": "Jakarta", "salary": 12_000_000, "remote": True, "company_id": 1},
    {"title": "QA Engineer", "city": "Bandung", "salary": 7_000_000, "remote": False, "company_id": 2},
    {"title": "Data Analyst", "city": "Jakarta", "salary": 9_000_000, "remote": False, "company_id": 9},
    {"title": "Frontend Dev", "city": "Jakarta", "salary": 10_000_001, "remote": True, "company_id": 2},
    {"title": "Support", "city": "Bandung", "salary": 5_000_000, "remote": True, "company_id": 1},
]
COMPANIES = [{"id": 1, "name": "Nusantara Tech"}, {"id": 2, "name": "Kopi Data"}]


def test_remote_titles():
    assert remote_titles(JOBS, 10_000_000) == ["Backend Dev", "Frontend Dev"]
    assert remote_titles(JOBS, 0) == ["Backend Dev", "Frontend Dev", "Support"]
    assert remote_titles([], 0) == []


def test_group_by_city():
    groups = group_by_city(JOBS)
    assert set(groups) == {"Jakarta", "Bandung"}
    assert [job["title"] for job in groups["Bandung"]] == ["QA Engineer", "Support"]


def test_city_summary():
    assert city_summary(JOBS) == {
        "Jakarta": {"count": 3, "average_salary": 10_333_333, "remote_share": 66},
        "Bandung": {"count": 2, "average_salary": 6_000_000, "remote_share": 50},
    }
    assert city_summary([]) == {}


def test_attach_company_left_join_without_mutation():
    before = copy.deepcopy(JOBS)
    joined = attach_company(JOBS, COMPANIES)
    assert [job["company"] for job in joined] == ["Nusantara Tech", "Kopi Data", None, "Kopi Data", "Nusantara Tech"]
    assert joined[0]["title"] == "Backend Dev"
    assert JOBS == before, "attach_company must not modify the input jobs"


def test_unique_emails():
    emails = ["Ana@Mail.com", "budi@mail.com", "ana@mail.com ", "BUDI@mail.com", "citra@mail.com"]
    assert unique_emails(emails) == ["Ana@Mail.com", "budi@mail.com", "citra@mail.com"]
