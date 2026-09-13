---
title: "Week 2 Placement Check"
summary: TypeScript types, unions and generics, and Tailwind CSS v4 — find out what you can skip before React.
type: placement-check
source: original
roles: { be: optional, fe: core, fs: core, ai: recommended, ops: none }
durationMinutes: 20
tags: [placement, typescript, tailwind]
---

::::placement{id="modules/m4/w2"}
:::quiz
1 · What's the difference between `unknown` and `any`?

`any` turns type checking off (anything goes, errors hide). `unknown` means "could be anything" but you must narrow it (`typeof`, type guards, validation) before using it. Prefer `unknown` for untrusted data.
:::

:::quiz
2 · Model an API response that is either `{ ok: true, data: Job[] }` or `{ ok: false, error: string }`. How does TypeScript know `data` exists?

A discriminated union: `type Response = { ok: true; data: Job[] } | { ok: false; error: string }`. Checking `if (res.ok)` narrows the type to the first member, so `res.data` is available.
:::

:::quiz
3 · Does TypeScript validate the JSON your Flask API returns at runtime?

No. Types are erased at build time. `await res.json()` is just trusted. Validate at the boundary with a schema library (Zod, Week 5) if the data might not match.
:::

:::quiz
4 · Write a generic `first` function that returns the first array element or `undefined` with the correct type.

`function first<T>(items: readonly T[]): T | undefined { return items[0]; }` — the type `T` is inferred from the argument.
:::

:::quiz
5 · In Tailwind, what does `md:grid-cols-2` mean, and is Tailwind mobile first?

Two columns from the `md` breakpoint (48rem) **and up**. Yes: unprefixed utilities apply to all sizes; prefixes add rules for larger screens.
:::

:::quiz
6 · Where do you define custom colors and breakpoints in Tailwind v4?

In CSS with `@theme { --color-brand-500: …; --breakpoint-3xl: 120rem; }` — each token becomes both utilities and CSS variables. No `tailwind.config.js` needed.
:::
::::

:::tip[Scoring yourself]
Pass with **5 of 6** → skim and do the exercises. Question 3 is the one many developers get wrong for years — make sure it's clear.
:::
