# Plain-language rewrite — plan, progress and handoff

**Goal.** Rewrite every lesson so it is easy to read for a learner whose first language is not English: fewer jargon terms, every term explained in one simple sentence, **more everyday analogies**, shorter sections — without losing technical accuracy, the 3-part structure, exercises or 🏆 Best practices. Rules: [`WRITING_STYLE.md`](WRITING_STYLE.md). Indonesian rules: [`TRANSLATION_GUIDE.md`](TRANSLATION_GUIDE.md). Decision entry: D35 in [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md).

**Order requested by the learner:** Module 4 (frontend) → Module 5 (deployment) → other modules → then new material (C5b part 2). Module 8 is low priority.

---

## 1. What "done" means for one lesson

A lesson counts as done only when **all** of these are true:

1. The English file follows the style rules below.
2. A `<lesson>.id.md` exists with a `sourceHash` matching the English file.
3. `npm run -s content:check` passes.
4. Mermaid diagrams parse (if the lesson has any).
5. It is committed with the standard trailers.

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

| Area | Total | Rewritten + translated | Status |
|---|---|---|---|
| Module 4 (frontend) | 50 | 50 | ✅ done |
| Module 5 (deployment) | 27 | 5 | 🚧 in progress |
| Module 1 | 14 | 0 | ⬜ |
| Module 2 | 52 | 0 | ⬜ |
| Module 8 | 12 | 0 | ⬜ low priority |
| Tracks: architecture | 19 | 0 | ⬜ |
| Tracks: DSA | 12 | 0 | ⬜ |
| Projects (careerpilot, studymind, supportdesk-ai) | 6 | 0 | ⬜ |
| Guides | 2 | 0 | ⬜ |

### Module 5 checklist (current work)

- [x] w1/00 placement check
- [x] w1/01 Docker in Depth
- [x] w1/02 Multi-stage: targets, tags, registries
- [x] w1/03 Docker Compose full stack
- [x] w1/04 Redis caching and queues
- [ ] w1/05 Ship RevoShop production containers
- [ ] w2/00 placement check · w2/01 pipeline concepts · w2/02 GitHub Actions · w2/03 environments · w2/04 secrets & OIDC · w2/05 Ship RevoShop CI/CD
- [ ] w3/00 placement check · w3/01 IAM & budgets · w3/02 regions & VPC · w3/03 EC2 · w3/04 RDS · w3/05 S3 & CloudFront · w3/06 AWS/GCP/Azure table · w3/07 Ship RevoShop EC2+RDS
- [ ] w4/00 placement check · w4/01 frontend on S3/CloudFront · w4/02 backend on EC2 · w4/03 ECS · w4/04 Lambda · w4/05 Parameter Store & Secrets Manager · w4/06 Ship RevoShop ECS Fargate

After Module 5: Module 2 (largest, 52), Module 1, tracks, projects, guides; Module 8 last. Then new material (C5b part 2: M5 W5–W7, Architecture F/H/I, CareerPilot Phase 5) — written in the new style in both languages from the start.

---

## 4. Resuming in a new session

Paste this as the first message:

> Continue the plain-language rewrite of the FSSE handbook as described in `docs/PLAIN_LANGUAGE_REWRITE.md`. Read that file and `docs/WRITING_STYLE.md` first, then continue at the first unchecked lesson in the Module 5 checklist. One lesson per commit, English + Indonesian, `content:check` must pass. Don't push.

The per-lesson git history is the other record: `git log --oneline | grep "plain language"`.

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

In Claude Code this is `Agent(subagent_type: "general-purpose", model: "haiku")` with a prompt that points at this file plus the exact lesson path.
