---
title: "Next.js Setup & React Components"
summary: Create a Next.js 16 app on a non-default port, understand its folders, and learn React's core idea — components that turn data into screens with JSX — plus the first idea of Server and Client Components.
type: lesson
source: core
sourceRef: "M3 · W3 · L1"
roles: { be: optional, fe: core, fs: core, ai: recommended, ops: none }
durationMinutes: 180
tags: [react, nextjs, components, jsx, app-router]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What React and Next.js are
- Creating a Next.js 16 project and running it on port 3091
- The main folders and files
- JSX: writing HTML-like code inside JavaScript
- Components, `children`, and lists with `key`
- Server Components vs Client Components (`"use client"`) — the basic idea
- Tools: React DevTools and the Next.js error overlay

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **React** | A library for building screens from components | Library UI |
| **Next.js** | A framework on top of React that adds pages, routing and server rendering | Framework React |
| **Component** | A function that returns a piece of screen, like `JobCard` | Komponen |
| **JSX** | HTML-like syntax inside JavaScript: `<h1>{title}</h1>` | Sintaks mirip HTML |
| **Props** | The inputs you give a component: `<JobCard job={job} />` | Input komponen |
| **Render** | React turning your components into what's on screen | Menampilkan |
| **Server Component** | Runs on the server; sends only HTML, no JavaScript | Komponen server |
| **Client Component** | Runs in the browser; can use clicks and state (`"use client"`) | Komponen browser |

## 🧠 The big idea

In Week 1 you changed the page step by step: "find the list, clear it, create an `li`, add it…". React turns this around: you **describe what the screen should look like for the current data**, and React works out the changes.

A component is like a **recipe**: `JobCard(job) → card on screen`. Different ingredients (data) → a different dish (card). Small recipes combine into bigger ones — a page is just a component made of components, like a nasi campur plate made of small dishes.

## ❓ Why it matters

- Changing the DOM by hand gets out of control as an app grows: every change must remember every place to update.
- React is the most-used frontend library. **Next.js** is the most popular React framework: it adds pages, server rendering and many optimizations.
- Without components, fixing one card means fixing it in 12 copies.
- React + Next.js is the most common stack in frontend and full-stack job ads, including remote roles.

## 📖 Step by step

### 1. Create the app

```bash
npx create-next-app@latest careerpilot-web --yes   # TypeScript, Tailwind, ESLint, App Router, Turbopack
cd careerpilot-web
npm run dev -- --port 3091                          # the handbook's frontend port (3000 is often taken)
```

Save the port in `package.json`, so everyone on the team uses the same one:

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

- Next.js 16 needs Node.js 20.9 or newer.
- The new project includes an `AGENTS.md` file that tells AI coding tools to read the Next.js docs that match your version (inside `node_modules/next/dist/docs`). Next.js changes fast, so this is useful.

### 2. The folders

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

The `app/` folder works like a **building directory**: each folder is a floor (a URL), and `page.tsx` is the room people visit.

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

- `layout.tsx` = the frame shared by all pages.
- `page.tsx` = the content of one page. `{children}` in the layout is where the page appears.

### 3. JSX

JSX looks like HTML, but it's JavaScript:

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

- `{ }` puts a JavaScript value inside the markup.
- `class` becomes `className`, `for` becomes `htmlFor`, event names use camelCase (`onClick`).
- Every tag must be closed (`<img />`).
- Return one outer element, or wrap siblings in `<>…</>` (a fragment).
- Text is **escaped automatically**: `{job.title}` can never inject HTML. The XSS problem from Week 1 is solved by default.

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

- A component is a function that returns JSX.
- Its name starts with a **capital letter**: `<JobCard />` is a component, `<article>` is an HTML tag.
- It should be **pure**: same props → same result, and no side effects (like API calls) while drawing. Like a calculator: 2 + 2 always shows 4.

### 5. `children`: putting things inside a component

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

`children` is whatever you put between the opening and closing tags — like a **gift box**: the box is always the same, the gift inside changes. Layouts, popups and wrappers all use this.

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

`key` is like a **name tag** for each item, so React knows which item is which after the list changes. Use a stable id from your data. Never use `Math.random()`, and avoid the array index when items can be added, removed or reordered (lesson 06 shows the bug).

### 7. Server Components and Client Components

In Next.js, **every component is a Server Component by default**. It runs on the server, can load data directly, keeps secrets there, and sends **no JavaScript** for itself to the browser — like a restaurant kitchen that sends you the finished dish, not the stove.

When a component needs **state, click handlers, effects or browser features**, write `"use client"` at the top of its file:

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

`"use client"` draws a **line**: that file and everything it imports are sent to the browser. Keep that part as small as possible. Week 4 explains this in depth. For now remember: **interactive → client**.

### 8. Tools

- **React Developer Tools** (browser extension): see the component tree, props and state.
- **Next.js error overlay**: errors appear in the browser with the file and line.
- `console.log` in a Server Component prints in your **terminal**; in a Client Component, in the **browser** console.

## ⚠️ Common mistakes

- `class` instead of `className`; forgetting to close tags.
- A lower-case component name (`<jobCard />` is treated as an unknown HTML tag).
- Using `useState` or `onClick` in a file without `"use client"`.
- Adding `"use client"` to `layout.tsx` "to make the error go away" — then the whole app runs in the browser.
- Copy-pasting markup instead of making a component.

## 🏆 Best practices

- [ ] Create projects with TypeScript and ESLint; set a non-default dev port in `package.json`.
- [ ] One job per component; typed props.
- [ ] Keep components pure — no side effects while rendering.
- [ ] Stable, unique `key`s from data ids.
- [ ] Server Components by default; `"use client"` only for the small interactive parts.
- [ ] Use the `@/` import alias instead of long `../../..` paths.
- [ ] Install React DevTools on day one.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain the difference between Week 1's DOM code ("find the list, add an item") and React ("describe the screen for this data") to a teammate. Use the recipe analogy.

## 📐 Design it

Split CareerPilot's **dashboard page** into components: a header with a user menu, stats cards, a "recent applications" list with status badges, a "saved jobs" panel with save/unsave buttons, and an empty state. Write each component's props, and mark which ones must be Client Components.

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

- Props are simple data (`stats`, `applications`) that can be sent from server to browser.
- Only `UserMenu` and the saved-jobs panel send JavaScript to the browser; the rest is plain HTML from the server.
- `StatusBadge` and `EmptyState` are small reusable pieces for many pages.
:::

### 📝 Self-review checklist

- [ ] Each component has one clear job and typed props
- [ ] Only the interactive parts are Client Components
- [ ] Reusable pieces are identified

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w3/01-components" ai="no-ai" title="Your first presentational components"}
Build `PageHeader`, `JobCard`, `EmptyState`, `JobList` and `JobsPage` as typed function components: an optional subtitle and salary, lists with stable keys, and `children`. The tests render them with Testing Library, fail on React key warnings and type-check the file.
:::

:::hints
- `{subtitle && <p>{subtitle}</p>}` shows the paragraph only when there's a subtitle (fine for strings; for numbers use `> 0`).
- `JobList` can return `<EmptyState … />` early when the array is empty.
- Wrap two top-level elements in a fragment `<>…</>`.
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
When does a component need `"use client"`?

When it uses state, effects, click handlers, custom hooks or browser-only features.
:::

## 📚 Keep learning

- [React docs: Your First Component](https://react.dev/learn/your-first-component)
- [React docs: Writing Markup with JSX](https://react.dev/learn/writing-markup-with-jsx)
- Next.js docs (also bundled in `node_modules/next/dist/docs`): Installation, Project Structure, Server and Client Components
