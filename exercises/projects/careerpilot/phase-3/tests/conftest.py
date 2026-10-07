"""Fixtures for the CareerPilot Phase 3 acceptance tests. Don't edit this file.

Every test gets a fresh app built with create_app({"jwt_secret": ...}), a TestClient,
and helpers to mint tokens and to swap the AI client and the audit log for fakes.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

AI_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AI_ROOT))  # so `import careerpilot_ai` works without installing the package

from p3_support import TEST_SECRET, FakeAuditLog, FakeFeedbackClient, make_token  # noqa: E402


@pytest.fixture
def app():
    from careerpilot_ai import create_app

    return create_app({"jwt_secret": TEST_SECRET})


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def auth():
    return {"Authorization": f"Bearer {make_token()}"}


@pytest.fixture
def fake_feedback(app):
    from careerpilot_ai.deps import get_feedback_client

    fake = FakeFeedbackClient()
    app.dependency_overrides[get_feedback_client] = lambda: fake
    yield fake
    app.dependency_overrides.pop(get_feedback_client, None)


@pytest.fixture
def audit(app):
    from careerpilot_ai.deps import get_audit_log

    fake = FakeAuditLog()
    app.dependency_overrides[get_audit_log] = lambda: fake
    yield fake
    app.dependency_overrides.pop(get_audit_log, None)
