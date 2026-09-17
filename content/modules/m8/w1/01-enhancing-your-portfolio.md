---
title: "Enhancing Your Software Engineering Portfolio"
summary: Turn projects into interview evidence — what reviewers look for, choosing 2–3 flagship projects, READMEs that sell, demos and live links, showing tests and decisions, and presenting AI-assisted work honestly.
type: career
source: core
sourceRef: "Special · L1"
roles: { be: core, fe: core, fs: core, ai: core, ops: core }
durationMinutes: 180
tags: [career, portfolio, github, readme, projects]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- How a portfolio is actually read: **30 seconds** by a recruiter, **10 minutes** by an engineer
- Picking **2–3 flagship projects** instead of 15 tutorials
- The anatomy of a **project README** that answers the reviewer's questions
- Proof signals: deployed link, demo GIF/video, tests and CI badges, architecture diagram, decisions
- Presenting **CareerPilot**, **RevoShop** and bootcamp work honestly — including AI assistance
- A portfolio checklist you'll reuse for every future project

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Portfolio** | The few projects you show as proof of what you can do | Kumpulan karya |
| **Flagship project** | Your best project, presented properly | Proyek unggulan |
| **README** | The first page of a repo: what it is, how to run it | Halaman perkenalan proyek |
| **Proof signal** | Something that shows the work is real (live link, tests, CI) | Bukti nyata |
| **Demo** | A short video or GIF of the app working | Peragaan singkat |
| **Architecture diagram** | A picture of the parts and how they connect | Gambar susunan sistem |
| **Decision log** | Short notes on why you chose X over Y | Catatan alasan keputusan |
| **AI-assisted** | Work where AI helped, stated honestly | Dibantu AI, disebut terbuka |

## 🧠 The big idea

A portfolio is a **property listing**, not a storage unit. Buyers don't want to see every box you own — they want 3 great photos, the floor plan, the location and proof the plumbing works. For a junior developer, that means: a few projects, each with a clear **what**, **how**, **proof** and **why**.

## ❓ Why it matters

Juniors compete with many applicants who all list "React, Node, Python". A portfolio is the cheapest way for a hiring team to lower their risk: *can this person build something real, finish it, test it, deploy it and explain it?*

That matters in Indonesia, where many companies — especially startups — look at GitHub and a deployed link before a degree. It matters even more for **remote roles abroad**, including US companies: they can't meet you, so your repo, your README and a working link are most of what they have to judge.

Without it, you're asking a stranger to take your word for it — and they have twenty other applications open.

## 📖 Step by step

### 1. How reviewers read

| Reviewer | Time | Looks at |
|---|---|---|
| Recruiter / HR | ~30 s | project names, one-line descriptions, live links, screenshots, tech keywords matching the job |
| Engineer / hiring manager | 5–15 min | README clarity, architecture, tests and CI, commit history, code in 2–3 key files, how you handled errors and security |
| Interviewer | during the call | *your explanation*: decisions, trade-offs, what broke, what you'd change |

Design for all three: a scannable top, a deep middle, and stories you can tell.

### 2. Choose flagship projects

| Keep as flagship | Archive or hide |
|---|---|
| Solves a realistic problem with real data | follow-along tutorials |
| Has auth, persistence, errors, tests, deployment | half-finished experiments |
| Matches the roles you apply for | projects you can't explain |
| You can talk about for 10 minutes | forks without changes |

For you right now: **CareerPilot** (Phases 1, 2, 4 → full-stack story), **RevoShop** (backend with payments — after the *Defend Your RevoShop* work), and optionally one smaller project that shows a different skill (a DSA/CLI tool or a UI component library). **Pin** these on GitHub.

### 3. The README that sells

Assume the reader has 30 seconds and no context. What it does, a screenshot, how to run it, and what's interesting technically — in that order.

```markdown
# CareerPilot — AI job-hunt assistant

Track job applications through a hiring pipeline, with a Flask API and a Next.js web app.

**Live:** https://careerpilot.example.com · **Demo video (90 s):** link · **API docs:** /docs

![Dashboard screenshot](docs/dashboard.png)

## Features
- Applications pipeline with valid transitions, history and notes
- Secure sessions (httpOnly encrypted cookie), per-user data isolation
- URL-based filters and pagination

## Architecture
(mermaid diagram: browser → Next.js → Flask → PostgreSQL)

## Tech stack
Next.js 16 · React 19 · TypeScript · Flask · SQLAlchemy · PostgreSQL · Docker · GitHub Actions · Playwright

## Run locally
1. `cp .env.example .env` …  2. `docker compose up` …  3. open http://localhost:3091

## Tests
`uv run pytest` (113 acceptance + unit) · `npx playwright test` (23 E2E) · CI badge

## Decisions & trade-offs
- Sessions over localStorage tokens because …
- Offset pagination now; keyset planned because …

## What I'd improve next
- Refresh-token rotation · Kanban board with optimistic updates
```

Order matters: **what + proof first** (live link, screenshot), details later.

### 4. Proof signals, ranked

1. **Deployed link that works** (with seeded demo account — never your real data).
2. **Screenshot or 60–90 s demo video/GIF** at the top.
3. **Tests + CI badge** — green, and meaningful (say what they cover).
4. **Architecture diagram** and a short **decisions** section.
5. **Commit history** with clear messages over weeks (not one giant "initial commit").
6. **Issues/PRs** in your own repo (even solo) showing planning and review habits.

### 5. Honesty about AI and bootcamp work

Saying "AI generated the first draft; I redesigned the payment flow and wrote the tests" is stronger than pretending otherwise. Companies expect AI use in 2026; they're checking whether you understand the result.

- Using AI tools is normal. Say how: *"I used an AI agent to scaffold the Docker and CI config and reviewed every line; the pipeline rules, session handling and tests are mine."*
- Bootcamp projects are fine; make them yours: improve something measurable (add tests, fix an N+1 query, add rate limiting) and document the change.
- Never claim team work as solo work. Write "team of 4 — I built the payment webhook and order service".

### Choosing your setup

Every option here is a trade-off:

| Choice | ✅ | ❌ |
|---|---|---|
| Few deep projects | shows finishing, depth, stories | less breadth on paper |
| Many small projects | breadth, keywords | looks unfinished, nothing to discuss deeply |
| Personal site | branding, control | time to build/maintain; GitHub + LinkedIn often enough for juniors |
| Deployed on free tiers | real proof | sleeps/limits; mention cold starts or keep a demo video |

## ⚠️ Common mistakes

- Screenshots of the default Next.js page; placeholder READMEs.
- Broken live links, demo credentials that don't work.
- Tech-stack lists without saying what the app does.
- Committing `.env` files or API keys.
- Hiding the fact that a project was a team or tutorial project.

## 🏆 Best practices

- [ ] 2–3 pinned flagship projects that match your target roles.
- [ ] Every flagship README: one-line pitch, live link, screenshot/GIF, features, architecture, tech stack, run, test, decisions, next steps.
- [ ] Working demo with a **demo account**; check links monthly.
- [ ] Green CI and a test summary; no secrets in the repo (run a secret scanner).
- [ ] Clear commit history and a license; `.env.example` provided.
- [ ] State your role and AI assistance honestly.
- [ ] You can explain any file in a flagship project for 2 minutes.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain the "property listing, not storage unit" idea to a classmate who wants to show all 25 of their bootcamp exercises.

## 📐 Design it

Plan your portfolio: list every project you have, mark **flagship / supporting / archive**, and for each flagship write the one-line pitch, the 3 strongest proof signals it has, and the 2 biggest gaps to fix before applying.

:::quiz
Show an example plan

| Project | Status | Pitch | Proof it has | Gaps to fix |
|---|---|---|---|---|
| CareerPilot | flagship | Job-hunt tracker: Flask API + Next.js app with a hiring pipeline | 113 API tests + 23 E2E, Docker, CI | live URL + demo video; decisions section |
| RevoShop | flagship | E-commerce backend with Midtrans payments, JWT + RBAC | tests, Locust report, layered architecture | README explains my role and AI use; fix the oversell race condition and document it |
| Job listings CLI (Phase 1) | supporting | CLI that analyzes job postings | tests, clean README | none — keep, not pinned |
| todo-app, learn-react | archive | — | — | archive repos |
:::

### 📝 Self-review checklist

- [ ] At most 3 flagships
- [ ] Each flagship has a live link or demo video planned
- [ ] Gaps are concrete and fixable in a week

::ai-review{task="design"}

::part[Practice]{n="3"}

## 🛠️ Do it

1. Archive or make private the repos that don't help you.
2. Pin 2–3 flagships; rewrite each README with the template above.
3. Record a 60–90 s demo (screen recording with voice or captions) for CareerPilot.
4. Check every link and demo account from an incognito window.
5. Ask one developer friend (or mentor) to review a README for 5 minutes and tell you what was unclear.

## ✅ Done when

- [ ] 2–3 pinned repos with complete READMEs, screenshots and working links
- [ ] Each README has a decisions section and honest role/AI notes
- [ ] You can pitch each flagship in under 2 minutes (use D-T-C from *Defend Your RevoShop*)

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Portfolio | Portofolio (kumpulan karya) |
| Flagship project | Proyek unggulan |
| Demo account | Akun contoh untuk mencoba aplikasi |
| Proof signal | Bukti kemampuan |
| Pitch | Penjelasan singkat yang meyakinkan |
