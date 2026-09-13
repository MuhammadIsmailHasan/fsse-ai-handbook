# M4 · W3 · 03 — State and Events: A Saved-Jobs Board

> 🚫🤖 **No-AI** · ⏱️ ~75 min · edit **`saved-jobs.tsx`**

Three components with `useState`. Mark the file `"use client"` (it's interactive — in Next.js this is required).

## `SaveButton({ saved, onToggle, jobTitle })`
A **controlled** button: it doesn't own state. Renders `<button type="button" aria-pressed={saved}>` with text `Saved` / `Save`, an accessible name `"Save {jobTitle}"` / `"Unsave {jobTitle}"` via `aria-label`, and calls `onToggle()` on click.

## `SavedJobsBoard({ jobs })`
Owns the state (**lifting state up**): a `Set` of saved job ids.
- renders `<h2>Jobs</h2>` and a list of `<li>` items with the job title and a `SaveButton`
- a `<p aria-live="polite">` with `"{n} saved"`
- a "Clear saved" `<button type="button">`, **disabled** when nothing is saved
- never mutate state: create a new `Set` on every change

## `ApplicationCounter()`
`<p>Applications sent: {count}</p>` and two buttons:
- `+1` adds one
- `+3` must add three by calling the state setter **three times** in one handler — use the **updater function** form (`setCount(c => c + 1)`), otherwise it only adds one

```bash
cd exercises/web
npx vitest run m4/w3/03-state-events
```
