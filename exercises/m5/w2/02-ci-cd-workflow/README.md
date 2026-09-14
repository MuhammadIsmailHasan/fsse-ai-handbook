# M5 · W2 · 02 — A complete CI/CD workflow

> 🚫🤖 **No-AI** · ⏱️ ~2.5 h

In Module 2 you wrote a CI workflow (lint, test, build). Now write the full path to production for a Flask API that uses `requirements.txt` / `requirements-dev.txt` (like RevoShop): **lint → test on PostgreSQL + Redis → build & push an image once → deploy that same image to staging → deploy to production with approval**. The tests parse your YAML.

Pinned actions you may use (all must be pinned to a **full commit SHA** with a version comment):

| Action | SHA | Version |
|---|---|---|
| actions/checkout | `3d3c42e5aac5ba805825da76410c181273ba90b1` | v7.0.1 |
| actions/setup-python | `5fda3b95a4ea91299a34e894583c3862153e4b97` | v7.0.0 |
| actions/upload-artifact | `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` | v7.0.1 |
| docker/setup-buildx-action | `37fe631027851001ddb9b187196cc803df7f5f0e` | v4.3.0 |
| docker/login-action | `dbcb813823bdd20940b903addbd779551569679f` | v4.6.0 |
| docker/metadata-action | `dc802804100637a589fabce1cb79ff13a1411302` | v6.2.0 |
| docker/build-push-action | `53b7df96c91f9c12dcc8a07bcb9ccacbed38856a` | v7.3.0 |
| aws-actions/configure-aws-credentials | `cbe3b392738ccf3f987d68400dafcf4b0624a56c` | v6.2.4 |

## `workflows/ci-cd.yml`
- **Triggers:** `pull_request` to `main`; `push` to `main` and tags matching `v*.*.*`; `workflow_dispatch`
- **Top-level** `permissions: contents: read`
- **Concurrency:** group `${{ github.workflow }}-${{ github.ref }}`, `cancel-in-progress: ${{ github.event_name == 'pull_request' }}` (never cancel a running deploy of main)
- **Every job** that has steps: `runs-on: ubuntu-latest` and `timeout-minutes`
- **Every checkout** uses `persist-credentials: false`
- **No `${{ … }}` expressions inside `run:` scripts** — pass values through `env:` (prevents script injection)

| Job | Requirements |
|---|---|
| `lint` | checkout · setup-python `3.12` with `cache: pip` · `pip install -r requirements-dev.txt` · a step running `ruff check .` |
| `test` | `needs: lint` · services `postgres` (`postgres:16-alpine`, `POSTGRES_PASSWORD: postgres`, `POSTGRES_DB: test`, port `5432:5432`, `--health-cmd pg_isready` options) and `redis` (`redis:8-alpine`, port `6379:6379`, `--health-cmd "redis-cli ping"`) · job `env` `DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test` and `REDIS_URL: redis://localhost:6379/0` · run `python -m pytest --junitxml=reports/junit.xml` · upload `reports/` with `if: always()` |
| `build` | `needs: test` · job permissions `contents: read`, `packages: write` · setup-buildx · login to `ghcr.io` with `${{ github.actor }}` / `${{ secrets.GITHUB_TOKEN }}` **only when not a pull request** · metadata-action (id `meta`) with `images: ghcr.io/${{ github.repository }}` and tags `type=sha`, `type=ref,event=branch`, `type=ref,event=pr`, `type=semver,pattern={{version}}`, `type=semver,pattern={{major}}.{{minor}}` · build-push-action (id `build`) with `target: prod`, `push: ${{ github.event_name != 'pull_request' }}`, tags and labels from `meta`, GitHub Actions cache (`type=gha`, `mode=max` on write) · job **output** `image` = `ghcr.io/${{ github.repository }}@${{ steps.build.outputs.digest }}` |
| `deploy-staging` | `needs: build` · only `if: github.ref == 'refs/heads/main'` · calls `./.github/workflows/deploy.yml` with `environment: staging`, `image: ${{ needs.build.outputs.image }}` · `secrets: inherit` · permissions `contents: read`, `id-token: write` |
| `deploy-production` | `needs: build` · only for tags: `if: startsWith(github.ref, 'refs/tags/v')` · same reusable workflow with `environment: production` |

## `workflows/deploy.yml` — reusable
- `on: workflow_call` with **required** string inputs `environment` and `image`
- top-level `permissions: contents: read`
- one job `deploy`: `environment: ${{ inputs.environment }}` (approvals and environment secrets live there), concurrency group `deploy-${{ inputs.environment }}` **without** cancelling, `timeout-minutes`, permissions `contents: read` + `id-token: write`
- steps: checkout · `aws-actions/configure-aws-credentials` with `role-to-assume: ${{ vars.AWS_ROLE_ARN }}` and `aws-region: ${{ vars.AWS_REGION }}` (**OIDC — no access keys**) · a step with `env: IMAGE: ${{ inputs.image }}` running `./scripts/deploy.sh "$IMAGE"` · a smoke test step with `env: REVOSHOP_URL: ${{ vars.APP_URL }}` running `python -m pytest tests/smoke`
- **no** `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` anywhere

```bash
cd exercises
uv run pytest m5/w2/02-ci-cd-workflow
```
