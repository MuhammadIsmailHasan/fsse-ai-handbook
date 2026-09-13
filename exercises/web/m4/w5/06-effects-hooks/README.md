# M4 · W5 · 06 — Side effects and custom hooks

> 🚫🤖 **No-AI** · ⏱️ ~2 h

`useEffect` is for **synchronizing with something outside React** (timers, network, browser APIs, storage). Everything else — derived values, event responses — doesn't need an effect.

## `hooks.ts` (`"use client"`)
1. **`useDebouncedValue<T>(value: T, delayMs: number): T`** — returns the latest value only after it stopped changing for `delayMs`. Clear the timer on change/unmount.
2. **`useOnlineStatus(): boolean`** — built with **`useSyncExternalStore`**: subscribe to window `online`/`offline`, snapshot `navigator.onLine`, **server snapshot `true`**.
3. **`useFetchJson<T>(url: string | null)`** → `{ status: "idle" | "loading" | "success" | "error"; data: T | null; error: string | null }`
   - `null` url → idle (no request)
   - uses an `AbortController`; aborts the previous request when `url` changes and on unmount
   - a **stale response must never overwrite** a newer one (race condition)
   - non-OK response → `error: "Request failed with status {status}"`; abort errors are ignored
4. **`useLocalStorage<T>(key: string, initial: T)`** → `[value, setValue]`
   - the first render (and server render) uses `initial`; read storage **after mount**
   - invalid JSON in storage → keep `initial`
   - `setValue` writes JSON to storage
   - listens to the `storage` event so other tabs' changes for the same key show up (remove the listener on unmount)

## `job-count.tsx`
`<JobCount jobs={[{ title }]} query="data" />` → `<p>{n} matching jobs</p>` (case-insensitive `title` contains `query`, trimmed; empty query = all).
**Rule:** compute it during render — this file must not use `useEffect` or `useState`.

```bash
cd exercises/web
npx vitest run m4/w5/06-effects-hooks
```
