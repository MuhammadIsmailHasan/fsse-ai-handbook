"""Reference refactor. Same behavior, readable structure."""

from datetime import date

FOLLOW_UP_AFTER_DAYS = 14
WAITING_STATUS = "applied"
OFFER_STATUS = "offer"


def status_report(applications: list[dict], today: date) -> str:
    counts = count_by_status(applications)
    lines = [f"Application report for {today.isoformat()}"]
    lines += [f"- {status}: {count}" for status, count in sorted(counts.items())]
    lines += follow_up_section(needs_follow_up(applications, today), today)
    lines += ["", f"Offer rate: {offer_rate(counts)}%"]
    return "\n".join(lines)


def count_by_status(applications: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for application in applications:
        counts[application["status"]] = counts.get(application["status"], 0) + 1
    return counts


def days_waiting(application: dict, today: date) -> int:
    return (today - application["applied_on"]).days


def needs_follow_up(applications: list[dict], today: date) -> list[dict]:
    waiting = [
        application
        for application in applications
        if application["status"] == WAITING_STATUS and days_waiting(application, today) > FOLLOW_UP_AFTER_DAYS
    ]
    return sorted(waiting, key=lambda application: application["applied_on"])


def follow_up_section(applications: list[dict], today: date) -> list[str]:
    if not applications:
        return []
    lines = ["", f"Follow up (applied > {FOLLOW_UP_AFTER_DAYS} days ago, no response):"]
    for application in applications:
        days = days_waiting(application, today)
        lines.append(f"- {application['company']} · {application['role']} ({days} days)")
    return lines


def offer_rate(counts: dict[str, int]) -> int:
    total = sum(counts.values())
    return counts.get(OFFER_STATUS, 0) * 100 // total if total else 0
