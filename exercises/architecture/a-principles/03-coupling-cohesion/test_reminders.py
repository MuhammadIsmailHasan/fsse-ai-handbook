import json
from datetime import date

import reminders

TODAY = date(2026, 9, 13)


def application(status="applied", applied_on=date(2026, 8, 20), company="Kopi Data", role="Data Analyst"):
    return {"email": "ana@mail.com", "company": company, "role": role, "status": status, "applied_on": applied_on}


class FakeNotifier:
    def __init__(self):
        self.sent = []

    def send(self, recipient, message):
        self.sent.append((recipient, message))


def test_needs_follow_up_rule():
    assert reminders.needs_follow_up(application(applied_on=date(2026, 8, 30)), TODAY) is False  # 14 days: not yet
    assert reminders.needs_follow_up(application(applied_on=date(2026, 8, 29)), TODAY) is True  # 15 days
    assert reminders.needs_follow_up(application(applied_on=date(2026, 8, 20)), TODAY) is True  # 24 days
    assert reminders.needs_follow_up(application(status="interview"), TODAY) is False
    assert reminders.needs_follow_up(application(applied_on=date(2026, 9, 1)), TODAY, after_days=7) is True


def test_build_message():
    assert reminders.build_message(application(), TODAY) == (
        "Follow up with Kopi Data about Data Analyst — applied 24 days ago."
    )


def test_send_uses_injected_notifier():
    notifier = FakeNotifier()
    apps = [application(), application(status="offer"), application(company="Awan Cloud", applied_on=date(2026, 9, 10))]
    assert reminders.send_follow_up_reminders(apps, TODAY, notifier) == 1
    assert notifier.sent == [("ana@mail.com", "Follow up with Kopi Data about Data Analyst — applied 24 days ago.")]


def test_load_applications_converts_dates(tmp_path):
    path = tmp_path / "applications.json"
    path.write_text(json.dumps([{**application(), "applied_on": "2026-08-20"}]))
    loaded = reminders.load_applications(path)
    assert loaded[0]["applied_on"] == date(2026, 8, 20)


def test_rule_and_message_do_not_read_the_clock():
    import inspect

    for func in (reminders.needs_follow_up, reminders.build_message, reminders.send_follow_up_reminders):
        assert "today()" not in inspect.getsource(func), f"{func.__name__} should receive `today`, not read the clock"
