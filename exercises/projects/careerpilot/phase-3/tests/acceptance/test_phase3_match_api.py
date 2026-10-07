"""C4 · POST /v1/match — validation, the response contract, and the audit trail."""

import pytest

from p3_support import CV, JOB


def post(client, auth, **body):
    return client.post("/v1/match", json=body, headers=auth)


def test_match_contract(client, auth):
    r = post(client, auth, cv_text=CV, job_text=JOB)
    assert r.status_code == 200
    assert r.json() == {
        "data": {
            "score": 57,
            "level": "partial",
            "matched_skills": ["docker", "git", "postgresql", "python"],
            "missing_skills": ["aws", "fastapi", "sql"],
        }
    }
    assert r.headers["X-Request-ID"]


def test_text_is_trimmed_before_checking(client, auth):
    r = post(client, auth, cv_text="   " + CV + "   ", job_text=JOB)
    assert r.status_code == 200


@pytest.mark.parametrize("missing", ["cv_text", "job_text"])
def test_missing_field_is_422_with_field_name(client, auth, missing):
    body = {"cv_text": CV, "job_text": JOB}
    del body[missing]
    r = client.post("/v1/match", json=body, headers=auth)
    assert r.status_code == 422
    error = r.json()["error"]
    assert error["code"] == "validation_failed"
    assert missing in error["fields"]
    assert error["fields"][missing]


@pytest.mark.parametrize("field", ["cv_text", "job_text"])
def test_too_short_is_422(client, auth, field):
    body = {"cv_text": CV, "job_text": JOB, field: "python"}
    r = client.post("/v1/match", json=body, headers=auth)
    assert r.status_code == 422
    assert field in r.json()["error"]["fields"]


def test_whitespace_only_counts_as_too_short(client, auth):
    r = post(client, auth, cv_text=" " * 50, job_text=JOB)
    assert r.status_code == 422


def test_20000_characters_is_fine_20001_is_not(client, auth):
    ok = ("python " * 3000)[:20000]
    assert post(client, auth, cv_text=ok, job_text=JOB).status_code == 200
    r = post(client, auth, cv_text=ok + "x", job_text=JOB)
    assert r.status_code == 422
    assert "cv_text" in r.json()["error"]["fields"]


def test_wrong_type_is_422(client, auth):
    assert post(client, auth, cv_text=12345, job_text=JOB).status_code == 422


def test_unknown_fields_are_rejected(client, auth):
    r = post(client, auth, cv_text=CV, job_text=JOB, admin=True)
    assert r.status_code == 422
    assert "admin" in r.json()["error"]["fields"]


def test_non_json_body_is_422(client, auth):
    r = client.post("/v1/match", content="cv_text=hello", headers={**auth, "Content-Type": "text/plain"})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_failed"


def test_job_without_known_skills_is_422_no_skills_found(client, auth):
    r = post(client, auth, cv_text=CV, job_text="We are a friendly team that likes long walks together.")
    assert r.status_code == 422
    error = r.json()["error"]
    assert error["code"] == "no_skills_found"
    assert "job_text" in error["fields"]


def test_a_successful_match_is_audited_after_the_response(client, auth, audit):
    r = post(client, auth, cv_text=CV, job_text=JOB)
    assert r.status_code == 200
    assert audit.events == [{"user": "user-1", "endpoint": "match", "score": 57}]


def test_audit_never_contains_the_cv_text(client, auth, audit):
    post(client, auth, cv_text=CV, job_text=JOB)
    assert CV not in str(audit.events)
    assert JOB not in str(audit.events)


def test_failed_requests_are_not_audited(client, auth, audit):
    post(client, auth, cv_text="short", job_text=JOB)
    client.post("/v1/match", json={"cv_text": CV, "job_text": JOB})  # no token
    assert audit.events == []


def test_audit_failure_does_not_break_the_response(app, client, auth):
    from careerpilot_ai.deps import get_audit_log

    class Broken:
        def record(self, event):
            raise RuntimeError("audit store is down")

    app.dependency_overrides[get_audit_log] = lambda: Broken()
    try:
        r = post(client, auth, cv_text=CV, job_text=JOB)
        assert r.status_code == 200
    finally:
        app.dependency_overrides.pop(get_audit_log, None)
