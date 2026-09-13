"""Checks for health checks, gunicorn config and a real gunicorn run. Don't edit this file."""

import json
import os
import runpy
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from app import create_app

HERE = Path(__file__).parent
DEAD_DB = "postgresql+psycopg://nobody:nothing@127.0.0.1:1/none"


def load_config(monkeypatch, **env):
    for key in ("PORT", "WEB_CONCURRENCY", "GUNICORN_THREADS", "GUNICORN_TIMEOUT", "LOG_LEVEL", "FORWARDED_ALLOW_IPS"):
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    return runpy.run_path(str(HERE / "gunicorn.conf.py"))


# ---------- gunicorn.conf.py ----------

def test_config_defaults(monkeypatch):
    config = load_config(monkeypatch)
    assert config["bind"] == "0.0.0.0:5091"
    assert 2 <= config["workers"] <= 8
    assert config["threads"] == 1 and config["worker_class"] == "sync"
    assert config["timeout"] == 30 and config["graceful_timeout"] == 30
    assert config["accesslog"] == "-" and config["errorlog"] == "-"
    assert config["max_requests"] > 0 and config["max_requests_jitter"] > 0
    assert config["loglevel"] == "info"
    assert config["forwarded_allow_ips"] == "127.0.0.1"


def test_config_from_env(monkeypatch):
    config = load_config(monkeypatch, PORT="8080", WEB_CONCURRENCY="3", GUNICORN_THREADS="4", GUNICORN_TIMEOUT="60", LOG_LEVEL="WARNING", FORWARDED_ALLOW_IPS="10.0.0.5")
    assert config["bind"] == "0.0.0.0:8080"
    assert config["workers"] == 3 and config["threads"] == 4 and config["worker_class"] == "gthread"
    assert config["timeout"] == 60 and config["loglevel"] == "warning" and config["forwarded_allow_ips"] == "10.0.0.5"


# ---------- health.py ----------

def test_live_and_ready_with_database(pg_url):
    client = create_app(pg_url).test_client()
    live = client.get("/health/live")
    assert live.status_code == 200 and live.get_json() == {"status": "ok"}
    assert live.headers["Cache-Control"] == "no-store"
    ready = client.get("/health/ready")
    assert ready.status_code == 200
    assert ready.get_json() == {"status": "ok", "checks": {"database": "ok"}}
    assert ready.headers["Cache-Control"] == "no-store"


def test_ready_is_503_when_database_is_down_but_live_is_200(caplog):
    client = create_app(DEAD_DB).test_client()
    assert client.get("/health/live").status_code == 200, "liveness must not depend on the database"
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.get_json() == {"status": "unavailable", "checks": {"database": "fail"}}
    assert "nobody" not in response.get_data(as_text=True), "don't leak connection details"
    assert any(record.levelname == "ERROR" for record in caplog.records), "log the reason server-side"
    assert client.get("/health/ready").status_code == 503, "later checks must still work"


def test_proxy_headers_trusted_only_when_enabled(pg_url, monkeypatch):
    headers = {"X-Forwarded-Proto": "https", "X-Forwarded-For": "203.0.113.7"}
    monkeypatch.delenv("TRUST_PROXY", raising=False)
    assert create_app(pg_url).test_client().get("/api/v1/whoami", headers=headers).get_json()["scheme"] == "http"
    monkeypatch.setenv("TRUST_PROXY", "1")
    body = create_app(pg_url).test_client().get("/api/v1/whoami", headers=headers).get_json()
    assert body["scheme"] == "https" and body["remote_addr"] == "203.0.113.7"


# ---------- a real gunicorn ----------

def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def get_json(url):
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read())


def test_gunicorn_serves_wsgi_app_and_shuts_down_gracefully(pg_url):
    port = free_port()
    env = {**os.environ, "PORT": str(port), "WEB_CONCURRENCY": "2", "DATABASE_URL": pg_url}
    server = subprocess.Popen(
        [sys.executable, "-m", "gunicorn", "-c", "gunicorn.conf.py", "--no-control-socket", "wsgi:app"],
        cwd=HERE, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    try:
        for _ in range(100):
            try:
                status, body = get_json(f"http://127.0.0.1:{port}/health/live")
                break
            except OSError:
                if server.poll() is not None:
                    pytest.fail("gunicorn exited:\n" + server.stdout.read()[-2000:])
                time.sleep(0.1)
        else:
            pytest.fail("gunicorn did not start listening on PORT")
        assert (status, body) == (200, {"status": "ok"})
        assert get_json(f"http://127.0.0.1:{port}/health/ready") == (200, {"status": "ok", "checks": {"database": "ok"}})
        pids = {get_json(f"http://127.0.0.1:{port}/api/v1/whoami")[1]["pid"] for _ in range(20)}
        assert server.pid not in pids, "requests are served by worker processes, not the master"
    finally:
        server.send_signal(signal.SIGTERM)
        output, _ = server.communicate(timeout=40)
    assert server.returncode == 0, output[-2000:]
    assert '"GET /health/live' in output, "access log should go to stdout"
