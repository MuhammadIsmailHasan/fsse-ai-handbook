"""Tests for pipeline.py. Don't edit this file."""

from datetime import date

import pytest

from pipeline import Application, InvalidTransition, ReminderService, SalaryRange


# ---- SalaryRange ---------------------------------------------------------------


def test_salary_range_validation_and_midpoint():
    salary = SalaryRange(9_000_000, 14_000_001)
    assert salary.midpoint == 11_500_000
    for bad in [(-1, 5), (10, 9)]:
        with pytest.raises(ValueError):
            SalaryRange(*bad)


def test_salary_range_value_semantics():
    assert SalaryRange(1, 2) == SalaryRange(1, 2)
    assert len({SalaryRange(1, 2), SalaryRange(1, 2)}) == 1
    assert repr(SalaryRange(9_000_000, 14_000_000)) == "SalaryRange(9000000, 14000000)"
    with pytest.raises(AttributeError):
        SalaryRange(1, 2).minimum = 5


# ---- Application ---------------------------------------------------------------


@pytest.fixture
def app():
    return Application("Kopi Data", "Data Analyst", date(2026, 9, 1))


def test_initial_state_and_repr(app):
    assert app.status == "applied" and app.is_active
    assert app.history == [("applied", date(2026, 9, 1))]
    assert repr(app) == "Application('Kopi Data', 'Data Analyst', status='applied')"


def test_status_is_read_only(app):
    with pytest.raises(AttributeError):
        app.status = "offer"


def test_valid_flow_records_history(app):
    app.move_to("interview", date(2026, 9, 5))
    app.move_to("interview", date(2026, 9, 10))
    app.move_to("offer", date(2026, 9, 15))
    app.move_to("accepted", date(2026, 9, 16))
    assert app.status == "accepted" and not app.is_active
    assert [status for status, _ in app.history] == ["applied", "interview", "interview", "offer", "accepted"]


@pytest.mark.parametrize("target", ["offer", "accepted", "hired", "applied"])
def test_invalid_transitions(app, target):
    with pytest.raises(InvalidTransition):
        app.move_to(target, date(2026, 9, 2))
    assert app.status == "applied"
    assert len(app.history) == 1


def test_history_cannot_be_mutated_from_outside(app):
    app.history.append(("offer", date(2026, 9, 9)))
    assert len(app.history) == 1


def test_sorting_by_applied_on():
    later = Application("B", "Dev", date(2026, 9, 10))
    earlier = Application("A", "Dev", date(2026, 8, 1))
    assert [a.company for a in sorted([later, earlier])] == ["A", "B"]


# ---- ReminderService ---------------------------------------------------------------


class FakeNotifier:
    def __init__(self):
        self.messages = []

    def send(self, message):
        self.messages.append(message)


def test_reminder_service_uses_last_change_and_active_only():
    waiting = Application("Kopi Data", "Data Analyst", date(2026, 8, 1))
    recent_interview = Application("Lintas AI", "AI Engineer", date(2026, 8, 1))
    recent_interview.move_to("interview", date(2026, 9, 10))
    rejected = Application("Garuda Pay", "QA", date(2026, 8, 1))
    rejected.move_to("rejected", date(2026, 8, 2))

    notifier = FakeNotifier()
    service = ReminderService(notifier)
    sent = service.send_follow_ups([waiting, recent_interview, rejected], today=date(2026, 9, 13))

    assert sent == 1
    assert notifier.messages == ["Follow up with Kopi Data (Data Analyst)"]


def test_reminder_boundary():
    application = Application("X", "Dev", date(2026, 9, 1))
    notifier = FakeNotifier()
    service = ReminderService(notifier)
    assert service.send_follow_ups([application], today=date(2026, 9, 15)) == 0   # exactly 14 days
    assert service.send_follow_ups([application], today=date(2026, 9, 16), after_days=14) == 1
