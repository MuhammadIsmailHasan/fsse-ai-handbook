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

Module 4 is fully rewritten and translated (50/50). Module 5 is in progress — see the checklist in `docs/PLAIN_LANGUAGE_REWRITE.md`, section 3.
