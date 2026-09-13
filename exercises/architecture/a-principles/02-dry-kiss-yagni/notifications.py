"""Architecture · A — Three copy-pasted message builders. Remove the duplicated knowledge."""

from datetime import date


def follow_up_reminder(name: str, company: str, applied_on: date) -> str:
    greeting = f"Hi {name.strip().title()},"
    when = applied_on.strftime("%a, %d %b %Y")
    body = f"You applied to {company} on {when}. It might be a good time to follow up."
    signature = "— CareerPilot 🚀"
    return f"{greeting}\n\n{body}\n\n{signature}"


def interview_reminder(name: str, company: str, interview_on: date) -> str:
    greeting = f"Hi {name.strip().title()},"
    when = interview_on.strftime("%a, %d %b %Y")
    body = f"Your interview with {company} is on {when}. Review your notes and prepare 3 questions."
    signature = "— CareerPilot 🚀"
    return f"{greeting}\n\n{body}\n\n{signature}"


def deadline_reminder(name: str, role: str, deadline: date) -> str:
    greeting = f"Hi {name.title()},"
    when = deadline.strftime("%d/%m/%Y")
    body = f"Applications for {role} close on {when}. Don't miss it!"
    signature = "— CareerPilot 🚀"
    return f"{greeting}\n\n{body}\n\n{signature}"
