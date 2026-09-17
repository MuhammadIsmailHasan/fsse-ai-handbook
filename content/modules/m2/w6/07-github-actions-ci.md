---
title: "🔥 CI with GitHub Actions"
summary: Make every push prove itself — a GitHub Actions pipeline that lints, type-checks and tests against real PostgreSQL, builds the Docker image, reports results clearly, and is fast, cheap and secure.
type: lesson
source: original
roles: { be: core, fe: core, fs: core, ai: recommended, ops: core }
durationMinutes: 180
tags: [ci, github-actions, automation, testing, supply-chain-security, devops]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- **CI** vs **CD**, and what a good pipeline checks
- GitHub Actions anatomy: workflows, events, jobs, steps, runners, actions
- Service containers (PostgreSQL), matrices, caching, job dependencies, conditions
- Job summaries and annotations: failures you can read in 10 seconds
- **Security**: least-privilege tokens, SHA-pinned actions, secrets, `pull_request_target` dangers
- Branch protection: CI as a **merge gate**

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **CI** | Automatic checks on every push and pull request | Pemeriksaan otomatis |
| **CD** | Automatically delivering or deploying what passed | Pengiriman otomatis |
| **Workflow** | A YAML file describing those automatic steps | Berkas alur otomatis |
| **Job** | One part of the workflow, on its own clean machine | Satu bagian pekerjaan |
| **Runner** | The machine GitHub gives that job | Mesin penjalan |
| **Action** | A reusable step written by someone else | Langkah siap pakai |
| **Service container** | A helper container (PostgreSQL) started for the tests | Kontainer pendukung tes |
| **Cache** | Reusing downloaded dependencies between runs | Penyimpanan sementara |
| **SHA pinning** | Locking an action to one exact commit, for safety | Mengunci versi action |
| **Merge gate** | The rule that a PR can't merge until checks pass | Syarat sebelum merge |

## 🧠 The big idea

CI is an **airport security checkpoint** for code. Every bag (commit) goes through the same scanner — lint, types, tests, build — no matter who packed it or how confident they are. If the scanner beeps, the bag doesn't board (merge).

The checkpoint is automatic, identical for everyone, and never gets tired at 11 p.m. on a Friday.

## ❓ Why it matters

- "Works on my machine" — CI runs on a **clean** machine with **locked** dependencies.
- People forget to run tests before pushing, especially close to a deadline.
- Reviewers should be reading design and logic, not formatting or checking whether tests pass.
- Deploying automatically is only safe when CI can be trusted.
- AI-generated pull requests need automated checking even more.

Without it:

- `main` breaks on Monday, and three people spend the morning finding which merge did it.
- Tests pass locally on SQLite and fail in production on PostgreSQL (lesson 02).
- A dependency released a new version overnight, and nobody notices until the deploy.
- A workflow uses `some-org/cool-action@main`; its author — or an attacker who took the account — pushes code that steals your repository secrets.

## 📖 Step by step

### 1. Anatomy

```mermaid
flowchart LR
    E["Event<br/>push / pull_request"] --> W["Workflow<br/>.github/workflows/ci.yml"]
    W --> L["Job: lint<br/>(runner VM)"]
    W --> T["Job: test × matrix<br/>(runner VM + Postgres)"]
    L & T --> B["Job: build<br/>needs: [lint, test]"]
```

- **Workflow**: a YAML file in `.github/workflows/`.
- **Event** (`on:`): push, pull_request, schedule, workflow_dispatch (manual button), release…
- **Job**: runs on a fresh **runner** VM; jobs run **in parallel** unless connected with `needs`.
- **Step**: a shell command (`run:`) or a reusable **action** (`uses:`).

### 2. A complete pipeline

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read                      # least privilege for GITHUB_TOKEN

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true            # new push cancels the outdated run

jobs:
  lint:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: astral-sh/setup-uv@bec219d24cd3e171d82865faccec33120bb574f4 # v10.1.0
        with:
          enable-cache: true
      - run: uv sync --locked
      - run: uv run ruff check .
      - run: uv run ruff format --check .
      - run: uv run mypy .

  test:
    runs-on: ubuntu-24.04
    timeout-minutes: 15
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.13", "3.14"]
    services:
      postgres:
        image: postgres:17-alpine
        env: { POSTGRES_USER: ci, POSTGRES_PASSWORD: ci-only-password, POSTGRES_DB: careerpilot_test }
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U ci -d careerpilot_test"
          --health-interval 5s --health-timeout 3s --health-retries 10
    env:
      DATABASE_URL: postgresql://ci:ci-only-password@localhost:5432/careerpilot_test
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: astral-sh/setup-uv@bec219d24cd3e171d82865faccec33120bb574f4 # v10.1.0
        with:
          enable-cache: true
          python-version: ${{ matrix.python-version }}
      - run: uv sync --locked
      - run: uv run pytest --junitxml=report.xml
      - name: Test summary
        if: always()
        run: uv run python junit_summary.py report.xml >> "$GITHUB_STEP_SUMMARY"

  build:
    needs: [lint, test]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: docker/setup-buildx-action@37fe631027851001ddb9b187196cc803df7f5f0e # v4.3.0
      - uses: docker/build-push-action@53b7df96c91f9c12dcc8a07bcb9ccacbed38856a # v7.3.0
        with:
          push: false
          tags: careerpilot-api:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

:::note[Versions change]
The SHAs above were current when this lesson was written. Always take the latest release SHA from each action's Releases page, and let **Dependabot** keep them updated.
:::

### 3. Key features explained

| Feature | What it does | Why |
|---|---|---|
| `services:` | starts a Docker container next to the job, reachable at `localhost:<port>` | test on **real PostgreSQL** |
| `options: --health-cmd` | the job waits until the service is healthy | no "connection refused" flakiness |
| `strategy.matrix` | runs the job once per value | test several Python versions / OSes |
| `fail-fast: false` | other matrix jobs keep running if one fails | see **all** failures in one run |
| `needs:` | job dependencies | build only after checks pass |
| `if:` | conditions | build/deploy only on `main` pushes |
| `enable-cache` / `cache-from: type=gha` | reuse downloads & Docker layers | minutes → seconds |
| `concurrency` | cancel superseded runs | saves runner minutes |
| `timeout-minutes` | kill stuck jobs | the default is **360 minutes** |
| `$GITHUB_STEP_SUMMARY` | markdown shown on the run page | readable results |
| `::error title=…::msg` | workflow command → annotation | failures highlighted in the UI |

:::warning[YAML gotchas]
- `python-version: [3.10]` → YAML reads the **number** `3.1`. Quote versions: `["3.10"]`.
- `on:` is parsed as boolean `true` by YAML 1.1 parsers like PyYAML (GitHub handles it; your scripts must too).
- Indentation errors silently change meaning — validate with **actionlint**.
:::

### 4. What a good CI checks (in order of speed)

Cheapest checks first: a typo should fail in 30 seconds, not after a six-minute build. Fast feedback is what keeps people running the pipeline instead of avoiding it.

1. **Format & lint** (seconds) — ruff
2. **Types** (seconds) — mypy / pyright, `tsc --noEmit` for frontends
3. **Unit tests** (seconds)
4. **Integration tests** with PostgreSQL (tens of seconds)
5. **Migrations apply** cleanly on an empty database (`flask db upgrade`)
6. **Security**: dependency audit (`pip-audit`), secret scan (gitleaks), image scan (Trivy)
7. **Build** the Docker image

Fast, cheap checks first — developers get feedback quickly.

### 5. Secrets and permissions

- `GITHUB_TOKEN` is created per run; set `permissions:` to the **minimum** (`contents: read`) and grant more per job only when needed (e.g. `packages: write` to push images).
- Repository secrets: `${{ secrets.NAME }}` — masked in logs, **not** available to pull requests from forks.
- Tests shouldn't need real third-party keys: use fakes (lesson 02). The CI database password is a throwaway value for a container that lives for minutes.
- Prefer **OIDC** (`id-token: write`) to get short-lived cloud credentials instead of storing long-lived AWS keys (Module 5).

### 6. Supply-chain security for workflows

A tag can be moved to different code; a commit SHA cannot. Pinning is the difference between "the action I reviewed" and "whatever is there today".

- **Pin actions to full commit SHAs** (tags like `v7` can be moved to different code; SHAs can't). Keep a `# v7.0.1` comment for humans; Dependabot updates both.
- Prefer official/verified actions; read the source of small third-party ones.
- ⚠️ `pull_request_target` runs with **write token and secrets** in the context of the base repo — combined with checking out PR code, it lets a stranger's PR steal secrets. Avoid it unless you truly understand it.
- Don't interpolate untrusted input straight into `run:` (`${{ github.event.pull_request.title }}` → shell injection); pass it via `env:` and quote it.

### 7. CI as a merge gate

In *Settings → Rules → Rulesets* (or branch protection) for `main`:
- require a pull request (optionally 1 approval),
- require status checks `lint` and `test (3.13)`, `test (3.14)` to pass,
- require branches to be up to date, block force pushes.

Now broken code **can't** reach `main` — even yours.

### 8. Costs on a free account

Public repositories get free standard runners; private repositories on the free plan get a monthly quota of runner minutes. Concurrency cancellation, caching, timeouts and path filters (`paths-ignore: ["**.md"]`) keep you well within it. Check GitHub's current billing page for exact numbers.

### Choosing your setup

Every option here is a trade-off:

| Choice | ✅ | ❌ |
|---|---|---|
| Big matrix (many versions/OS) | broad compatibility | more minutes, slower feedback |
| Real Postgres service | realistic | ~10 s startup |
| SHA pinning | tamper-proof | noisy updates (automate with Dependabot) |
| One big job | simple | no parallelism; one failure hides others |
| Many small jobs | parallel, clear status | repeated setup (mitigate with caching) |
| Required checks on `main` | protects main | a flaky test blocks everyone → fix flakiness fast |

- ✅ Every repository you'll show employers — a green CI badge and a real pipeline are strong portfolio signals.
- ✅ Run on pull requests **and** on `main` after merge.
- 🚫 Don't run full load tests or long E2E suites on every push — schedule them nightly or before releases.
- 🚫 Don't use CI as your only feedback loop; run the fast checks locally (pre-commit) too.

## ⚠️ Common mistakes

- `uses: something@main` or `@v1` tags from unknown authors.
- No `timeout-minutes` → a hung test burns hours of minutes.
- `pip install` without a lockfile → CI tests different versions than production.
- Tests needing real API keys → CI breaks for every fork and leaks costs.
- Ignoring red builds "because it's flaky" until nobody trusts CI.

:::revoshop
RevoShop has **no `.github/workflows` folder**, yet its README lists pytest, Pylint, Bandit and pip-audit. (1) Write a `ci.yml` for RevoShop with jobs: `lint` (pylint + bandit), `audit` (pip-audit on `requirements.txt`), `test` (pytest on PostgreSQL 16 service — and switch the test DB from SQLite, lesson 02), and `build` (Docker image, `push: false`). (2) RevoShop uses `requirements.txt` with pip, not uv: replace setup-uv with `actions/setup-python` (SHA-pinned) and `cache: pip`. (3) Add a status badge to the README. (4) Push to a branch, open a PR on your fork, and screenshot a green run for your portfolio.
:::

## 🏆 Best practices

- [ ] Trigger on `pull_request` and `push` to `main`; add `workflow_dispatch` for manual runs.
- [ ] Top-level `permissions: contents: read`; widen per job only when needed.
- [ ] Pin every action to a **full commit SHA** with a version comment; enable **Dependabot** for `github-actions` and your package ecosystem.
- [ ] Install with the **lockfile** (`uv sync --locked`, `npm ci`); cache dependencies.
- [ ] Order checks fast → slow; split into parallel jobs; `fail-fast: false` on matrices.
- [ ] Test against **real services** (PostgreSQL) with health checks; run migrations in CI.
- [ ] Set `timeout-minutes` and `concurrency` with `cancel-in-progress`.
- [ ] Publish readable results: job summaries, annotations, uploaded artifacts (coverage, reports) when useful.
- [ ] No long-lived secrets where OIDC works; never expose secrets to fork PRs; avoid `pull_request_target`.
- [ ] Make CI a **required check** on `main`; fix flaky tests immediately.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a teammate why `uses: actions/checkout@v7` is less safe than a full commit SHA, and why SHA pinning doesn't mean you'll be stuck on old versions.

## 📐 Design it

Design CareerPilot's complete CI/CD workflow set for a monorepo with `api/` (Flask), `web/` (React) and `infra/` (Terraform, later): which workflows and jobs, triggers and path filters, required checks, caching, where the image is pushed, which job deploys to staging vs production and with what approvals, and which secrets/permissions each job needs.

:::quiz
Show a possible design

**Workflows**
1. `api-ci.yml` — on PR/push when `api/**` changes: `lint` (ruff, mypy) → parallel `test` (Postgres service, matrix 3.13/3.14), `migrations` (upgrade on empty DB + `alembic check`), `audit` (pip-audit, gitleaks) → `build` image.
2. `web-ci.yml` — on `web/**`: `npm ci`, `tsc --noEmit`, eslint, vitest, `npm run build`; Playwright E2E nightly.
3. `infra-ci.yml` — on `infra/**`: `terraform fmt -check`, `validate`, `tflint`, `plan` posted as PR comment.
4. `deploy.yml` — on push to `main` (after CI via `workflow_run` or in the same workflow with `needs`): push `careerpilot-api:<sha>` to GHCR/ECR → deploy **staging** automatically → smoke tests → **production** job using a GitHub **Environment** with required reviewer approval.
5. `nightly.yml` — schedule: Locust smoke load test on staging, dependency audit, AI eval suite.

**Required checks on main:** `api-ci / lint`, `api-ci / test (3.13)`, `api-ci / test (3.14)`, `web-ci / build`, gitleaks. Path-filtered workflows use a tiny "always passes when skipped" job or rulesets that allow skipped checks.

**Permissions/secrets:** default `contents: read`; `build` gets `packages: write`; deploy jobs get `id-token: write` for **AWS OIDC** (no stored AWS keys) scoped by environment; production secrets only in the `production` Environment.

**Speed:** uv/npm caching, Docker `type=gha` cache, `concurrency` cancel on PRs (not on deploys — deploys queue instead of cancelling).
:::

### 📝 Self-review checklist

- [ ] Fast checks gate slow ones
- [ ] Production deploy needs approval and uses short-lived credentials
- [ ] Path filters don't let changes skip required checks
- [ ] Deploy concurrency doesn't cancel an in-progress deploy

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m2/w6/07-github-actions-ci" ai="ai-allowed" title="Fix a weak workflow and publish readable test results"}
Turn a naive one-job workflow into a real pipeline — triggers, least-privilege permissions, concurrency, SHA-pinned actions, lint/type-check job, PostgreSQL service with a Python matrix, and a main-only image build — plus Dependabot config. Then write `junit_summary.py`, which turns a real pytest JUnit report into a job summary and correctly escaped error annotations.
:::

:::hints
- `xml.etree.ElementTree.fromstring` + `root.findall("testsuite")` / `suite.iter("testcase")`.
- `case.find("failure")` returns `None` when absent — don't rely on truthiness of an Element.
- Escape `%` **first**, otherwise you'll double-escape the `%` in `%0A`.
- The tests read YAML with PyYAML, which turns `on:` into `True` — the fixture handles it for you.
- Get SHAs with `git ls-remote https://github.com/<owner>/<repo> refs/tags/<tag>`.
:::

### 🏆 Stretch goal

Install **actionlint** (`brew install actionlint`) and run it on your `workflows/ci.yml`. Then create a small public repo with this workflow and a failing test — look at the job summary and annotations on GitHub.

## ✅ Quick check

:::quiz
How do jobs in a workflow run by default, and how do you make one wait for another?

In parallel on separate runners; use `needs: [job_a, job_b]` to wait.
:::

:::quiz
Why set `permissions: contents: read` at the top?

So the automatic `GITHUB_TOKEN` has only read access — if a step or action is compromised, it can't push code, create releases or modify issues.
:::

:::quiz
Why quote `"3.10"` in a matrix?

Unquoted, YAML parses it as the number 3.1, which selects the wrong Python version.
:::


## 📚 Keep learning

- [GitHub Docs — Understanding GitHub Actions](https://docs.github.com/en/actions/get-started/understand-github-actions)
- [GitHub Docs — Security hardening for GitHub Actions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)
- [GitHub Docs — Creating PostgreSQL service containers](https://docs.github.com/en/actions/use-cases-and-examples/using-containerized-services/creating-postgresql-service-containers)
- [uv: Using uv in GitHub Actions](https://docs.astral.sh/uv/guides/integration/github/)
- [actionlint](https://github.com/rhysd/actionlint)
