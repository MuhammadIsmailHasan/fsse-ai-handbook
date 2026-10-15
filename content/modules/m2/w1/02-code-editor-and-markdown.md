---
title: "Code Editor & Markdown"
summary: Set up your editor like a professional and write clear documentation in Markdown — starting with a README recruiters actually read.
type: lesson
source: core
roles: { be: core, fe: core, fs: core, ai: core, ops: core }
durationMinutes: 120
tags: [tooling, vscode, markdown, documentation, readme]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What a good **editor setup** gives you: navigation, linting, formatting, debugging
- The keyboard shortcuts that save hours
- **Markdown** syntax (GitHub Flavored), including tables, task lists, code blocks and Mermaid diagrams
- How to write a **README** that works as documentation *and* portfolio

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Editor / IDE** | The program you write code in (VS Code, PyCharm) | Alat menulis kode |
| **Extension** | A small add-on that teaches your editor a new trick | Pengaya editor |
| **Linter** | A tool that points out mistakes and bad patterns while you type | Pemeriksa kode otomatis |
| **Formatter** | A tool that fixes spacing and layout for you, the same way every time | Perapi kode otomatis |
| **Go to definition** | Jumping straight to where a function or class is written | Lompat ke definisi |
| **Markdown** | A simple text format that turns into headings, lists, tables and code | Format teks sederhana |
| **Code fence** | Three backticks around code, so it keeps its shape and gets colours | Blok kode |
| **README** | The first file people read in a repository — what it is and how to run it | Berkas perkenalan proyek |
| **Mermaid** | Text that renders as a diagram, so diagrams live in Git too | Diagram dari teks |

## 🧠 The big idea

Your editor is your **workshop**. A carpenter with sharp, well-organised tools isn't just faster — they make fewer mistakes. An editor that flags errors as you type, formats on save and jumps to definitions turns hours of hunting into seconds.

:term[Markdown]{bahasa="Markdown — format teks sederhana yang diubah menjadi dokumen rapi (judul, daftar, tabel, kode)"} is the **language of developer documentation**: READMEs, pull requests, issues, docs sites — and every lesson in this handbook.

## ❓ Why it matters

- Code is read and navigated far more often than it is typed: *where is this function used? what does this type look like?*
- People make formatting and spelling mistakes that tools catch instantly.
- Projects need documentation that reads well as plain text (in the terminal, in a diff) **and** renders nicely on GitHub.

Without a good setup:

- You search files by hand for a function name, miss one use of it → a bug.
- Reviews fill up with "missing space" and "wrong indentation" instead of real feedback.
- A great project whose README says only `# my-project` → a recruiter closes the tab in ten seconds.

## 📖 Step by step

### 1. Choose an editor

| Editor | Notes |
|---|---|
| **VS Code** | Free, most popular, huge extension ecosystem |
| **Cursor / Kiro / Windsurf** | VS Code-based, with deeper AI features (Module 6) |
| **PyCharm / WebStorm** | Powerful IDEs, heavier, great refactoring |
| **Neovim** | Keyboard-driven, steep learning curve |

Everything below uses VS Code names; VS Code-based editors behave the same.

### 2. The essential setup

Set this up once and it works for every project afterwards — like organising the toolbox before the first job, not during it.

| Extension / setting | What it does |
|---|---|
| **Python** + **Pylance** | IntelliSense, go-to-definition, type checking |
| **Ruff** | Python linting + formatting (very fast) |
| **ESLint** + **Prettier** | JS/TS linting + formatting (Module 4) |
| **GitLens** *(optional)* | Who changed this line and why |
| **Docker**, **Even Better TOML**, **YAML** | File support you'll need soon |
| `"editor.formatOnSave": true` | Format automatically |
| `"files.trimTrailingWhitespace": true` | Clean diffs |
| Select the project's **Python interpreter** (`.venv`) | So imports and types resolve |

Project-level settings can live in `.vscode/settings.json` and recommended extensions in `.vscode/extensions.json` — useful for teams.

### 3. Shortcuts worth learning this week

| Action | macOS | Windows/Linux |
|---|---|---|
| Command palette | `Cmd Shift P` | `Ctrl Shift P` |
| Open file by name | `Cmd P` | `Ctrl P` |
| Search in all files | `Cmd Shift F` | `Ctrl Shift F` |
| Go to definition | `F12` | `F12` |
| Find all references | `Shift F12` | `Shift F12` |
| Rename symbol everywhere | `F2` | `F2` |
| Multi-cursor | `Option Click` | `Alt Click` |
| Toggle terminal | ``Ctrl ` `` | ``Ctrl ` `` |
| Move line up/down | `Option ↑/↓` | `Alt ↑/↓` |

:::tip
`F2` (rename symbol) is safer than find-and-replace: it understands code, so renaming `user` won't touch `username`.
:::

### 4. Markdown essentials

````md
# Title (one per document)
## Section
### Subsection

**bold**, *italic*, `inline code`, [link](https://example.com)

- bullet
  - nested bullet
1. numbered

> A quote or note

```python
print("fenced code block with a language")
```

| Column | Another |
|---|---|
| cell | cell |

- [ ] task not done
- [x] task done

![Screenshot](docs/screenshot.png)
````

GitHub also renders **Mermaid** diagrams in fenced ` ```mermaid ` blocks — perfect for architecture diagrams in a README.

### 5. Anatomy of a great README

A README is your project's **shop window**. A recruiter spends less than a minute there: they want to see what it does, a screenshot or diagram, and how to run it.

| Section | Why it matters |
|---|---|
| **Name + one-line description** | what it is, in 5 seconds |
| **Screenshot / GIF / demo link** | proof it works |
| **Features** | what it does |
| **Tech stack** | recruiters scan for keywords |
| **Architecture** (diagram) | shows engineering thinking |
| **Getting started** (prerequisites, install, env vars, run) | anyone can run it |
| **Testing** | shows quality habits |
| **API docs / usage** | how to use it |
| **Decisions & trade-offs** *(optional but powerful)* | shows judgment |
| **Roadmap / known limitations** | honesty and direction |

### Choosing your setup

Every option here is a trade-off:

| Choice | ✅ | ❌ |
|---|---|---|
| Lightweight editor + extensions | fast, flexible | setup time; extension conflicts |
| Full IDE | powerful out of the box | heavier, sometimes slower |
| Heavy AI editor features | speed | can hide what's happening; learning suffers if overused |
| Very long README | complete | nobody reads it — put details in `docs/` and link them |

- ✅ Use Markdown for READMEs, docs, PR descriptions, notes and decision records.
- ✅ Keep docs **next to the code** (in the repo) so they change together.
- 🚫 Don't rely on formatting-by-hand; let tools do it.
- 🚫 Don't put secrets, internal URLs or real personal data in READMEs and screenshots.

## ⚠️ Common mistakes

- Running the project with the wrong Python interpreter selected in the editor.
- README with install steps that no longer work (never re-tested).
- Screenshots containing tokens, emails or `.env` values.
- Walls of text without headings, tables or code blocks.

:::revoshop
Your RevoShop README is already strong: *Live Demo* with demo accounts, *Architecture*, *Order Lifecycle*, two ways to run it (with and without Docker), API docs, testing and code-quality sections. Review it like a recruiter with a **30-second timer**: What do you learn in 30 seconds? Is there a screenshot or diagram near the top? Is there anything you **can't explain** in an interview? Write 3 improvements in your notes.
:::

## 🏆 Best practices

- [ ] **Format on save** + a **linter** in the editor, with the **same** config running in CI.
- [ ] Commit shared editor config: `.editorconfig`, `.vscode/extensions.json` (not personal settings).
- [ ] Learn navigation shortcuts first (go to definition, references, rename) — they pay off every day.
- [ ] README **top section answers**: what, why, demo, how to run — in under 30 seconds of reading.
- [ ] Use **relative links** and keep images in the repo (`docs/images/`) so they don't break.
- [ ] One `#` title per document; use headings in order (`##` then `###`) for accessibility and table-of-contents tools.
- [ ] Always add a **language** to code blocks (` ```python `) for highlighting.
- [ ] Keep diagrams as **Mermaid code** where possible — they're versioned and reviewable, unlike images.
- [ ] Update the README in the **same PR** that changes behavior.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a non-programmer why a developer's GitHub README matters for getting hired, and what the first screen of it should show.

## 📐 Design it

Outline (headings only, plus one sentence each) the README for **CareerPilot** as it will look after Phase 2 (Flask API). Decide what goes in the README and what gets moved into `docs/`.

:::quiz
Show a possible outline

```md
# CareerPilot — track your job hunt, powered by data (and soon AI)
<one-line pitch + demo link + screenshot/GIF>

## Features            ← applications pipeline, notes, auth, job market report (Phase 1 CLI)
## Tech stack          ← Python, Flask, PostgreSQL, SQLAlchemy, pytest, Docker
## Architecture        ← Mermaid: client → Flask API → PostgreSQL; link to docs/architecture.md
## Getting started     ← prerequisites, .env.example, docker compose up, migrations, seed
## API                 ← link to Swagger UI + 3 example requests
## Testing             ← how to run, coverage
## Decisions           ← link to docs/decisions/ (e.g. "why JWT", "why soft delete")
## Roadmap             ← Phase 3 AI matching, Phase 4 web app
```

Moved to `docs/`: full endpoint reference, detailed architecture, decision records, deployment runbook.
:::

### 📝 Self-review checklist

- [ ] The first screen answers *what, why, proof, how to run*
- [ ] Details live in `docs/`, linked from the README
- [ ] There's a section showing engineering quality (tests, decisions)

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m2/w1/02-markdown-readme" ai="no-ai" title="Write CareerPilot's README"}
Write the README for your **Phase 1 CareerPilot CLI** in `README.md` inside the exercise folder (then copy it into your real repo).

The tests check structure, not wording: a single `#` title, required sections, a fenced `bash` code block with the run command, a table, a Mermaid diagram, relative links only, and no secrets. Read `README_REQUIREMENTS.md` for the exact list.
:::

:::hints
- Run the tests first — their messages tell you exactly what's missing.
- Paste real terminal output from your CLI into a ` ```text ` block.
- A simple Mermaid flowchart is enough: CSV → load & clean → analyze → report.
:::

### 🏆 Stretch goal

Record a 10-second terminal GIF of your CLI (e.g. with [asciinema](https://asciinema.org/) + agg, or [VHS](https://github.com/charmbracelet/vhs)) and add it under the title.

## ✅ Quick check

:::quiz
Why is `F2` rename better than find-and-replace?

It renames the **symbol** using code understanding — every real usage across files, and nothing that merely contains the same text.
:::

:::quiz
Where should detailed documentation live, and why?

In the repository (e.g. `docs/`), next to the code, so it's versioned, reviewed and updated in the same pull requests as the behavior it describes.
:::


## 📚 Keep learning

- [VS Code: Python in VS Code](https://code.visualstudio.com/docs/python/python-tutorial)
- [GitHub Docs: Basic writing and formatting syntax](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
- [GitHub Docs: Creating Mermaid diagrams](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams)
