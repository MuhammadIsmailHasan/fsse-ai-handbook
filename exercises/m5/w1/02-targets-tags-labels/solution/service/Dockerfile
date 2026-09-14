# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.13

# ---------- base: shared settings ----------
FROM python:${PYTHON_VERSION}-slim AS base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:0.11.29 /uv /bin/uv

# ---------- deps: production dependencies only (cached until the lock changes) ----------
FROM base AS deps
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-install-project

# ---------- dev: + dev dependencies, code mounted by compose ----------
FROM deps AS dev
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project
CMD ["uv", "run", "flask", "--app", "app:create_app", "run", "--debug", "--host", "0.0.0.0", "--port", "5091"]

# ---------- test: the build fails if the tests fail ----------
FROM dev AS test
COPY . .
RUN uv run python -m pytest -q tests/check_smoke.py

# ---------- prod: clean image, no uv, no dev deps ----------
FROM base AS prod
ARG VERSION=dev
ARG REVISION=unknown
LABEL org.opencontainers.image.title="careerpilot-api" \
      org.opencontainers.image.version=$VERSION \
      org.opencontainers.image.revision=$REVISION \
      org.opencontainers.image.source="https://github.com/<you>/careerpilot"
RUN rm /bin/uv \
    && groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app
ENV PATH="/app/.venv/bin:$PATH" \
    PORT=5091
COPY --from=deps --chown=app:app /app/.venv /app/.venv
COPY --chown=app:app . .
USER 10001
EXPOSE 5091
HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5091/health/live', timeout=2)"]
CMD ["gunicorn", "-c", "gunicorn.conf.py", "--no-control-socket", "wsgi:app"]
