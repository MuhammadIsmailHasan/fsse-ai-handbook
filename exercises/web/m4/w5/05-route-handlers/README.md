# M4 · W5 · 05 — HTTP methods with Route Handlers (Backend-for-Frontend)

> 🚫🤖 **No-AI** · ⏱️ ~90 min

Client Components can't read the httpOnly session cookie — good! So they call **our own** Next.js endpoints (`/api/applications…`), and those Route Handlers add the Flask token on the server. This is the **BFF** (Backend for Frontend) pattern.

Provided: `lib/session.ts` → `getSession()` returns `{ accessToken }` or `null`.

## 1. `lib/bff.ts`
`forwardToFlask(path: string, init: { method: string; body?: unknown }): Promise<Response>`
1. no session → `401` JSON `{ error: { code: "unauthenticated" } }` (and **no** upstream call)
2. `fetch(process.env.API_URL + path, { method, headers: { Authorization: "Bearer <token>", Accept: "application/json" (+ "Content-Type: application/json" only when there is a body) }, body: JSON.stringify(body), cache: "no-store" })`
3. network failure → `502` `{ error: { code: "upstream_unavailable" } }` (don't leak the error message)
4. upstream `204` → `new Response(null, { status: 204 })`; otherwise return the upstream body **text** with the same status and `Content-Type: application/json`

`readJson(request)` → `{ ok: true, data }` or `{ ok: false, response }` where response is `400` `{ error: { code: "invalid_json" } }`.

## 2. `app/api/applications/route.ts`
- `GET(request)` → forward `GET /api/v1/applications` **keeping the query string** (`?status=applied&page=2`)
- `POST(request)` → read JSON (400 on invalid), forward as `POST`

## 3. `app/api/applications/[id]/route.ts`
Second argument: `{ params }: { params: Promise<{ id: string }> }` (params are async in Next.js 15+).
- `id` must be digits only → else `400` `{ error: { code: "invalid_id" } }`
- `GET` → forward; `PATCH` → JSON body, forward; `DELETE` → forward (expect 204)

## 4. `lib/applications-client.ts` — used by Client Components
`ApiError(status, code)` and `applicationsClient`:
- `list(status?)` → `GET /api/applications` (+ `?status=` when given, URL-encoded)
- `create(input)` → `POST`, `update(id, patch)` → `PATCH /api/applications/{id}`, `remove(id)` → `DELETE`
- JSON header only when sending a body; non-OK → throw `ApiError` using `body.error.code` (fallback `"unknown_error"`); `204` → `null`

```bash
cd exercises/web
npx vitest run m4/w5/05-route-handlers
```
