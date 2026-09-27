# Plain-language rewrite — plan, progress and handoff

**Goal.** Rewrite every lesson so it is easy to read for a learner whose first language is not English: fewer jargon terms, every term explained in one simple sentence, **more everyday analogies**, shorter sections — without losing technical accuracy, the 3-part structure, exercises or 🏆 Best practices. Rules: [`WRITING_STYLE.md`](WRITING_STYLE.md). Indonesian rules: [`TRANSLATION_GUIDE.md`](TRANSLATION_GUIDE.md). Decision entry: D35 in [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md).

**Order requested by the learner:** Module 4 (frontend) → Module 5 (deployment) → other modules → then new material (C5b part 2). Module 8 is low priority.

---

## 0. English first (current policy, from Module 5 onwards)

The learner decided: **rewrite the English lessons only, and translate later** with a separate cheaper model of their own. Good English material is the priority. So from Module 5 on:

- Rewrite `<lesson>.md` only. Do **not** create `<lesson>.id.md`.
- If an Indonesian file already exists for that lesson (Module 4, and Module 5 W1 00–04), rewriting the English file makes it **stale** — so re-run `npm run -s i18n -- hash <file>` and update that file's `sourceHash`, or `content:check` will fail.
- Commit messages: `Rewrite M5 W2 lesson 01 (pipeline concepts) in plain language (EN)`.
- The Indonesian pass happens later as its own batch, using the templates in section 6 (C2 is the prompt for whichever model does it).

## 1. What "done" means for one lesson

A lesson counts as done only when **all** of these are true:

1. The English file follows the style rules below.
2. `npm run -s content:check` passes (including no stale translation, if an `.id.md` exists).
3. Mermaid diagrams parse (if the lesson has any).
4. It is committed with the standard trailers.
5. *(Indonesian pass, later)* a `<lesson>.id.md` exists with a `sourceHash` matching the English file.

### Style rules, short version

| Rule | Detail |
|---|---|
| 🔤 Key words table | Right after "What you'll learn". EN columns: `Word / In simple words / Bahasa Indonesia`. ID columns: `Istilah / Artinya (sederhana)`. 6–10 rows, only terms the lesson really uses. |
| Analogy per main idea | One or two sentences, everyday life (warung, kos, ATM, antrean dapur, kasir, hotel). Then the real code. |
| Merge sections | Old `❓ Why does this exist?` + `💥 What happens if we DON'T?` → one `❓ Why it matters`. Old `⚖️ Trade-offs` + `✅ When to use it` → a short "When to use it / Choosing" block inside Step by step. |
| Remove | The end-of-lesson `📖 Kamus (glossary)` table (the key words table replaces it) and `🏭 How it's used in industry` (fold one or two facts into the text if they matter). |
| Keep unchanged | Frontmatter fields, all code blocks, all directives (`::part`, `:::exercise`, `:::hints`, `:::quiz`, `:::revoshop`, `:::linkedin`, `::ai-review`, `::::placement`), internal links, 🏆 Best practices, RevoShop boxes. |
| Headings | EN `📖 Step by step`; ID `📖 Langkah demi langkah`, `🏆 Praktik terbaik`, `📚 Lanjut belajar`, `⚠️ Kesalahan umum`, parts `[Pelajari Konsepnya]` / `[Jelaskan & Rancang]` / `[Latihan Kecil]`. |
| Summary | ≤ 240 characters, or `content:check` fails. |

---

## 2. Per-lesson workflow (copy this)

```bash
cd fsse-handbook

# 1. read the current lesson
cat content/modules/m5/w2/01-pipeline-concepts.md

# 2. write the plain-language English version (same path, same frontmatter fields)

# 3. get the hash of the NEW English file
npm run -s i18n -- hash content/modules/m5/w2/01-pipeline-concepts.md

# 4. write <lesson>.id.md with that hash in `sourceHash`
#    - code blocks IDENTICAL to English (comments inside code stay English)
#    - mermaid node labels MAY be translated
#    - same directives in the same order, same internal links

# 5. verify
npm run -s content:check
node scripts-or-scratchpad/mermaid-check.mjs content/modules/m5/w2/01-*.md   # only if the lesson has mermaid

# 6. commit
git add -A && git commit -m "Rewrite M5 W2 lesson 01 (pipeline concepts) in plain language (EN + ID)

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: <session url>"
```

Useful checks: `npm run -s i18n` (translation coverage per module), `npm run -s typecheck && npm run -s lint && npm run -s test && npm run -s build` (run after a batch, not after every lesson).

Common failures:

| Message | Cause | Fix |
|---|---|---|
| `Too big: expected string to have <=240 characters → at summary` | summary too long | shorten the frontmatter summary, then re-hash and update `sourceHash` |
| `translation is stale` | English changed after the ID file was written | re-run `i18n -- hash` and update `sourceHash` |
| directive/code-block mismatch | ID file changed a code block or dropped a directive | copy the code block from English verbatim |

---

## 3. Progress

Counts are lessons (files), from `npm run -s i18n`.

| Area | Total | English rewritten | Indonesian | Status |
|---|---|---|---|---|
| Module 4 (frontend) | 50 | 50 | 50 | ✅ done |
| Module 5 (deployment) | 27 | 27 | 27 | ✅ done |
| Module 1 | 14 | 12 | 14 | ✅ done |
| Module 2 (backend) | 52 | 45 | 52 | ✅ done |
| Module 8 (career) | 12 | 12 | 12 | ✅ done, aimed at remote/US roles |
| Tracks: architecture | 19 | 19 | 19 | ✅ done |
| Tracks: DSA | 12 | 12 | 12 | ✅ done |
| Projects (careerpilot, studymind, supportdesk-ai) | 6 | 6 | 6 | ✅ done |
| Guides | 2 | 2 | 1 | ✅ how-to-study done; components-showcase is an authoring reference, left as is (not counted) |

### Modules 1 and 8 — English pass ✅ complete

- [x] M1 W0 (7): how the web works, variables, operators, conditionals, lists & loops, functions, debugging
- [x] M1 W1 (5): counting, searching, sorting, filtering/aggregation, problem-solving process
- [x] M8 W1 (5): portfolio, GitHub profile, LinkedIn, learning in public, tech CV
- [x] M8 W2 (7): job search, hiring process, STAR, live coding, system design, teamwork, salary negotiation

Module 8 was also updated for the learner's target market: remote roles outside Indonesia, especially the US. Each career lesson now says what changes for that market (English one-page CV without photo or personal data, time-zone overlap in the LinkedIn headline, companies that already hire outside the US, contractor offers without BPJS/THR, written communication as the visible work in a remote team).

### Tracks, projects and guides — English pass ✅ complete

- [x] DSA (12): Big-O, memory, recursion, arrays, hash maps, stacks/queues, linked lists, two pointers, sliding window, prefix sums, binary search, sorting
- [x] Architecture (19): principles (3), system design basics (3), OOP design (2), design patterns (4), backend architecture (3), frontend patterns (4)
- [x] Projects (6): CareerPilot overview + phases 1, 2 and 4; StudyMind; SupportDesk AI
- [x] Guides: how-to-study (components-showcase is an authoring reference, left unchanged)

Project briefs and guides got a lighter treatment — they have no `🧠 The big idea` section, so the work was plain-language intros and analogies at each major heading.

### Module 2 checklist — English pass ✅ complete

- [x] w1 (7 lessons): software engineering, editor & Markdown, terminal, Git, collaboration, uv, Docker basics
- [x] w2 (7): PostgreSQL setup, schema design, SQL queries, relationships, joins, indexes, transactions
- [x] w3 (9): Python syntax, control flow, generators, functions, data structures, OOP, type hints, exceptions, project layout
- [x] w4 (6): Flask structure, SQLAlchemy, models, migrations, relationships, layered architecture
- [x] w5 (8): REST & GET, writes, validation, error handling, JWT, RBAC, OpenAPI, webhooks
- [x] w6 (9): pytest, API tests, Locust, secrets, deployment, Docker for production, GitHub Actions, logging, Defend Your RevoShop

The 7 placement checks were left as they were: short, already plain, and mostly question-and-answer.

### Module 5 checklist — English pass ✅ complete

- [x] w1: 00 placement · 01 Docker in depth · 02 targets/tags/registries · 03 Compose full stack · 04 Redis · 05 Ship RevoShop containers
- [x] w2: 00 placement · 01 pipeline concepts · 02 GitHub Actions · 03 environments · 04 secrets & OIDC · 05 Ship RevoShop CI/CD
- [x] w3: 00 placement · 01 IAM & budgets · 02 regions & VPC · 03 EC2 · 04 RDS · 05 S3 & CloudFront · 06 cloud translation table · 07 Ship RevoShop EC2+RDS
- [x] w4: 00 placement · 01 frontends on AWS · 02 backend on EC2 · 03 ECS Fargate · 04 Lambda jobs · 05 Parameter Store & Secrets Manager · 06 Ship RevoShop ECS

All 27 Module 5 lessons now have `.id.md` files — the Indonesian pass for this module is done.

**Both the English pass and the Indonesian pass are complete for every existing lesson.** New material since then, written in the plain-language style from the start (EN + ID): **Module 5 W5 (Microservices), W6 (Orchestration) and W7 (IaC & Operations) — 14 lessons + 11 exercises — and CareerPilot Phase 5** (deploy to AWS with Terraform). The only remaining new material from C5b part 2 is **Architecture stages F, H and I** (see `docs/IMPLEMENTATION_PLAN.md`).

---

## 4. Resuming in a new session

Every new Claude Code session in this repo reads `CLAUDE.md` at the root automatically, so it already knows the standing rules (never push, commit trailers, ports, RevoShop is read-only) and that this file is the current task. A short prompt is therefore enough — see the templates in section 6.

Three things tell you where the work stopped:

```bash
git log --oneline | grep "plain language" | head -5   # last lessons finished
git status --short                                    # anything half-written (should be empty)
npm run -s i18n                                       # Indonesian coverage per module
```

Plus the checklist in section 3 of this file. If `git status` is **not** empty, the previous session stopped mid-lesson: finish that lesson (write the `.id.md`, run `content:check`, commit) before starting a new one.

---

## 5. Delegating to a cheaper / faster model

The work splits into two kinds of tasks.

| Task | Good for a cheaper model? | Why |
|---|---|---|
| Indonesian version of an already-rewritten English lesson | ✅ yes | mechanical: structure is fixed, code blocks are copied, and `content:check` verifies directives, code blocks, links and the hash |
| Placement checks (`00-*.md`, ~400 words, mostly Q&A) | ✅ yes | short, formulaic |
| Rewriting a conceptual English lesson (Docker, AWS, CI/CD) | ⚠️ review needed | this is where accuracy slips: analogies that mislead, wrong claims about IAM/VPC/ECS, dropped nuance |
| RevoShop boxes and anything referencing the learner's real repo | ❌ keep on the stronger model | needs the repo context and correct file/function names |
| Choosing which sections to merge or delete | ⚠️ review needed | affects every later lesson's consistency |

**Recommended split:** the stronger model rewrites the English lesson; a cheaper model (Haiku) produces the Indonesian file from it and runs the checks; the stronger model reviews the diff before commit.

Guard rails that make delegation safe:

- `npm run -s content:check` mechanically rejects a translation that changes code, directives, links, or that is stale.
- `npm run -s i18n` shows coverage, so nothing is silently skipped.
- One lesson per commit → a bad lesson is one `git revert` away.
- Spot-check rule: read the 🔤 Key words table and one analogy per delegated lesson; if either is vague or wrong, redo that lesson on the stronger model.

### The delegation loop, step by step

1. Strong model rewrites the **English** lesson and runs `npm run -s i18n -- hash <file>`.
2. Strong model starts a subagent: `Agent(subagent_type: "general-purpose", model: "haiku")` with template **C2** below (it contains the file path and the hash).
3. Subagent writes `<lesson>.id.md` and runs `npm run -s content:check`; it does **not** commit.
4. Strong model reads the new `.id.md` (key words table + one analogy + the RevoShop box), fixes what is off, then commits both files together.
5. Repeat. Every 5 lessons: `npm run -s typecheck && npm run -s lint && npm run -s test && npm run -s build`.

Two subagents can work on two different lessons at the same time; they must never touch the same file, and only the main session commits.

---

## 6. Prompt templates (copy-paste)

### A — Start a new session (default)

> Baca `CLAUDE.md` dan `docs/PLAIN_LANGUAGE_REWRITE.md`, lalu lanjutkan pekerjaan dari bagian yang belum selesai di checklist (saat ini: pass terjemahan Indonesia). Satu materi per commit, `content:check` harus lulus, jangan push.

### B — Continue a specific module

> Lanjutkan plain-language rewrite untuk `content/modules/m5/w2/` (semua materi W2), sesuai `docs/PLAIN_LANGUAGE_REWRITE.md`. Update checklist di dokumen itu setiap minggu selesai.

### C1 — Turn on delegation (cheap model does the Indonesian version)

> Pakai pola delegasi di `docs/PLAIN_LANGUAGE_REWRITE.md` bagian 5: kamu tulis versi Inggrisnya, lalu delegasikan file `.id.md` ke subagent Haiku, review hasilnya, baru commit. Lanjutkan dari materi pertama yang belum dicentang.

### C2 — Prompt for the subagent itself (the strong model writes this)

> You are writing the Indonesian version of one lesson in the FSSE handbook.
>
> 1. Read `docs/TRANSLATION_GUIDE.md` and `docs/WRITING_STYLE.md`.
> 2. Read the English lesson `<PATH>.md` and an example pair already done: `content/modules/m5/w1/03-docker-compose-full-stack.md` and `.id.md`.
> 3. Write `<PATH>.id.md` with frontmatter `title`, `summary` (≤ 240 characters, Indonesian) and `sourceHash: <HASH>`.
> 4. Rules: translate prose into plain Indonesian; keep every code block **byte-identical** to the English file (comments inside code stay English); keep the same directives in the same order; keep internal links unchanged; mermaid node labels may be translated; use the standard Indonesian headings from the translation guide (`📖 Langkah demi langkah`, `🏆 Praktik terbaik`, `📚 Lanjut belajar`, `⚠️ Kesalahan umum`, `[Pelajari Konsepnya]` / `[Jelaskan & Rancang]` / `[Latihan Kecil]`).
> 5. Run `npm run -s content:check` and fix any problem it reports.
> 6. Do **not** commit and do not touch any other file. Report the path you wrote and the check output.

### D — Ask for status only

> Berikan status plain-language rewrite: berapa materi selesai per modul, apa yang sedang dikerjakan, dan sisa tugasnya. Jangan ubah file apa pun.

### E — New material (after the rewrite)

> Semua materi lama sudah ditulis ulang dalam bahasa Inggris. Lanjutkan membuat materi baru C5b part 2 (M5 W5–W7, Architecture F/H/I, CareerPilot Phase 5) sesuai `docs/IMPLEMENTATION_PLAN.md`, langsung dalam gaya bahasa sederhana sesuai `docs/WRITING_STYLE.md` (tabel 🔤 Key words, analogi sehari-hari, ❓ Why it matters yang digabung). Satu materi per commit, `content:check` harus lulus, jangan push.

### F — Health check before closing a session

> Jalankan semua pengecekan (`typecheck`, `lint`, `test`, `build`, `content:check`, `i18n`), pastikan `git status` bersih, update checklist di `docs/PLAIN_LANGUAGE_REWRITE.md`, lalu laporkan hasilnya.

### H — Indonesian pass (the main remaining work)

> Baca `CLAUDE.md`, `docs/PLAIN_LANGUAGE_REWRITE.md` dan `docs/TRANSLATION_GUIDE.md`. Jalankan `npm run -s i18n` untuk melihat modul mana yang belum punya versi Indonesia, lalu buat file `.id.md` untuk materi berikutnya yang belum diterjemahkan (mulai dari `content/modules/m5/w1/05-*`, lanjut ke M5 W2–W4, lalu Module 2, Module 1, tracks, projects, Module 8).
>
> Untuk tiap materi: ambil hash dengan `npm run -s i18n -- hash <file EN>`, tulis `<file>.id.md` dengan `sourceHash` itu, blok kode **identik** dengan versi Inggris, directive dan link internal sama persis, heading Indonesia sesuai panduan terjemahan. Jalankan `npm run -s content:check`, lalu commit per materi dengan trailer standar. Jangan push, jangan ubah file Inggrisnya.

### G — Fix one lesson that feels wrong

> Materi `<PATH>` masih terasa sulit/terlalu banyak istilah. Tulis ulang bagian yang bermasalah (EN + ID), pertahankan kode dan directive-nya, jalankan `content:check`, lalu commit.
