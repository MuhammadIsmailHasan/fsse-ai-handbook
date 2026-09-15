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
Answer from memory. If a word is new to you, that's a sign to study the lesson.

:::quiz
1 · What's the difference between `unknown` and `any`?

`any` turns type checking off — anything is allowed, and mistakes stay hidden. `unknown` also means "could be anything", but TypeScript makes you check it first (`typeof`, validation) before you use it. Use `unknown` for data you don't trust.
:::

:::quiz
2 · An API response is either `{ ok: true, data: Job[] }` or `{ ok: false, error: string }`. How does TypeScript know `data` exists?

Write it as one type with two options: `type Response = { ok: true; data: Job[] } | { ok: false; error: string }`. After `if (res.ok)`, TypeScript knows it's the first option, so `res.data` is available.
:::

:::quiz
3 · Does TypeScript check the JSON your Flask API returns while the app runs?

No. Types are removed when the code is built. `await res.json()` is simply trusted. If the data might not match, check it with a validation library (Zod, Week 5).
:::

:::quiz
4 · Write a function `first` that returns the first item of any array (or `undefined`) with the correct type.

`function first<T>(items: readonly T[]): T | undefined { return items[0]; }` — `T` is a placeholder type that TypeScript fills in from the argument.
:::

:::quiz
5 · In Tailwind, what does `md:grid-cols-2` mean? Is Tailwind mobile first?

Two columns from the `md` screen width (48rem) **and bigger**. Yes: classes without a prefix apply to all sizes; prefixes add rules for bigger screens.
:::

:::quiz
6 · Where do you add your own colors and breakpoints in Tailwind v4?

In CSS, with `@theme { --color-brand-500: …; --breakpoint-3xl: 120rem; }`. Each value becomes both a Tailwind class and a CSS variable. No `tailwind.config.js` needed.
:::
::::

:::tip[Scoring yourself]
Pass with **5 of 6** → skim the lessons and do the exercises. Many developers get question 3 wrong for years — make sure it's clear to you.
:::
