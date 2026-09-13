---
title: "Next.js Setup & React Components"
summary: Create a Next.js 16 app on a non-default port, understand its folders, and learn React's core idea — components that turn data into UI with JSX — plus how Server and Client Components fit in.
type: lesson
source: core
sourceRef: "M3 · W3 · L1"
roles: { be: optional, fe: core, fs: core, ai: recommended, ops: none }
durationMinutes: 180
tags: [react, nextjs, components, jsx, app-router]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What React is and why component-based UI won
- Creating a Next.js 16 project with `create-next-app` (TypeScript, Tailwind, ESLint, App Router, Turbopack)
- Running it on a **non-default port** and the project structure (`app/`, `layout.tsx`, `page.tsx`, `public/`)
- JSX rules, components as functions, composition with `children`
- Rendering lists with `key`
- Server Components (default) vs Client Components (`"use client"`) — the first mental model
- The React DevTools and the Next.js dev overlay

## 🧠 The big idea

In Week 1 you updated the DOM step by step: "find the list, clear it, create an `li`, append it…". React flips this: you **describe what the UI should look like for the current data**, and React figures out the DOM changes.

A component is a **recipe**: `JobCard(job) → UI`. Give it different data, get a different card. Build small recipes, combine them into bigger ones — a page is just a component made of components.

## ❓ Why does this exist?

Manual DOM code becomes unmanageable as apps grow: every state change must remember every place to update. React (2013, Meta) popularized **declarative, component-based UI**; today it's the most-used frontend library, and **Next.js** is the most popular React framework, adding routing, server rendering, data fetching, and production optimizations.

## 💥 What happens if we DON'T?

- Hand-written DOM updates drift out of sync with data (Week 1 lesson 05's pain, multiplied by 50 screens).
- Plain React without a framework means choosing and wiring a router, a bundler, SSR, image optimization, and deployment yourself.
- Copy-pasted markup instead of components: fixing a card means fixing it in 12 places.

## 📖 How it works, step by step

### 1. Create the app

```bash
npx create-next-app@latest careerpilot-web --yes   # TypeScript, Tailwind, ESLint, App Router, Turbopack
cd careerpilot-web
npm run dev -- --port 3091                          # the handbook's frontend port (3000 is often taken)
```

Make the port permanent in `package.json` so teammates get the same one:

```json
{
  "scripts": {
    "dev": "next dev --port 3091",
    "build": "next build",
    "start": "next start --port 3091",
    "lint": "eslint"
  }
}
```

(`next dev` also reads `PORT` from the environment.) Next.js 16 needs Node.js 20.9+, uses **Turbopack** by default, and the default setup includes an `AGENTS.md` that tells AI coding agents to read the version-matched docs in `node_modules/next/dist/docs` — useful because Next.js changes fast.

### 2. Project structure

```text
careerpilot-web/
├── app/                    ← App Router: folders = URLs
│   ├── layout.tsx          ← root layout: <html>, <body>, shared UI (required)
│   ├── page.tsx            ← the "/" route
│   ├── globals.css         ← @import "tailwindcss"
│   └── jobs/
│       └── page.tsx        ← the "/jobs" route (Week 4)
├── public/                 ← static files served at "/" (logo.svg → /logo.svg)
├── next.config.ts
├── tsconfig.json           ← includes the "@/*" import alias
├── eslint.config.mjs
└── package.json
```

```tsx
// app/layout.tsx
import "./globals.css";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

```tsx
// app/page.tsx
export default function Page() {
  return <h1 className="text-3xl font-bold">Hello, CareerPilot!</h1>;
}
```

### 3. JSX

JSX looks like HTML but is JavaScript:

```tsx
const job = { title: "Backend Engineer", company: "Kopi Data", remote: false };

<article className="rounded-xl p-4">            {/* class → className */}
  <h2>{job.title}</h2>                           {/* { } embeds any JS expression */}
  <p>{job.company.toUpperCase()}</p>
  <label htmlFor="note">Note</label>             {/* for → htmlFor */}
  <input id="note" disabled={!job.remote} />      {/* attributes can be expressions */}
  <img src="/logo.png" alt="" />                  {/* every tag must close */}
</article>
```

Rules: one root element per return (or a fragment `<>…</>`), `camelCase` attributes (`onClick`, `tabIndex`), `style={{ width: 40 }}` takes an object, and text is **escaped automatically** — `{job.title}` can't inject HTML (goodbye, XSS from Week 1).

### 4. Components

```tsx
type Job = { id: number; title: string; company: string; city: string };

export function JobCard({ job }: { job: Job }) {
  return (
    <article>
      <h2>{job.title}</h2>
      <p>{job.company} · {job.city}</p>
    </article>
  );
}
```

- A component is a function that returns JSX; its name starts with a **capital letter** (`<JobCard />` vs a DOM tag `<article>`).
- It should be **pure**: same props → same output, no side effects while rendering.

### 5. Composition and `children`

```tsx
export function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded-xl border p-4">
      <h2>{title}</h2>
      {children}
    </section>
  );
}

<Card title="Notes">
  <p>Recruiter called on Monday</p>
</Card>
```

`children` is whatever you put between the tags — the key to layouts, modals and wrappers.

### 6. Lists and keys

```tsx
<ul>
  {jobs.map((job) => (
    <li key={job.id}>
      <JobCard job={job} />
    </li>
  ))}
</ul>
```

`key` tells React which item is which between renders. Use a **stable id** from your data, never `Math.random()`, and avoid the index when items can be added, removed or reordered (lesson 06 shows the bug).

### 7. Server and Client Components

In the App Router, **every component is a Server Component by default**: it renders on the server, can `await` data directly, keeps secrets on the server, and sends **no JavaScript** for itself to the browser.

When a component needs **state, event handlers, effects or browser APIs**, put `"use client"` at the top of its file:

```tsx
// app/jobs/save-button.tsx
"use client";

import { useState } from "react";

export function SaveButton() {
  const [saved, setSaved] = useState(false);
  return <button onClick={() => setSaved(!saved)}>{saved ? "Saved" : "Save"}</button>;
}
```

```tsx
// app/jobs/page.tsx — Server Component using a Client Component
import { SaveButton } from "./save-button";

export default function JobsPage() {
  return (
    <main>
      <h1>Jobs</h1>
      <SaveButton />
    </main>
  );
}
```

`"use client"` marks a **boundary**: that file and everything it imports go to the browser bundle. Keep the boundary as low (small) as possible. Week 4 goes deep on this; for Week 3, remember: **interactive → client**.

### 8. Tools

- **React Developer Tools** (browser extension): inspect the component tree, props, state and hooks.
- **Next.js dev overlay**: build and runtime errors in the browser with source locations.
- `console.log` in a Server Component prints in the **terminal**; in a Client Component, in the **browser** console.

## ⚖️ Trade-offs

| Choice | ✅ | ❌ |
|---|---|---|
| Next.js | routing, server rendering, optimizations, deployment story | framework conventions, more concepts (server vs client) |
| Vite + React (like this handbook app) | simple SPA, full control | you choose routing/data/SSR yourself |
| Server Components by default | less JS, secrets stay on server, fast first load | need to learn the boundary |
| Many small components | reusable, testable | too much prop passing if split carelessly |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ Next.js for product apps with many pages, SEO needs, or server data (CareerPilot Phase 4).
- ✅ Vite + React for internal tools or apps behind login where SSR doesn't matter.
- 🚫 A heavy framework for a static brochure page — plain HTML (or a static site generator) is fine.

## 🏆 Best practices

- [ ] Create projects with TypeScript, ESLint and strict mode; set a non-default dev port in `package.json`.
- [ ] One component per responsibility; named exports for shared components, default exports where Next.js requires them (`page.tsx`, `layout.tsx`).
- [ ] Keep components **pure**; no side effects while rendering.
- [ ] Stable, unique `key`s from data ids.
- [ ] Default to Server Components; add `"use client"` only to the interactive leaves.
- [ ] Use the `@/` alias instead of long relative imports.
- [ ] Install React DevTools on day one.

## 🏭 How it's used in industry

- React + Next.js is the most common stack in frontend and full-stack job listings; many Indonesian startups run their web apps on it.
- Vercel, Netlify and container platforms deploy Next.js apps; teams also self-host with `next start` in Docker (Week 6).
- AI app builders generate Next.js + Tailwind code — understanding the structure lets you review and fix what they produce.

## ⚠️ Common mistakes

- `class` instead of `className`; forgetting to close tags.
- Lower-case component names (`<jobCard />` is treated as an unknown HTML tag).
- Using hooks or `onClick` in a file without `"use client"`.
- Putting `"use client"` in `layout.tsx` "to make errors go away" — the whole app becomes client-side.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain the difference between Week 1's DOM code ("find the list, append an item") and React ("describe the UI for this data") to a teammate. Use the recipe analogy.

## 📐 Design it

Break CareerPilot's **dashboard page** into a component tree: header with user menu, stats cards, a "recent applications" list with status badges, a "saved jobs" panel with save/unsave buttons, and an empty state. For each component write its props, and mark which ones must be Client Components.

:::quiz
Show a possible tree

```text
app/dashboard/page.tsx            (Server) — loads data, composes the page
├── <SiteHeader user>             (Server)
│   └── <UserMenu user>           (Client: open/close state, click outside)
├── <StatsGrid stats>             (Server)
│   └── <StatCard label value trend?>   (Server)
├── <RecentApplications applications>   (Server)
│   ├── <ApplicationRow application>    (Server)
│   │   └── <StatusBadge status>        (Server)
│   └── <EmptyState message action?>    (Server)
└── <SavedJobsPanel initialJobs>        (Client: saving/unsaving updates the list)
    └── <SavedJobItem job onUnsave>     (Client, inside the client boundary)
        └── <SaveButton saved onToggle jobTitle>
```

- Props are plain serializable data (`stats`, `applications`) so the Server → Client boundary works.
- Only `UserMenu` and the saved-jobs panel ship JavaScript; everything else is HTML from the server.
- `StatusBadge` and `EmptyState` are reusable presentational components shared by many pages.
:::

### 📝 Self-review checklist

- [ ] Each component has one clear job and typed props
- [ ] Client Components are only the interactive parts
- [ ] Reusable pieces identified

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w3/01-components" ai="no-ai" title="Your first presentational components"}
Build `PageHeader`, `JobCard`, `EmptyState`, `JobList` and `JobsPage` as typed function components: conditional subtitle and salary, lists with stable keys, composition with `children`. Tests render them with Testing Library, fail on React key warnings and type-check the file.
:::

:::hints
- `{subtitle && <p>{subtitle}</p>}` renders only when there's a subtitle (strings are safe here; numbers need `> 0` checks).
- `JobList` can return `<EmptyState … />` early when the array is empty.
- Wrap siblings in a fragment `<>…</>` when you need two top-level elements.
:::

:::sandpack{template="react-ts" title="Try JSX in the browser"}
```tsx App.tsx
type Job = { id: number; title: string; company: string };

const jobs: Job[] = [
  { id: 1, title: "Backend Engineer", company: "Kopi Data" },
  { id: 2, title: "AI Engineer", company: "Lintas AI" },
];

function JobCard({ job }: { job: Job }) {
  return (
    <article style={{ border: "1px solid #ddd", borderRadius: 12, padding: 12, marginBottom: 8 }}>
      <h2 style={{ margin: 0 }}>{job.title}</h2>
      <p style={{ margin: 0, color: "#64748b" }}>{job.company}</p>
    </article>
  );
}

export default function App() {
  return (
    <main style={{ fontFamily: "system-ui", padding: 16 }}>
      <h1>Jobs for you</h1>
      {jobs.map((job) => (
        <JobCard key={job.id} job={job} />
      ))}
    </main>
  );
}
```
:::

## ✅ Quick check

:::quiz
Why must component names start with a capital letter?

JSX treats lower-case tags as HTML elements (`<article>`) and capitalized ones as components (`<JobCard />`).
:::

:::quiz
When does a component need `"use client"` in the App Router?

When it uses state, effects, event handlers, custom hooks or browser-only APIs.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Component | Komponen — potongan UI yang bisa dipakai ulang |
| JSX | Sintaks mirip HTML di dalam JavaScript |
| Props | Properti — input untuk komponen |
| Composition | Komposisi — menyusun komponen dari komponen lain |
| Server / Client Component | Komponen yang dirender di server / di browser |
| Hydration | Hidrasi — menambahkan interaktivitas ke HTML dari server |

## 📚 Keep learning

- [React docs: Your First Component](https://react.dev/learn/your-first-component)
- [React docs: Writing Markup with JSX](https://react.dev/learn/writing-markup-with-jsx)
- Next.js docs (also bundled in `node_modules/next/dist/docs`): Installation, Project Structure, Server and Client Components
