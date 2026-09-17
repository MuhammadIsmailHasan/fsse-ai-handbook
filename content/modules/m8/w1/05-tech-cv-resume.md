---
title: "Tech CV / Resume"
summary: Write a one-page tech CV that passes ATS filters and convinces engineers — structure, impact bullets with the XYZ formula, projects for career switchers, skills that match the job, tailoring per application, and Indonesian CV conventions.
type: career
source: original
roles: { be: core, fe: core, fs: core, ai: core, ops: core }
durationMinutes: 150
tags: [career, cv, resume, ats, job-search]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- How CVs are screened: **ATS** keyword filters, recruiters, hiring managers
- A clean **one-page structure** for junior developers and career switchers
- **Impact bullets** with the "Accomplished X, measured by Y, by doing Z" formula
- Presenting **projects**, bootcamp and non-tech experience
- **Tailoring** a CV to each job post in 15 minutes
- Indonesian conventions: photo, personal data, language, file format

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **CV / resume** | The one-page document that gets you an interview | Dokumen lamaran singkat |
| **ATS** | Software that reads CVs and ranks them against the job post | Sistem penyaring lamaran |
| **Keyword match** | Using the same words as the job description | Kecocokan kata kunci |
| **Impact bullet** | A line showing result, measure and method | Poin berisi hasil nyata |
| **XYZ formula** | "Accomplished X, measured by Y, by doing Z" | Rumus menulis poin |
| **Tailoring** | Adjusting the CV for each job | Menyesuaikan per lamaran |
| **One-pager** | Everything on a single page — standard for juniors | Satu halaman saja |
| **Parseable format** | A layout the software can read (no columns or images) | Format yang terbaca mesin |

## 🧠 The big idea

A CV is a **movie trailer**, not the movie. In 30 seconds it must show the best scenes (projects and results), the genre (target role) and make the viewer want to watch (invite you to interview). Everything that doesn't serve that goal gets cut.

## ❓ Why it matters

Popular junior roles get hundreds of applications. Recruiters skim, and many companies use software (an ATS) that reads your CV and ranks it against the job description. A CV that can't be read, or doesn't use the job's own words, may never reach a human at all.

For remote roles at US companies, two extra rules apply: keep it to **one page in English**, and drop the photo, date of birth, marital status and full address that are normal in Indonesian CVs — US recruiters expect them to be absent, and some systems flag them.

Think of it as a **movie trailer**, not the movie: best scenes, right genre, and a reason to watch more.

## 📖 Step by step

### 1. Structure (one page for juniors)

```text
MUHAMMAD ISMAIL
Full-Stack Developer · Jakarta, Indonesia (open to remote)
you@example.com · linkedin.com/in/<you> · github.com/<you> · portfolio link

SUMMARY (2 lines)
Full-stack developer (Python, TypeScript) who builds and deploys tested web apps. Built CareerPilot (Flask API + Next.js, 130+ automated tests) and an e-commerce API with payments.

SKILLS
Languages: Python, TypeScript, SQL · Backend: Flask, FastAPI, SQLAlchemy, REST · Frontend: React, Next.js, Tailwind · Data: PostgreSQL, Redis · Tools: Docker, GitHub Actions, Playwright, pytest

PROJECTS
CareerPilot — job-hunt tracker (github link · live link)                                   2026
• Built a Flask REST API with JWT auth, a hiring-pipeline state machine and per-user isolation, verified by 113 acceptance tests on PostgreSQL in CI
• Developed a Next.js frontend with Server Actions and encrypted httpOnly sessions; 23 Playwright E2E tests run against production builds
• Cut the list endpoint from 21 to 2 SQL queries by fixing an N+1 query (p95 180 → 35 ms under Locust load)

RevoShop — e-commerce backend (github link)                                                2026
• Implemented order and payment flows with Midtrans webhooks and role-based access for admins and customers
• …

EXPERIENCE
[Previous role], [Company] — [City]                                                       2022–2025
• Automated weekly sales reporting with spreadsheets and scripts, saving ~4 hours per week for a team of 6
• …

EDUCATION & TRAINING
the bootcamp — Full-Stack Software Engineering program                                           2026
[Degree], [University]                                                                    2021
```

For career switchers, **Projects come before Experience**. Keep the previous job but rewrite bullets around transferable skills (automation, data, communication, ownership).

### 2. Impact bullets

"Reduced the applications page from 21 queries to 2, cutting p95 latency from 1.8 s to 240 ms" beats "Worked on backend performance" — same work, one of them is evidence.

Formula (from Google's "XYZ"): **Accomplished [X] as measured by [Y], by doing [Z]**.

| ❌ Weak | ✅ Strong |
|---|---|
| Worked on the backend API | Built 25 REST endpoints in Flask with validation and ownership checks, covered by 113 acceptance tests |
| Made the website faster | Improved job page LCP from 3.9 s to 2.1 s by moving markdown rendering to Server Components and preloading the hero image |
| Used Docker | Containerized API and web app with multi-stage non-root images; one-command local setup with Docker Compose |

Start with a strong verb (Built, Designed, Reduced, Automated, Migrated), include a number when honest, and name the technology in context.

### 3. ATS-friendly formatting

- Single column, standard headings (Summary, Skills, Projects, Experience, Education).
- Real text (not images), common fonts, no tables/text boxes for key content, no skill bars.
- Export **PDF** unless the portal asks for DOCX. File name: `Muhammad-Ismail-Full-Stack-Developer-CV.pdf`.
- Use the job's exact wording where true ("REST APIs", "PostgreSQL", "Next.js").

### 4. Tailoring in 15 minutes

1. Highlight must-have skills and repeated words in the job post.
2. Reorder Skills so matching ones come first.
3. Pick the 2 project bullets most relevant to the role (backend role → API, database, performance; frontend role → UI, accessibility, Web Vitals).
4. Adjust the 2-line summary with the role title.
5. Save a copy per application and note it in your job tracker (CareerPilot!).

### 5. Indonesian conventions

Keep two versions: the local one with the conventions Indonesian companies expect, and an international one for remote and US applications. Same content, different packaging.

- **Photo, date of birth, marital status**: still common on Indonesian CVs, but not required by most tech companies; many startups and multinationals prefer **no photo**. For remote/international roles, leave them out.
- **Language**: English CVs are standard for tech roles in Jakarta startups and multinationals; use Bahasa Indonesia if the post is in Bahasa and the company is local.
- **Personal data**: city is enough — no full address, KTP number or NPWP on a CV.
- Expected salary: don't put it on the CV; answer when asked (lesson on negotiation).

### Choosing your setup

Every option here is a trade-off:

| | ✅ | ❌ |
|---|---|---|
| One page | forces focus, fast to read | hard to fit everything — good! |
| Designed template | memorable for humans | ATS parsing risks |
| Master CV + tailored copies | best match per role | versions to manage |
| Listing every technology | more keyword hits | shallow, interviewers probe everything |

## ⚠️ Common mistakes

- Objective statements ("seeking a challenging position to grow…").
- Listing tasks instead of results.
- Typos in technology names (Postgre, Nextjs, Javascript).
- Different CV content from what you can explain in the interview.

## 🏆 Best practices

- [ ] One page, single column, standard headings, PDF.
- [ ] Links: GitHub, LinkedIn, live projects — all working.
- [ ] 2–3 projects with impact bullets (verb + what + how + result/number).
- [ ] Skills grouped and matched to the target role; no skill bars or ratings.
- [ ] Tailor summary, skills order and bullets for each application.
- [ ] Consistent dates and titles with LinkedIn.
- [ ] Proofread; ask one engineer and one non-engineer to read it in 30 seconds and tell you what you do.
- [ ] Never exaggerate — every bullet is an interview question.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain the movie-trailer analogy to a friend who wants to include every course certificate and school achievement.

## 📐 Design it

Write 3 impact bullets for CareerPilot and 2 for a previous non-tech job, then tailor your skills section for two different job posts (one backend, one frontend) — show both orders.

:::quiz
Show a review rubric

- Each bullet starts with a strong past-tense verb and names **what** you built.
- At least one number per project (tests, queries, latency, endpoints, users) — only if true.
- Non-tech bullets show transferable skills with outcomes (time saved, errors reduced, customers served).
- Backend tailoring leads with Python, Flask/FastAPI, PostgreSQL, Docker; frontend tailoring leads with TypeScript, React/Next.js, accessibility, testing.
- No bullet you couldn't explain for 2 minutes.
:::

### 📝 Self-review checklist

- [ ] ATS-safe format
- [ ] Impact bullets with evidence
- [ ] Tailoring is fast and repeatable

::ai-review{task="design"}

::part[Practice]{n="3"}

## 🛠️ Do it

1. Build your master CV in a plain document editor (Google Docs/Word) using the structure above.
2. Create two tailored versions: backend and full-stack/frontend.
3. Paste the PDF text into a plain text editor — if the order is scrambled, simplify the layout.
4. Get feedback from one engineer (mentor, alumni, community).

## ✅ Done when

- [ ] Master CV + 2 tailored PDFs
- [ ] Every link works; every bullet defensible
- [ ] Feedback applied

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| CV / Resume | Daftar riwayat hidup |
| ATS (Applicant Tracking System) | Sistem pelacak pelamar |
| Impact bullet | Poin pencapaian berdampak |
| Tailoring | Menyesuaikan CV untuk tiap lowongan |
| Transferable skills | Keterampilan yang bisa dipakai lintas bidang |
