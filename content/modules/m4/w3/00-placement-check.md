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
:::quiz
1 · What's the difference between props and state?

Props are inputs passed in by the parent (read-only for the child). State is data a component owns and changes over time with its setter; changing it re-renders the component.
:::

:::quiz
2 · Why does `items.push(x); setItems(items)` often not update the screen?

It mutates the same array reference, so React sees the "same" value and may skip re-rendering. Create a new array: `setItems([...items, x])` or `setItems(prev => [...prev, x])`.
:::

:::quiz
3 · Why do list items need a `key`, and why is the array index a bad key when items can be removed or reordered?

Keys let React match items between renders. With index keys, removing the first item shifts all indexes, so React reuses the wrong component (and its internal state, e.g. input text) for the remaining items.
:::

:::quiz
4 · What does `"use client"` do in a Next.js App Router project?

It marks a file (and what it imports) as a Client Component so it can use state, effects, event handlers and browser APIs. Without it, components are Server Components by default.
:::

:::quiz
5 · What is a controlled input?

An input whose `value` comes from React state and updates through `onChange` — React state is the single source of truth.
:::

:::quiz
6 · What prints on screen: `{count && <span>{count} new</span>}` when `count` is 0?

`0` — React renders the number 0. Use `{count > 0 && …}` or a ternary.
:::
::::

:::tip[Scoring yourself]
Pass with **5 of 6** → skim and go to the exercises. Still do lesson 06 (debugging) — it pays off every week after this.
:::
