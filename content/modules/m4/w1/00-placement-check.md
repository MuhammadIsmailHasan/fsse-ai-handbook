---
title: "Week 1 Placement Check"
summary: HTML semantics, CSS layout, JavaScript fundamentals, the DOM, async code and accessibility — see which parts of the web platform you can skip.
type: placement-check
source: original
roles: { be: optional, fe: core, fs: core, ai: recommended, ops: none }
durationMinutes: 25
tags: [placement, html, css, javascript, dom]
---

::::placement{id="modules/m4/w1"}
You built APIs in Module 2. This week is the other side: what runs in the browser. Answer without looking anything up.

:::quiz
1 · Why use `<button>` instead of a `<div onclick>` for an action?

A `<button>` is focusable, works with Enter/Space, is announced as a button by screen readers, and can submit forms. A `<div>` needs `tabindex`, key handlers and ARIA roles to approximate that — and usually still misses something.
:::

:::quiz
2 · Flexbox or Grid for (a) a navbar with logo left and links right, (b) a page with sidebar + content + card grid?

(a) Flexbox — one-dimensional alignment in a row. (b) Grid — two-dimensional layout of rows and columns (cards with `repeat(auto-fill, minmax(...))`). They're often combined.
:::

:::quiz
3 · What does this print, and why? `console.log(0 == "", [] == false, null ?? "x", 0 || "x")`

`true true "x" "x"` — `==` performs type coercion (use `===`); `??` only falls back for `null`/`undefined`; `||` falls back for any falsy value, including `0`.
:::

:::quiz
4 · Why is `element.innerHTML = job.title` dangerous, and what should you use?

If `job.title` contains HTML (e.g. `<img onerror=...>`), it gets parsed and can run scripts (XSS). Use `textContent` or `createElement` for data.
:::

:::quiz
5 · `fetch("/api/jobs")` returns a 500 response. Does the promise reject?

No. `fetch` only rejects on network failures (or aborts). You must check `response.ok` / `response.status` and throw yourself.
:::

:::quiz
6 · Name three things you'd check to make a form accessible.

Every input has a visible `<label for>`; errors are announced and linked with `aria-describedby` + `aria-invalid`; it works with the keyboard alone; focus moves to the first error; enough color contrast; don't rely on color alone.
:::
::::

:::tip[Scoring yourself]
Pass with **5 of 6** → skim the lessons and go straight to the exercises. Coming from Python, lessons 04 and 07 (JavaScript and async) are the most important ones not to skip.
:::
