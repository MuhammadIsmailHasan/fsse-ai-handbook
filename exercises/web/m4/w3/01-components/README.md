# M4 · W3 · 01 — Your First React Components

> 🚫🤖 **No-AI** · ⏱️ ~60 min · edit **`job-components.tsx`**

Turn Week 1's job page into small, reusable components. They're **presentational** (no state yet): data in via props, JSX out.

| Component | Renders |
|---|---|
| `PageHeader({ title, subtitle? })` | `<header>` with an `<h1>` and, only if given, a `<p>` subtitle |
| `JobCard({ job })` | `<article>` containing `<h2>{title}</h2>`, `<p>{company} · {city}</p>`, a `<ul aria-label="Skills">` with one `<li>` per skill, and — only when `salaryMax` isn't `null` — `<p>Up to Rp {salaryMax formatted with dots}</p>` |
| `JobList({ jobs })` | `<ul>` with one `<li>` per job containing a `JobCard` (use `job.id` as the **key**) — or `<EmptyState message="No jobs yet" />` when the list is empty |
| `EmptyState({ message, children? })` | `<div role="status">` with `<p>{message}</p>` and any `children` (e.g. a button) below it |
| `JobsPage({ jobs })` | `PageHeader` (title `"Jobs for you"`, subtitle `"{n} open positions"`) + `<main>` with the `JobList` |

`type Job = { id: number; title: string; company: string; city: string; salaryMax: number | null; skills: string[] }` is provided.

Rules: function components, named exports, no `any`, and **no React key warnings** (the test fails if React logs one).

```bash
cd exercises/web
npx vitest run m4/w3/01-components
```
