# Architecture G · 01 — Container / Presentational

> 🚫🤖 **No-AI** · ⏱️ ~60 min

`tangled-applications.tsx` fetches, filters, handles errors and renders — all in one component, so it can only be tested with a mocked `fetch` and it can't be reused (Storybook, another page, a Server Component). Split it.

## 1. `applications-view.tsx` — presentational (no hooks, no fetching)
`ApplicationsView(props)` with props:
`{ state: { kind: "loading" } | { kind: "error"; message: string } | { kind: "ready"; items: { id: number; role: string; company: string; status: string }[] }; status: string; onStatusChange(status: string): void; onRetry(): void }`
- always renders a **Status** select (`all`, `applied`, `interview`, `offer`, `rejected`; labels `All`, `Applied`, `Interview`, `Offer`, `Rejected`) with the current `status`
- `loading` → `<p role="status">Loading applications…</p>`
- `error` → `<div role="alert">` with the message and a **Retry** button calling `onRetry`
- `ready` with no items → **No applications**; otherwise `<ul aria-label="Applications">` with items `"{role} — {company} ({status})"`
- the file must not import from `react` except types, and must not call `fetch`

## 2. `applications-container.tsx` — container (`"use client"`)
`ApplicationsContainer({ loadApplications }: { loadApplications(status: string, signal: AbortSignal): Promise<Item[]> })`
- holds `status` (default `"all"`) and the load `state`
- loads on mount and whenever `status` changes; aborts the previous request; ignores stale results
- errors → `{ kind: "error", message: "Couldn't load applications" }`; **Retry** loads again
- renders `<ApplicationsView … />` — nothing else

The loader is **injected** — in the real app you pass a function that calls your BFF; in tests a fake.

```bash
cd exercises/web
npx vitest run architecture/g-frontend-patterns/01-container-presentational
```
