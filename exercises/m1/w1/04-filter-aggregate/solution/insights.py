"""Reference solution — compare AFTER a real attempt."""

Job = dict[str, object]
Company = dict[str, object]


def remote_titles(jobs: list[Job], min_salary: int) -> list[str]:
    return [job["title"] for job in jobs if job["remote"] and job["salary"] >= min_salary]


def group_by_city(jobs: list[Job]) -> dict[str, list[Job]]:
    groups: dict[str, list[Job]] = {}
    for job in jobs:
        groups.setdefault(job["city"], []).append(job)
    return groups


def summarize(city_jobs: list[Job]) -> dict[str, int]:
    count = len(city_jobs)
    remote_count = sum(1 for job in city_jobs if job["remote"])
    return {
        "count": count,
        "average_salary": sum(job["salary"] for job in city_jobs) // count,
        "remote_share": remote_count * 100 // count,
    }


def city_summary(jobs: list[Job]) -> dict[str, dict[str, int]]:
    return {city: summarize(city_jobs) for city, city_jobs in group_by_city(jobs).items()}


def attach_company(jobs: list[Job], companies: list[Company]) -> list[Job]:
    company_by_id = {company["id"]: company for company in companies}
    joined = []
    for job in jobs:
        company = company_by_id.get(job["company_id"])
        joined.append({**job, "company": company["name"] if company else None})
    return joined


def unique_emails(emails: list[str]) -> list[str]:
    seen: set[str] = set()
    unique = []
    for email in emails:
        key = email.strip().lower()
        if key not in seen:
            seen.add(key)
            unique.append(email)
    return unique
