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
- Building and pushing to **GHCR** with `docker/metadata-action` and passing the **digest** forward
- **Reusable workflows** (`workflow_call`) for deployment
- Deploy targets: **a VM over SSH** (Week 3–4 EC2) and **AWS APIs with OIDC**
- Post-deploy **smoke tests**, deployment history and **rollback** workflows
- Workflow **security**: permissions, SHA pinning, script injection, `pull_request_target`

## 🧠 The big idea

A workflow is a **relay race with a clipboard**. Each runner (job) starts on a fresh track (a new VM), does one leg, and writes results on the clipboard (job outputs, artifacts) for the next runner. The most important thing on the clipboard is the **image digest**: every later leg must carry exactly that one, not "whatever `latest` is now".

## ❓ Why does this matter?

In Module 2 your CI proved that code works. Now the pipeline must also **deliver** it: push an image, deploy it to staging, check it's alive, and let you promote the same image to production with one approval — safely, even when strangers open pull requests on your public repo.

## 💥 What happens if we DON'T?

- The deploy job builds the image again → staging and production run different bits.
- `run: ssh deploy@server "docker pull app:latest"` — `latest` changed between staging and production.
- A PR from a fork edits the workflow to print `secrets.DEPLOY_KEY`.
- A deploy is cancelled halfway because a newer commit arrived (`cancel-in-progress: true` on deploys).

## 📖 How it works, step by step

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

- Jobs run on **separate machines**; share data with **outputs** (small strings) and **artifacts** (files).
- A job-level `if` skips the job. When a job listed in `needs` is skipped or fails, its dependents are skipped too — unless their `if` uses a status function like `!cancelled()` or `always()`. Keep conditions simple.

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

Match the **production database engine and major version** — SQLite tests miss PostgreSQL behavior (constraints, JSON, time zones, locking).

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

`GITHUB_TOKEN` with `packages: write` pushes to GHCR — no personal token needed. Pull requests build (to catch Dockerfile errors) but don't push.

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

One implementation, called for staging and production — the only difference is the environment's variables, secrets and protection rules.

### 6. Deploy targets

**A VM with Docker Compose (your EC2 in Week 4)**:

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

On the server, `deploy.sh` pulls the digest, runs the `migrate` service, recreates `api`, waits for health, and records the digest for rollback.

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

- GitHub records deployments per environment (URL, commit, status) — your deployment history.
- Add a manual **rollback** workflow (`workflow_dispatch` with an `image` input) that calls the same `deploy.yml` with a previous digest.
- If smoke tests fail after a production deploy, fail the job loudly; automatic rollback is a good next step once smoke tests are reliable.

### 8. Workflow security

| Risk | Defense |
|---|---|
| Compromised third-party action (e.g. a moved tag) | pin **full commit SHAs** (with version comments); Dependabot/Renovate to update |
| Over-privileged `GITHUB_TOKEN` | `permissions: contents: read` at top; add scopes per job |
| **Script injection** from PR titles, branch names, issue bodies | never `${{ github.event.* }}` inside `run:`; pass via `env:` and quote `"$VAR"` |
| `pull_request_target` running untrusted PR code with secrets | avoid it; never check out the PR head in it |
| Secrets exposed to forks | secrets aren't passed to workflows triggered from forks — don't work around it |
| Leaked credentials in logs | `::add-mask::` for dynamic secrets; prefer OIDC over stored keys |
| Deploys from unreviewed branches | environments with required reviewers and deployment branch rules |

Tools: **actionlint** (syntax and expression errors) and **zizmor** (security audit for workflows) in CI.

## ⚖️ Trade-offs

| Choice | ✅ | ❌ |
|---|---|---|
| Reusable workflows | one deploy implementation | debugging across files; input/secret plumbing |
| Composite actions | reusable steps | can't define jobs/environments |
| SSH deploys to a VM | simple, cheap | key management, less auditable than cloud APIs |
| Cloud-native deploy (ECS/App Runner) | IAM/OIDC, rollbacks, scaling | more AWS concepts and cost |
| GitHub-hosted runners | zero maintenance | minutes limits on private repos; no private network access |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ This shape (verify → build once → deploy staging → approve → production) for any service.
- ✅ Reusable workflows once two environments or two services deploy the same way.
- 🚫 Don't give PR workflows write permissions or deploy secrets.
- 🚫 Don't deploy by tag names like `latest` or branch names — use digests.

## 🏆 Best practices

- [ ] Job graph with explicit `needs`; share the digest through outputs.
- [ ] Integration tests against the production database engine via services.
- [ ] Cache dependencies and Docker layers; keep PR runs fast.
- [ ] Push images only from trusted events; tag with SHA; deploy by digest.
- [ ] One reusable deploy workflow; environments hold config, secrets and approvals.
- [ ] Deploy concurrency groups without cancellation; `timeout-minutes` everywhere.
- [ ] Smoke tests after every deploy; a rollback workflow you've tried once.
- [ ] Least privilege, SHA-pinned actions, no expressions in `run:`, no `pull_request_target` with PR code.
- [ ] Lint workflows (actionlint, zizmor) in CI.

## 🏭 How it's used in industry

- The Docker metadata + build-push + GHCR/ECR pattern is standard for container services on GitHub.
- Organizations publish internal reusable workflows ("golden paths") so every repository deploys the same way.
- High-profile supply-chain incidents involving compromised or retagged GitHub Actions led many companies to require SHA pinning and workflow security scanning.

## ⚠️ Common mistakes

- Using the image **tag** as the job output instead of the digest.
- Service containers with no health options → tests start before PostgreSQL is ready.
- `needs.build.outputs.image` empty because the output wasn't declared at job level.
- Forgetting `packages: write` → "denied: installation not allowed to Create organization package".

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain the relay race with a clipboard, and why the clipboard should carry a digest instead of a tag.

## 📐 Design it

Write the job list (names, triggers, `needs`, permissions, outputs) for a repository with **two services** — RevoShop API (Python) and a Next.js storefront — that deploy independently to staging on main and to production on tags. Include path filters, caching and how you avoid duplicating deploy logic.

:::quiz
Show a possible design

- **Triggers:** PR + push main + tags `api-v*` and `web-v*` (independent releases).
- **changes** job: `dorny/paths-filter` (SHA-pinned) → outputs `api`, `web` booleans (or native `paths` filters in two workflows).
- **api-verify** (`if: needs.changes.outputs.api == 'true'`): pip cache, ruff, pytest on PostgreSQL + Redis services.
- **web-verify**: npm cache, lint, typecheck, Vitest; Playwright against a production build.
- **api-build** / **web-build**: `packages: write` only on non-PR events; outputs `image` digests.
- **deploy-api-staging** / **deploy-web-staging** (`main`): `uses: ./.github/workflows/deploy.yml` with `service`, `environment: staging`, `image`; `id-token: write` only here.
- **deploy-*-production** on `api-v*` / `web-v*` tags with the `production` environment (required reviewers, tag rules).
- **rollback.yml**: `workflow_dispatch` inputs `service`, `environment`, `image` → same reusable workflow.
- Top-level `permissions: contents: read`; concurrency `deploy-${service}-${environment}` without cancellation; SHA-pinned actions; zizmor + actionlint job.
:::

### 📝 Self-review checklist

- [ ] One deploy implementation reused
- [ ] Secrets and OIDC only in deploy jobs
- [ ] Unchanged service isn't rebuilt or redeployed

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m5/w2/02-ci-cd-workflow" ai="no-ai" title="A complete CI/CD workflow"}
Write a `ci-cd.yml` (lint, test on PostgreSQL and Redis, build and push by digest, staging on main, production on tags) and a reusable `deploy.yml` (environment, non-cancelling concurrency, OIDC credentials, deploy script and smoke tests) — with pinned actions, least privilege and no script injection.
:::

:::hints
- YAML reads `on:` as the boolean `True` — the test handles it, but remember it when you debug with Python.
- A job that `uses:` a reusable workflow can't have `steps` or `runs-on`.
- Pass `${{ inputs.image }}` through `env:` and quote `"$IMAGE"` in the script.
:::

## ✅ Quick check

:::quiz
Why can't `deploy-staging` in a reusable-workflow call have a `timeout-minutes`?

Jobs that call reusable workflows only accept a limited set of keys (`needs`, `if`, `with`, `secrets`, `permissions`, `concurrency`, `strategy`); timeouts are set on the jobs inside the called workflow.
:::

:::quiz
A PR from a fork changes `ci-cd.yml` to print `secrets.DEPLOY_SSH_KEY`. What happens with `pull_request` triggers?

Workflows from forks run without repository secrets (and with a read-only token), so the secret isn't available. Using `pull_request_target` and checking out the PR code would break that protection.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Workflow | Alur kerja otomatis |
| Job output | Keluaran job untuk job berikutnya |
| Service container | Kontainer layanan pendukung (DB, Redis) |
| Reusable workflow | Alur kerja yang dapat dipakai ulang |
| Script injection | Injeksi skrip |
| Smoke test | Uji asap (cek cepat pasca-deploy) |

## 📚 Keep learning

- [GitHub docs: Reusing workflows](https://docs.github.com/en/actions/sharing-automations/reusing-workflows) · [Security hardening for GitHub Actions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)
- [Docker docs: GitHub Actions](https://docs.docker.com/build/ci/github-actions/)
- [zizmor](https://docs.zizmor.sh/) · [actionlint](https://github.com/rhysd/actionlint)
