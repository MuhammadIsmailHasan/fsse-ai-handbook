# M4 · W5 · 04 — Context API without the foot-guns

> 🚫🤖 **No-AI** · ⏱️ ~75 min

Build three small pieces in `context-kit.tsx` (a Client Component module, starts with `"use client"`).

## 1. `createStrictContext<T>(name: string)`
Returns `[Provider, useValue] as const`:
- `Provider` is the context provider (`<Provider value={...}>`)
- `useValue()` throws `Error("use{name} must be used inside <{name}Provider>")` when there's no provider (e.g. name `Filters` → `useFilters must be used inside <FiltersProvider>`)
- default context value is `undefined` — so a provider with a falsy value like `0` or `""` must still work

## 2. Filters: split state and dispatch
- `type Filters = { status: "all" | "applied" | "interview" | "offer" | "rejected"; query: string }`
- `filtersReducer(state, action)` with actions `{ type: "setStatus", status }`, `{ type: "setQuery", query }`, `{ type: "reset" }` (back to `{ status: "all", query: "" }`)
- `<FiltersProvider initial?>` holds `useReducer` and provides **two** contexts
- `useFilters()` → state, `useFiltersDispatch()` → dispatch
- A component that only uses `useFiltersDispatch()` must **not re-render** when filters change (dispatch is stable)

## 3. Toasts
- `<ToastProvider>` renders children plus `<div role="status" aria-live="polite">` with one `<p>` per toast
- `useToast()` → `{ show(message: string): void; dismiss(id: number): void }`
  - the returned object must be **referentially stable** across renders (use `useCallback`/`useMemo`)
  - toasts auto-dismiss after **4000 ms**; each toast has a `Dismiss` button (`aria-label="Dismiss notification"`)
  - clean up timers when the provider unmounts

```bash
cd exercises/web
npx vitest run m4/w5/04-context
```
