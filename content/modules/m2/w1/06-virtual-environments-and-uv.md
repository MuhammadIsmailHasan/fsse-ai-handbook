---
title: "Virtual Environments & uv: Reproducible Python Projects"
summary: Isolate each project's dependencies, pin versions with a lock file, and use uv — the fast, modern Python project manager.
type: lesson
source: original
roles: { be: core, fe: optional, fs: core, ai: core, ops: recommended }
durationMinutes: 90
tags: [python, virtualenv, uv, dependencies, bonus]
lastReviewed: 2026-09
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Why every Python project needs its own **virtual environment**
- **Direct** vs **transitive** dependencies, version ranges and **lock files**
- `pyproject.toml`: the standard place for project metadata and dependencies
- The **uv** workflow: `init`, `add`, `sync`, `run`, `lock`
- How `requirements.txt` + `venv` + `pip` compare (you'll meet them in older projects, like RevoShop)

## 🧠 The big idea

A virtual environment is a **separate toolbox per project**. Project A needs Flask 2, project B needs Flask 3. If both share the system's one toolbox, installing for one breaks the other.

A :term[lock file]{bahasa="lock file — daftar versi pasti semua dependensi agar instalasi selalu sama di setiap komputer"} is the **exact shopping receipt**: not "some flour", but "Brand X flour, 1 kg, batch 2026-09". Everyone who installs gets the **same** versions — on your laptop, your teammate's, CI and production.

## ❓ Why does this exist?

- Different projects need **different versions** of the same library.
- `pip install flask` today and next month can install **different** versions → "works on my machine".
- Libraries depend on other libraries (**transitive** dependencies) — you need those pinned too.
- Installing into the system Python can break OS tools.

## 💥 What happens if we DON'T use them?

- `pip install` into the global Python; six months later three projects conflict and nothing runs.
- `requirements.txt` says `flask` with no version; a new major release changes behavior; production breaks on the next deploy.
- A new teammate spends a full day getting the project to run.

## 📖 How it works, step by step

### 1. The classic way: `venv` + `pip`

```bash
python3 -m venv .venv              # create an isolated environment in .venv/
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install flask==3.1.3
pip freeze > requirements.txt      # record EVERYTHING installed, exact versions
deactivate
```

Works everywhere, but it's manual: activating, keeping `requirements.txt` in sync, separating dev tools from runtime dependencies (RevoShop does this with `requirements.txt` + `requirements-dev.txt`).

### 2. The modern way: `pyproject.toml` + a lock file

`pyproject.toml` is the **standard** file for Python project settings:

```toml
[project]
name = "careerpilot-api"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "flask>=3.1,<4",
    "sqlalchemy>=2.0,<3",
]

[dependency-groups]
dev = ["pytest>=8", "ruff>=0.6"]
```

- `dependencies` lists **direct** dependencies with **compatible ranges**.
- A **lock file** (`uv.lock`) records the **exact** resolved versions of *everything*, including transitive dependencies.
- Dev-only tools live in a separate group.

### 3. uv in practice

[uv](https://docs.astral.sh/uv/) is a very fast Python package and project manager (it can also install Python itself).

```bash
uv init careerpilot-api          # create a project with pyproject.toml
cd careerpilot-api
uv add flask sqlalchemy          # add runtime deps → updates pyproject.toml and uv.lock
uv add --dev pytest ruff         # add dev deps
uv run pytest                    # run inside the project's environment (creates .venv automatically)
uv sync                          # make .venv match uv.lock exactly (e.g. after git pull)
uv lock --upgrade-package flask  # deliberately upgrade one package
uv python pin 3.12               # pin the Python version for the project
```

No manual activation needed: `uv run` always uses the right environment. (The handbook's `exercises/` folder is a uv project — you've been using it already.)

### 4. Version specifiers

| Specifier | Means | Use for |
|---|---|---|
| `flask==3.1.3` | exactly this | lock files, reproducible apps |
| `flask>=3.1,<4` | any 3.x from 3.1 | `pyproject.toml` ranges |
| `flask~=3.1` | ≥3.1, <4.0 | shorthand for compatible releases |
| `flask` | anything | ❌ avoid |

Most libraries follow **semantic versioning**: `MAJOR.MINOR.PATCH` — major can break things, minor adds features, patch fixes bugs.

### 5. What to commit

| File | Commit? |
|---|---|
| `pyproject.toml` | ✅ |
| `uv.lock` (or pinned `requirements.txt`) | ✅ for applications |
| `.python-version` | ✅ |
| `.venv/` | ❌ never (it's machine-specific and large) |

## ⚖️ Trade-offs

| Tool | ✅ | ❌ |
|---|---|---|
| `venv` + `pip` + `requirements.txt` | built into Python, universal | manual; no real lock of transitive deps unless you `pip freeze`; slower |
| **uv** | extremely fast, lock file, manages Python versions, one tool | newer; teams must install it |
| Poetry / PDM | lock files, mature | slower; different config conventions |
| Conda | great for data science with native (C/CUDA) libraries | heavy for web apps |

| Pinning | ✅ | ❌ |
|---|---|---|
| Exact versions everywhere | reproducible | you must update deliberately (security patches!) |
| Loose ranges only | automatic updates | surprise breakages |

**Balance:** ranges in `pyproject.toml`, exact versions in the lock file, and a tool (Dependabot/Renovate) that proposes updates as PRs.

## ✅ When to use it / 🚫 When NOT to use it

- ✅ Always: one environment per project.
- ✅ Commit the lock file for **applications** (APIs, CLIs, services).
- ✅ For **libraries** you publish, keep ranges flexible so users can combine them with other packages.
- 🚫 Don't `sudo pip install` or install into the system Python.
- 🚫 Don't commit `.venv/`.

## 🏆 Best practices

- [ ] Use **`pyproject.toml`** as the single source of project metadata and dependencies.
- [ ] Commit the **lock file** and install with `uv sync` (or `pip install -r` a fully pinned file) in CI and Docker.
- [ ] Separate **runtime** and **dev** dependencies (dependency groups).
- [ ] Pin the **Python version** (`.python-version` / `requires-python`).
- [ ] Update dependencies **regularly and deliberately**: automated PRs (Dependabot/Renovate) + tests.
- [ ] Scan for known vulnerabilities (`pip-audit`, GitHub Dependabot alerts).
- [ ] Never install project packages globally; run tools via `uv run` (or an activated venv).
- [ ] Keep the dependency list lean — every package is code you trust and must update.

## 🏭 How it's used in industry

- CI pipelines run `uv sync --frozen` (fail if the lock file is out of date) before tests.
- Docker images install from the lock file for identical builds.
- Security teams track vulnerable dependency versions across all company repos.

## ⚠️ Common mistakes

- Running `pip install` without an active venv (installs globally).
- Editor using a different interpreter than the terminal.
- Forgetting to commit the lock file after `uv add`.
- Unpinned dependencies in production.
- Mixing `pip install` into a uv-managed environment (use `uv add`).

:::revoshop
Open RevoShop's `requirements.txt` and `requirements-dev.txt`. Notice the comments ("Production runtime dependencies only", "Shared transitive runtime deps (pinned for reproducible installs)") and `-r requirements.txt` at the top of the dev file. Explain in your own words: why are **transitive** deps like `Werkzeug` and `Jinja2` pinned too? Why is `locust` only in the dev file? Then sketch how the same split would look in a `pyproject.toml` with dependency groups.
:::

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a non-programmer why "just install the libraries" isn't enough for a team, using the recipe/shopping-receipt idea (or your own analogy). Include the words *virtual environment* and *lock file*.

## 📐 Design it

Plan dependencies for **CareerPilot Phase 2** (Flask API). Classify each into *runtime* or *dev*, and choose a version constraint style for `pyproject.toml`:

`flask`, `flask-sqlalchemy`, `psycopg[binary]`, `alembic`/`flask-migrate`, `pyjwt`, `pytest`, `pytest-cov`, `ruff`, `locust`, `python-dotenv`, `gunicorn`

:::quiz
Show a possible plan

**Runtime:** flask, flask-sqlalchemy, psycopg[binary], flask-migrate, pyjwt, python-dotenv, gunicorn — each as `>=current,<next major` (e.g. `flask>=3.1,<4`).

**Dev:** pytest, pytest-cov, ruff, locust.

Exact versions of everything (including transitive dependencies) live in `uv.lock`. Docker and CI run `uv sync --frozen --no-dev` (runtime only) or `uv sync --frozen` (tests).

`python-dotenv` is debatable: in production, real environment variables are set by the platform, so some teams keep it dev-only.
:::

### 📝 Self-review checklist

- [ ] Test and performance tools are not runtime dependencies
- [ ] I used ranges in `pyproject.toml` and exact versions in the lock file
- [ ] I considered what production actually needs

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{ai="no-ai" title="Bootstrap CareerPilot's API project with uv"}
In your own **careerpilot** repository:

1. `uv init api --app` (creates `api/pyproject.toml`) and `uv python pin 3.12` inside `api/`
2. `uv add flask` and `uv add --dev pytest ruff`
3. Create `api/app.py` with a Flask app that returns `{"status": "ok"}` on `GET /health`
4. Create `api/test_app.py` using Flask's test client to check that endpoint
5. Run `uv run pytest` and `uv run ruff check .`
6. Commit `pyproject.toml`, `uv.lock`, `.python-version`, the code — **not** `.venv/`
7. Delete `.venv/`, run `uv sync`, and run the tests again: it should just work

Write in **My notes**: which files uv created, and what `uv.lock` contains for Flask (its version and at least two transitive dependencies).
:::

:::hints
- Flask test client: `client = app.test_client(); response = client.get("/health"); assert response.json == {"status": "ok"}`.
- Check what's tracked with `git status` before committing.
- `uv tree` shows the dependency tree — find Flask's transitive dependencies there.
:::

## ✅ Quick check

:::quiz
What's the difference between `pyproject.toml` and `uv.lock`?

`pyproject.toml` lists your **direct** dependencies with allowed ranges (human-edited). `uv.lock` records the **exact** versions of all resolved dependencies, including transitive ones (tool-generated), for reproducible installs.
:::

:::quiz
Why shouldn't `.venv/` be committed?

It's large, machine- and OS-specific, and fully reproducible from `pyproject.toml` + the lock file.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Virtual environment | Lingkungan Python terisolasi per proyek |
| Dependency | Dependensi — pustaka yang dibutuhkan proyek |
| Transitive dependency | Dependensi dari dependensi |
| Lock file | File berisi versi pasti semua dependensi |
| Semantic versioning | Penomoran versi MAJOR.MINOR.PATCH |

## 📚 Keep learning

- [uv documentation: Working on projects](https://docs.astral.sh/uv/guides/projects/)
- [Python Packaging User Guide: Writing pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
- [Python docs: venv](https://docs.python.org/3/library/venv.html)
