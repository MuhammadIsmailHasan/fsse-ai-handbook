---
title: "Learning in Public"
summary: Share your progress in a way that builds credibility — what to post, a weekly rhythm, writing clearly about what you learned and broke, turning posts into proof, avoiding hype and oversharing, and measuring what matters.
type: career
source: original
roles: { be: recommended, fe: recommended, fs: recommended, ai: recommended, ops: recommended }
durationMinutes: 90
tags: [career, linkedin, writing, personal-brand, community]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What **learning in public** is and why it works for career switchers
- Post types: weekly progress, concept explainers, "I broke it / I fixed it", build updates, milestones
- A sustainable **weekly rhythm** (the handbook's LinkedIn templates)
- Writing posts people read: hook, specifics, lesson, question
- Using AI for writing **without** sounding generic
- What not to share (secrets, company info, negativity) and measuring results

## 🧠 The big idea

Learning in public is a **gym logbook shared with friends**. Nobody expects you to lift the heaviest weights — they notice that you show up every week, record what you did, and get stronger. Over months, the logbook becomes proof of consistency that a CV can't show.

## ❓ Why does this matter?

Recruiters and engineers rarely see how you think. Short, honest posts about real problems ("my list endpoint ran 21 SQL queries — here's the fix") demonstrate understanding, communication and persistence. Posts also create conversations with engineers who later become referrals.

## 💥 What happens if we DON'T (or do it badly)?

- Silence: 6 months of work invisible until the CV.
- Hype: "I built a SaaS in 2 hours with AI 🚀🔥" — attracts likes, not hiring managers.
- Certificate-only posts with no substance.

## 📖 How it works, step by step

### 1. Post types (templates are in every week's lessons)

| Type | Example hook | Frequency |
|---|---|---|
| **Weekly** | "Week 5: forms, authentication and 'who can do what' in Next.js." | weekly |
| **Concept** | "Why hiding a button isn't authorization." | every 2 weeks |
| **Debugging story** | "My tests passed and the app was still broken. The bug: …" | when it happens |
| **Build** | "CareerPilot Phase 4 is live." | per milestone |
| **Reflection** | "3 things I'd tell myself on day 1 of learning to code." | monthly |

### 2. The anatomy of a good post

```text
[Hook — 1 line, specific]
My job list endpoint ran 21 SQL queries for 20 rows.

[Context — what you were doing]
Building the applications API for CareerPilot (Flask + SQLAlchemy).

[What happened + how you found it]
Turned on SQL logging: 1 query for the list, then 1 per row to load the company. Classic N+1.

[Fix + result]
selectinload(Application.company) → 2 queries. p95 from 180 ms to 35 ms in my Locust test.

[Lesson]
Relationship access in a loop is a hidden query. Log SQL before you optimize anything.

[Question / call to action]
What's the sneakiest performance bug you've found?

#Python #SQLAlchemy #BackendDevelopment
```

- One idea per post. Short paragraphs. Code as a screenshot or a short snippet.
- Numbers and specifics > adjectives.
- 3–5 relevant hashtags, not 20.

### 3. A sustainable rhythm

- **Friday, 20 minutes**: fill the weekly template from your *My notes*.
- **Every other week**: one concept or debugging post.
- **Reply** to comments within a day; comment thoughtfully on 3 posts by engineers each week.
- Batch drafts; it's fine to schedule posts.

### 4. Using AI well

Use AI to **tighten** your draft (shorter, clearer, check grammar in English), not to invent experiences. Keep your voice: specific details, your mistakes, your numbers. Delete clichés like "thrilled to announce", "game-changer", "delve".

### 5. What not to share

- Secrets, internal company code, customer data, screenshots with tokens.
- Negative posts about bootcamps, teachers, employers or interviewers.
- Claims you can't back up ("expert", "10x").
- Personal details (home address, phone) and other people's info without consent.

### 6. Measure what matters

Likes are noisy. Track: profile views from recruiters, meaningful comments from engineers, connection requests from your target companies, conversations that turned into referrals or interviews.

## ⚖️ Trade-offs

| | ✅ | ❌ |
|---|---|---|
| Posting weekly | consistency, compounding visibility | time; pressure to post filler |
| Long blog articles | depth, SEO, portfolio pieces | slower; fewer readers at first |
| Short LinkedIn posts | reach where recruiters are | shallow if not careful |
| Posting in Bahasa Indonesia vs English | local community vs global reach | choose per goal; English helps for remote roles |

## 🏆 Best practices

- [ ] Share real work with specifics: problem, approach, result, lesson.
- [ ] Post on a rhythm you can keep (weekly template + occasional deep post).
- [ ] Engage genuinely with others; answer comments.
- [ ] Link to code, demos or write-ups when possible.
- [ ] Keep it honest and humble; credit people and resources.
- [ ] Never post secrets, company internals or private data.
- [ ] Review AI-polished text so it still sounds like you.

## 🏭 How it's used in industry

- Developer advocates and many senior engineers built careers through writing and talks; for juniors, the same habit signals communication skills.
- Hiring managers sometimes reference a candidate's post in interviews ("tell me more about that N+1 bug").
- Tech communities in Indonesia (meetups, Discord/Telegram groups, LinkedIn) share job leads with members they know.

## ⚠️ Common mistakes

- Only posting certificates and "Day 47 of #100DaysOfCode" without content.
- Engagement-bait questions unrelated to the post.
- Copy-pasting AI posts that sound like everyone else's.
- Giving up after two weeks because posts got few likes.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain the gym logbook analogy to a friend who feels they "aren't good enough yet" to post.

## 📐 Design it

Plan the next 4 weeks: one weekly post per week (use the handbook templates) plus two deeper posts (concept or debugging). For each deeper post write the hook, the specific numbers/details you'll include and the question you'll end with.

:::quiz
Show an example plan

| Week | Weekly post | Deeper post |
|---|---|---|
| 1 | M4 W5 template (forms, auth, RBAC) | **Concept:** "Hiding a button isn't authorization" — show the Server Action check; end with "How does your team test permissions?" |
| 2 | M4 W6 template (testing, deploy) | — |
| 3 | Phase 4 build post | **Debugging:** "My Playwright tests found a bug my unit tests missed" — the mutant that survived, the assertion that killed it; end with "What's your favorite E2E testing habit?" |
| 4 | Reflection: Milestone 1 reached | — |
:::

### 📝 Self-review checklist

- [ ] Every deeper post has specific details
- [ ] Rhythm fits your study schedule
- [ ] Nothing confidential

::ai-review{task="explain"}

::part[Practice]{n="3"}

## 🛠️ Do it

1. Write and publish one debugging or concept post from your recent work.
2. Schedule next week's weekly post.
3. Comment thoughtfully on 3 posts by engineers.

## ✅ Done when

- [ ] One substantive post published
- [ ] A 4-week posting plan saved in *My notes*
- [ ] You replied to every comment on your post

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Learning in public | Belajar secara terbuka (berbagi proses) |
| Hook | Kalimat pembuka yang menarik |
| Engagement | Interaksi (komentar, reaksi) |
| Consistency | Konsistensi |
| Call to action | Ajakan bertindak |
