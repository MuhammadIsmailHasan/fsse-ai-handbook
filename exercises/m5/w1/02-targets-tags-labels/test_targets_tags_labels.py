"""Checks for service/Dockerfile and image_meta.py. Don't edit this file.

Real builds run only when you opt in:  RUN_DOCKER_TESTS=1 uv run pytest m5/w1/02-targets-tags-labels
"""

import json
import os
import shutil
import subprocess
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from image_meta import image_tags, oci_labels

SERVICE = Path(__file__).parent / "service"
SHA = "3f2c1ab9d4e5f60718293a4b5c6d7e8f90123456"


def instructions():
    result, buffer, start = [], "", 0
    for number, raw in enumerate((SERVICE / "Dockerfile").read_text().splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if not buffer:
            start = number
        if line.endswith("\\"):
            buffer += line[:-1] + " "
            continue
        keyword, _, args = (buffer + line).strip().partition(" ")
        result.append((keyword.upper(), " ".join(args.split())))
        buffer = ""
    return result


def stages():
    found, preamble = {}, []
    current = None
    for keyword, args in instructions():
        if keyword == "FROM":
            tokens = args.split()
            name = tokens[2].lower() if len(tokens) >= 3 and tokens[1].lower() == "as" else f"#{len(found)}"
            current = name
            found[name] = [(keyword, args)]
        elif current is None:
            preamble.append((keyword, args))
        else:
            found[current].append((keyword, args))
    return preamble, found


def has(stage, keyword, needle):
    return any(k == keyword and needle in a for k, a in stage)


# ---------- Dockerfile ----------

def test_stage_names_order_and_python_arg():
    preamble, found = stages()
    assert list(found) == ["base", "deps", "dev", "test", "prod"]
    assert ("ARG", "PYTHON_VERSION=3.13") in preamble
    assert found["base"][0][1].startswith("python:${PYTHON_VERSION}-slim")
    assert found["deps"][0][1].split()[0] == "base"
    assert found["dev"][0][1].split()[0] == "deps"
    assert found["test"][0][1].split()[0] == "dev"
    assert found["prod"][0][1].split()[0] == "base"


def test_base_settings_and_pinned_uv():
    _, found = stages()
    base = found["base"]
    env = " ".join(a for k, a in base if k == "ENV")
    assert "PYTHONUNBUFFERED=1" in env and "PYTHONDONTWRITEBYTECODE=1" in env
    assert ("WORKDIR", "/app") in base
    uv = [a for k, a in base if k == "COPY" and "astral-sh/uv" in a]
    assert uv and "uv:latest" not in uv[0] and ":" in uv[0].split("astral-sh/uv")[1], "pin the uv image version"


def test_deps_layer_is_cached_and_production_only():
    _, found = stages()
    deps = found["deps"]
    copies = [a for k, a in deps if k == "COPY"]
    assert copies == ["pyproject.toml uv.lock ./"], "copy only the lock files in deps"
    runs = [a for k, a in deps if k == "RUN"]
    assert any("--mount=type=cache,target=/root/.cache/uv" in r and "uv sync --locked --no-dev --no-install-project" in r for r in runs)


def test_dev_and_test_targets():
    _, found = stages()
    assert any(k == "RUN" and "--mount=type=cache" in a and "uv sync --locked" in a and "--no-dev" not in a for k, a in found["dev"])
    cmd = [a for k, a in found["dev"] if k == "CMD"]
    assert cmd and json.loads(cmd[-1])[:3] == ["uv", "run", "flask"] and "--debug" in json.loads(cmd[-1])
    test = found["test"]
    assert ("COPY", ". .") in test
    assert any(k == "RUN" and "pytest" in a for k, a in test)


def test_prod_is_clean_non_root_and_labeled():
    _, found = stages()
    prod = found["prod"]
    assert has(prod, "COPY", "--from=deps") and has(prod, "COPY", "/app/.venv")
    assert not has(prod, "RUN", "uv sync") and not has(prod, "RUN", "pytest") and not has(prod, "COPY", "astral-sh/uv")
    users = [a for k, a in prod if k == "USER"]
    assert users and users[-1].split(":")[0] == "10001"
    assert has(prod, "RUN", "10001")
    assert any(k == "ENV" and "/app/.venv/bin" in a for k, a in prod)
    assert ("EXPOSE", "5091") in prod
    assert has(prod, "HEALTHCHECK", "/health/live")
    cmd = [a for k, a in prod if k == "CMD"]
    assert cmd and json.loads(cmd[-1])[0] == "gunicorn"
    args = [a for k, a in prod if k == "ARG"]
    assert any(a.startswith("VERSION") for a in args) and any(a.startswith("REVISION") for a in args)
    labels = " ".join(a for k, a in prod if k == "LABEL")
    for key in ("title", "version", "revision", "source"):
        assert f"org.opencontainers.image.{key}=" in labels
    assert "org.opencontainers.image.version=$VERSION" in labels and "org.opencontainers.image.revision=$REVISION" in labels


# ---------- image_meta.py ----------

@pytest.mark.parametrize(
    ("ref", "expected"),
    [
        ("refs/heads/main", ["api:edge", "api:main", "api:sha-3f2c1ab"]),
        ("refs/heads/feat/Login-Page", ["api:feat-login-page", "api:sha-3f2c1ab"]),
        ("refs/heads/-Weird_Branch.", ["api:sha-3f2c1ab", "api:weird_branch"]),
        ("refs/tags/v1.4.2", ["api:1", "api:1.4", "api:1.4.2", "api:latest", "api:sha-3f2c1ab"]),
        ("refs/tags/v2.0.0-rc.1", ["api:2.0.0-rc.1", "api:sha-3f2c1ab"]),
        ("refs/tags/release-2026", ["api:sha-3f2c1ab"]),
        ("refs/pull/42/merge", ["api:pr-42", "api:sha-3f2c1ab"]),
    ],
)
def test_image_tags(ref, expected):
    assert image_tags("api", ref=ref, sha=SHA) == expected


def test_image_tags_edge_cases():
    assert image_tags("ghcr.io/sari/api", ref="refs/heads/develop", sha=SHA, default_branch="develop") == [
        "ghcr.io/sari/api:develop",
        "ghcr.io/sari/api:edge",
        "ghcr.io/sari/api:sha-3f2c1ab",
    ]
    long_branch = image_tags("api", ref="refs/heads/" + "x" * 200, sha=SHA)
    assert max(len(t.split(":", 1)[1]) for t in long_branch) == 128
    for bad in ["3f2c1ab", SHA.upper(), SHA + "0", "z" * 40]:
        with pytest.raises(ValueError):
            image_tags("api", ref="refs/heads/main", sha=bad)


def test_oci_labels():
    created = datetime(2026, 9, 15, 15, 30, tzinfo=timezone(timedelta(hours=7)))
    assert oci_labels(title="careerpilot-api", source="https://github.com/sari/careerpilot", version="1.4.2", revision=SHA, created=created) == {
        "org.opencontainers.image.title": "careerpilot-api",
        "org.opencontainers.image.source": "https://github.com/sari/careerpilot",
        "org.opencontainers.image.version": "1.4.2",
        "org.opencontainers.image.revision": SHA,
        "org.opencontainers.image.created": "2026-09-15T08:30:00Z",
    }


# ---------- optional: real builds ----------

@pytest.mark.skipif(os.environ.get("RUN_DOCKER_TESTS") != "1" or not shutil.which("docker"), reason="set RUN_DOCKER_TESTS=1")
def test_real_builds():
    tag = f"m5-targets-{uuid.uuid4().hex[:8]}"
    try:
        subprocess.run(["docker", "build", "--target", "test", "-t", f"{tag}:test", str(SERVICE)], check=True, capture_output=True, timeout=900)
        subprocess.run(["docker", "build", "--build-arg", "VERSION=1.4.2", "--build-arg", f"REVISION={SHA}", "-t", f"{tag}:prod", str(SERVICE)], check=True, capture_output=True, timeout=900)
        inspect = json.loads(subprocess.run(["docker", "image", "inspect", f"{tag}:prod"], check=True, capture_output=True, text=True).stdout)[0]
        assert inspect["Config"]["User"].startswith("10001")
        assert inspect["Config"]["Labels"]["org.opencontainers.image.revision"] == SHA
        which = subprocess.run(["docker", "run", "--rm", "--entrypoint", "sh", f"{tag}:prod", "-c", "command -v uv || echo none; python -c 'import pytest' 2>/dev/null && echo pytest || echo no-pytest"], capture_output=True, text=True, timeout=120)
        assert which.stdout.split() == ["none", "no-pytest"]
    finally:
        subprocess.run(["docker", "image", "rm", "-f", f"{tag}:test", f"{tag}:prod"], capture_output=True)
