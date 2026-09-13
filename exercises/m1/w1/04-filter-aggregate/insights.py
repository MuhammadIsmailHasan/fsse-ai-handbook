"""M1 · W1 · 04 — Filter, group, join."""

Job = dict[str, object]
Company = dict[str, object]


def remote_titles(jobs: list[Job], min_salary: int) -> list[str]:
    # YOUR CODE HERE
    return []


def group_by_city(jobs: list[Job]) -> dict[str, list[Job]]:
    # YOUR CODE HERE
    return {}


def city_summary(jobs: list[Job]) -> dict[str, dict[str, int]]:
    """{city: {"count": n, "average_salary": int, "remote_share": percent}}"""
    # YOUR CODE HERE
    return {}


def attach_company(jobs: list[Job], companies: list[Company]) -> list[Job]:
    """New job dicts with a "company" name (or None). Don't modify inputs."""
    # YOUR CODE HERE
    return jobs


def unique_emails(emails: list[str]) -> list[str]:
    # YOUR CODE HERE
    return emails
