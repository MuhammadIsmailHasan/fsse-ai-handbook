"""Checks for structured logging. Don't edit this file."""

import io
import json
import logging
import re

import pytest
from flask import Flask

from logging_setup import JsonFormatter, configure_logging, redact, request_id_var
from request_logging import init_request_logging


@pytest.fixture
def stream():
    buffer = io.StringIO()
    configure_logging("DEBUG", stream=buffer)
    yield buffer
    root = logging.getLogger()
    for handler in list(root.handlers):
        if getattr(handler, "stream", None) is buffer:
            root.removeHandler(handler)


def lines(buffer):
    return [json.loads(line) for line in buffer.getvalue().splitlines() if line.strip()]


# ---------- formatter ----------

def test_one_json_object_per_line_with_core_fields(stream):
    logging.getLogger("careerpilot.jobs").info("imported %d jobs", 42)
    [entry] = lines(stream)
    assert entry["level"] == "INFO" and entry["logger"] == "careerpilot.jobs" and entry["message"] == "imported 42 jobs"
    assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z", entry["timestamp"])
    assert "request_id" not in entry


def test_timestamp_is_utc_from_record():
    record = logging.LogRecord("x", logging.WARNING, __file__, 1, "hello", (), None)
    record.created = 1_767_225_600.5  # 2026-01-01T00:00:00.500Z
    assert json.loads(JsonFormatter().format(record))["timestamp"] == "2026-01-01T00:00:00.500Z"


def test_extra_fields_are_included_and_redacted(stream):
    logging.getLogger("auth").warning(
        "login failed",
        extra={"user_id": 7, "attempts": 3, "password": "hunter2", "payload": {"email": "a@b.id", "API_KEY": "sk-123", "nested": [{"refresh_token": "t"}]}},
    )
    [entry] = lines(stream)
    assert entry["user_id"] == 7 and entry["attempts"] == 3
    assert entry["password"] == "[REDACTED]"
    assert entry["payload"] == {"email": "a@b.id", "API_KEY": "[REDACTED]", "nested": [{"refresh_token": "[REDACTED]"}]}
    assert "hunter2" not in stream.getvalue() and "sk-123" not in stream.getvalue()


def test_redact_helper():
    assert redact({"Authorization": "Bearer x", "headers": {"Cookie": "s=1", "Accept": "json"}, "items": ({"secret_key": 1},)}) == {
        "Authorization": "[REDACTED]",
        "headers": {"Cookie": "[REDACTED]", "Accept": "json"},
        "items": [{"secret_key": "[REDACTED]"}],
    }
    assert redact("plain") == "plain"


def test_exceptions_are_structured(stream):
    try:
        {}["missing"]
    except KeyError:
        logging.getLogger("worker").exception("job crashed")
    [entry] = lines(stream)
    assert entry["level"] == "ERROR" and entry["exc_type"] == "KeyError" and entry["exc_message"] == "'missing'"
    assert "Traceback" in entry["stack"] and "\n" not in stream.getvalue().strip(), "the whole entry stays on ONE line"


def test_non_json_values_do_not_crash(stream):
    from datetime import date
    from decimal import Decimal

    logging.getLogger("x").info("values", extra={"on": date(2026, 9, 13), "amount": Decimal("150000.50")})
    [entry] = lines(stream)
    assert entry["on"] == "2026-09-13" and entry["amount"] == "150000.50"


def test_configure_logging_is_idempotent_and_sets_level():
    buffer = io.StringIO()
    configure_logging("warning", stream=buffer)
    configure_logging("WARNING", stream=buffer)
    logging.getLogger("x").info("hidden")
    logging.getLogger("x").warning("shown")
    assert [e["message"] for e in lines(buffer)] == ["shown"], "no duplicates, INFO filtered out"
    configure_logging("DEBUG", stream=io.StringIO())
    assert logging.getLogger().level == logging.DEBUG


def test_request_id_from_context(stream):
    token = request_id_var.set("abc123")
    try:
        logging.getLogger("x").info("inside")
    finally:
        request_id_var.reset(token)
    logging.getLogger("x").info("outside")
    first, second = lines(stream)
    assert first["request_id"] == "abc123" and "request_id" not in second


# ---------- Flask ----------

@pytest.fixture
def client(stream):
    app = Flask(__name__)
    init_request_logging(app)

    @app.get("/api/v1/jobs")
    def jobs():
        logging.getLogger("careerpilot.jobs").info("listing jobs")
        return {"data": []}

    @app.get("/api/v1/missing")
    def missing():
        return {"error": {"code": "not_found"}}, 404

    @app.get("/boom")
    def boom():
        raise RuntimeError("database exploded")

    return app.test_client()


def test_generates_request_id_and_logs_access_line(client, stream):
    response = client.get("/api/v1/jobs?q=python&token=should-not-appear")
    request_id = response.headers["X-Request-ID"]
    assert re.fullmatch(r"[0-9a-f]{32}", request_id)
    app_line, access = lines(stream)
    assert app_line["message"] == "listing jobs" and app_line["request_id"] == request_id
    assert access["message"] == "request completed" and access["logger"] == "http" and access["level"] == "INFO"
    assert access["request_id"] == request_id
    assert (access["method"], access["path"], access["status"]) == ("GET", "/api/v1/jobs", 200)
    assert isinstance(access["duration_ms"], (int, float)) and access["duration_ms"] >= 0
    assert "should-not-appear" not in stream.getvalue(), "don't log query strings (they can contain tokens)"


def test_reuses_valid_incoming_request_id_but_not_unsafe_ones(client, stream):
    assert client.get("/api/v1/jobs", headers={"X-Request-ID": "lb-7f3a.01_x"}).headers["X-Request-ID"] == "lb-7f3a.01_x"
    for bad in ("has spaces", "x" * 65, '"}, {"level": "CRITICAL'):
        assert client.get("/api/v1/jobs", headers={"X-Request-ID": bad}).headers["X-Request-ID"] != bad


def test_levels_follow_status_and_errors_keep_request_id(client, stream):
    client.application.config["PROPAGATE_EXCEPTIONS"] = False
    assert client.get("/api/v1/missing").status_code == 404
    boom = client.get("/boom")
    assert boom.status_code == 500
    entries = lines(stream)
    access = [e for e in entries if e["message"] == "request completed"]
    assert [(e["status"], e["level"]) for e in access] == [(404, "WARNING"), (500, "ERROR")]
    crash = next(e for e in entries if e.get("exc_type") == "RuntimeError")
    assert crash["request_id"] == boom.headers["X-Request-ID"]


def test_request_id_does_not_leak_after_request(client, stream):
    client.get("/api/v1/jobs")
    assert request_id_var.get() is None
