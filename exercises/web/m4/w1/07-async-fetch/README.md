# M4 · W1 · 07 — Talking to an API with fetch and async/await

> 🚫🤖 **No-AI** · ⏱️ ~75 min · edit **`api-client.js`**

Every function receives `fetchImpl` (the real `fetch` in the browser, a fake in tests) — this is dependency injection, just like the Flask lessons.

| Export | Behavior |
|---|---|
| `class ApiError extends Error` | `new ApiError(status, body)` with `.status`, `.body`, `.name = "ApiError"`, message `"Request failed with status {status}"` |
| `getJson(fetchImpl, url, options = {})` | `await fetchImpl(url, { ...options, headers: { Accept: "application/json", ...options.headers } })`; non-2xx (`!response.ok`) → throw `ApiError` with the parsed JSON body (or `null` if the body isn't JSON); 2xx → parsed JSON (`204` → `null`) |
| `class TimeoutError extends Error` | `.name = "TimeoutError"` |
| `getJsonWithTimeout(fetchImpl, url, ms)` | uses an `AbortController`; if the request takes longer than `ms`, abort it and throw `TimeoutError`. Always clear the timer |
| `loadDashboard(fetchImpl, baseUrl)` | fetches `/api/v1/me`, `/api/v1/applications` and `/api/v1/stats` **in parallel** (`Promise.all`) and returns `{ user, applications, stats }` (each response has a `data` field) |
| `loadCompanies(fetchImpl, baseUrl, ids)` | fetches `/api/v1/companies/{id}` for each id with `Promise.allSettled`; returns `{ companies: [data…], failedIds: [id…] }` (keep the input order) |
| `withRetry(fn, { attempts = 3, delayMs = 200, sleep })` | calls `await fn()`; on an `ApiError` with status `>= 500` (or a `TypeError` = network error) waits `delayMs * 2 ** (attempt - 1)` via `sleep` and retries; other errors are thrown immediately; after the last attempt, rethrow |

```bash
cd exercises/web
npx vitest run m4/w1/07-async-fetch
```
