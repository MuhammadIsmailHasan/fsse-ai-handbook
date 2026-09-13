# Adding & Editing Content

Lessons are **Markdown files**. You never need to touch React code to add one.

## 1. Where files go

The **path decides** the lesson's id, URL and place in the sidebar:

| Kind | Path | URL |
|---|---|---|
| Module lesson | `content/modules/<module>/<week>/<NN-slug>.md` | `/modules/m2/w4/01-flask-routes` |
| Track lesson | `content/tracks/<track>/<stage>/<NN-slug>.md` | `/tracks/dsa/stage-2/01-hash-maps` |
| Project page | `content/projects/<project>/<NN-slug>.md` | `/projects/careerpilot/02-phase-2-api` |
| Guide | `content/guides/<slug>.md` | `/guides/how-to-study` |

- File names: lowercase letters, numbers and dashes only.
- **Order = file name order** → prefix with numbers (`00-placement-check.md`, `01-…`, `02-…`).
- Modules, weeks, tracks, stages and projects must exist in `content/course.json`.

## 2. Start from the template

Copy [`docs/templates/lesson-template.md`](templates/lesson-template.md). It contains every section in the right order, including **🏆 Best practices**.

## 3. Frontmatter

```yaml
---
title: "Flask Routes & App Structure"
summary: One sentence, max 240 characters.
type: lesson              # lesson | placement-check | project | case-study | career | guide
source: core             # core | original
sourceRef: "M2 · W4 · L1"  # required when source is core
split: false              # true if split from one the bootcamp lesson
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: recommended }
durationMinutes: 150      # total study time incl. exercises
tags: [flask, routing]
lastReviewed: 2026-09     # required for AI & cloud topics
awsCost: free             # free | small | concept (AWS lessons)
draft: false              # true = only visible in `npm run dev`
---
```

Role levels: `core`, `recommended`, `optional`, `none`. Unknown fields are rejected (catches typos).

## 4. Building blocks

| Write | Renders |
|---|---|
| `::part[Learn the Concept]{n="1"}` | Part divider |
| `:term[Middleware]{bahasa="perantara — …"}` | Term with Bahasa tooltip |
| `:::tip` … `:::` (also `note`, `warning`, `danger`) | Callout |
| `:::warning[Custom title]` | Callout with a title |
| `:::revoshop` … `:::` | 🔍 Find it in RevoShop |
| `:::fastapi` … `:::` | 🔄 In FastAPI… |
| `:::bahasa` … `:::` | 🇮🇩 Bahasa note |
| `:::quiz` question-paragraph, then answer `:::` | Question with hidden answer |
| `:::hints` + a bullet list + `:::` | Hints revealed one at a time |
| `:::exercise{path="exercises/…" ai="no-ai" title="…"}` | Local exercise card with run command |
| `:::problem{id="unique-id" title="…" difficulty="easy" path="exercises/…"}` | DSA problem + review queue button |
| `::::placement{id="modules/m2/w1"}` … (quizzes inside) … `::::` | Placement check (**4 colons** so quizzes can nest) |
| `:::linkedin{type="weekly"}` … `:::` | Post template (`weekly`, `concept`, `dsa`, `build`, `reflection`, `milestone`) |
| `:::sandpack{template="test-ts" title="…"}` + code blocks with file names | In-browser editor |
| `::ai-review{task="explain"}` | AI review slot (future) |
| ```` ```mermaid ```` | Diagram |
| ```` ```python ```` | Highlighted code |

See them all live on the **Components Showcase** guide page.

Sandpack code blocks need a file name after the language:

````md
:::sandpack{template="test-ts" title="Sum"}
```ts sum.ts
export const sum = (a: number, b: number) => a + b
```

```ts sum.test.ts
import { sum } from './sum'
test('adds', () => expect(sum(1, 2)).toBe(3))
```
:::
````

## 5. Adding an exercise

```text
exercises/m2/w3/04-dictionaries/
├── README.md               ← task, examples, run command
├── inventory.py            ← starter (unique module name!)
├── test_inventory.py       ← tests (student doesn't edit)
└── solution/inventory.py   ← reference solution
```

Rules:
- Use a **unique module name** per exercise (not `starter.py`) and avoid names of Python standard modules (`random.py`, `string.py`…).
- The starter must **fail** the tests; the solution must **pass**:

```bash
bash scripts/check-exercises.sh m2/w3
```

- Project starter kits (`exercises/projects/…`) have acceptance tests but **no** `solution/`.

## 6. Writing guidelines

- Beginner point of view; explain *why* before *how*.
- One analogy per big idea. Real examples (CareerPilot, shops, job listings) over foo/bar.
- Include **🏆 Best practices** with current, industry-standard advice. Link official docs.
- Key terms get a `:term` with a Bahasa explanation, and the glossary table at the end.
- Short paragraphs, tables for comparisons, code blocks under ~25 lines.
- Only original material — never paste the bootcamp (or any paid course) content.

## 7. Check before committing

```bash
npm run content:check          # frontmatter, structure, links, exercise folders
bash scripts/check-exercises.sh
npm run dev                    # read it in the browser
```
