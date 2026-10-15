# FSSE Handbook

A **local, beginner-friendly handbook** for becoming an **AI full-stack software engineer** — built with React, TypeScript and Tailwind CSS.

- 📘 8 core modules plus bonus modules: FastAPI, Cloud & AWS, AI Engineering
- 🧩 Parallel tracks: **DSA for Interviews** and **Architecture** (design patterns + system design)
- 🧸 Every lesson: *Learn the concept → Explain & design → Toy exercise*, with automatic tests
- ⭐ Portfolio projects: **CareerPilot**, **SupportDesk AI**, **StudyMind**
- 🎯 Role labels, job-ready milestones, weekly plan, spaced review, LinkedIn templates

> Every explanation, example, exercise, project brief and template in this repository is original.

---

## Requirements

| Tool | Version | Check |
|---|---|---|
| Node.js | 20 or newer | `node -v` |
| npm | comes with Node | `npm -v` |
| Python | 3.11 or newer (for exercises) | `python3 --version` |
| uv *(recommended)* | any recent | `uv --version` — [install](https://docs.astral.sh/uv/getting-started/installation/) |

## Run it locally

```bash
# 1. Install dependencies (once)
npm install

# 2. (Optional) change ports — see "Ports" below
cp .env.example .env

# 3. Start the handbook
npm run dev
```

Open **http://localhost:5391** 🎉

Stop it with `Ctrl + C`.

## Set up the exercises (once)

```bash
cd exercises
uv sync                                   # creates .venv and installs pytest
uv run pytest _example/01-word-count      # try the sample (fails until you solve it)
```

No uv? See [`exercises/README.md`](exercises/README.md) for the pip alternative.

## Scripts

| Command | What it does |
|---|---|
| `npm run dev` | Start the dev server with hot reload |
| `npm run build` | Type-check and build for production into `dist/` |
| `npm run preview` | Serve the production build locally (port 4391) |
| `npm test` | Run the app's unit tests (Vitest) |
| `npm run lint` | Check code with ESLint |
| `npm run format` | Format code with Prettier |
| `npm run typecheck` | TypeScript type-check only |
| `npm run content:check` | Validate all lessons (frontmatter, links, exercise folders) |
| `bash scripts/check-exercises.sh` | Verify every exercise: starter fails, solution passes |

## Ports

Ports are deliberately **not** the usual defaults, to avoid clashing with other apps on your machine. Change them in `.env` (copy from `.env.example`).

| Variable | Used by | Default here | Usual default |
|---|---|---|---|
| `HANDBOOK_PORT` | `npm run dev` | 5391 | 5173 |
| `HANDBOOK_PREVIEW_PORT` | `npm run preview` | 4391 | 4173 |
| `FLASK_PORT` | Flask exercises | 5091 | 5000 |
| `FASTAPI_PORT` | FastAPI exercises | 8091 | 8000 |
| `NEXT_PORT` | Next.js exercises | 3091 | 3000 |
| `POSTGRES_PORT` | PostgreSQL (Docker) | 5491 | 5432 |
| `REDIS_PORT` | Redis (Docker) | 6391 | 6379 |
| `LANGFUSE_PORT` | Langfuse (Docker) | 3191 | 3000 |

The dev server uses **strict ports**: if a port is taken you get a clear error instead of a random new port. Pick another number in `.env` and restart.

## Your progress

Progress, notes, target role and review queue are stored in **your browser's localStorage** — nothing is sent anywhere.
Use **Settings → Export progress** regularly; clearing browser data deletes it.

## Push to a private GitHub repository

```bash
git init
git add .
git commit -m "Initial commit: FSSE Handbook"

# with the GitHub CLI (https://cli.github.com):
gh repo create fsse-handbook --private --source=. --push

# or create an empty PRIVATE repo on github.com, then:
git remote add origin git@github.com:<your-username>/fsse-handbook.git
git branch -M main
git push -u origin main
```

`.env`, `node_modules/`, `dist/` and Python virtual environments are already git-ignored.

## Project structure

```text
fsse-handbook/
├── content/          ← lessons (Markdown), course.json, outline.json
├── exercises/        ← local Python exercises with tests and solutions
├── docs/             ← plan, market check, guides
├── scripts/          ← content check, exercise check, Vite plugin
└── src/              ← the React + TypeScript app
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `Port 5391 is already in use` | Set another `HANDBOOK_PORT` in `.env` |
| Blank page / old content | Hard refresh (`Cmd/Ctrl + Shift + R`) |
| A lesson shows a red error overlay | Its frontmatter is invalid — run `npm run content:check` for details |
| Code editor blocks don't load | They need internet (Sandpack runs in CodeSandbox's bundler) |
| `uv: command not found` | Install uv, or use the pip steps in `exercises/README.md` |

## Docs

- [`docs/HANDBOOK.md`](docs/HANDBOOK.md) — simple explanation of the handbook and how to study with it
- [`docs/LEARN_THE_CODEBASE.md`](docs/LEARN_THE_CODEBASE.md) — guided tour of the React + TypeScript code
- [`docs/ADDING_CONTENT.md`](docs/ADDING_CONTENT.md) — add or edit lessons and exercises
- [`docs/IMPLEMENTATION_PLAN.md`](docs/IMPLEMENTATION_PLAN.md) — the full roadmap and decisions
- [`docs/MARKET_CHECK.md`](docs/MARKET_CHECK.md) — job-market research behind the course
