# M4 · W4 · 04 — Calling the Flask API: Typed Client, Errors and Error Boundaries

> 🚫🤖 **No-AI** · ⏱️ ~90 min

CareerPilot's frontend talks to the **Phase 2 Flask API** (`/api/v1/applications`, errors shaped like `{"error": {"code", "message", "fields"?}}`).

## 1. `lib/api-client.ts`
- `class ApiError extends Error` with `status: number`, `code: string`, `fields?: Record<string, string[]>`, `name = "ApiError"`
- `createApiClient({ baseUrl, getToken, fetchImpl = fetch })` returns:
  - `listApplications({ status?, page? })` → `GET {baseUrl}/api/v1/applications` with only the given params (`status`, `page`), headers `Accept: application/json` and `Authorization: Bearer {token}` when `getToken()` returns one, and `cache: "no-store"`. Resolves to `{ data: Application[]; meta: { page; per_page; total } }`
  - `getApplication(id)` → `GET …/api/v1/applications/{id}` → the `data` object
  - non-2xx → `ApiError(status, error.code, error.message, error.fields)`; if the body isn't the expected JSON → code `"unknown_error"`; network failure (fetch throws) → `ApiError(0, "network_error", …)`

## 2. `app/applications/page.tsx` (async Server Component)
Props `{ searchParams: Promise<{ status?: string; page?: string }> }`. Get the client with the provided `getServerApi()` from `lib/server-api.ts`.
- Only pass `status` if it's one of `saved, applied, interview, offer, rejected`; `page` only if it's a positive integer (otherwise page 1)
- Render `<h1>Applications</h1>`; if there are no applications `<p>No applications found</p>`; otherwise a `<ul>` of `<li>{role} at {company.name}</li>` and `<p>Page {page} of {totalPages}</p>` (`totalPages = max(1, ceil(total / per_page))`)
- `ApiError` with status `401` → `redirect("/login?next=/applications")` (from `next/navigation`); any other error: let it throw (the error boundary handles it)

## 3. `app/applications/error.tsx` and `loading.tsx`
- `error.tsx`: a **Client Component** receiving `{ error, retry }`. Log the error with `console.error` in an effect; render `<div role="alert">` with `<h2>We couldn't load your applications</h2>` and a `<button>Try again</button>` calling `retry()`
- `loading.tsx`: `<p role="status">Loading applications…</p>`

```bash
cd exercises/web
npx vitest run m4/w4/04-api-integration
```
