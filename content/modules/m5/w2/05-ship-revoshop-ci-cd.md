---
title: "🚀 Ship RevoShop 2: CI/CD Pipeline"
summary: Put RevoShop behind a real pipeline — a green, fast test suite, lint, migrations checked on PostgreSQL, the production stack smoke-tested in CI, images on GHCR by digest, protected branches and a deploy job ready for AWS.
type: project
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: core }
durationMinutes: 480
tags: [revoshop, ci-cd, github-actions, ghcr, testing, project]
---

## 🎯 Goal

After Lab 1, RevoShop *can* run in production mode. After this lab, **every change has to prove it**: nothing merges without green checks, every commit on `main` produces an image in GHCR, and a deploy job sits ready, waiting only for the server you'll create in Week 3–4.

Think of it as hiring a quality inspector who never gets tired: the same checks run on every change, in the same order, without you remembering them.

```text
Before                                          After this lab
────────────────────────────────────────────    ────────────────────────────────────────────────────
no .github/workflows                            ci-cd.yml + deploy.yml (reusable)
5 tests fail in a clean checkout                green suite, decisions documented
~7.5 min test run (bcrypt cost 12 per user)     seconds (bcrypt cost 4 in tests only)
SQLite tests only, migrations never tested       Alembic upgrade → downgrade → upgrade on PostgreSQL 16
"works on my machine"                           compose.prod.yaml stack + smoke tests inside CI
images built on the server                      ghcr.io/<you>/revoshop@sha256:… per commit on main
anyone can push to main                         rulesets: PR + required checks; environments ready
```

## 🔤 Key words

| Word | In simple words |
|---|---|
| **Pipeline job** | One part of the workflow that runs on its own fresh machine (lint, test, build…) |
| **bcrypt cost** | How much work password hashing does; high is safe for production, slow for tests |
| **Migration check** | Proving the database scripts can run forward, backward and forward again |
| **Service container** | A helper container (PostgreSQL) started only for that job |
| **Digest** | An image's fingerprint (`sha256:…`), so the deploy uses exactly the tested build |
| **Ruleset** | GitHub rules for a branch: require a PR, require green checks, block force pushes |
| **Dependabot** | A bot that opens PRs to update pinned actions, packages and base images |
| **Smoke test** | A few quick checks against a running app to prove a deploy works |

:::note[Prerequisites]
Lab 1 merged in your **personal** copy of RevoShop (Dockerfile targets, `gunicorn.conf.py`, `compose.prod.yaml`, Caddyfile, liveness endpoint, rate limiter). Work on a new branch: `git switch -c ci/pipeline`.
:::

## 🧭 Checkpoints

### C1 · Make the tests fast (45 min)

Every test user's password is hashed with bcrypt's default cost (`bcrypt.gensalt()` in `app/auth.py`). Strong hashing is deliberately slow — that's the point in production, and a disaster when you do it 467 times in a test run. It's like using a bank vault door for a storage box you open a hundred times a day.

```python
# app/auth.py
import os

import bcrypt


def hash_password(plain_password):
    rounds = int(os.getenv('BCRYPT_ROUNDS', '12'))
    return bcrypt.hashpw(str(plain_password).encode('utf-8'), bcrypt.gensalt(rounds=rounds)).decode('utf-8')
```

```python
# tests/conftest.py — at the very top, before importing the app
import os

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ.setdefault('BCRYPT_ROUNDS', '4')   # fast hashing in tests only
```

Measure before and after with `time python -m pytest -q`. On a clean copy of RevoShop this took the suite from **7 min 27 s to 9 s**, with identical results. Put your own numbers in the PR description — that's your first measurable pipeline improvement.

Then guard production: add a test proving `hash_password` uses cost 12 when `BCRYPT_ROUNDS` isn't set (bcrypt hashes start with `$2b$12$`), and never set `BCRYPT_ROUNDS` in `compose.prod.yaml`. A speed-up that quietly weakens production passwords would be a bad trade.

### C2 · Make the suite green (1 h)

In a clean checkout these fail:

```text
tests/integration/test_cart.py::TestCartAvailabilityIsLive::test_cancel_restores_cart_item_availability
tests/integration/test_categories.py::TestGetCategories::test_get_categories_with_products_no_auth
tests/integration/test_categories.py::TestGetCategories::test_get_categories_no_auth
tests/integration/test_product_images.py::TestListProductImages::test_list_no_auth
tests/integration/test_products.py::TestGetProducts::test_get_products_no_auth
```

1. **Four `*_no_auth` tests** expect `401`, but those listing endpoints return `200` without a token. For a shop, browsing products and categories without logging in is normal — a customer shouldn't need a membership card to look at the shelves. So decide on purpose: if public is intended, rename them to `test_*_is_public` expecting `200`, and add tests proving the **write** endpoints (`POST /products/`, `DELETE /categories/<id>`, …) still return `401` without a token. Record the decision in the PR.
2. **The cart availability test**: run it alone (`-k test_cancel_restores_cart_item_availability -vv`), then inside its own file, then with the whole suite. Does it fail alone? If it only fails with the others, the tests are sharing state. Read the `OrderService` cancellation code and how cart `available` is computed, then fix the bug or the test — don't skip it without an issue explaining why.
3. Commit when `python -m pytest -q` is fully green locally **without** your `.env` loaded (`env -u JWT_SECRET_KEY -u DATABASE_URL python -m pytest -q`), because CI won't have it.

### C3 · Smoke tests live in the repo (15 min)

Copy the smoke tests from the handbook (`exercises/m5/w1/05-revoshop-smoke/test_revoshop_smoke.py`) to `tests/smoke/test_smoke.py`. They **skip** themselves when `REVOSHOP_URL` isn't set, so your normal test run doesn't change.

### C4 · The workflows (2 h)

**`.github/workflows/ci-cd.yml`**

```yaml
name: CI/CD

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]
    tags: ["v*.*.*"]
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

jobs:
  lint:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
        with:
          python-version: "3.12"
          cache: pip
      - run: pip install -r requirements-dev.txt
      - name: Pylint
        run: pylint app config --fail-under=9.5

  test:
    needs: lint
    runs-on: ubuntu-latest
    timeout-minutes: 15
    env:
      BCRYPT_ROUNDS: "4"
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
        with:
          python-version: "3.12"
          cache: pip
      - run: pip install -r requirements-dev.txt
      - name: Unit and API tests
        run: python -m pytest -q --cov=app --cov-report=xml --junitxml=reports/junit.xml
      - uses: actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7.0.1
        if: always()
        with:
          name: test-reports
          path: |
            reports/
            coverage.xml
          retention-days: 7

  migrations:
    needs: lint
    runs-on: ubuntu-latest
    timeout-minutes: 10
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: revoshop
        ports: ["5432:5432"]
        options: >-
          --health-cmd pg_isready
          --health-interval 5s
          --health-timeout 3s
          --health-retries 10
    env:
      APP_ENV: development
      FLASK_APP: run:application
      DATABASE_URL: postgresql://postgres:postgres@localhost:5432/revoshop
      LOG_TO_FILE: "false"
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
        with:
          python-version: "3.12"
          cache: pip
      - run: pip install -r requirements.txt
      - name: Upgrade, downgrade and upgrade again on PostgreSQL
        run: |
          flask db upgrade
          flask db downgrade base
          flask db upgrade
          flask db check   # fails if models and migrations disagree

  e2e:
    needs: [test, migrations]
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
        with:
          python-version: "3.12"
      - name: Throwaway secrets for this run
        run: |
          {
            echo "POSTGRES_PASSWORD=$(openssl rand -hex 16)"
            echo "JWT_SECRET_KEY=$(openssl rand -hex 32)"
            echo "HTTP_PORT=8080"
            echo "HTTPS_PORT=8443"
          } > .env.ci
      - name: Start the production stack
        run: docker compose --env-file .env.ci -f compose.prod.yaml up -d --build
      - name: Wait until healthy
        run: |
          for attempt in $(seq 1 60); do
            if curl -fsS http://localhost:8080/api/v1/health; then exit 0; fi
            sleep 3
          done
          docker compose --env-file .env.ci -f compose.prod.yaml logs
          exit 1
      - name: Smoke tests
        env:
          REVOSHOP_URL: http://localhost:8080
        run: |
          pip install pytest
          python -m pytest tests/smoke -v
      - name: Logs on failure
        if: failure()
        run: docker compose --env-file .env.ci -f compose.prod.yaml logs --no-color

  build:
    needs: [test, migrations]
    runs-on: ubuntu-latest
    timeout-minutes: 20
    permissions:
      contents: read
      packages: write
    outputs:
      image: ghcr.io/${{ github.repository }}@${{ steps.build.outputs.digest }}
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: docker/setup-buildx-action@37fe631027851001ddb9b187196cc803df7f5f0e # v4.3.0
      - uses: docker/login-action@dbcb813823bdd20940b903addbd779551569679f # v4.6.0
        if: github.event_name != 'pull_request'
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: meta
        uses: docker/metadata-action@dc802804100637a589fabce1cb79ff13a1411302 # v6.2.0
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=sha
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
      - id: build
        uses: docker/build-push-action@53b7df96c91f9c12dcc8a07bcb9ccacbed38856a # v7.3.0
        with:
          context: .
          target: prod
          platforms: linux/amd64
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          build-args: |
            VERSION=${{ steps.meta.outputs.version }}
            REVISION=${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-staging:
    needs: [build, e2e]
    if: github.ref == 'refs/heads/main' && vars.STAGING_ENABLED == 'true'
    uses: ./.github/workflows/deploy.yml
    with:
      environment: staging
      image: ${{ needs.build.outputs.image }}
    secrets: inherit
    permissions:
      contents: read
      id-token: write

  deploy-production:
    needs: [build, e2e]
    if: startsWith(github.ref, 'refs/tags/v') && vars.PRODUCTION_ENABLED == 'true'
    uses: ./.github/workflows/deploy.yml
    with:
      environment: production
      image: ${{ needs.build.outputs.image }}
    secrets: inherit
    permissions:
      contents: read
      id-token: write
```

- `platforms: linux/amd64` because GitHub's runners and a `t3` EC2 instance are x86. If you choose Graviton (`t4g`) in Week 3, change it to `linux/arm64`.
- On a clean copy of RevoShop, upgrade → `downgrade base` → upgrade → `flask db check` all pass on PostgreSQL 16 (`No new upgrade operations detected`). If a future model change forgets its migration, `flask db check` fails — that's the point.
- `pylint --fail-under=9.5`: a clean copy of RevoShop scores **9.77/10** today, so 9.5 catches regressions without blocking you; raise it as you fix warnings.

**`.github/workflows/deploy.yml`** — ready for Week 4 (EC2 over SSH); disabled until you set `STAGING_ENABLED=true`:

```yaml
name: Deploy

on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
      image:
        required: true
        type: string

permissions:
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    environment: ${{ inputs.environment }}
    concurrency:
      group: deploy-${{ inputs.environment }}
      cancel-in-progress: false
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - name: Deploy over SSH
        env:
          IMAGE: ${{ inputs.image }}
          SSH_KEY: ${{ secrets.DEPLOY_SSH_KEY }}
          HOST: ${{ vars.DEPLOY_HOST }}
          KNOWN_HOSTS: ${{ vars.DEPLOY_KNOWN_HOSTS }}
        run: |
          mkdir -p ~/.ssh
          install -m 600 /dev/null ~/.ssh/deploy_key
          printf '%s\n' "$SSH_KEY" > ~/.ssh/deploy_key
          printf '%s\n' "$KNOWN_HOSTS" >> ~/.ssh/known_hosts
          ssh -i ~/.ssh/deploy_key "deploy@$HOST" "API_IMAGE=$IMAGE /opt/revoshop/deploy.sh"
      - uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
        with:
          python-version: "3.12"
      - name: Smoke tests
        env:
          REVOSHOP_URL: ${{ vars.APP_URL }}
          REVOSHOP_EXPECT_HTTPS: "1"
        run: |
          pip install pytest
          python -m pytest tests/smoke -v
```

`/opt/revoshop/deploy.sh` on the server, and the SSH/OIDC setup, come in Week 4. Because the deploy steps live in one reusable file, moving to ECS later changes only this file — not the whole pipeline.

### C5 · Repository settings (45 min)

In your personal repository on GitHub:

1. **Settings → Rules → Rulesets → New branch ruleset** for `main`: require a pull request (1 approval is optional when solo — at least require the PR), require status checks `lint`, `test`, `migrations`, `e2e`, `build`, block force pushes and deletions.
2. **Settings → Environments**: create `staging` (deployment branch: `main`) and `production` (deployment tags: `v*`; required reviewers if your plan allows). Add variables `STAGING_ENABLED=false` / `PRODUCTION_ENABLED=false` at repository level for now.
3. **Settings → Code security**: enable secret scanning and push protection (free for public repos; check what your plan offers for private).
4. **`.github/dependabot.yml`** so pinned SHAs and base images don't rot:

```yaml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule: { interval: weekly }
  - package-ecosystem: pip
    directory: /
    schedule: { interval: weekly }
  - package-ecosystem: docker
    directory: /
    schedule: { interval: weekly }
```

5. **Settings → Actions → General → Workflow permissions**: "Read repository contents and packages permissions" (your workflows add what they need).

### C6 · Prove the pipeline (45 min)

- Open the PR `ci/pipeline` → all checks green; download the `test-reports` artifact.
- Break something on purpose in a throwaway branch (change a migration's column type, or return `500` from `/api/v1/health/live`) and confirm the *right* job fails. A pipeline you've never seen fail is a smoke alarm you've never tested.
- Merge → a `sha-…` image appears under **Packages** in your profile/repository. Pull it on your laptop: `docker pull ghcr.io/<you>/revoshop@sha256:…` (log in with a PAT with `read:packages` if the package is private).
- Record in `docs/pipeline.md`: job durations, total PR feedback time, and the DORA baseline you wrote in lesson 01.

## ✅ Done when

- [ ] Test suite green in a clean checkout and running in seconds; bcrypt cost 12 still enforced outside tests
- [ ] `ci-cd.yml` + `deploy.yml` merged; PR checks required by a ruleset
- [ ] Migrations verified upgrade → downgrade → upgrade on PostgreSQL 16
- [ ] The production Compose stack starts in CI and smoke tests pass
- [ ] Images on GHCR tagged `sha-*` and `main`, referenced by digest in job outputs
- [ ] `staging` and `production` environments created; deploy jobs guarded until Week 4
- [ ] Dependabot, secret scanning and least-privilege workflow permissions enabled

## 🧠 AI policy

🤖✅ AI may help with YAML syntax errors and GitHub settings navigation. 🚫🤖 Diagnose and fix the failing tests yourself, and be able to explain every job, condition and permission.

## ❓ Questions an interviewer might ask

- Your tests took 7.5 minutes. How did you find the cause, and how do you make sure production still uses a strong bcrypt cost?
- Four tests expected `401` on public endpoints. How did you decide whether the code or the tests were wrong?
- Why test migrations separately on PostgreSQL when the suite already passes on SQLite?
- What does the `e2e` job prove that unit tests can't?
- Why does the deploy job receive an image **digest**, and what would go wrong with `latest`?

## 📣 Share it

:::linkedin{type="weekly"}
⚙️ Module 5 · Week 2: my RevoShop API now has a real CI/CD pipeline.

The part I'm proudest of: the test suite went from 7 min 27 s to 9 s. The cause was bcrypt hashing every test user at production cost — now tests use a low cost, production still uses 12 (and a test proves it).

Also:
- fixed 5 tests that had been failing unnoticed (4 expected 401 on endpoints that are intentionally public)
- migrations checked upgrade → downgrade → upgrade on PostgreSQL 16
- the full production stack (Caddy, gunicorn, PostgreSQL, Redis) boots inside CI and smoke tests hit it
- images pushed to GHCR by digest, actions pinned to commit SHAs, branch rules requiring green checks

Next: AWS. ☁️

#GitHubActions #CICD #Python #DevOps #LearningInPublic
:::
