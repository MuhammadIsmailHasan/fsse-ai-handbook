"""Static best-practice checks for Dockerfile and .dockerignore. Don't edit this file."""

import json
import re
from pathlib import Path

import pytest

HERE = Path(__file__).parent


def instructions():
    text = (HERE / "Dockerfile").read_text()
    text = re.sub(r"\\\n", " ", text)  # join line continuations
    result = []
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            keyword, _, rest = line.partition(" ")
            result.append((keyword.upper(), rest.strip()))
    return result


@pytest.fixture(scope="module")
def steps():
    return instructions()


def first_index(steps, predicate):
    return next((i for i, step in enumerate(steps) if predicate(step)), None)


def test_pinned_slim_base_image(steps):
    base = next(rest for keyword, rest in steps if keyword == "FROM")
    image = base.split()[0]
    assert ":" in image, "Pin a tag, e.g. python:3.12-slim"
    tag = image.split(":", 1)[1]
    assert tag != "latest", "Never use :latest"
    assert image.startswith("python:") and "slim" in tag, "Use a slim Python base image"
    assert re.match(r"3\.\d+", tag), "Pin the Python version, e.g. 3.12"


def test_workdir(steps):
    assert any(keyword == "WORKDIR" for keyword, _ in steps), "Set WORKDIR"


def test_dependencies_before_code(steps):
    copy_requirements = first_index(steps, lambda s: s[0] == "COPY" and "requirements.txt" in s[1] and not s[1].startswith(". "))
    install = first_index(steps, lambda s: s[0] == "RUN" and "pip install" in s[1])
    copy_all = first_index(steps, lambda s: s[0] == "COPY" and re.match(r"^\.\s", s[1]))
    assert copy_requirements is not None, "COPY requirements.txt on its own first"
    assert install is not None and copy_all is not None
    assert copy_requirements < install < copy_all, "Copy + install requirements BEFORE `COPY . .`"


def test_pip_no_cache(steps):
    install = next(rest for keyword, rest in steps if keyword == "RUN" and "pip install" in rest)
    assert "--no-cache-dir" in install


def test_non_root_user(steps):
    users = [(i, rest) for i, (keyword, rest) in enumerate(steps) if keyword == "USER"]
    assert users, "Add a USER instruction"
    cmd_index = first_index(steps, lambda s: s[0] == "CMD")
    last_user_index, user = users[-1]
    assert user not in ("root", "0"), "Don't run as root"
    assert cmd_index is None or last_user_index < cmd_index


def test_no_secrets_in_env_or_arg(steps):
    for keyword, rest in steps:
        if keyword in ("ENV", "ARG"):
            assert not re.search(r"SECRET|PASSWORD|TOKEN|KEY", rest, flags=re.I), f"Secret in {keyword}: {rest}"


def test_expose(steps):
    assert ("EXPOSE", "8000") in steps


def test_cmd_exec_form(steps):
    cmd = next((rest for keyword, rest in steps if keyword == "CMD"), None)
    assert cmd is not None, "Add a CMD"
    parsed = json.loads(cmd)  # raises if not a JSON array
    assert isinstance(parsed, list) and parsed[0] == "gunicorn"


def test_dockerignore():
    path = HERE / ".dockerignore"
    assert path.exists(), "Create .dockerignore"
    entries = {line.strip().rstrip("/") for line in path.read_text().splitlines() if line.strip() and not line.startswith("#")}
    for required in (".env", ".venv", ".git", "__pycache__"):
        assert required in entries, f".dockerignore should exclude {required}"
