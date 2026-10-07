"""Shared constants and fakes for the Phase 3 acceptance tests. Don't edit this file."""

import time

import jwt

TEST_SECRET = "acceptance-tests-only-" + "x" * 32

CV = "Backend developer with 3 years of Python, Flask, PostgreSQL and Docker. I use Git and write tests with pytest."
JOB = "We need a Python and FastAPI engineer. You know SQL, PostgreSQL, Docker and AWS, and you use Git every day."


def make_token(sub="user-1", secret=TEST_SECRET, expires_in=3600, **claims) -> str:
    payload = {"sub": sub, "exp": int(time.time()) + expires_in, **claims}
    if sub is None:
        del payload["sub"]
    return jwt.encode(payload, secret, algorithm="HS256")


class FakeFeedbackClient:
    """Stands in for the LLM. Records prompts; yields the tokens you give it."""

    def __init__(self, tokens=("Good ", "start. ", "Add AWS."), fail_after=None):
        self.tokens = list(tokens)
        self.fail_after = fail_after
        self.prompts: list[str] = []

    def stream(self, prompt: str):
        self.prompts.append(prompt)
        for index, token in enumerate(self.tokens):
            if self.fail_after is not None and index >= self.fail_after:
                raise RuntimeError("model went away")
            yield token


class FakeAuditLog:
    def __init__(self):
        self.events: list[dict] = []

    def record(self, event: dict) -> None:
        self.events.append(event)
