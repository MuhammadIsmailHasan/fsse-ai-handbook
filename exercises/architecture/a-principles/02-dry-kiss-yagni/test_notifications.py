import ast
from datetime import date
from pathlib import Path

from notifications import deadline_reminder, follow_up_reminder, interview_reminder


def test_follow_up_reminder():
    assert follow_up_reminder(" ana ", "Kopi Data", date(2026, 9, 14)) == (
        "Hi Ana,\n\nYou applied to Kopi Data on Mon, 14 Sep 2026. It might be a good time to follow up."
        "\n\n— CareerPilot 🚀"
    )


def test_interview_reminder():
    message = interview_reminder("budi", "Awan Cloud", date(2026, 9, 18))
    assert message.startswith("Hi Budi,\n\nYour interview with Awan Cloud is on Fri, 18 Sep 2026.")
    assert message.endswith("\n\n— CareerPilot 🚀")


def test_deadline_reminder_is_consistent_with_the_others():
    assert deadline_reminder("  citra ", "ML Engineer", date(2026, 10, 1)) == (
        "Hi Citra,\n\nApplications for ML Engineer close on Thu, 01 Oct 2026. Don't miss it!\n\n— CareerPilot 🚀"
    )


def test_shared_knowledge_lives_in_one_place():
    source = Path(__file__).with_name("notifications.py").read_text()
    assert source.count("strftime") == 1, "Date formatting should be defined once"
    assert source.count("CareerPilot 🚀") == 1, "The signature should be defined once"
    assert source.count("Hi {") == 1, "The greeting should be defined once"
    names = {n.name for n in ast.parse(source).body if isinstance(n, ast.FunctionDef)}
    assert {"follow_up_reminder", "interview_reminder", "deadline_reminder"} <= names
