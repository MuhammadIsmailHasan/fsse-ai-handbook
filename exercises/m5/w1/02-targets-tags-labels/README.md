# M5 · W1 · 02 — One Dockerfile, three targets · image tags & labels

> 🚫🤖 **No-AI** · ⏱️ ~2 h

In Module 2 you built a production image. Real teams build **several images from one Dockerfile** (dev, test, prod), tag them so every deployment is traceable to a commit, and label them with metadata. Do both.

## 1. `service/Dockerfile` with targets
Stages (names exactly):

| Stage | From | Must |
|---|---|---|
| `base` | `python:${PYTHON_VERSION}-slim` with `ARG PYTHON_VERSION=3.13` declared **before** the first `FROM` | set `PYTHONUNBUFFERED=1`, `PYTHONDONTWRITEBYTECODE=1`, `WORKDIR /app`; copy `uv` from `ghcr.io/astral-sh/uv:<pinned version>` |
| `deps` | `base` | copy **only** `pyproject.toml uv.lock`; `uv sync --locked --no-dev --no-install-project` with a **cache mount** on `/root/.cache/uv` |
| `dev` | `deps` | `uv sync --locked` (with dev deps, cache mount); `CMD ["uv", "run", "flask", "--app", "app:create_app", "run", "--debug", "--host", "0.0.0.0", "--port", "5091"]` |
| `test` | `dev` | `COPY . .` then `RUN uv run python -m pytest -q tests/check_smoke.py` (`python -m` puts `/app` on the import path) (the build **fails** if tests fail; the file isn't named `test_*.py` so the handbook's own pytest run skips it) |
| `prod` | `base` (clean) | copy `/app/.venv` from `deps` and the source (`COPY --chown=app:app . .`); non-root user with **numeric uid 10001**; `PATH` includes `/app/.venv/bin`; `EXPOSE 5091`; `HEALTHCHECK` on `/health/live`; exec-form `CMD` running gunicorn; OCI labels (below) |

`prod` must **not** contain uv, pytest or dev dependencies, and must be the **last** stage (so `docker build .` without `--target` builds prod).

OCI labels in `prod`, from build args `VERSION` and `REVISION` (declared in that stage):
`org.opencontainers.image.title="careerpilot-api"`, `org.opencontainers.image.version=$VERSION`, `org.opencontainers.image.revision=$REVISION`, `org.opencontainers.image.source="https://github.com/<you>/careerpilot"`.

## 2. `image_meta.py` — tags like a CI pipeline would compute
`image_tags(image, *, ref, sha, default_branch="main") -> list[str]` where `ref` is a Git ref (`refs/heads/main`, `refs/heads/feat/Login-Page`, `refs/tags/v1.4.2`, `refs/pull/42/merge`):
- always `image:sha-<first 7 chars of sha>`
- branch → `image:<branch>` sanitized: lower-case, anything not `[a-z0-9._-]` becomes `-`, trimmed of leading/trailing `-`/`.`, max 128 chars; the **default branch** also gets `image:edge`
- tag `vMAJOR.MINOR.PATCH` → `image:MAJOR.MINOR.PATCH`, `image:MAJOR.MINOR`, `image:MAJOR` and `image:latest`; **pre-releases** (`v2.0.0-rc.1`) get only the full version (`image:2.0.0-rc.1`), never `latest`/`MAJOR`
- pull request → `image:pr-<number>`
- other refs → only the sha tag
- `sha` must be 40 hex characters, else `ValueError`; result has no duplicates and is sorted

`oci_labels(*, title, source, version, revision, created) -> dict[str, str]` → the five `org.opencontainers.image.*` keys `title, source, version, revision, created` (`created` is a `datetime`, formatted RFC 3339 UTC like `2026-09-15T08:30:00Z`).

```bash
cd exercises
uv run pytest m5/w1/02-targets-tags-labels
RUN_DOCKER_TESTS=1 uv run pytest m5/w1/02-targets-tags-labels    # also builds test and prod targets (slow)
```
