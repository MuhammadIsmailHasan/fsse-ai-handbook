"""Architecture · A — A tangled job: file I/O, clock, business rule and output all in one place."""

import json
from datetime import date


def run_reminders():
    with open("applications.json") as file:
        applications = json.load(file)
    for application in applications:
        applied_on = date.fromisoformat(application["applied_on"])
        days = (date.today() - applied_on).days
        if application["status"] == "applied" and days > 14:
            print(f"To {application['email']}: Follow up with {application['company']} about {application['role']} — applied {days} days ago.")


# TODO: replace run_reminders with the decoupled functions described in the README.
