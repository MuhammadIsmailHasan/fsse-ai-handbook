"""CareerPilot AI service — Phase 3.

The acceptance tests call:

    create_app({"jwt_secret": "..."})  ->  a FastAPI app

Values passed in the dict must override anything loaded from the environment.
They also import these names, so create the modules:

    careerpilot_ai/matching.py   extract_skills(text) -> set[str]
                                 compare(cv_text, job_text) -> dict
                                 class NoSkillsFound(ValueError)
    careerpilot_ai/deps.py       get_feedback_client()  → object with .stream(prompt) -> iterable of str
                                 get_audit_log()        → object with .record(event: dict) -> None
"""

from fastapi import FastAPI


def create_app(overrides: dict | None = None) -> FastAPI:
    raise NotImplementedError("Build the app factory — start with checkpoint C1 in README.md")
