---
title: "GitHub Profile README"
summary: Make your GitHub profile work for you — the profile README, pinned repos, a clean contribution story, repository hygiene, commit messages, and what to avoid (stat-card clutter, fake activity, leaked secrets).
type: career
source: original
roles: { be: core, fe: core, fs: core, ai: core, ops: core }
durationMinutes: 90
tags: [career, github, profile, open-source, personal-brand]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What a recruiter and an engineer see on `github.com/<you>` in the first 10 seconds
- Writing a **profile README** (the special `<username>/<username>` repo)
- **Pinned repositories**, repo descriptions, topics and website links
- Repository hygiene: README, license, `.gitignore`, no secrets, releases/tags
- Commit messages and history that tell a story
- Small, real **open-source contributions** for juniors

## 🧠 The big idea

Your GitHub profile is a **shop window**. People walking past decide in seconds whether to come in. A clean window with three well-lit products (pinned projects) and a small sign saying what you sell (profile README) beats a window piled with everything in the warehouse.

## ❓ Why does this matter?

Your CV and LinkedIn link to GitHub. For developers without years of experience, GitHub is where claims become evidence: real code, tests, commit habits and how you write documentation.

## 💥 What happens if we DON'T?

- Profile shows six forks and a "hello world" repo pinned.
- A profile README full of animated banners, 30 technology badges and stat cards — but no link to a single project.
- An old repo with a committed `.env` file containing a real API key (bots scan GitHub for these within minutes).

## 📖 How it works, step by step

### 1. The profile README

Create a public repo named exactly like your username; its `README.md` appears on your profile.

```markdown
# Hi, I'm Muhammad Ismail 👋

Full-stack developer (Python · TypeScript) based in Indonesia, building products end to end — APIs, web apps and AI features.

🔭 **Currently building:** [CareerPilot](https://github.com/<you>/careerpilot) — a job-hunt assistant (Flask API + Next.js, 130+ tests, Docker, CI)
🛒 **Backend project:** [RevoShop](https://github.com/<you>/revoshop) — e-commerce API with Midtrans payments and RBAC
🌱 **Learning:** system design, RAG and LLM evaluation

**Stack:** Python, Flask, FastAPI, PostgreSQL, TypeScript, React, Next.js, Docker, GitHub Actions

📫 [LinkedIn](https://linkedin.com/in/<you>) · [Email](mailto:you@example.com) · Open to junior backend/full-stack roles (Jakarta or remote)
```

Keep it short: who you are, what you build, 2–3 links, how to reach you. One small stats card is fine; a wall of badges isn't.

### 2. Pins, descriptions, topics

- Pin up to 6 repos — show your 2–3 flagships first.
- Every repo: a one-line **description**, **topics** (`nextjs`, `flask`, `postgresql`), and the **website** field with the live URL.
- Archive repos you don't maintain (they stay visible but marked read-only), or make them private.

### 3. Repository hygiene checklist

| File / setting | Why |
|---|---|
| `README.md` | what, why, how to run and test |
| `LICENSE` (e.g. MIT) | tells others how they may use it |
| `.gitignore` | no `node_modules`, `.env`, `__pycache__` |
| `.env.example` | shows config without secrets |
| CI workflow + badge | proof of tests |
| Tags/releases (`phase-2`, `v1.0.0`) | milestones and changelog |
| Secret scanning / push protection | GitHub can block pushes containing known secret formats — keep it on |

If you ever committed a secret: **rotate it first** (revoke the key), then remove it from history. Deleting the file in a new commit doesn't remove it from history.

### 4. Commits that tell a story

```text
feat(api): add status transition rules with history
fix(web): keep typed values after server validation errors
test(api): cover invalid transitions and ownership 404s
docs: add architecture diagram and decisions to README
```

- Small commits with **Conventional Commits** style prefixes (`feat`, `fix`, `test`, `docs`, `refactor`, `chore`).
- Work in branches and merge through pull requests even when solo — reviewers can see how you break work down.
- Don't fake activity (scripts that commit daily). Engineers notice, and it signals the wrong values.

### 5. Open source for juniors

Realistic first contributions: fix a typo or unclear step in docs you used, add a missing test, reproduce a bug with a minimal example, translate docs to Bahasa Indonesia. Look for `good first issue` labels, read `CONTRIBUTING.md`, and keep PRs small.

## ⚖️ Trade-offs

| | ✅ | ❌ |
|---|---|---|
| Minimal profile README | fast to read, professional | less "personality" |
| Heavy stat cards/badges | colorful | slow, noisy, says little about ability |
| All repos public | transparency | exposes unfinished/embarrassing work; archive instead |
| Contribution graph focus | shows consistency | easy to game; not a hiring signal on its own |

## 🏆 Best practices

- [ ] Profile README: one-paragraph intro, current flagship, stack, contact, availability.
- [ ] 2–3 flagship repos pinned, each with description, topics and live link.
- [ ] Every public repo has a README; unmaintained ones archived.
- [ ] No secrets in any repo or history; push protection enabled; `.env.example` instead.
- [ ] Clear commit messages; PRs for features; tags for milestones.
- [ ] Same name, photo and headline as LinkedIn for recognisability.
- [ ] Use a professional email for commits (or GitHub's noreply address for privacy).

## 🏭 How it's used in industry

- Hiring managers often open 1–2 repos and read the README, a test file and a core module.
- Some companies source candidates by searching GitHub for technologies and locations.
- Open-source maintainers' PR reviews are public — thoughtful discussion there is visible evidence of collaboration skills.

## ⚠️ Common mistakes

- A profile README longer than any project README.
- Forks of popular repos pinned as if they were your work.
- Private flagship repos while the CV says "see my GitHub".
- Personal phone number and home address in a public README.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain the shop-window idea and why "30 badges" doesn't help a recruiter decide to call you.

## 📐 Design it

Draft your profile README (≤ 15 lines) and list: which 3 repos you'll pin and in which order, their one-line descriptions and topics, and which repos you'll archive.

:::quiz
Show a quality bar

- **Intro** names your role target and location/remote preference in one sentence.
- **Links** go to working projects, not to "coming soon".
- **Pins:** CareerPilot (full-stack story) → RevoShop (backend depth) → one supporting project. Descriptions start with *what it does*, not the stack: "Job-hunt tracker with a hiring pipeline — Flask API + Next.js, 130+ tests".
- **Topics:** 5–8 accurate ones per repo.
- **Archive:** tutorials, forks without changes, abandoned experiments.
:::

### 📝 Self-review checklist

- [ ] Readable in 10 seconds
- [ ] Every link works
- [ ] Nothing private or secret exposed

::ai-review{task="explain"}

::part[Practice]{n="3"}

## 🛠️ Do it

1. Create `<username>/<username>` and publish your profile README.
2. Update pins, descriptions, topics and website fields.
3. Run a secret scan on your flagship repos (e.g. `gitleaks detect`) and enable push protection.
4. Add a `LICENSE`, `.env.example` and CI badge where missing.

## ✅ Done when

- [ ] Profile README live and linked from LinkedIn
- [ ] Flagships pinned with descriptions, topics and live links
- [ ] Secret scan clean on all public repos

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Profile README | README profil GitHub |
| Pinned repository | Repositori yang disematkan |
| Push protection | Perlindungan saat push (blokir rahasia) |
| Conventional Commits | Format standar pesan commit |
| Good first issue | Isu yang cocok untuk kontributor pemula |
