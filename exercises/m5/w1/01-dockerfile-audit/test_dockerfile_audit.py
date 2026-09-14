"""Checks for dockerfile_audit.py. Don't edit this file."""

from pathlib import Path
from textwrap import dedent

from dockerfile_audit import Finding, Instruction, audit, main, parse

SAMPLES = Path(__file__).parent / "samples"


def rules(text: str) -> list[tuple[str, int]]:
    return [(f.rule, f.line) for f in audit(dedent(text).lstrip("\n"))]


def test_parse_joins_continuations_and_skips_comments():
    text = dedent(
        """\
        # syntax=docker/dockerfile:1
        FROM python:3.13-slim AS base

        run apt-get update \\
            # a comment inside the continuation
            && apt-get install -y curl
        CMD ["python", "app.py"]
        """
    )
    assert parse(text) == [
        Instruction(2, "FROM", "python:3.13-slim AS base"),
        Instruction(4, "RUN", "apt-get update && apt-get install -y curl"),
        Instruction(7, "CMD", '["python", "app.py"]'),
    ]


def test_clean_dockerfile_has_no_findings():
    assert rules(
        """
        FROM --platform=$BUILDPLATFORM python:3.13-slim AS builder
        COPY pyproject.toml uv.lock ./
        RUN uv sync --frozen --no-dev
        COPY . .
        FROM python:3.13-slim@sha256:0123abcd AS runtime
        COPY --from=builder /app /app
        USER 10001
        HEALTHCHECK CMD ["python", "-c", "print(1)"]
        ENTRYPOINT ["gunicorn"]
        CMD ["wsgi:app"]
        """
    ) == []


def test_df001_unpinned_images_but_not_stage_references():
    assert rules(
        """
        FROM node AS deps
        FROM deps AS build
        FROM Docker.io/library/nginx:latest
        FROM registry.example.com:5000/team/app
        FROM scratch
        USER app
        HEALTHCHECK NONE
        """
    ) == [("DF001", 1), ("DF001", 3), ("DF001", 4)]


def test_df002_root_in_final_stage_only():
    assert ("DF002", 1) in rules("FROM python:3.13-slim\nHEALTHCHECK NONE\n")
    assert rules("FROM python:3.13-slim AS build\nUSER app\nFROM python:3.13-slim\nUSER app\nUSER root\nHEALTHCHECK NONE\n") == [("DF002", 5)]
    assert rules("FROM python:3.13-slim\nUSER 0:0\nHEALTHCHECK NONE\n") == [("DF002", 2)]
    assert rules("FROM python:3.13-slim AS build\nFROM python:3.13-slim\nUSER app\nHEALTHCHECK NONE\n") == []


def test_df003_shell_form():
    assert rules(
        """
        FROM python:3.13-slim
        USER app
        HEALTHCHECK NONE
        ENTRYPOINT entrypoint.sh
        CMD ["gunicorn", "app:app"]
        CMD gunicorn app:app
        """
    ) == [("DF003", 4), ("DF003", 6)]


def test_df004_copy_everything_before_install():
    assert rules(
        """
        FROM python:3.13-slim AS build
        COPY . .
        RUN pip install -r requirements.txt
        RUN npm ci
        FROM python:3.13-slim
        COPY requirements.txt .
        RUN pip install -r requirements.txt
        COPY --chown=app:app ./ /app
        RUN python -m compileall /app
        USER app
        HEALTHCHECK NONE
        """
    ) == [("DF004", 3), ("DF004", 4)]


def test_df005_apt():
    assert rules(
        """
        FROM debian:13-slim
        RUN apt-get update && apt-get install -y curl
        RUN apt-get update && apt-get install -y --no-install-recommends curl
        RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
        USER app
        HEALTHCHECK NONE
        """
    ) == [("DF005", 2), ("DF005", 3)]


def test_df006_secrets_with_values():
    assert rules(
        """
        FROM python:3.13-slim
        ARG GITHUB_TOKEN
        ARG STRIPE_API_KEY=sk_test_123
        ENV DB_PASSWORD=hunter2 APP_ENV=production
        ENV JWT_SECRET_KEY change-me
        ENV PYTHONUNBUFFERED=1
        ENV EMPTY_SECRET
        USER app
        HEALTHCHECK NONE
        """
    ) == [("DF006", 3), ("DF006", 4), ("DF006", 5)]


def test_df007_add_url_and_df008_healthcheck():
    assert rules(
        """
        FROM python:3.13-slim AS build
        ADD https://example.com/tool.tar.gz /tmp/
        ADD --chmod=755 https://example.com/run.sh /usr/local/bin/run.sh
        ADD local.tar.gz /opt/
        FROM python:3.13-slim
        USER app
        """
    ) == [("DF007", 2), ("DF007", 3), ("DF008", 5)]


def test_findings_are_sorted_with_severity_and_message():
    findings = audit("FROM python\nCMD python app.py\n")
    assert [(f.rule, f.line, f.severity) for f in findings] == [
        ("DF001", 1, "error"),
        ("DF002", 1, "error"),
        ("DF008", 1, "warning"),
        ("DF003", 2, "error"),
    ]
    assert all(isinstance(f, Finding) and f.message for f in findings)


def test_revoshop_like_dockerfile():
    text = (SAMPLES / "revoshop-like.Dockerfile").read_text()
    assert [(f.rule, f.line) for f in audit(text)] == [("DF008", 1), ("DF003", 33)]


def test_cli_output_and_exit_code(tmp_path, capsys):
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("FROM python:3.13-slim\nUSER app\nCMD python app.py\n")
    assert main([str(dockerfile)]) == 1
    out = capsys.readouterr().out.splitlines()
    assert out[0].startswith("Dockerfile:1 DF008 warning: ")
    assert out[1].startswith("Dockerfile:3 DF003 error: ")
    assert out[-1] == "1 error(s), 1 warning(s)"

    dockerfile.write_text("FROM python:3.13-slim\nUSER app\nCMD [\"python\", \"app.py\"]\n")
    assert main([str(dockerfile)]) == 0
    assert capsys.readouterr().out.splitlines()[-1] == "0 error(s), 1 warning(s)"
