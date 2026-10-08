# Working on this repo with Claude Code

Read this first in every new session. It is short on purpose; the details live in `docs/`.

## What this is

A local React 19 + TypeScript + Tailwind v4 (Vite) handbook for learning AI full-stack engineering. Lessons are Markdown files in `content/` with Zod-validated frontmatter and custom directives. The app is bilingual: English is the source, Indonesian lives in `<lesson>.id.md`.

| Doc | Read it when |
|---|---|
| `docs/PLAIN_LANGUAGE_REWRITE.md` | **current main task** — rewriting lessons in plain language; progress checklist + prompt templates |
| `docs/WRITING_STYLE.md` | writing or editing any lesson |
| `docs/TRANSLATION_GUIDE.md` | writing an Indonesian `.id.md` file |
| `docs/ADDING_CONTENT.md` | adding a new lesson, exercise or directive |
| `docs/IMPLEMENTATION_PLAN.md` | why the app is built this way (decision table D1–D35) |

## Commands

```bash
npm run dev            # handbook on port 5391
npm run -s content:check   # validates frontmatter, directives, links, translations  ← run after every lesson edit
npm run -s i18n            # Indonesian coverage per module
npm run -s i18n -- hash <english.md>   # sourceHash to put in the .id.md file
npm run -s typecheck && npm run -s lint && npm run -s test && npm run -s build   # full check, run after a batch
```

## Standing rules

- **Never push.** Commit often, locally only, unless the learner explicitly asks to push.
- **Commit trailers** (both lines, every commit):
  ```
  Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
  Claude-Session: <this session's URL>
  ```
- **One lesson per commit** for content work, so a bad lesson can be reverted alone.
- **No browser/Chrome checks** of the handbook UI — the learner checks the display themselves.
- **Non-default ports everywhere**: handbook 5391, Flask 5091, FastAPI 8091, Next.js 3091, Postgres 5491, Redis 6391.
- **RevoShop repo** (`~/path/to/revoshop`) is **read-only** here: never modify it, never read or print its `.env` / `.env.docker` secrets.
- **Never** enter credentials, create cloud accounts, or use the learner's the bootcamp login.
- Lessons must teach **industry best practices** (🏆 section), include a **🔍 RevoShop box** when the topic touches the learner's project, and ship in **English + Indonesian**.

## Writing style (summary)

The learner's first language is Indonesian. Plain words, short sentences, **more everyday analogies**, fewer jargon terms, every term explained once in simple words (🔤 Key words table), and not long-winded. Full rules: `docs/WRITING_STYLE.md`.

## Current state

The **plain-language rewrite is complete in both English and Indonesian for every existing lesson** (Modules 1, 2, 4, 5, 8, both tracks, projects and guides — 193/194; `components-showcase` is an authoring reference and isn't counted).

Module 5 **W5–W7** (Microservices, Orchestration, IaC & Operations — 14 lessons + 11 exercises) and **CareerPilot Phase 5** (deploy to AWS with Terraform) are written in the plain style, in both languages.

**C5b part 2 is complete.** Architecture stages **F (Data & API Design, 6 lessons), H (Distributed Systems, 4 lessons) and I (System Design Practice, 5 lessons)** are written in both languages, each with a verified starter/solution exercise. The architecture track is now 34/34 lessons.

**C3 is written and waiting for the learner's review ✋.** Module 3 (W1–W3, 15 files incl. placement checks), the CareerPilot Phase 3 brief + starter kit (70 acceptance tests) and **DSA Stage 4 — Trees & Graphs** (5 lessons, 20 problems: binary trees, BST, heaps, BFS/DFS, basic graph problems) are all written in both languages.

**C4 is written and waiting for the learner's review ✋.** Module 7 **W1–W5** (LLM basics, prompts & tools, embeddings & vector search, RAG in depth, evals & observability — 23 lessons + 5 placement checks, 23 offline exercises) and the **SupportDesk AI** brief + starter kit (132 acceptance tests) are written in both languages.

What remains: only future-batch material outside C5b — e.g. **Architecture Stage J · Interviews** (C8), other Module 5 depth, Module 6 (C6), Module 7 W0/W6–W8, Phase 7, StudyMind (C7), DSA Stages 5–6 (C8). There is no outstanding C5b work.

Progress, per-lesson workflow and copy-paste prompts: `docs/PLAIN_LANGUAGE_REWRITE.md`.
