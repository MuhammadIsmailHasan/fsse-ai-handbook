"""Reference solution: pure rules, injected side effects, one I/O function."""

import json
from datetime import date
from pathlib import Path
from typing import Protocol


class Notifier(Protocol):
    def send(self, recipient: str, message: str) -> None: ...


def days_since_applied(application: dict, today: date) -> int:
    return (today - application["applied_on"]).days


def needs_follow_up(application: dict, today: date, after_days: int = 14) -> bool:
    return application["status"] == "applied" and days_since_applied(application, today) > after_days


def build_message(application: dict, today: date) -> str:
    days = days_since_applied(application, today)
    return f"Follow up with {application['company']} about {application['role']} — applied {days} days ago."


def send_follow_up_reminders(applications: list[dict], today: date, notifier: Notifier) -> int:
    sent = 0
    for application in applications:
        if needs_follow_up(application, today):
            notifier.send(application["email"], build_message(application, today))
            sent += 1
    return sent


def load_applications(path: str | Path) -> list[dict]:
    raw = json.loads(Path(path).read_text())
    return [{**item, "applied_on": date.fromisoformat(item["applied_on"])} for item in raw]


class PrintNotifier:
    """A real (if simple) notifier for running from the terminal."""

    def send(self, recipient: str, message: str) -> None:
        print(f"To {recipient}: {message}")


if __name__ == "__main__":
    count = send_follow_up_reminders(load_applications("applications.json"), date.today(), PrintNotifier())
    print(f"{count} reminder(s) sent")
