"""Matching logic — pure Python, no HTTP. Checkpoint C3.

extract_skills(text)  -> set of skills from careerpilot_ai.skills.SKILLS found in `text`
compare(cv, job)      -> {"score": int, "level": str, "matched_skills": [...], "missing_skills": [...]}
                         score = round(100 * matched / skills in the job)
                         level = "strong" (>= 75), "partial" (>= 40), else "weak"
                         lists are sorted; raise NoSkillsFound if the job mentions no known skill
"""

from careerpilot_ai.skills import SKILLS  # noqa: F401


class NoSkillsFound(ValueError):
    """The job description mentions none of the known skills."""


def extract_skills(text: str) -> set[str]:
    raise NotImplementedError("Checkpoint C3")


def compare(cv_text: str, job_text: str) -> dict:
    raise NotImplementedError("Checkpoint C3")
