"""Provided: 60 deterministic fictional jobs."""

from datetime import date, timedelta

CITIES = ["Jakarta", "Bandung", "Surabaya", None]
TITLES = ["Backend Engineer", "Data Analyst", "Frontend Developer", "QA Engineer", "AI Engineer"]
COMPANIES = ["Nusantara Tech", "Kopi Data", "Lintas AI", "Garuda Pay", "Batik Soft", "Awan Cloud"]


def seed_jobs() -> list[dict]:
    jobs = []
    for i in range(1, 61):
        jobs.append(
            {
                "title": f"{TITLES[i % 5]} {i:02d}",
                "company": COMPANIES[i % 6],
                "city": CITIES[i % 4],
                "remote": i % 3 == 0,
                "salary_max": None if i % 7 == 0 else 8_000_000 + (i * 137_000) % 15_000_000,
                "posted_on": date(2026, 9, 13) - timedelta(days=i % 25),
            }
        )
    return jobs
