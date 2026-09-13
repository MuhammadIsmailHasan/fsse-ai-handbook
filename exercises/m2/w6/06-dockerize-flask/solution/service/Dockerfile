# syntax=docker/dockerfile:1

# ---------- Stage 1: build the virtual environment ----------
FROM python:3.14-slim AS builder

# uv as a static binary from its official image (pinned version).
COPY --from=ghcr.io/astral-sh/uv:0.11.29 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# 1) Dependencies only: this layer is cached until pyproject.toml or uv.lock change.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-install-project

# 2) Application code: changes often, so it comes last.
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev


# ---------- Stage 2: small runtime image ----------
FROM python:3.14-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    PORT=5091

# A dedicated unprivileged user (no login shell, no home needed).
RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app
# Only the built app + venv — no uv, no build caches, no dev dependencies.
COPY --from=builder --chown=app:app /app /app

USER app

EXPOSE 5091

HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen(f\"http://127.0.0.1:{os.environ['PORT']}/health/live\", timeout=2)"]

# Exec form: gunicorn is PID 1 and receives SIGTERM directly for graceful shutdown.
CMD ["gunicorn", "-c", "gunicorn.conf.py", "--no-control-socket", "wsgi:app"]
