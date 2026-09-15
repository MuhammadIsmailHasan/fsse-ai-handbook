---
title: "Week 3 Placement Check"
summary: React components, props, state, rendering lists and controlled forms inside a Next.js project — check what you already know.
type: placement-check
source: original
roles: { be: optional, fe: core, fs: core, ai: recommended, ops: none }
durationMinutes: 20
tags: [placement, react, nextjs]
---

::::placement{id="modules/m4/w3"}
Answer from memory. If a word is new to you, that's a sign to study the lesson.

:::quiz
1 · What's the difference between props and state?

Props are inputs the parent gives to a component — the child only reads them. State is data the component owns and changes over time with its setter; changing it redraws the component.
:::

:::quiz
2 · Why does `items.push(x); setItems(items)` often not update the screen?

It changes the same array, so React sees "the same" array and may skip redrawing. Make a new array instead: `setItems([...items, x])` or `setItems(prev => [...prev, x])`.
:::

:::quiz
3 · Why do list items need a `key`, and why is the array index a bad key when items can be removed or reordered?

Keys tell React which item is which between renders. With index keys, removing the first item shifts all the numbers, so React gives the wrong item's saved state (for example, typed text) to the items that remain.
:::

:::quiz
4 · What does `"use client"` do in a Next.js App Router project?

It marks a file (and what it imports) as a Client Component, so it can use state, effects, click handlers and browser features. Without it, components are Server Components by default.
:::

:::quiz
5 · What is a controlled input?

An input whose `value` comes from React state and is updated through `onChange`. React state is the only source of truth.
:::

:::quiz
6 · What shows on screen for `{count && <span>{count} new</span>}` when `count` is 0?

`0` — React shows the number 0. Use `{count > 0 && …}` or a ternary (`? :`).
:::
::::

:::tip[Scoring yourself]
Pass with **5 of 6** → skim the lessons and go to the exercises. Still do lesson 06 (debugging) — it helps every week after this.
:::
