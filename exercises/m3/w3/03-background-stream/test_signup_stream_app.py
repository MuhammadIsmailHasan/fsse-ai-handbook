import pytest
from fastapi.testclient import TestClient

from signup_stream_app import OUTBOX, app, word_events

client = TestClient(app)


@pytest.fixture(autouse=True)
def empty_outbox():
    OUTBOX.clear()
    yield
    OUTBOX.clear()


def test_signup_returns_201_and_sends_welcome_after_response():
    r = client.post("/signup", json={"email": "sari@example.com"})
    assert r.status_code == 201
    assert r.json() == {"email": "sari@example.com"}
    # TestClient runs background tasks before it hands the response back.
    assert OUTBOX == ["welcome:sari@example.com"]


def test_bad_email_is_400_and_nothing_is_scheduled():
    r = client.post("/signup", json={"email": "not-an-email"})
    assert r.status_code == 400
    assert OUTBOX == []


def test_missing_email_is_422():
    assert client.post("/signup", json={}).status_code == 422
    assert OUTBOX == []


def test_each_signup_schedules_its_own_task():
    client.post("/signup", json={"email": "a@x.com"})
    client.post("/signup", json={"email": "b@x.com"})
    assert OUTBOX == ["welcome:a@x.com", "welcome:b@x.com"]


def test_word_events_is_a_lazy_generator_of_sse_lines():
    events = word_events("hi there")
    assert next(events) == "data: hi\n\n"
    assert list(events) == ["data: there\n\n", "data: [DONE]\n\n"]


def test_stream_endpoint_media_type_and_body():
    r = client.get("/stream", params={"text": "hello big world"})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/event-stream")
    assert r.text == "data: hello\n\ndata: big\n\ndata: world\n\ndata: [DONE]\n\n"


def test_stream_of_empty_text_is_just_done():
    r = client.get("/stream", params={"text": ""})
    assert r.text == "data: [DONE]\n\n"
