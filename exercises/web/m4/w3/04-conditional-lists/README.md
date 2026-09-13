# M4 · W3 · 04 — Conditional Rendering & Lists: The Applications View

> 🚫🤖 **No-AI** · ⏱️ ~75 min · edit **`applications-view.tsx`**

`ApplicationsView({ state, onRetry })` renders every state of a data request (provided type: `RequestState<Application[]>` is a discriminated union: `idle`, `loading`, `error` with `message`, `success` with `data`).

| `state` | Render |
|---|---|
| `idle` | nothing (`null`) |
| `loading` | `<div role="status" aria-live="polite">Loading applications…</div>` |
| `error` | `<div role="alert">` with `<p>{message}</p>` and a `<button type="button">Try again</button>` that calls `onRetry` |
| `success` with `[]` | `<p>No applications yet</p>` |
| `success` with data | status **filter tabs**, then groups |

**Filter** (component state): a `<div role="group" aria-label="Filter by status">` with one `<button aria-pressed>` per option: `All ({n})` then one per status that **has applications**, in the order `saved, applied, interview, offer, rejected`, e.g. `Interview (2)`. `All` is selected initially.

**Groups**: for each status with visible applications (same order), a `<section aria-label="{Label}">` with an `<h2>{Label}</h2>` and a `<ul>` of `<li>` items: `{role} at {company}`. An item with `unread > 0` also shows `<span>{unread} new</span>` — and must **not** render a stray `0` when `unread` is 0 (the classic `{count && …}` bug).

Keys must be stable ids (the test fails on React key warnings).

```bash
cd exercises/web
npx vitest run m4/w3/04-conditional-lists
```
