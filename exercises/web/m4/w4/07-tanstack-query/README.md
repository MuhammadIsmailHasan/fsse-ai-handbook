# M4 · W4 · 07 — Server State with TanStack Query

> 🤖✅ **AI-allowed** (explain every line) · ⏱️ ~90 min · Client Components with `@tanstack/react-query` v5

The API is injected (`ApplicationsApi` type is provided) so tests can control responses.

## 1. `lib/query-keys.ts` — a key factory
```ts
applicationKeys.all            // ["applications"]
applicationKeys.lists()        // ["applications", "list"]
applicationKeys.list(filters)  // ["applications", "list", filters]
applicationKeys.detail(id)     // ["applications", "detail", id]
```
(`as const` arrays so keys are typed.)

## 2. `lib/applications-hooks.ts`
- `useApplications(api, filters)` → `useQuery` with key `applicationKeys.list(filters)`, `queryFn: ({ signal }) => api.listApplications(filters, { signal })`, `staleTime: 30_000`, and `placeholderData: keepPreviousData` (the old list stays visible while a new filter loads)
- `useMoveStatus(api)` → `useMutation` calling `api.moveStatus(id, status)` with an **optimistic update**:
  - `onMutate`: `cancelQueries` for `applicationKeys.lists()`, snapshot every list with `getQueriesData`, update the item's `status` in every cached list with `setQueriesData`, return the snapshot
  - `onError`: restore every snapshot
  - `onSettled`: `invalidateQueries` for `applicationKeys.lists()` and `applicationKeys.detail(id)`

## 3. `lib/applications-panel.tsx` — `ApplicationsPanel({ api, filters })`
- first load (`isPending`): `<p role="status">Loading applications…</p>`
- error: `<div role="alert">Couldn't load applications <button>Retry</button></div>` → `refetch()`
- success: `<ul>` with `<li>` per application containing the role and a `<select aria-label="Status for {role}">` (options `saved`, `applied`, `interview`, `offer`, `rejected`) that calls the mutation on change
- while refetching in the background (`isFetching` but not pending): `<p aria-live="polite">Updating…</p>`
- if the mutation fails: `<p role="alert">Couldn't move {role}</p>` (use the mutation's `error` + `variables`)

```bash
cd exercises/web
npx vitest run m4/w4/07-tanstack-query
```
