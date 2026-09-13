"""Reference solution: each piece of knowledge lives in one helper."""

from datetime import date

SIGNATURE = "— CareerPilot 🚀"


def greeting(name: str) -> str:
    return f"Hi {name.strip().title()},"


def format_date(day: date) -> str:
    return day.strftime("%a, %d %b %Y")


def compose(name: str, body: str) -> str:
    return f"{greeting(name)}\n\n{body}\n\n{SIGNATURE}"


def follow_up_reminder(name: str, company: str, applied_on: date) -> str:
    body = f"You applied to {company} on {format_date(applied_on)}. It might be a good time to follow up."
    return compose(name, body)


def interview_reminder(name: str, company: str, interview_on: date) -> str:
    body = f"Your interview with {company} is on {format_date(interview_on)}. Review your notes and prepare 3 questions."
    return compose(name, body)


def deadline_reminder(name: str, role: str, deadline: date) -> str:
    body = f"Applications for {role} close on {format_date(deadline)}. Don't miss it!"
    return compose(name, body)
