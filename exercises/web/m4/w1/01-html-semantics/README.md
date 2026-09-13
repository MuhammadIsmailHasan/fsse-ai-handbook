# M4 · W1 · 01 — A Semantic Job Detail Page

> 🚫🤖 **No-AI** · ⏱️ ~45 min

`job.html` shows a CareerPilot job posting, but it's built from `<div>` soup. Rewrite it with semantic HTML. Keep the same **content**; change the **elements**.

Requirements checked by the tests:
- document basics: `<!doctype html>`, `<html lang="en">`, `<meta charset="utf-8">`, a viewport `<meta>`, a non-empty `<title>`
- landmarks: exactly one `<header>`, `<nav>` (with at least 2 links), `<main>` and `<footer>` at the top level of `<body>`
- exactly **one** `<h1>` (the job title), and heading levels never skip (no `h2` → `h4`)
- the posting is an `<article>`; "Requirements" and "Apply" are `<section>`s, each starting with an `<h2>`
- skills are a `<ul>` of `<li>`; the salary uses `<data value="14000000">`; the posted date uses `<time datetime="2026-09-01">`
- the company logo `<img>` has meaningful `alt` text; links have descriptive text (never "click here" / "here")
- the apply form: every `<input>`/`<textarea>` has a `<label for>` pointing to its `id`; the email input has `type="email"` and `required`; the submit control is a `<button type="submit">`
- no inline `style` attributes and no `onclick` attributes

```bash
cd exercises/web
npx vitest run m4/w1/01-html-semantics
```
Open `job.html` in your browser too, and try it with a screen reader (VoiceOver: `Cmd + F5`).
