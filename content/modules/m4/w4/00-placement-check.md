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
Answer from memory. If a word is new to you, that's a sign to study the lesson.

:::quiz
1 · Which file creates the URL `/jobs/42`, and what does the page receive?

`app/jobs/[id]/page.tsx`. It receives `params` as a **Promise** (`{ params: Promise<{ id: string }> }`) that you `await`. `id` is the text `"42"`, not a number.
:::

:::quiz
2 · What's the difference between `API_TOKEN` and `NEXT_PUBLIC_API_URL` in a Next.js `.env` file?

Variables without the prefix only exist on the server. `NEXT_PUBLIC_` variables are copied into the browser JavaScript when you build — anyone can read them, so never put secrets there.
:::

:::quiz
3 · When should a component be a Client Component?

When it needs state, effects, click handlers, custom hooks or browser features. Loading data with secrets, heavy formatting and static markup belong in Server Components.
:::

:::quiz
4 · In Next.js 16 with Cache Components, is `fetch` cached automatically? How do you cache the public job list for an hour and refresh it after an admin edits a job?

No — data is fresh (dynamic) by default. Put `"use cache"`, `cacheLife("hours")` and `cacheTag("jobs")` in the data function, then call `updateTag("jobs")` (or `revalidateTag`) in the Server Action after the edit succeeds.
:::

:::quiz
5 · What does `error.tsx` do, and why must it be a Client Component?

It catches errors for its part of the app and shows a fallback screen with the `error` and a `retry()` function. Catching render errors needs browser-side React, so the file needs `"use client"`.
:::

:::quiz
6 · Why use TanStack Query instead of `useEffect` + `useState` to load data in Client Components?

It handles caching, avoiding duplicate requests, refreshing in the background, retries, cancelling, loading/error states and updates after changes — without race conditions and repeated code.
:::
::::

:::tip[Scoring yourself]
Pass with **5 of 6**. Question 4 changed in Next.js 15 and 16 — even experienced developers should read lesson 06.
:::
