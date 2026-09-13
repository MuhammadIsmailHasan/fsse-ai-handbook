"""Checks for service/Dockerfile, service/.dockerignore and service/compose.prod.yaml. Don't edit this file.

Static checks always run. The real build + run test runs only when you opt in:
    RUN_DOCKER_TESTS=1 uv run pytest m2/w6/06-dockerize-flask
"""

import json
import os
import re
import secrets
import shutil
import subprocess
import time
import urllib.request
import uuid
from pathlib import Path

import pytest
import yaml

SERVICE = Path(__file__).parent / "service"


def instructions(path=SERVICE / "Dockerfile"):
    """[(KEYWORD, arguments)] with comments removed and line continuations joined."""
    result, buffer = [], ""
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not buffer and (not line or line.startswith("#")):
            continue
        if line.startswith("#"):
            continue
        if line.endswith("\\"):
            buffer += line[:-1] + " "
            continue
        buffer += line
        keyword, _, args = buffer.strip().partition(" ")
        result.append((keyword.upper(), args.strip()))
        buffer = ""
    return result


def stages():
    """List of stages; each stage is its list of instructions, starting with FROM."""
    found = []
    for keyword, args in instructions():
        if keyword == "FROM":
            found.append([])
        if found:
            found[-1].append((keyword, args))
    return found


# ---------- Dockerfile ----------

def test_multi_stage_with_pinned_slim_bases():
    all_stages = stages()
    assert len(all_stages) >= 2, "use a builder stage and a runtime stage"
    for stage in all_stages:
        image = stage[0][1].split()[0]
        assert ":" in image and not image.endswith(":latest"), f"pin the base image tag: {image}"
    assert "slim" in all_stages[-1][0][1], "use a slim runtime base image"
    assert re.search(r"\bAS\s+\w+", all_stages[0][0][1], re.IGNORECASE), "name the build stage (FROM ... AS builder)"


def test_uv_is_pinned_and_installs_locked_production_dependencies():
    text = " ".join(args for _, args in instructions())
    match = re.search(r"ghcr\.io/astral-sh/uv:([\w.\-]+)", text)
    assert match and match.group(1) != "latest", "copy uv from ghcr.io/astral-sh/uv:<pinned version>"
    syncs = [args for keyword, args in instructions() if keyword == "RUN" and "uv sync" in args]
    assert syncs, "install dependencies with uv sync"
    assert all(("--locked" in s or "--frozen" in s) and "--no-dev" in s for s in syncs), "uv sync --locked --no-dev"


def test_dependencies_are_installed_before_the_source_is_copied():
    builder = stages()[0]
    copy_all = next((i for i, (k, a) in enumerate(builder) if k == "COPY" and re.match(r"^(--\S+\s+)*\.\s", a + " ")), None)
    assert copy_all is not None, "the builder stage should COPY . (the source) at some point"
    first_sync = next((i for i, (k, a) in enumerate(builder) if k == "RUN" and "uv sync" in a), None)
    assert first_sync is not None and first_sync < copy_all, "install dependencies BEFORE copying the source, so the layer is cached"
    assert any(k == "COPY" and "uv.lock" in a for k, a in builder[:first_sync]) or "uv.lock" in builder[first_sync][1], "the dependency layer needs pyproject.toml and uv.lock"


def test_runtime_stage_is_small_safe_and_observable():
    runtime = stages()[-1]
    keywords = [k for k, _ in runtime]
    assert not any(k == "RUN" and "uv sync" in a for k, a in runtime), "don't install in the runtime stage — copy the built venv"
    assert any(k == "COPY" and "--from=" in a for k, a in runtime), "COPY --from=<builder> the built app/venv"
    users = [a for k, a in runtime if k == "USER"]
    assert users and users[-1].split(":")[0] not in ("root", "0"), "run as a non-root USER"
    assert keywords.index("USER") < keywords.index("CMD")
    env = " ".join(a for k, a in runtime if k == "ENV")
    assert re.search(r"PYTHONUNBUFFERED\s*=?\s*1", env), "PYTHONUNBUFFERED=1 so logs appear immediately"
    assert any(k == "EXPOSE" and "5091" in a for k, a in runtime)
    healthchecks = [a for k, a in runtime if k == "HEALTHCHECK"]
    assert healthchecks and "/health/live" in healthchecks[-1], "HEALTHCHECK should call /health/live"


def test_cmd_uses_exec_form_gunicorn():
    cmd = [a for k, a in stages()[-1] if k == "CMD"][-1]
    parsed = json.loads(cmd)  # exec form is a JSON array
    assert parsed[0] == "gunicorn" and "wsgi:app" in parsed, "CMD [\"gunicorn\", ..., \"wsgi:app\"]"


def test_no_secrets_baked_into_the_image():
    for keyword, args in instructions():
        if keyword in ("ENV", "ARG"):
            assert not re.search(r"(?i)(secret|password|token|api_key)\w*\s*=", args), f"secret in {keyword}: {args}"


# ---------- .dockerignore ----------

def test_dockerignore_excludes_secrets_and_junk():
    patterns = {line.strip().rstrip("/") for line in (SERVICE / ".dockerignore").read_text().splitlines() if line.strip() and not line.startswith("#")}
    for required in (".git", ".venv", "__pycache__", ".env"):
        assert required in patterns, f".dockerignore should exclude {required}"
    assert any(p.startswith(".env.") or p == ".env*" for p in patterns), "also exclude .env.* files"


# ---------- compose.prod.yaml ----------

def compose():
    return yaml.safe_load((SERVICE / "compose.prod.yaml").read_text())


def test_compose_requires_secrets_from_environment():
    services = compose()["services"]
    for name, service in services.items():
        environment = service.get("environment", {})
        assert isinstance(environment, dict), "use the mapping form for environment"
        for key, value in environment.items():
            if re.search(r"(?i)password|secret|database_url", key):
                assert re.search(r"\$\{\w+:\?", str(value)), f"{name}.{key} must come from a required variable like ${{VAR:?message}}"
    assert "JWT_SECRET_KEY" in services["api"]["environment"]


def test_compose_health_ordering_and_exposure():
    services = compose()["services"]
    api, db = services["api"], services["db"]
    assert db["image"].startswith("postgres:") and db["image"] != "postgres:latest", "pin the postgres image"
    assert "healthcheck" in db and "pg_isready" in str(db["healthcheck"]["test"])
    assert api["depends_on"]["db"]["condition"] == "service_healthy", "start the API only after the DB is healthy"
    assert "ports" not in db, "don't publish the database port in production"
    assert all(s.get("restart") in ("unless-stopped", "always", "on-failure") for s in services.values())
    assert any(":/var/lib/postgresql/data" in v for v in db.get("volumes", [])), "persist data in a named volume"
    assert any(str(p).endswith(":5091") and "${" in str(p) for p in api["ports"]), "publish the API on a configurable host port"


# ---------- optional: really build and run it ----------

@pytest.mark.skipif(os.environ.get("RUN_DOCKER_TESTS") != "1", reason="set RUN_DOCKER_TESTS=1 to build and run the image")
def test_image_builds_runs_healthy_as_non_root():
    assert shutil.which("docker"), "docker not found"
    project = f"w6docker{uuid.uuid4().hex[:6]}"
    port = "5098"
    env = {**os.environ, "JWT_SECRET_KEY": secrets.token_urlsafe(40), "POSTGRES_PASSWORD": secrets.token_urlsafe(16), "API_PORT": port}
    base = ["docker", "compose", "-f", "compose.prod.yaml", "-p", project]
    run = lambda *args, **kw: subprocess.run([*base, *args], cwd=SERVICE, env=env, capture_output=True, text=True, **kw)
    try:
        up = run("up", "-d", "--build", "--wait", timeout=600)
        assert up.returncode == 0, up.stderr[-3000:]
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health/ready", timeout=5) as response:
            assert json.loads(response.read())["checks"]["database"] == "ok"
        assert run("exec", "-T", "api", "id", "-u").stdout.strip() not in ("", "0"), "container runs as root"
        stop_started = time.monotonic()
        assert run("stop", "api", timeout=60).returncode == 0
        assert time.monotonic() - stop_started < 10, "SIGTERM should stop gunicorn quickly (exec-form CMD)"
    finally:
        run("down", "-v", "--rmi", "local", timeout=120)
