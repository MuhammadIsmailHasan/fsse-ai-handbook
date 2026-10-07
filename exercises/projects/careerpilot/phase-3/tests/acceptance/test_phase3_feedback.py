"""C5 · POST /v1/feedback — stream the AI's feedback as Server-Sent Events."""

import json

from p3_support import CV, JOB, FakeFeedbackClient, make_token

BODY = {"cv_text": CV, "job_text": JOB}


def events(response):
    """Split an SSE body into the text after each 'data: ' line."""
    chunks = [c for c in response.text.split("\n\n") if c]
    assert all(c.startswith("data: ") for c in chunks), chunks
    return [c.removeprefix("data: ") for c in chunks]


def test_streams_tokens_then_done(client, auth, fake_feedback):
    r = client.post("/v1/feedback", json=BODY, headers=auth)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/event-stream")
    assert events(r) == [
        json.dumps({"token": "Good "}),
        json.dumps({"token": "start. "}),
        json.dumps({"token": "Add AWS."}),
        "[DONE]",
    ]


def test_streaming_headers(client, auth, fake_feedback):
    r = client.post("/v1/feedback", json=BODY, headers=auth)
    assert r.headers["cache-control"] == "no-cache"
    assert r.headers["x-accel-buffering"] == "no"
    assert r.headers["X-Request-ID"]


def test_tokens_with_newlines_stay_valid_events(client, auth, app):
    from careerpilot_ai.deps import get_feedback_client

    fake = FakeFeedbackClient(tokens=["line one\nline two", "\n\n- bullet"])
    app.dependency_overrides[get_feedback_client] = lambda: fake
    try:
        r = client.post("/v1/feedback", json=BODY, headers=auth)
    finally:
        app.dependency_overrides.pop(get_feedback_client, None)
    parsed = [json.loads(e) for e in events(r)[:-1]]
    assert [p["token"] for p in parsed] == ["line one\nline two", "\n\n- bullet"]
    assert events(r)[-1] == "[DONE]"


def test_prompt_contains_the_missing_skills_and_the_job(client, auth, fake_feedback):
    client.post("/v1/feedback", json=BODY, headers=auth)
    assert len(fake_feedback.prompts) == 1
    prompt = fake_feedback.prompts[0].lower()
    for skill in ("aws", "fastapi", "sql"):
        assert skill in prompt
    assert JOB.lower() in prompt


def test_prompt_never_contains_the_token(client, fake_feedback):
    token = make_token()
    client.post("/v1/feedback", json=BODY, headers={"Authorization": f"Bearer {token}"})
    assert token not in fake_feedback.prompts[0]


def test_error_midstream_sends_an_error_event_and_no_done(client, auth, app):
    from careerpilot_ai.deps import get_feedback_client

    fake = FakeFeedbackClient(tokens=["one ", "two ", "three"], fail_after=1)
    app.dependency_overrides[get_feedback_client] = lambda: fake
    try:
        r = client.post("/v1/feedback", json=BODY, headers=auth)
    finally:
        app.dependency_overrides.pop(get_feedback_client, None)
    assert r.status_code == 200   # the status was already sent when the model failed
    assert events(r) == [json.dumps({"token": "one "}), json.dumps({"error": "feedback_failed"})]


def test_validation_errors_come_before_streaming(client, auth, fake_feedback):
    r = client.post("/v1/feedback", json={"cv_text": "short", "job_text": JOB}, headers=auth)
    assert r.status_code == 422
    assert r.headers["content-type"].startswith("application/json")
    assert fake_feedback.prompts == []   # the model was never called


def test_job_without_skills_is_422_before_streaming(client, auth, fake_feedback):
    r = client.post(
        "/v1/feedback",
        json={"cv_text": CV, "job_text": "We are a friendly team that likes long walks together."},
        headers=auth,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "no_skills_found"
    assert fake_feedback.prompts == []


def test_default_client_works_offline(client, auth):
    # No fake installed: the built-in template client must still produce feedback.
    r = client.post("/v1/feedback", json=BODY, headers=auth)
    parsed = events(r)
    assert r.status_code == 200
    assert parsed[-1] == "[DONE]"
    text = "".join(json.loads(e)["token"] for e in parsed[:-1]).lower()
    assert "aws" in text   # it mentions at least one missing skill


def test_feedback_is_audited_when_the_stream_ends(client, auth, fake_feedback, audit):
    client.post("/v1/feedback", json=BODY, headers=auth)
    assert audit.events == [{"user": "user-1", "endpoint": "feedback", "status": "ok"}]


def test_failed_stream_is_audited_as_error(client, auth, app, audit):
    from careerpilot_ai.deps import get_feedback_client

    fake = FakeFeedbackClient(tokens=["one "], fail_after=0)
    app.dependency_overrides[get_feedback_client] = lambda: fake
    try:
        client.post("/v1/feedback", json=BODY, headers=auth)
    finally:
        app.dependency_overrides.pop(get_feedback_client, None)
    assert audit.events == [{"user": "user-1", "endpoint": "feedback", "status": "error"}]
