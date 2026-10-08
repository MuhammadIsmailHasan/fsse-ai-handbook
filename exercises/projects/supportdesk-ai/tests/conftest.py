"""Fixtures for the SupportDesk acceptance tests. Don't edit this file.

Every test gets a fresh app (create_app) whose four dependencies are replaced with fakes:
FakeLLM (scripted), HashEmbedder, FakeOrders and FakeTracer.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

KIT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT_ROOT))   # so `import supportdesk_api` works without installing the package

from p_support import (  # noqa: E402
    ARTICLES, TEST_SECRET, FakeLLM, FakeOrders, FakeTracer, HashEmbedder, bearer, make_token,
)


@pytest.fixture
def app():
    from supportdesk_api import create_app

    return create_app({"jwt_secret": TEST_SECRET})


@pytest.fixture
def llm(app):
    from supportdesk_api.deps import get_llm

    fake = FakeLLM()
    app.dependency_overrides[get_llm] = lambda: fake
    return fake


@pytest.fixture
def orders(app):
    from supportdesk_api.deps import get_orders_api

    fake = FakeOrders()
    app.dependency_overrides[get_orders_api] = lambda: fake
    return fake


@pytest.fixture
def tracer(app):
    from supportdesk_api.deps import get_tracer

    fake = FakeTracer()
    app.dependency_overrides[get_tracer] = lambda: fake
    return fake


@pytest.fixture
def embedder(app):
    from supportdesk_api.deps import get_embedder

    fake = HashEmbedder()
    app.dependency_overrides[get_embedder] = lambda: fake
    return fake


@pytest.fixture
def client(app, llm, orders, tracer, embedder):
    return TestClient(app)


@pytest.fixture
def customer():
    return bearer(make_token("user-1"))


@pytest.fixture
def customer2():
    return bearer(make_token("user-2"))


@pytest.fixture
def admin():
    return bearer(make_token("admin-1", role="admin"))


@pytest.fixture
def kb(client, admin):
    """The help center, with all four articles indexed."""
    for article in ARTICLES.values():
        response = client.post("/v1/articles", json=article, headers=admin)
        assert response.status_code == 201, response.text
    return client


@pytest.fixture
def build():
    """build(**overrides) -> (client, fakes): a separate app with different settings, same fakes."""
    from types import SimpleNamespace

    from supportdesk_api import create_app
    from supportdesk_api.deps import get_embedder, get_llm, get_orders_api, get_tracer

    def _build(**overrides):
        application = create_app({"jwt_secret": TEST_SECRET, **overrides})
        fakes = SimpleNamespace(llm=FakeLLM(), orders=FakeOrders(), tracer=FakeTracer(), embedder=HashEmbedder())
        application.dependency_overrides[get_llm] = lambda: fakes.llm
        application.dependency_overrides[get_orders_api] = lambda: fakes.orders
        application.dependency_overrides[get_tracer] = lambda: fakes.tracer
        application.dependency_overrides[get_embedder] = lambda: fakes.embedder
        test_client = TestClient(application)
        admin_headers = bearer(make_token("admin-1", role="admin"))
        for article in ARTICLES.values():
            assert test_client.post("/v1/articles", json=article, headers=admin_headers).status_code == 201
        return test_client, fakes

    return _build
