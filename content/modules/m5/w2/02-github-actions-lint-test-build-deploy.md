---
title: "GitHub Actions: Lint → Test → Build → Push → Deploy"
summary: Build a complete GitHub Actions pipeline — job graphs and outputs, service containers, caching, pushing to GHCR by digest, reusable deploy workflows, SSH and AWS deploys, smoke tests, rollbacks and workflow security.
type: lesson
source: original
roles: { be: recommended, fe: recommended, fs: core, ai: recommended, ops: core }
durationMinutes: 180
tags: [github-actions, ci-cd, docker, ghcr, deployment, security]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Designing a **job graph** with `needs`, conditions and **job outputs**
- **Service containers** (PostgreSQL, Redis) for integration tests
- Caching (`setup-python`, Docker `type=gha`), **matrices** and path filters
- Building and pushing to **GHCR** with `docker/metadata-action`, and passing the **digest** forward
- **Reusable workflows** (`workflow_call`) for deployment
- Deploy targets: **a server over SSH** (Week 3–4 EC2) and **AWS APIs with OIDC**
- **Smoke tests** after deploy, deployment history and **rollback** workflows
- Workflow **security**: permissions, SHA pinning, script injection, `pull_request_target`

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Workflow** | A YAML file describing automatic steps GitHub runs for you | Alur kerja otomatis |
| **Job** | One part of a workflow, running on its own fresh machine | Satu bagian pekerjaan |
| **Runner** | The temporary machine GitHub gives a job | Mesin sementara |
| **Job output** | A small piece of text one job passes to the next | Keluaran antar job |
| **Service container** | A helper container (PostgreSQL, Redis) started just for the tests | Kontainer pendukung tes |
| **GHCR** | GitHub Container Registry — where your images are stored | Gudang image GitHub |
| **Reusable workflow** | One workflow file that other workflows call, instead of copy-paste | Alur kerja yang dipakai ulang |
| **OIDC** | Logging in to AWS with a short-lived token instead of stored keys | Login token sesaat |
| **Script injection** | Text written by a stranger ending up inside your shell command | Teks asing masuk ke perintah |
| **Concurrency group** | A rule so two runs of the same thing never overlap | Aturan anti-tumpang-tindih |

## 🧠 The big idea

A workflow is a **relay race with a clipboard**. Each runner (job) starts on a fresh track (a new machine), runs one leg, and writes the result on the clipboard (job outputs, artifacts) for the next runner.

The most important thing on the clipboard is the **image digest**: every later leg must carry exactly that build, not "whatever `latest` happens to be now".

## ❓ Why it matters

In Module 2 your CI proved the code works. Now the pipeline must also **deliver** it: push an image, deploy it to staging, check it's alive, and let you promote that same image to production with one approval — safely, even when strangers open pull requests on your public repo.

Without this care:

- The deploy job builds the image again → staging and production run different code.
- `run: ssh deploy@server "docker pull app:latest"` — and `latest` changed between staging and production.
- A pull request from a fork edits the workflow to print `secrets.DEPLOY_KEY`.
- A deploy is cancelled halfway because a newer commit arrived (`cancel-in-progress: true` on deploys).

## 📖 Step by step

### 1. The job graph

```mermaid
flowchart LR
    lint --> test --> build
    build -->|main| staging["deploy-staging<br/>(reusable workflow)"]
    build -->|tag v*| production["deploy-production<br/>(reusable workflow, approval)"]
```

```yaml
jobs:
  build:
    needs: test
    outputs:
      image: ghcr.io/${{ github.repository }}@${{ steps.build.outputs.digest }}
    steps: [...]
  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/main'
    uses: ./.github/workflows/deploy.yml
    with:
      environment: staging
      image: ${{ needs.build.outputs.image }}
    secrets: inherit
```

- Jobs run on **separate machines**, so nothing is shared automatically: pass small strings with **outputs** and files with **artifacts**.
- A job-level `if` skips the job. If a job in `needs` is skipped or fails, the jobs after it are skipped too — unless their `if` uses `!cancelled()` or `always()`. Keep the conditions simple.

### 2. Integration tests with services

```yaml
test:
  services:
    postgres:
      image: postgres:16-alpine
      env: { POSTGRES_PASSWORD: postgres, POSTGRES_DB: test }
      ports: ["5432:5432"]
      options: >-
        --health-cmd pg_isready --health-interval 5s --health-timeout 3s --health-retries 10
    redis:
      image: redis:8-alpine
      ports: ["6379:6379"]
      options: --health-cmd "redis-cli ping" --health-interval 5s --health-retries 10
  env:
    DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
    REDIS_URL: redis://localhost:6379/0
```

Use the **same database engine and major version as production**. Testing on SQLite is like rehearsing a wedding in your living room: the steps fit, but the real hall behaves differently (constraints, JSON, time zones, locking).

### 3. Speed: caching, matrices, filters

```yaml
- uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
  with: { python-version: "3.12", cache: pip }

strategy:
  fail-fast: false
  matrix:
    python-version: ["3.12", "3.13"]     # libraries: test several versions; apps: test the one you deploy

on:
  pull_request:
    paths-ignore: ["docs/**", "**.md"]
```

### 4. Build and push by digest

```yaml
build:
  permissions: { contents: read, packages: write }
  steps:
    - uses: docker/setup-buildx-action@37fe631027851001ddb9b187196cc803df7f5f0e # v4.3.0
    - uses: docker/login-action@dbcb813823bdd20940b903addbd779551569679f # v4.6.0
      if: github.event_name != 'pull_request'
      with: { registry: ghcr.io, username: "${{ github.actor }}", password: "${{ secrets.GITHUB_TOKEN }}" }
    - id: meta
      uses: docker/metadata-action@dc802804100637a589fabce1cb79ff13a1411302 # v6.2.0
      with:
        images: ghcr.io/${{ github.repository }}
        tags: |
          type=sha
          type=ref,event=branch
          type=semver,pattern={{version}}
    - id: build
      uses: docker/build-push-action@53b7df96c91f9c12dcc8a07bcb9ccacbed38856a # v7.3.0
      with:
        target: prod
        push: ${{ github.event_name != 'pull_request' }}
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

`GITHUB_TOKEN` with `packages: write` is enough to push to GHCR — no personal token needed. Pull requests still build the image (to catch Dockerfile errors) but don't push it.

### 5. A reusable deploy workflow

```yaml
# .github/workflows/deploy.yml
on:
  workflow_call:
    inputs:
      environment: { required: true, type: string }
      image: { required: true, type: string }
permissions:
  contents: read
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    concurrency: { group: "deploy-${{ inputs.environment }}", cancel-in-progress: false }
    timeout-minutes: 20
    steps: [...]
```

One recipe, cooked for staging and for production — only the environment's variables, secrets and approval rules differ. `cancel-in-progress: false` matters here: cancelling a deploy halfway can leave migrations applied but the old code running.

### 6. Deploy targets

**A server with Docker Compose (your EC2 in Week 4)**:

```yaml
- name: Deploy over SSH
  env:
    IMAGE: ${{ inputs.image }}
    SSH_KEY: ${{ secrets.DEPLOY_SSH_KEY }}
    HOST: ${{ vars.DEPLOY_HOST }}
    KNOWN_HOSTS: ${{ vars.DEPLOY_KNOWN_HOSTS }}
  run: |
    install -m 600 /dev/null ~/.ssh/deploy_key && printf '%s\n' "$SSH_KEY" > ~/.ssh/deploy_key
    printf '%s\n' "$KNOWN_HOSTS" >> ~/.ssh/known_hosts          # pin the host key: no "yes" to strangers
    ssh -i ~/.ssh/deploy_key "deploy@$HOST" "API_IMAGE=$IMAGE /opt/revoshop/deploy.sh"
```

Writing `known_hosts` yourself means your pipeline only talks to the server it already knows — like checking the driver's plate number before getting in.

On the server, `deploy.sh` pulls the digest, runs the `migrate` service, recreates `api`, waits for health, and records the digest so you can roll back.

**AWS APIs (ECS, App Runner) with OIDC** — no SSH, no long-lived keys (lesson 04):

```yaml
- uses: aws-actions/configure-aws-credentials@cbe3b392738ccf3f987d68400dafcf4b0624a56c # v6.2.4
  with:
    role-to-assume: ${{ vars.AWS_ROLE_ARN }}
    aws-region: ${{ vars.AWS_REGION }}
```

### 7. Smoke tests, history and rollback

```yaml
- name: Smoke test
  env: { REVOSHOP_URL: "${{ vars.APP_URL }}" }
  run: python -m pytest tests/smoke -q
```

- GitHub records deployments per environment (URL, commit, status) — that's your deployment history.
- Add a manual **rollback** workflow (`workflow_dispatch` with an `image` input) that calls the same `deploy.yml` with an older digest.
- If smoke tests fail after a production deploy, fail the job loudly. Automatic rollback is a good next step once you trust the smoke tests.

### 8. Workflow security

| Risk | Defence |
|---|---|
| A third-party action gets compromised (e.g. a tag moved to new code) | pin **full commit SHAs** with a version comment; let Dependabot/Renovate update them |
| `GITHUB_TOKEN` with too many rights | `permissions: contents: read` at the top; add more only in the job that needs it |
| **Script injection** from PR titles, branch names, issue bodies | never put `${{ github.event.* }}` inside `run:`; pass it via `env:` and quote `"$VAR"` |
| `pull_request_target` running a stranger's code with your secrets | avoid it; never check out the PR's own code in it |
| Secrets reaching forks | GitHub doesn't give secrets to fork workflows — don't try to work around that |
| Credentials printed in logs | `::add-mask::` for values you create at runtime; prefer OIDC over stored keys |
| Deploys from unreviewed branches | environments with required reviewers and branch/tag rules |

Tools: **actionlint** (syntax and expression mistakes) and **zizmor** (security review of workflows) in CI.

### Choosing your setup

- ✅ This shape — verify → build once → deploy staging → approve → production — fits almost any service.
- ✅ Move deploy steps into a reusable workflow as soon as two environments or two services deploy the same way.
- 🚫 Never give pull request workflows write permissions or deploy secrets.
- 🚫 Never deploy by `latest` or a branch name — deploy digests.
- SSH to a server is simple and cheap but you manage keys; cloud-native deploys (ECS/App Runner) give IAM, rollbacks and scaling but add AWS concepts and cost.

## ⚠️ Common mistakes

- Using the image **tag** as the job output instead of the digest.
- Service containers without health options → tests start before PostgreSQL is ready.
- `needs.build.outputs.image` is empty because the output wasn't declared at job level.
- Forgetting `packages: write` → "denied: installation not allowed to Create organization package".

## 🏆 Best practices

- [ ] A job graph with explicit `needs`; pass the digest through outputs.
- [ ] Integration tests against the production database engine, using services.
- [ ] Cache dependencies and Docker layers; keep PR runs fast.
- [ ] Push images only from trusted events; tag with the SHA; deploy by digest.
- [ ] One reusable deploy workflow; environments hold config, secrets and approvals.
- [ ] Deploy concurrency groups that don't cancel; `timeout-minutes` on every job.
- [ ] Smoke tests after every deploy; a rollback workflow you have actually tried once.
- [ ] Least privilege, SHA-pinned actions, no expressions inside `run:`, no `pull_request_target` with PR code.
- [ ] Lint the workflows themselves (actionlint, zizmor) in CI.

:::revoshop
1. **SQLite vs PostgreSQL.** `tests/conftest.py` sets `os.environ['DATABASE_URL'] = 'sqlite:///:memory:'` and uses `db.create_all()`. So your 467 tests never exercise **Alembic migrations** or PostgreSQL constraints (the test output even prints your `ck_payments_status_valid` CHECK constraint DDL for SQLite). Design a separate CI job that starts a `postgres:16-alpine` service, runs `flask db upgrade` from an empty database, and then boots the app against it.
2. **Lint.** You already have `.pylintrc` and `pylint` in `requirements-dev.txt`. Run `pylint app config` locally. Will CI fail on warnings from day one, or will you start with `--fail-under` and raise it over time?
3. **What gets built.** In CI the `build` job should use the `prod` target from lesson W1·05. Which job outputs does the deploy job need (hint: the digest), and what should happen on a pull request?
4. **An end-to-end job.** Your `compose.prod.yaml` from W1·05 can run inside a GitHub runner: generate throwaway secrets, `docker compose … up -d --build --wait`, then run the smoke tests with `REVOSHOP_URL=http://localhost:8080`. Where in the job graph does that belong, and how long can you afford it to take?
5. **Deploy target.** You have no server yet (that's Week 3–4). Design `deploy-staging` now but guard it with `if: vars.STAGING_ENABLED == 'true'` so the pipeline stays green until the server exists.
:::

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain the relay race with a clipboard, and why the clipboard should carry a digest instead of a tag.

## 📐 Design it

Write the job list (names, triggers, `needs`, permissions, outputs) for a repository with **two services** — the RevoShop API (Python) and a Next.js storefront — that deploy independently to staging on main and to production on tags. Include path filters, caching and how you avoid duplicating the deploy logic.

:::quiz
Show a possible design

- **Triggers:** PR + push to main + tags `api-v*` and `web-v*` (independent releases).
- **changes** job: `dorny/paths-filter` (SHA-pinned) → outputs `api`, `web` booleans (or native `paths` filters in two workflows).
- **api-verify** (`if: needs.changes.outputs.api == 'true'`): pip cache, ruff, pytest on PostgreSQL + Redis services.
- **web-verify**: npm cache, lint, typecheck, Vitest; Playwright against a production build.
- **api-build** / **web-build**: `packages: write` only on non-PR events; each outputs its `image` digest.
- **deploy-api-staging** / **deploy-web-staging** (`main`): `uses: ./.github/workflows/deploy.yml` with `service`, `environment: staging`, `image`; `id-token: write` only here.
- **deploy-*-production** on `api-v*` / `web-v*` tags with the `production` environment (required reviewers, tag rules).
- **rollback.yml**: `workflow_dispatch` with inputs `service`, `environment`, `image` → the same reusable workflow.
- Top-level `permissions: contents: read`; concurrency `deploy-${service}-${environment}` without cancellation; SHA-pinned actions; a zizmor + actionlint job.
:::

### 📝 Self-review checklist

- [ ] One deploy implementation, reused
- [ ] Secrets and OIDC only in deploy jobs
- [ ] An unchanged service isn't rebuilt or redeployed

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m5/w2/02-ci-cd-workflow" ai="no-ai" title="A complete CI/CD workflow"}
Write a `ci-cd.yml` (lint, test on PostgreSQL and Redis, build and push by digest, staging on main, production on tags) and a reusable `deploy.yml` (environment, non-cancelling concurrency, OIDC credentials, deploy script and smoke tests) — with pinned actions, least privilege and no script injection.
:::

:::hints
- YAML reads `on:` as the boolean `True` — the test handles it, but remember it when you debug with Python.
- A job that `uses:` a reusable workflow can't also have `steps` or `runs-on`.
- Pass `${{ inputs.image }}` through `env:` and quote `"$IMAGE"` in the script.
:::

## ✅ Quick check

:::quiz
Why can't the `deploy-staging` job that calls a reusable workflow have its own `timeout-minutes`?

A job that calls a reusable workflow only accepts a few keys (`needs`, `if`, `with`, `secrets`, `permissions`, `concurrency`, `strategy`). Timeouts belong to the jobs inside the called workflow.
:::

:::quiz
A pull request from a fork changes `ci-cd.yml` to print `secrets.DEPLOY_SSH_KEY`. What happens with a `pull_request` trigger?

Fork workflows run without your repository secrets and with a read-only token, so the secret simply isn't there. Using `pull_request_target` and checking out the PR's code would break that protection.
:::

## 📚 Keep learning

- [GitHub docs: Reusing workflows](https://docs.github.com/en/actions/sharing-automations/reusing-workflows) · [Security hardening for GitHub Actions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)
- [Docker docs: GitHub Actions](https://docs.docker.com/build/ci/github-actions/)
- [zizmor](https://docs.zizmor.sh/) · [actionlint](https://github.com/rhysd/actionlint)
