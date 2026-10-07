"""Dependencies the tests replace with fakes (dependency_overrides). Checkpoints C4 and C5.

get_feedback_client() -> an object with  .stream(prompt: str) -> iterable of str tokens
                         (default: a template client that works offline, no API key)
get_audit_log()       -> an object with  .record(event: dict) -> None
"""


def get_feedback_client():
    raise NotImplementedError("Checkpoint C5")


def get_audit_log():
    raise NotImplementedError("Checkpoint C4")
