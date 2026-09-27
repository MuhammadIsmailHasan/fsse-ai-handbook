# FSSE Handbook — Implementation Plan

> **Status:** v1.8 — B1–B6, C1, C2, C5a done; C5b Weeks 3–7 + CareerPilot Phase 5 done (Architecture F/H/I still remaining)
> **Last updated:** 2026-09-13
> **Owner:** Muhammad Ismail Hasan (learner) · written with Claude Code

This document is the roadmap for the whole project: **what** we build (a local handbook app + course content), **why** each decision was made, and **in what order** we build it. Come back to it whenever you feel lost.

---

## Table of Contents

1. [Goals](#1-goals)
2. [Content Policy (Originality)](#2-content-policy-originality)
3. [Learner Profile & Starting Point](#3-learner-profile--starting-point)
4. [Decisions Log](#4-decisions-log)
5. [Roles & Labels](#5-roles--labels)
6. [Course Map](#6-course-map)
7. [Modules in Detail](#7-modules-in-detail)
8. [Parallel Tracks](#8-parallel-tracks)
9. [Portfolio Projects](#9-portfolio-projects)
10. [Lesson Format](#10-lesson-format)
11. [Exercise System](#11-exercise-system)
12. [LinkedIn: Learning in Public](#12-linkedin-learning-in-public)
13. [Milestones, Timeline & Weekly Schedule](#13-milestones-timeline--weekly-schedule)
14. [App Architecture](#14-app-architecture)
15. [Ports & Environment Config](#15-ports--environment-config)
16. [Documentation Set](#16-documentation-set)
17. [Build Plan (Implementation Milestones)](#17-build-plan-implementation-milestones)
18. [Future: AI Review](#18-future-ai-review)
19. [Out of Scope](#19-out-of-scope)
20. [Risks & Mitigations](#20-risks--mitigations)

---

## 1. Goals

| # | Goal | How this project delivers it |
|---|---|---|
| 1 | **Deep understanding** of AI full-stack software engineering | 3-part lessons: concept (why, trade-offs, when/when not) → explain & design → hands-on toy |
| 2 | **Job-ready** as a junior developer, then as an AI-integrated full-stack engineer | Role labels, job-ready milestones, DSA + system design tracks, career module |
| 3 | **2+ strong portfolio projects**, AI-integrated, not e-commerce | ⭐ CareerPilot (grows through every module) + 🧠 SupportDesk AI (+ StudyMind for extra practice) |
| 4 | **Visible progress** to recruiters while learning | LinkedIn templates per week, milestone and project checkpoint |
| 5 | **Pleasant local reading experience** | React + TypeScript + Tailwind reader app, run locally, stored in a private GitHub repo |
| 6 | **Learn from the app's code itself** | Teaching comments + `docs/LEARN_THE_CODEBASE.md` |

---

## 2. Content Policy (Originality)

- **Taken from the bootcamp:** only the course **outline** — module, week and lesson **titles** and their order. Saved in [`content/outline.json`](../content/outline.json).
- **Not taken from the bootcamp:** lesson text, bullet points, code, diagrams, quizzes, assignment briefs, logo or branding.
- **Written originally:** every explanation, example, exercise, project brief and template in this repo.
- Lessons based on a the bootcamp lesson carry a small `sourceRef` tag (e.g. `M2 · W4 · L1`) so you can match them with your class.
- Bonus material is marked 🔥 **Bonus**.

---

## 3. Learner Profile & Starting Point

| Item | Value |
|---|---|
| Progress in the bootcamp | Finished through **Module 2 (Backend)** |
| Existing portfolio | [RevoShop backend](https://github.com/Bootcamp-FSSE-Jun26/module-2-MuhammadIsmailHasan) — Flask, flask-smorest, SQLAlchemy, Flask-Migrate, JWT + RBAC, Midtrans webhooks, pytest, Locust, Docker, layered architecture |
| Honest gap | Much of RevoShop was implemented with Kiro → understanding is weaker than the code suggests |
| Study time | ~3 h/day → planned as **6 days/week ≈ 18 h/week** (buffer for missed days) |
| Machine | Python and Node already installed |
| Language | English, with key terms explained in Bahasa Indonesia |

**Consequences for the plan:**
1. **Placement checks** at the start of each week → skip what you truly know.
2. **🔍 "Find it in RevoShop"** boxes in Module 2 → connect each concept to your own code.
3. **🎤 "Defend your project"** exercises → practice the interview questions RevoShop will trigger.
4. **🧠 Brain-first rule** → core exercises are labeled 🚫🤖 No-AI.

---

## 4. Decisions Log

| # | Topic | Decision | Why |
|---|---|---|---|
| D1 | App framework | **Vite 8 + React 19 + TypeScript 6** | Fast dev server, simple mental model; no server needed for a local reader |
| D2 | Styling | **Tailwind CSS v4** | Requested; also taught in the course |
| D3 | Content format | **Markdown files + YAML frontmatter** | Easy to edit without touching code |
| D4 | FastAPI placement | **Separate module after Flask + "🔄 In FastAPI…" boxes** in Flask lessons | Learn one framework at a time, still see connections |
| D5 | Toy exercises | **Mix:** JS/TS/React in the browser (Sandpack); Python/Flask/FastAPI/Next.js as local folders with tests | Frameworks need real runtimes; real tooling is job practice |
| D6 | Lesson language | English + Bahasa explanations of key terms | Learner preference |
| D7 | Long lessons | Split into smaller lessons | Keep each lesson readable |
| D8 | Ports | Non-default, configurable via `.env`, strict port | Avoid conflicts with other local services |
| D9 | AI-assisted dev module | **Tool-agnostic** (Kiro, Claude Code, Cursor, Copilot…) | Skills transfer across tools |
| D10 | Next.js | Taught as the bootcamp does; the handbook app itself stays on Vite | Follow curriculum; keep reader simple |
| D11 | DSA | **Parallel track in Python** | Interview skill needs spaced practice |
| D12 | Architecture | **Parallel track** (principles → patterns → system design), starting in Module 1 | Learner wants it early |
| D13 | Main project | ⭐ **CareerPilot** — AI job-hunt assistant | Useful to learner; strong interview story |
| D14 | Standalone AI project | 🧠 **SupportDesk AI** (main) + **StudyMind** (extra practice) | Covers RAG, agents, guardrails, evals |
| D15 | LinkedIn | Weekly recap + concept + DSA + project checkpoint + module reflection | Consistent without spamming |
| D16 | Cloud | **AWS**, CI/CD, microservices, orchestration; Kubernetes practiced locally | Market demand; free-tier constraints |
| D17 | Infra as Code | **Terraform** | Cloud-agnostic, common in job listings |
| D18 | Role labels | 5 roles × 4 levels, per module **and** per lesson; ⭐ AI Full-Stack preset | Learner can focus on a target role |
| D19 | Weekly schedule | Included in the app | Combines modules + tracks + project |
| D20 | AI review | Designed now (disabled slot), implemented later; **Ollama first** | Free, private, no API key to leak |
| D21 | Market alignment | Adjusted after market check (see [`MARKET_CHECK.md`](./MARKET_CHECK.md)) | Added LangGraph, evals libs, Langfuse, ML foundations, Redis, GraphQL, Bedrock, multi-cloud mapping |
| D22 | Milestone fix | Module 6 (AI-Assisted Development) belongs to **Milestone 2** (it was missing from the milestone table) | Core for every role; needed before AI engineering |
| D23 | Lesson ids | Lesson id, module and week are **derived from the file path**, not written in frontmatter | Less duplication, no id typos |
| D24 | Best practices | Every lesson from Module 2 on has a **🏆 Best practices** section (learner request after the Module 1 review) | Learn how professionals actually do it, not only the concept |
| D25 | Testing exercises | Exercises where the learner writes tests are **graded by mutants** (buggy copies of correct code) | Proves tests catch bugs, not just that they run |
| D26 | Project kits | Project acceptance tests are validated against a **private reference implementation** that is not committed | Correct tests without handing out the solution |
| D27 | Frontend exercises | JS/TS/React exercises run **locally with Vitest + jsdom + Testing Library** in `exercises/web/` (verified by `scripts/check-web-exercises.sh`); Sandpack stays for ungraded playgrounds | Works offline, same starter/solution workflow as Python, and every exercise is verifiable |
| D28 | E2E exercises | Playwright exercises run against a **tiny no-build Node app** (`exercises/web/m4/w6/_app`) whose bugs are switched on with `APP_VARIANT`; the config falls back to an installed Google Chrome when Playwright's Chromium isn't downloaded | Fast, deterministic mutant grading without building a Next.js app per run |
| D29 | Frontend project contract | CareerPilot Phase 4 acceptance tests find elements by **accessible names** and run against a **mock of the Phase 2 API** | Styling stays free, accessibility is enforced, and results don't depend on the learner's API data |
| D30 | Batch order | **C5 (Module 5) moved before C3/C4**, split into **C5a** (W1–W2, local only) and **C5b** (W3–W7 + Architecture F/H/I + Phase 5) with a ✋ review before AWS | Learner wants to deploy RevoShop now; the pause keeps the AWS free-plan clock from starting early |
| D31 | Ship RevoShop | Each Module 5 week ends with a **🚀 Ship RevoShop** lab applied to the learner's real RevoShop repo (production image, Compose, Redis, CI/CD, AWS deploy, IaC); the handbook guides, the learner changes their own repo; every M5 lesson also has a 🔍 RevoShop box (learner request) | Deploying a project you already know teaches DevOps on real constraints (Midtrans webhooks, migrations, secrets) |
| D32 | AWS exercises | AWS exercises run **locally**: pure Python models (IAM evaluation, costs, networks) and boto3 code tested against **moto**; real AWS happens only in the 🚀 labs, whose scripts are first exercised locally (local registry, fake RDS, fake AWS CLI) | Verifiable without an account or bill; learners create resources only when they understand them |
| D33 | Bilingual handbook | English is the source; Indonesian lives in `<lesson>.id.md` (title, summary, `sourceHash` only), `content/course.id.json` and `src/i18n/messages.ts`. A toggle switches the whole app; missing translations fall back to English with a badge. `content:check` rejects stale translations and any change to directives, code or internal links. Translate Module 4 first, then new lessons ship in both languages | Learner asked for Indonesian with a toggle; gradual translation keeps the app usable while ~340k words are translated, and automated parity checks stop the two versions drifting apart |
| D34 | Flexible study goal | Target + minimum + actual time log instead of one fixed 18 h/week plan; today's plan is built from the time available today; pure logic in `src/lib/study-time.ts` | Learner aims for 5 h/day but often has less; a rigid plan either overwhelms or is ignored, while a minimum keeps busy days counting |
| D35 | Plain-language rewrite | Every lesson is rewritten for readers whose first language is not English: a 🔤 Key words table, an everyday analogy per main idea, merged `❓ Why it matters`, no end-of-lesson glossary or industry section; code, directives, exercises and 🏆 Best practices stay unchanged. Progress and the per-lesson workflow live in `docs/PLAIN_LANGUAGE_REWRITE.md`; order is Module 4 → Module 5 → other modules → new material | Learner found the content accurate but hard to follow: too many terms, too few analogies; a written workflow plus per-lesson commits make the rollout resumable and delegable |

---

## 5. Roles & Labels

### Roles
| Code | Role |
|---|---|
| 🟦 **BE** | Backend Developer |
| 🟩 **FE** | Frontend Developer |
| 🟪 **FS** | Full-Stack Developer |
| 🤖 **AI** | AI Engineer (applied — building products with LLMs) |
| ☁️ **Ops** | Cloud / DevOps Engineer |
| ⭐ **AI-FS** | Preset = FS + AI (**learner's target**) — a lesson is Core if it is Core for FS *or* AI |

### Levels
| Label | Meaning |
|---|---|
| 🟢 **Core** | Needed for junior interviews in this role |
| 🔵 **Recommended** | Strong advantage |
| ⚪ **Optional** | Deep dive when you have time |
| ➖ **Not needed** | Skip for this role |

### Other badges
| Badge | Meaning |
|---|---|
| 🔥 Bonus | Not in the bootcamp outline |
| 🚫🤖 No-AI / 🤖✅ AI-allowed | Exercise AI policy |
| 🟢 Free / 🟡 Small cost / 🔴 Concept only | AWS cost badge |
| 🕒 Last reviewed | Date, on fast-changing topics (AI, cloud) |

### Module-level matrix
| Module / Track | 🟦 BE | 🟩 FE | 🟪 FS | 🤖 AI | ☁️ Ops |
|---|---|---|---|---|---|
| 1 Algorithm & Programming | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 |
| 2 Backend: Flask | 🟢 | ⚪ | 🟢 | 🔵 | 🔵 |
| 3 Backend: FastAPI | 🔵 | ➖ | 🔵 | 🟢 | ⚪ |
| 4 Frontend: Next.js | ⚪ | 🟢 | 🟢 | 🔵 | ➖ |
| 5 Cloud, DevOps & AWS | 🔵 | ⚪ | 🔵 | 🔵 | 🟢 |
| 6 AI-Assisted Development | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 |
| 7 AI Engineering in Production | ⚪ | ⚪ | 🔵 | 🟢 | ⚪ |
| 7·W0 ML Foundations | ➖ | ➖ | ⚪ | 🔵 | ➖ |
| 8 Career & Portfolio | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 |
| 🧩 DSA — core patterns | 🟢 | 🟢 | 🟢 | 🟢 | 🔵 |
| 🧩 DSA — advanced (DP, graphs) | ⚪ | ⚪ | ⚪ | ⚪ | ➖ |
| 🏛️ Principles & design patterns | 🟢 | 🔵 | 🟢 | 🔵 | ⚪ |
| 🏛️ System design | 🔵 | ⚪ | 🔵 | 🔵 | 🟢 |

Per-lesson labels are set in each lesson's frontmatter while writing content (they often differ from the module default).

---

## 6. Course Map

```
MODULES (in order)                               PARALLEL TRACKS
1  Algorithm & Programming      (the bootcamp M1)      ┌ 🧩 DSA for Interviews (Python)
2  Backend: Flask               (the bootcamp M2)      │
3  Backend: FastAPI             (🔥 bonus)      │ 🏛️ Architecture:
4  Frontend: Next.js            (the bootcamp M3)      │   principles → design patterns
5  Cloud, DevOps & AWS          (🔥 bonus)      │   → system design
6  AI-Assisted Development      (the bootcamp M4)      │
7  AI Engineering in Production (🔥 bonus)      └
8  Career & Portfolio           (the bootcamp Special + 🔥 bonus) — unlocks at Milestone 1

⭐ CareerPilot: Phase 1 (M1) → Phase 7 (M7), monolith → microservices on AWS
🧠 SupportDesk AI (M7)  ·  StudyMind (extra practice)
📣 LinkedIn: weekly + milestones
```

**Approximate size:** ~200 lessons + 2 tracks + 3 projects. Exact counts are finalized while writing each module.

**Numbering:** the handbook uses its own module numbers. the bootcamp's M3 is our Module 4, the bootcamp's M4 is our Module 6.

---

## 7. Modules in Detail

Legend: `L` = the bootcamp-based lesson · `S` = split from a the bootcamp lesson · 🔥 = bonus · 📋 = project/assignment · ✅ = placement check

### Module 1 — Algorithm & Programming *(the bootcamp M1)*
**Language:** Python. **Default roles:** all 🟢.

| Week | Lessons |
|---|---|
| **W0 Logic Foundations & Web Architecture** | ✅ Placement check · S How the Web Works: Client, Server & HTTP · S Data Containers: Variables & Data Types · L Operators: Arithmetic, Comparison, Logic · L Conditionals · L Lists & Loops · L Functions · 🔥 Reading Errors & Debugging Basics |
| **W1 Algorithms & System Logic** | ✅ Placement check · L Counting & Frequency · L Searching · L Sorting · L Filtering, Aggregation & Combining · L Problem Solving Process · 📋 **CareerPilot Phase 1** (replaces the bootcamp mini project & assignment) |

Tracks alongside: 🧩 DSA Stage 1 (Big-O, memory, recursion) · 🏛️ Architecture Stages A–B.

### Module 2 — Backend: Flask *(the bootcamp M2)* — "Rebuild with understanding"
Every week includes 🔍 **Find it in RevoShop** boxes and 🔄 **In FastAPI…** boxes (W4–W6).

| Week | Lessons |
|---|---|
| **W1 Software Engineer Toolkit** | ✅ · L Intro to Software Engineering · L Code Editor & Markdown · L Terminal & CLI · L Git Fundamentals · L Git Collaboration (branches, PRs, conflicts) · 🔥 Virtual Environments & `uv` · 🔥 Docker Basics |
| **W2 Database with PostgreSQL** | ✅ · L Setup & SQL Client · L Schema Design & Normalization · L CRUD Queries · L Relationships & Foreign Keys · L JOINs & Subqueries · 🔥 Indexes & Query Performance (`EXPLAIN`) · 🔥 Transactions & ACID |
| **W3 Python Core** | ✅ · S Python Setup & Syntax · S Control Flow · L Loops · L Functions · L Lists & Dictionaries (+ sets, tuples) · L OOP Basics · 🔥 Type Hints · 🔥 Exceptions & Error Handling · 🔥 Modules, Packages & Project Layout |
| **W4 Flask Framework** | ✅ · L Routes & App Structure (app factory, blueprints) · L SQLAlchemy Connection · L Models · L Migrations · L Relationships · 🔥 Layered Architecture: Routes → Services → Repositories |
| **W5 API Development** | ✅ · L REST & GET · L POST/PUT/PATCH/DELETE · L Validation & Status Codes · L Error Handling & CRUD Review · 🔥 JWT Authentication · 🔥 Role-Based Access Control · 🔥 Pagination, Filtering & Sorting · 🔥 OpenAPI Docs · 🔥 Webhooks & Third-Party Integrations · 📋 CareerPilot Phase 2 checkpoint (replaces Build Day) |
| **W6 Quality Assurance & Deployment** | ✅ · L pytest Basics · L Testing Flask Endpoints · L Performance Testing with Locust · L Env Vars, Secrets & GitHub · L Deploying the Flask API · 🔥 Dockerizing a Flask App · 🔥 GitHub Actions CI Basics · 🔥 Logging · 🎤 Defend Your RevoShop · 📋 **CareerPilot Phase 2** final |

### Module 3 — Backend: FastAPI *(🔥 bonus)*
| Week | Lessons |
|---|---|
| **W1 Foundations** | Why FastAPI Exists · Type Hints & Pydantic v2 · Routing, Path/Query Params & Bodies · Automatic Docs & Validation |
| **W2 Core** | async/await: When It Helps and When It Doesn't · Dependency Injection · Database with SQLAlchemy 2.0 (and SQLModel) · JWT Auth |
| **W3 Real Apps** | Testing with pytest & TestClient · Project Structure for Real Apps · Background Tasks & Streaming Responses · Flask vs FastAPI Decision Guide · 📋 **CareerPilot Phase 3** (AI service) |

### Module 4 — Frontend: Next.js *(the bootcamp M3)*
| Week | Lessons |
|---|---|
| **W1 HTML, CSS, JavaScript** | ✅ · S HTML Structure & Semantics · S CSS Fundamentals · L Layout & Responsive Design · L JS Basics & Functions · L DOM & Events · L Arrays & Exercise · 🔥 Async JS: Promises, `fetch`, async/await · 🔥 Accessibility Basics |
| **W2 TypeScript & Tailwind** | ✅ · L TS Setup & Basics · L Interfaces, Type Aliases & Unions · S TS Arrays & Objects · S Tailwind Setup · L Typography, Responsive & Components · L Integration Patterns · 🔥 Generics (⚪) |
| **W3 React with Next.js** | ✅ · L Next.js Setup & Components · L Props & TS Interfaces · L State & Events · L Conditional Rendering & Lists · L Controlled Inputs · 🔥 Debugging React |
| **W4 App Router & APIs** | ✅ · L File-based Routing & Layouts · L Navigation · L Env Vars & Metadata · L API Integration & Errors · L Server vs Client Components · 🔥 Data Fetching & Caching · 🔥 TanStack Query |
| **W5 Forms & Auth** | ✅ · L Forms & Async Responses · L Client State & Auth Flow · L RBAC & Conditional Rendering · S Context API · S HTTP Methods from the Frontend · S Side Effects (`useEffect`) · 🔥 React Hook Form + Zod · 🔥 shadcn/ui · 🔥 Zustand (⚪) · 📋 CareerPilot Phase 4 checkpoint |
| **W6 QA & Deployment** | ✅ · L Playwright Setup · L E2E: Forms & Flows · L E2E: Navigation & Journeys · L Build Optimization · L Deployment · 🔥 Component Tests with Vitest + Testing Library · 🔥 Core Web Vitals (⚪) · 📋 **CareerPilot Phase 4** final |

### Module 5 — Cloud, DevOps & AWS *(🔥 bonus)*
> ⚠️ **Do not create an AWS account before this module.** New accounts (since July 15, 2025) get a credit-based free plan that ends after **6 months or when credits run out**.

| Week | Lessons |
|---|---|
| **W1 Containers** | Docker in Depth · Multi-stage Builds · Docker Compose: Full Stack Locally · Redis for Caching & Queues |
| **W2 CI/CD** | Pipeline Concepts · GitHub Actions: Lint → Test → Build → Push → Deploy · Environments (dev/staging/prod) · Secrets & OIDC to AWS |
| **W3 AWS Foundations** | 🚨 Account Safety: Root MFA, IAM, Budget Alarms · Regions & VPC Basics · EC2 · RDS · S3 & CloudFront · AWS ↔ GCP ↔ Azure Translation Table |
| **W4 Deploying to AWS** | Frontend: S3 + CloudFront / Amplify · Backend on EC2 · Containers on ECS · Lambda for Background Jobs · Parameter Store & Secrets Manager |
| **W5 Microservices** | Monolith First: When to Split · Service Boundaries & Data Ownership · Sync (REST) vs Async (SQS) · API Gateway · Distributed Tracing |
| **W6 Orchestration** | Kubernetes Concepts · Kubernetes Locally with `kind` · ECS/Fargate & EKS (🔴 concept) · Helm Intro |
| **W7 IaC & Operations** | Terraform Basics · Terraform for CareerPilot · Observability: Logs, Metrics, Traces, Alarms · Rollbacks, Blue/Green & Canary · Teardown & Cost Review · 📋 **CareerPilot Phase 5** |

Every hands-on AWS lesson: cost badge + 🧹 cleanup checklist.

### Module 6 — AI-Assisted Development *(the bootcamp M4, tool-agnostic)*
| Week | Lessons |
|---|---|
| **W1 AI Dev Lifecycle & Requirements** | L AI Development Lifecycle · L Requirements Gathering for AI Projects · L Spec-Driven Workflow (requirements → design → tasks) · L Reviewing AI-Generated Documents · L Iterating AI Output to Production Quality |
| **W2 Steering & Code Generation** | L How AI Coding Agents Work (Kiro, Claude Code, Cursor, Copilot) · L Steering Files & Context Management · L Prompting for Code Generation · L Reviewing AI-Generated Code · L Iterative Development with AI · 🔥 When AI Slows You Down: Skill Atrophy & Brain-First |
| **W3 Implementation, Testing & Deployment** | L Full-Stack AI App Development · L Frontend Pages & Advanced Features · L Integration & Error Handling · L E2E Testing & Environment Config · L Production Deployment & Documentation · 📋 **CareerPilot Phase 6** |

### Module 7 — AI Engineering in Production *(🔥 bonus)* · 🕒 all lessons carry "last reviewed"
| Week | Lessons |
|---|---|
| **W0 ML Foundations** (🔵 AI, ⚪ FS) | What Machine Learning Is · Training vs Inference · Overfitting & Evaluation Metrics · Hands-on: scikit-learn Classifier · Hands-on: Tiny PyTorch Model · Fine-tuning & LoRA Explained |
| **W1 How LLMs Work & LLM APIs** | Tokens, Context Window, Temperature · Choosing a Model (cost, latency, quality) · Chat API & Streaming · Structured JSON Output · Running Local Models with Ollama |
| **W2 Prompting & Tools** | Prompts as Code: Versioning & Testing · Tool / Function Calling · Guardrails · Prompt Caching |
| **W3 Embeddings & Search** | Embeddings Explained Simply · pgvector in PostgreSQL · Semantic Search · Hybrid Search |
| **W4 RAG in Depth** | RAG Architecture · Chunking Strategies · Retrieval & Reranking · Citations · Why RAG Fails and How to Fix It |
| **W5 Evaluation & Observability** | Why Evals · Test Datasets · LLM-as-Judge & Calibration · Evals Library (Ragas / DeepEval) · Tracing with Langfuse (traces vs spans) |
| **W6 Agents & MCP** | Agent Loop from Scratch · Multi-step Tools & State · MCP: Using and Building Servers · Rebuild with LangGraph · When NOT to Use an Agent · Multi-agent Patterns (⚪) · Voice & Browser Agents (⚪) |
| **W7 Production** | Prompt Injection & Security · Private Data Handling · Caching & Cost Control · Rate Limits, Retries & Fallbacks · AI on AWS: Bedrock |
| **W8 Decisions & Case Studies** | Prompting vs RAG vs Fine-tuning · Local vs Cloud Models · AI System Design · 🏭 Case studies (below) · 📋 **CareerPilot Phase 7** · 📋 **SupportDesk AI** |

**🏭 Case studies** (format: problem → architecture diagram → trade-offs → failure modes → success metrics):
1. Customer support assistant over help docs (RAG)
2. Document data extraction (invoices/receipts → JSON)
3. Semantic product/content search
4. AI code review bot in CI
5. Meeting & call summarization
6. Internal knowledge assistant
7. Operations agent with tools (ticket triage)

### Module 8 — Career & Portfolio *(the bootcamp Special + 🔥 bonus)* — unlocks at Milestone 1
L Enhancing Your Portfolio · GitHub Profile README · LinkedIn Profile (headline, About, Featured) · Learning in Public · Tech CV / Resume · Job Search Strategy (Indonesia + remote) · The Hiring Process · Behavioral Interviews (STAR) · Live Coding Interviews · System Design Interviews · Working in a Team: Git Workflow, Code Review, Agile · Salary Negotiation Basics

---

## 8. Parallel Tracks

### 🧩 DSA for Interviews (Python)
| Stage | Starts with | Topics |
|---|---|---|
| 1 Foundations | Module 1 | Big-O · How Memory Works · Recursion |
| 2 Core Structures | Module 2 W1 | Arrays & Strings · Hash Maps & Sets · Stacks & Queues · Linked Lists |
| 3 Patterns | Module 2 W4 | Two Pointers · Sliding Window · Prefix Sum · Binary Search · Sorting Patterns |
| 4 Trees & Graphs | Module 3 | Binary Trees · BST · Heaps · BFS/DFS · Basic Graph Problems |
| 5 Advanced (⚪) | Module 4+ | Backtracking · Greedy · Dynamic Programming (intro → common patterns) · Intervals |
| 6 Interview Skills | Milestone 1 | Hiring process for coding rounds · Step-by-step problem approach · Thinking out loud · When you're stuck |

**Each pattern lesson:** 3-part format + 🧭 "How to spot this pattern" card + problem set (3 easy · 2 medium · 1 stretch) with tests + 🔁 spaced review (intervals: 1 → 3 → 7 → 14 → 30 days).

### 🏛️ Architecture (Design Patterns + System Design)
| Stage | Starts with | Topics |
|---|---|---|
| A Principles | Module 1 | Clean Code · DRY/KISS/YAGNI · Naming · Single-purpose Functions · Coupling & Cohesion |
| B System Design Basics | Module 1 W0 | Client-Server · Latency vs Throughput · Vertical vs Horizontal Scaling · Availability · Load Balancers, Caches, CDNs |
| C OOP Design | Module 2 W3 | SOLID · Composition over Inheritance |
| D Design Patterns | Module 2 W3–W4 | Factory · Builder · Singleton (and why it's a trap) · Adapter · Decorator · Facade · Proxy · Strategy · Observer · Command · State · Template Method |
| E Backend Architecture | Module 2 W4 / Module 3 | Repository · Service Layer · Dependency Injection · Unit of Work · Layered → Clean/Hexagonal · Anti-patterns |
| F Data & API Design | Module 2 W5 | SQL vs NoSQL · Indexing · Replication · Sharding · REST vs GraphQL vs gRPC (+ hands-on GraphQL) · Pagination · Versioning · Idempotency · Rate Limiting · Caching with Redis |
| G Frontend Patterns | Module 4 | Container/Presentational · Custom Hooks · Compound Components · Where State Lives |
| H Distributed Systems | Module 5 | Queues · Eventual Consistency · Retries & Backoff · Circuit Breaker · Saga · CAP Simply |
| I System Design Practice | Module 5 + 7 | URL Shortener · Rate Limiter · Notification System · Chat App · File Upload Service · RAG System at Scale · LLM Gateway |
| J Interviews | Module 8 | System Design Interview Approach · Diagrams · Talking Trade-offs |

**Pattern lessons** show "💥 code without the pattern vs ✅ with it", and apply the pattern to CareerPilot where possible.

---

## 9. Portfolio Projects

Projects live in **their own public GitHub repos** (that's what recruiters see). The handbook only holds briefs, checkpoints and acceptance criteria.

Every project brief includes: goal · user stories · checkpoints · acceptance criteria · stretch goals · 🚀 LinkedIn checkpoint post · portfolio-ready checklist (README, architecture diagram, demo video/GIF, deployed link, tests passing).

### ⭐ CareerPilot — AI Job-Hunt Assistant
| Phase | Module | What you build | Key skills |
|---|---|---|---|
| 1 | M1 | **CLI:** analyze job listings from CSV (skill frequency, sorting, filtering, summary report) | Algorithms, functions, files |
| 2 | M2 | **REST API (Flask):** companies, applications, status pipeline, notes; JWT auth; tests; Docker; deployed | Flask, SQLAlchemy, Postgres, testing |
| 3 | M3 | **AI service (FastAPI):** CV vs job description matching — embedding similarity score + LLM feedback | FastAPI, Pydantic, LLM API, embeddings |
| 4 | M4 | **Frontend (Next.js):** dashboard, application pipeline board, CV match page; E2E tests | Next.js, TS, Tailwind, forms, auth |
| 5 | M5 | **Microservices on AWS:** `core-api` + `ai-service` + `worker` (SQS/Redis); CI/CD; Terraform; observability | Docker, GitHub Actions, AWS, Terraform |
| 6 | M6 | **New feature via spec-driven AI workflow** (e.g. follow-up reminders + company research notes); full E2E | AI-assisted development, code review |
| 7 | M7 | **Interview prep agent** (questions from JD, answer feedback) + RAG over your notes + evals + Langfuse tracing | Agents, RAG, evals, observability |

### 🧠 SupportDesk AI — Help-Desk Assistant (main standalone AI project, Module 7)
A support assistant for a **fictional company** with its own help docs.
- RAG over help docs with citations
- Tool calling: check order/ticket status from a mock API, create tickets
- Guardrails: refuse off-topic, detect prompt injection, protect private data
- **Human handoff** when confidence is low
- Admin view: conversations, feedback, failed answers
- Evals dataset + regression tests in CI; tracing
- Deployed with CI/CD

### 📚 StudyMind — AI Tutor (extra practice, open any time after Module 7 W4)
An AI tutor over **this handbook's content**: answers with citations, generates quizzes, tracks weak topics.

---

## 10. Lesson Format

### Frontmatter
The **file path** decides the lesson's id, module/week and URL:
`content/modules/m2/w4/01-flask-routes.md` → `/modules/m2/w4/01-flask-routes`. Files are ordered by name.

```yaml
---
title: "Flask Routes & App Structure"
summary: One sentence shown in lists and search (max 240 chars).
type: lesson                  # lesson | placement-check | project | case-study | career | guide
source: core                 # core | original (bonus)
sourceRef: "M2 · W4 · L1"      # only when source = core
split: false                  # true if split from a the bootcamp lesson
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: recommended }
durationMinutes: 150
tags: [flask, routing]
lastReviewed: 2026-09         # required for AI & cloud lessons
awsCost: free                 # free | small | concept (cloud lessons only)
draft: false                  # drafts only show during `npm run dev`
---
```
Frontmatter is validated with **Zod** by `npm run content:check`.

### Body template
```
━━━━━━━━━ PART 1 · LEARN THE CONCEPT ━━━━━━━━━
🎯 What you'll learn
🧠 The big idea (real-life analogy)
❓ Why does this exist?
💥 What happens if we DON'T use it?
📖 How it works (step by step + code)
⚖️ Trade-offs
✅ When to use it / 🚫 When NOT to use it
🏆 Best practices               (industry-standard checklist: conventions, tools, security, testing)
🏭 How it's used in industry
⚠️ Common mistakes
🔍 Find it in RevoShop          (Module 2 only)
🔄 In FastAPI…                  (Module 2 W4–W6 only)

━━━━━━━━━ PART 2 · EXPLAIN & DESIGN ━━━━━━━━━
🗣️ Explain it
📐 Design it
📝 Self-review checklist
🤖 Ask AI to review               (disabled slot until AI review is built)

━━━━━━━━━ PART 3 · TOY EXERCISE ━━━━━━━━━
🧸 Task  ·  🚫🤖 / 🤖✅ label
📦 Starter code  (browser editor or local folder link)
🧪 Automatic checks
💡 Hints (revealed one at a time)
🏆 Stretch goal

━━━━━━━━━ WRAP-UP ━━━━━━━━━
✅ Quick check (3 questions, answers hidden)
📝 My notes (saved locally)
📣 Share progress (only on weekly / milestone lessons)
📚 Keep learning (official docs)
```

### Bahasa key terms
Inline term component in Markdown, rendered as a highlighted term with a tooltip/aside:
```md
:term[Middleware]{id="perantara: kode yang berjalan di antara request dan route kamu"}
```
Every lesson also ends with a small **📖 Kamus (glossary)** of its key terms.

### Custom Markdown directives
| Directive | Renders |
|---|---|
| `:::tip` / `:::warning` / `:::danger` | Callout boxes |
| `:::revoshop` | 🔍 Find it in RevoShop box |
| `:::fastapi` | 🔄 In FastAPI… box |
| `:::hint` | Collapsible hint (one at a time) |
| `:::quiz` | Question with hidden answer |
| `:::sandpack{template="react-ts"}` | In-browser editor |
| `:::exercise{path="exercises/m1/w0/01-operators"}` | Local exercise card with run commands |
| `:::linkedin{type="weekly"}` | Share-progress template with copy button |
| `:::problem{id="…" title="…" difficulty="easy" path="…"}` | DSA problem card that joins the spaced review queue |
| `::::placement{id="modules/m1/w0"}` | Placement check (4 colons so quizzes can nest inside) |
| `::ai-review{task="explain"}` | Disabled AI review slot (future) |
| ` ```mermaid ` | Diagram |

---

## 11. Exercise System

### Where exercises run
| Kind | Runs in | Checks | Needs |
|---|---|---|---|
| JS / TS / React / Tailwind toys | Local folder `exercises/web/` (see D27, D28) | Vitest + jsdom + Testing Library; Playwright for E2E | Node 20.9+ |
| Quick playgrounds (ungraded) | Browser (**Sandpack**) | — | Internet |
| Python (M1, M2 core, DSA) | Local folder | `pytest` | Python 3.11+ |
| Flask / FastAPI | Local folder | `pytest` + API test client | Python 3.11+, sometimes Docker/Postgres |
| Next.js | Local folder | Vitest / Playwright | Node 20+ |
| Cloud | Local (Docker, `kind`, Terraform) or AWS | Checklist + scripted checks | Docker; AWS account from Module 5 |

### Local exercise layout
```
exercises/
├── README.md                 ← how to run any exercise
├── pyproject.toml            ← one Python env for all Python exercises (uv or pip)
├── m1/w0/01-operators/
│   ├── README.md             ← task, hints, stretch goal
│   ├── operators.py          ← you edit this (unique module name per exercise)
│   ├── test_operators.py     ← automatic checks
│   └── solution/             ← reference solution (open only after trying)
└── dsa/stage-3/two-pointers/…
```
Run: `cd exercises && uv run pytest m1/w0/03-operators`

Project starter kits (`exercises/projects/…`) have acceptance tests but **no** solution folder.

### Placement checks
3–5 explain/design questions + 1 small coding task per week. Self-assessed with a rubric: **pass → skip to toy exercises; not yet → study the week.**

### AI policy
- 🚫🤖 **No-AI:** fundamentals (M1, M2 core, DSA, core patterns). Use AI only *after* you finish, for review.
- 🤖✅ **AI-allowed:** integration-heavy tasks, Module 6 onward. Rule: you must be able to explain every line.

---

## 12. LinkedIn: Learning in Public

| When | Post type | Template id |
|---|---|---|
| Every lesson | 📝 Private note in the app (no post) | — |
| Every week | 📣 Weekly recap | `weekly` |
| Selected concepts | 💡 "Explained simply" (reuse Part 2 explain exercise) | `concept` |
| DSA milestones | 🧩 Pattern + problem solved | `dsa` |
| Project checkpoint | 🚀 Build in public (screenshot/GIF) | `build` |
| Module finished | 🎓 Reflection | `reflection` |
| Milestone reached | 🎯 Open to work / skills summary | `milestone` |

Each template: filled-in draft with topic info · copy button · tips (hook, structure, visual, hashtags) · reminder to rewrite in your own voice · reminder **not to share the bootcamp paid material**.

Module 8 adds: LinkedIn profile guide, GitHub profile README template, portfolio README template.

*The app only provides templates. You post yourself.*

---

## 13. Milestones, Timeline & Weekly Schedule

### Job-ready milestones (at ~18 h/week)
| Milestone | Scope | Hours left | Estimated time |
|---|---|---|---|
| 🎯 **1. Junior Full-Stack** — start applying | M1 · M2 · M4 core · basic deploy · DSA Stages 1–3 · Architecture A–E · CareerPilot Phases 1, 2, 4 deployed · LinkedIn & GitHub profiles | ~320–370 h | **~4–5 months** |
| 🎯 **2. AI-Integrated Full-Stack** | + M3 FastAPI · **M6 AI-Assisted Dev** · M7 W1–W5 core · DSA Stage 4 · SupportDesk AI · CareerPilot Phases 3 & 6 | +~250 h | **~7–8 months** |
| 🎯 **3. Stronger candidate** | + M5 Cloud · Architecture F–I · M7 W6–W8 · ML Foundations · CareerPilot Phases 5–7 | +~300–400 h | **~11–13 months** |
| 🌱 Keep growing | DSA Stage 5 · optional deep dives · StudyMind | ongoing | — |

Note: Milestone 1 skips ahead to Module 4 core before Module 3 so a full-stack portfolio exists sooner. The app's schedule follows this order; the sidebar keeps module numbers.

### Default weekly schedule (3 h/day, 6 days)
| Day | Plan |
|---|---|
| Mon–Fri | 2 h module lesson + 1 h DSA |
| Sat | 1.5 h Architecture + 1.5 h CareerPilot |
| Sun | Light: DSA spaced review + weekly LinkedIn post, or rest |

The **Study Plan** page (`/schedule`) makes this flexible (D34): Settings hold a **daily target** (default 5 h), a **minimum that still counts** (default 1 h) and **study days** (5/6/7). Each day the learner picks how much time they really have; the page splits it by the routine above (weekdays 65% module / 35% DSA, Saturday Architecture + CareerPilot, Sunday module + DSA review), shows the next lessons that fit, logs real study time (timer or +15/30/60 min buttons), and charts the week with an honest recent average. Milestone cards turn `hours` (per milestone, in `course.json`) minus finished lessons into an apply-by estimate at the target pace and, after 5+ logged study days, at the real recent pace.

---

## 14. App Architecture

### Tech stack
| Concern | Choice | Learning note |
|---|---|---|
| Build / dev server | Vite | Why a bundler exists; env files; `import.meta.glob` |
| UI | React 19 + TypeScript (strict) | Components, props, hooks, types |
| Styling | Tailwind CSS v4 + `@tailwindcss/typography` | Utility-first CSS; dark mode |
| Routing | React Router v8 (data router) | Nested routes, URL params |
| Markdown | `react-markdown` + `remark-gfm` + `remark-directive` + `rehype-slug` | The unified/remark/rehype pipeline |
| Code highlighting | Shiki | |
| Diagrams | Mermaid | |
| Frontmatter validation | `yaml` + Zod | Runtime validation vs static types |
| Search | Fuse.js | Fuzzy search, building an index |
| In-browser editor | Sandpack | |
| State & persistence | React Context + custom hooks + `localStorage` | No state library on purpose (explained in docs) |
| Tests (app) | Vitest | Testing pure functions |
| Quality | ESLint + Prettier | |

### Features
| Feature | Build milestone |
|---|---|
| Layout: sidebar (module → week → lesson), top bar, table of contents | B1, B3 |
| Dark mode | B1 |
| Markdown rendering + all directives | B2 |
| Role labels, 🎯 target role selector, role filter, per-role progress | B3 |
| Mark as done, progress bars, reading time, prev/next | B3 |
| Search (Ctrl/Cmd + K) | B3 |
| My notes per lesson | B3 |
| Placement checks, hints, quizzes | B4 |
| Sandpack editor, local exercise cards | B4 |
| LinkedIn template cards with copy | B4 |
| DSA spaced review queue | B4 |
| Home dashboard: milestone progress, this week's plan | B5 |
| Schedule page | B5 |
| Projects pages | B5 |
| AI review | Later (§18) |

### Routes
| Path | Page |
|---|---|
| `/` | Dashboard |
| `/roadmap` | Course map + milestones |
| `/modules/:moduleId` | Module overview |
| `/modules/:moduleId/:weekId/:lessonSlug` | Lesson |
| `/tracks/dsa`, `/tracks/architecture` | Track overviews |
| `/tracks/dsa/review` | Spaced review queue |
| `/projects/:projectId` | Project brief |
| `/schedule` | Weekly plan |
| `/settings` | Target role, theme, reset progress, export/import progress (JSON) |

### Folder structure
```
fsse-handbook/
├── README.md
├── .env.example
├── .gitignore
├── package.json
├── tsconfig.json
├── vite.config.ts
├── docs/
│   ├── IMPLEMENTATION_PLAN.md
│   ├── MARKET_CHECK.md
│   ├── HANDBOOK.md
│   ├── LEARN_THE_CODEBASE.md
│   └── ADDING_CONTENT.md
├── content/
│   ├── outline.json             ← the bootcamp outline (titles only)
│   ├── course.json              ← handbook structure: modules, weeks, tracks, order
│   ├── modules/m1/w0/01-how-the-web-works.md
│   ├── tracks/dsa/…  tracks/architecture/…
│   ├── projects/careerpilot.md …
│   └── career/…
├── exercises/                   ← local exercises (see §11) + projects/ starter kits
├── scripts/
│   ├── content-check.ts         ← validates frontmatter, links, exercise folders
│   ├── check-exercises.sh       ← every starter fails, every solution passes
│   └── vite-plugin-lesson-meta.ts ← `.md?meta` imports return validated metadata only
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── routes.tsx
    ├── types/                   ← Lesson, Module, Role, Progress…
    ├── content/                 ← loader, schema (Zod), search index
    ├── components/
    │   ├── layout/              ← Sidebar, TopBar, TableOfContents
    │   ├── markdown/            ← Callout, Term, Hint, Quiz, SandpackBlock, ExerciseCard, LinkedInCard, Mermaid
    │   └── ui/                  ← Badge, RoleBadges, ProgressBar, Button
    ├── hooks/                   ← useProgress, useTargetRole, useTheme, useNotes, useSearch, useReviewQueue
    ├── pages/
    ├── lib/                     ← storage, schedule, spaced-repetition, reading-time
    └── styles/
```

### Key types (preview)
```ts
type RoleCode = 'be' | 'fe' | 'fs' | 'ai' | 'ops'
type Level = 'core' | 'recommended' | 'optional' | 'none'
type RoleLabels = Record<RoleCode, Level>

type LessonMeta = {
  id: string
  title: string
  module: string
  week: string
  order: number
  type: 'lesson' | 'placement-check' | 'project' | 'case-study' | 'career'
  source: 'core' | 'original'
  sourceRef?: string
  roles: RoleLabels
  durationMinutes: number
  tags: string[]
  lastReviewed?: string
  awsCost?: 'free' | 'small' | 'concept'
}
```

### Code teaching style
- Every file starts with a header comment: *what this file does* + *which concept it teaches*.
- Comments explain **why**, not what.
- No clever tricks; readable over short.

---

## 15. Ports & Environment Config

| Variable | Service | Normal default | Ours |
|---|---|---|---|
| `HANDBOOK_PORT` | Handbook dev server | 5173 | **5391** |
| `HANDBOOK_PREVIEW_PORT` | Handbook preview | 4173 | **4391** |
| `FLASK_PORT` | Flask exercises | 5000 | **5091** |
| `FASTAPI_PORT` | FastAPI exercises | 8000 | **8091** |
| `NEXT_PORT` | Next.js exercises | 3000 | **3091** |
| `POSTGRES_PORT` | Postgres (Docker) | 5432 | **5491** |
| `REDIS_PORT` | Redis (Docker) | 6379 | **6391** |
| `LANGFUSE_PORT` | Langfuse (Docker) | 3000 | **3191** |
| `OLLAMA_URL` | Ollama | `http://localhost:11434` | kept (Ollama's own service) |

- `.env.example` is committed; `.env` / `.env.local` are git-ignored.
- Vite uses `strictPort: true` → a clear error instead of silently picking another port.
- Port 5000 is also used by macOS AirPlay Receiver — another reason to avoid it.

---

## 16. Documentation Set

| File | Contents |
|---|---|
| `README.md` | What this is · requirements · install · run (`npm run dev` → `http://localhost:5391`) · build/preview · exercises setup · changing ports · push to a private GitHub repo · troubleshooting |
| `docs/HANDBOOK.md` | Simple explanation of the handbook · roadmap diagram · roles & labels · how to study (placement checks, brain-first, spaced review) · milestones |
| `docs/LEARN_THE_CODEBASE.md` | Guided tour: Vite → `main.tsx` → routing → components & props → types → hooks → Tailwind → Markdown pipeline → persistence |
| `docs/ADDING_CONTENT.md` | Add/edit a lesson · frontmatter fields · directives · ordering · `npm run content:check` |
| `docs/MARKET_CHECK.md` | Job-market findings, sources, date · how to refresh |
| `docs/IMPLEMENTATION_PLAN.md` | This file |

---

## 17. Build Plan (Implementation Milestones)

✋ = stop for learner review.

### B0 — Plan ✋
- [x] Map the bootcamp outline → `content/outline.json`
- [x] Market check → `docs/MARKET_CHECK.md`
- [x] Learner approves this plan

### B1 — App skeleton
- [x] Vite + React 19 + TS strict + Tailwind v4 + ESLint/Prettier
- [x] `.env.example`, port config, `strictPort`
- [x] Layout shell: sidebar, top bar, content area, dark mode
- [x] React Router routes with placeholder pages
- [x] Teaching comments in every file
- [x] `.gitignore`

### B2 — Content pipeline
- [x] `content/course.json` structure + TS types
- [x] Markdown loader via `import.meta.glob`
- [x] Frontmatter parsing + Zod schema
- [x] Markdown renderer: GFM, headings/anchors, Shiki, Mermaid
- [x] Directives: callouts, term, hint, quiz, revoshop, fastapi
- [x] `npm run content:check`
- [x] Sample lesson exercising every component
- [x] Vitest tests for loader & schema

### B3 — Navigation & progress
- [x] Sidebar from `course.json` + role badges
- [x] 🎯 Target role selector (incl. ⭐ AI-FS) + filter/highlight
- [x] Mark as done, per-role progress, reading time, prev/next, table of contents
- [x] Search (Ctrl/Cmd + K)
- [x] My notes
- [x] Settings: export/import/reset progress

### B4 — Exercises & engagement
- [x] Sandpack block with tests
- [x] Local exercise card + `exercises/` Python env + first pytest exercise
- [x] Placement check component
- [x] LinkedIn template card
- [x] DSA spaced review queue
- [x] AI review slot (disabled)

### B5 — Module 1 content + dashboard ✋
- [x] Module 1: W0 + W1 lessons, placement checks, exercises
- [x] DSA Stage 1 lessons + problem sets
- [x] Architecture Stages A–B lessons
- [x] CareerPilot brief + Phase 1
- [x] LinkedIn templates for Module 1
- [x] Dashboard, roadmap, schedule, project pages
- [x] **Learner reviews tone, depth, format** (approved; asked for best-practice sections → D24)

### B6 — Docs & repo ✋
- [x] README, HANDBOOK, LEARN_THE_CODEBASE, ADDING_CONTENT
- [x] Final run-through: fresh install → `npm run dev` works
- [x] `git init` + first commit (**push only when learner asks**)

### Content batches (after B6, each ends with ✋ review)
| Batch | Content |
|---|---|
| C1 | Module 2 (+ 🔍 RevoShop boxes, 🎤 Defend Your RevoShop) · DSA Stages 2–3 · Architecture C–E · CareerPilot Phase 2 |
| C2 | Module 4 · Architecture G · CareerPilot Phase 4 · Module 8 (Milestone 1 career lessons) |
| C3 | Module 3 · DSA Stage 4 · CareerPilot Phase 3 |
| C4 | Module 7 W1–W5 · SupportDesk AI |
| C5 | Module 5 · Architecture F, H, I (part) · CareerPilot Phase 5 — **moved up (D30)**: C5a = W1–W2 + 🚀 Ship RevoShop labs 1–2 ✋ · C5b = W3–W7 + tracks + Phase 5 |
| C6 | Module 6 · CareerPilot Phase 6 |
| C7 | Module 7 W0, W6–W8 · case studies · Architecture I (AI) · CareerPilot Phase 7 · StudyMind |
| C8 | DSA Stages 5–6 · Architecture J · remaining Module 8 |

#### C1 — progress
- [x] Module 2 W1–W6 lessons, placement checks, exercises, 🔍 RevoShop boxes, weekly LinkedIn templates
- [x] 🎤 Defend Your RevoShop + Module 2 reflection template
- [x] CareerPilot Phase 2 brief + starter kit (113 acceptance tests)
- [x] DSA Stage 2 (4 lessons) and Stage 3 (5 lessons), 36 problems
- [x] Architecture Stages C (2), D (4), E (3) with exercises
- [x] **Learner reviews C1** ✋ (approved — "u can continue")

#### C2 — progress
- [x] Module 4 W1–W6: lessons, placement checks, weekly LinkedIn templates, 44 web exercises (Vitest; W6 adds Playwright)
- [x] Mutation-graded test-writing exercises for the frontend (Playwright mini app with 17 mutants, component tests with 9 mutants)
- [x] Architecture Stage G (4 lessons) with exercises
- [x] CareerPilot Phase 4 brief + starter kit (mock Phase 2 API, 23 Playwright acceptance tests, validated against a private reference app)
- [x] Module 8 W1 (portfolio, GitHub, LinkedIn, learning in public, CV) and W2 (job search, hiring process, STAR, live coding, system design, teamwork, salary negotiation)
- [x] **Learner reviews C2** ✋ (asked to continue with Module 5)

#### C5a — progress
- [x] Module 5 W1 Containers: lessons, placement check, exercises (Dockerfile auditor, targets/tags, Compose, Redis patterns), RevoShop smoke-test tool, 🚀 Ship RevoShop 1 (validated on a scratch copy)
- [x] Module 5 W2 CI/CD: lessons, placement check, exercises (DORA metrics, CI/CD workflow, env parity, OIDC trust policy), 🚀 Ship RevoShop 2
- [x] 🔍 RevoShop boxes in every Module 5 lesson (learner request) — continue in W3–W7
- [x] **Learner reviews C5a** ✋ (approved: "u can continue for week 3 and 4")

#### C5b — progress (part 1: Weeks 3–4)
- [x] Module 5 W3 AWS Foundations: 6 lessons + RevoShop boxes, 5 exercises (IAM simulator, cost guard, VPC & security groups, cloud-init, S3/RDS secrets with moto), 🚀 Ship RevoShop 3 (EC2 + RDS + HTTPS; deploy scripts tested locally incl. rollback)
- [x] Module 5 W4 Deploying to AWS: 5 lessons + RevoShop boxes, 5 exercises (static sync plan, blue/green, ECS task definition, Lambda jobs, SSM config loader), 🚀 Ship RevoShop 4 (ECS Fargate + ALB + OIDC deploys + teardown)
- [ ] **Learner reviews W3–W4** ✋

#### C5b — progress (part 2: Weeks 5–7 + Phase 5)
- [x] Module 5 W5 Microservices: 5 lessons + RevoShop boxes, 5 exercises (should-split, data-ownership, idempotent consumer, gateway routing, trace bottleneck) — plain-language style, EN + ID
- [x] Module 5 W6 Orchestration: 4 lessons (Kubernetes concepts, kind local, ECS/Fargate/EKS, Helm), 2 exercises (reconcile control loop, Helm render) — EN + ID
- [x] Module 5 W7 IaC & Operations: 5 lessons (Terraform basics, Terraform for CareerPilot, observability, rollbacks/blue-green/canary, teardown & cost review), 4 exercises (terraform plan, evaluate alarms, canary decision, cost review) — EN + ID
- [x] CareerPilot Phase 5 brief (deploy to AWS with Terraform — ECS Fargate + RDS + IaC + observability + teardown) — EN + ID
- [ ] Architecture stages F (Data & API Design), H (Distributed Systems), I (System Design Practice) — still to write

Batch order follows the **milestone path**, not module numbers.

---

## 18. Future: AI Review

Designed now, built later.

```ts
interface ReviewProvider {
  id: 'ollama' | 'gemini' | 'openrouter' | 'groq'
  review(input: { lessonId: string; task: string; answer: string; rubric: string[] }): Promise<ReviewResult>
}
```

| Option | Cost | Privacy | Notes |
|---|---|---|---|
| **Ollama (first)** | Free | 100% local | Needs `OLLAMA_ORIGINS` set so the browser can call it |
| Gemini free tier | Free with limits | Sent to Google | API key in `.env.local` |
| Groq / OpenRouter free models | Free with limits | Sent to provider | API key in `.env.local` |

- Enabled with `VITE_AI_REVIEW_ENABLED=true`.
- Review uses the lesson's self-review rubric → consistent feedback.
- ⚠️ Keys in a Vite app are visible in the browser. Fine for **local-only** use; never deploy the handbook publicly with keys.

---

## 19. Out of Scope

- Copying the bootcamp lesson content, assignments or branding
- Login, user accounts, backend for the handbook
- Deploying the handbook publicly
- Posting to LinkedIn automatically
- Project source code inside this repo (projects live in their own repos)
- Mobile app

---

## 20. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Scope is huge → learner burnout | Role labels, ⚪ optional tags, milestone path, apply at Milestone 1 |
| AI/cloud content goes stale | `lastReviewed` dates, `MARKET_CHECK.md` refresh every few months |
| AWS surprise bill | No account until Module 5, budget alarms first, cost badges, cleanup checklists, Kubernetes locally |
| Understanding stays shallow (AI dependence) | Brain-first rule, No-AI labels, explain & design exercises, Defend Your RevoShop |
| Sandpack needs internet | Local exercise alternative for key JS/TS exercises |
| Content errors | Runnable examples with tests; learner review at every ✋ checkpoint |
| Private data in repo | `.env*` git-ignored; no credentials anywhere in content or code |
