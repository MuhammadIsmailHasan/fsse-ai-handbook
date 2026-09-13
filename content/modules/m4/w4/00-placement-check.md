---
title: "Week 4 Placement Check"
summary: App Router routing, navigation, environment variables, calling APIs, Server vs Client Components, caching and TanStack Query — check what you can skip.
type: placement-check
source: original
roles: { be: optional, fe: core, fs: core, ai: recommended, ops: none }
durationMinutes: 20
tags: [placement, nextjs, app-router, caching]
---

::::placement{id="modules/m4/w4"}
:::quiz
1 · Which files create the URL `/jobs/42` and what props does the page receive?

`app/jobs/[id]/page.tsx`. It receives `params` as a **Promise** (`{ params: Promise<{ id: string }> }`) that you `await`; `id` is the string `"42"`.
:::

:::quiz
2 · What's the difference between `API_TOKEN` and `NEXT_PUBLIC_API_URL` in a Next.js `.env` file?

Variables without the prefix are only available on the server. `NEXT_PUBLIC_` variables are inlined into the browser JavaScript at build time — never put secrets in them.
:::

:::quiz
3 · When should a component be a Client Component?

When it needs state, effects, event handlers, custom hooks or browser APIs. Data fetching with secrets, heavy formatting and static markup belong in Server Components.
:::

:::quiz
4 · In Next.js 16 with Cache Components, is `fetch` cached by default? How do you cache the public job list for an hour and refresh it after an admin edits a job?

No — data is dynamic by default. Put `"use cache"`, `cacheLife("hours")` and `cacheTag("jobs")` in the data function, and call `updateTag("jobs")` (or `revalidateTag`) in the Server Action after the mutation succeeds.
:::

:::quiz
5 · What does `error.tsx` do and why must it be a Client Component?

It's an error boundary for its route segment: it renders fallback UI when something below throws, and receives `error` and `retry()`. Error boundaries rely on client-side React features, so the file needs `"use client"`.
:::

:::quiz
6 · Why use TanStack Query instead of `useEffect` + `useState` for fetching in Client Components?

It handles caching, deduplication, background refetching, retries, cancellation, loading/error state and mutations with invalidation — avoiding race conditions and boilerplate.
:::
::::

:::tip[Scoring yourself]
Pass with **5 of 6**. Question 4 changed in Next.js 15 and 16 — even experienced developers should read lesson 06.
:::
