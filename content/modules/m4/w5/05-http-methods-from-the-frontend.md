---
title: "HTTP Methods from the Frontend"
summary: Call GET, POST, PATCH and DELETE correctly from a Next.js app — Route Handlers as a Backend-for-Frontend, forwarding the session token, status codes like 201/204/422, idempotency, and a typed browser client.
type: lesson
source: core
sourceRef: "M3 · W5 · L5"
split: true
roles: { be: recommended, fe: core, fs: core, ai: recommended, ops: none }
durationMinutes: 150
tags: [http, rest, route-handlers, bff, fetch, nextjs]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Which HTTP method to use for each UI action, and what **safe** and **idempotent** mean
- Three ways a Next.js frontend talks to Flask: Server Components, Server Actions, **Route Handlers**
- The **Backend-for-Frontend (BFF)** pattern: forwarding requests with the session token
- `route.ts` handlers for `GET`, `POST`, `PATCH`, `DELETE` with async `params`
- Passing through status codes (`201`, `204`, `401`, `404`, `409`, `422`, `502`)
- A small typed browser client for Client Components (and TanStack Query)

## 🧠 The big idea

HTTP methods are **verbs** in a sentence to the server:

- `GET /applications` — "show me" (reading, no side effects)
- `POST /applications` — "create this"
- `PATCH /applications/7` — "change part of this"
- `PUT /applications/7` — "replace this entirely"
- `DELETE /applications/7` — "remove this"

The BFF is a **receptionist**: the browser talks only to the receptionist (your Next.js server, same domain, with the session cookie), and the receptionist calls the right department (Flask) with the staff badge (access token) the visitor never holds.

## ❓ Why does this exist?

Client Components (a drag-and-drop board, an autosave notes editor) need to call the API **from the browser**. But:

- The Flask token is in an **httpOnly cookie** — browser JavaScript can't read it (lesson 02).
- Calling Flask directly from the browser needs CORS configuration and exposes the API's address.

Route Handlers solve both: the browser calls `/api/applications` on the **same origin**; the handler reads the session on the server and forwards the request.

## 💥 What happens if we DON'T?

- `POST` used for everything → caches, retries and logs can't reason about requests.
- `DELETE` returns `200` with `{"success": true}` in one place and `204` elsewhere → client code breaks on `response.json()` of an empty body.
- A proxy that forwards **any path** (`/api/proxy/[...path]`) lets users reach admin endpoints you never meant to expose.
- Upstream error messages (`connect ECONNREFUSED 10.0.3.7:5091`) leak internal infrastructure to users.

## 📖 How it works, step by step

### 1. Methods and their guarantees

| Method | Use | Safe (no changes)? | Idempotent (repeat = same result)? | Typical success |
|---|---|---|---|---|
| GET | read | ✅ | ✅ | 200 |
| POST | create / run an action | ❌ | ❌ | 201 (+ `Location`) / 200 / 202 |
| PUT | replace | ❌ | ✅ | 200 / 204 |
| PATCH | partial update | ❌ | not guaranteed | 200 |
| DELETE | remove | ❌ | ✅ | 204 |

Idempotency matters for **retries**: a network timeout on `DELETE` can be retried safely; retrying `POST` might create two applications (use an `Idempotency-Key` header for payments, see Architecture F).

### 2. Picking the channel in Next.js

| Need | Use |
|---|---|
| Render a page with data | **Server Component** calls Flask directly (DAL) |
| Form submit / button mutation that refreshes server-rendered UI | **Server Action** (lesson 01) |
| Client Component fetching/mutating (TanStack Query, autosave, drag and drop) | **Route Handler** (BFF) |
| Webhooks, third-party callbacks, files, public API for other clients | **Route Handler** |

### 3. A shared forwarding helper

```ts
// lib/bff.ts
export async function forwardToFlask(path: string, init: { method: string; body?: unknown }) {
  const session = await getSession();
  if (!session) return Response.json({ error: { code: "unauthenticated" } }, { status: 401 });

  const hasBody = init.body !== undefined;
  let upstream: Response;
  try {
    upstream = await fetch(`${process.env.API_URL}${path}`, {
      method: init.method,
      headers: {
        Authorization: `Bearer ${session.accessToken}`,
        Accept: "application/json",
        ...(hasBody ? { "Content-Type": "application/json" } : {}),
      },
      body: hasBody ? JSON.stringify(init.body) : undefined,
      cache: "no-store",
    });
  } catch {
    return Response.json({ error: { code: "upstream_unavailable" } }, { status: 502 });
  }

  if (upstream.status === 204) return new Response(null, { status: 204 });
  return new Response(await upstream.text(), { status: upstream.status, headers: { "Content-Type": "application/json" } });
}
```

- **Explicit routes only** — each handler decides which Flask path it calls.
- Status codes pass through so the client sees Flask's `422` field errors.
- `204` must have **no body**.

### 4. Route Handlers

```ts
// app/api/applications/route.ts → /api/applications
export async function GET(request: Request) {
  const { search } = new URL(request.url);             // keep ?status=applied&page=2
  return forwardToFlask(`/api/v1/applications${search}`, { method: "GET" });
}

export async function POST(request: Request) {
  const body = await readJson(request);                // 400 on invalid JSON
  if (!body.ok) return body.response;
  return forwardToFlask("/api/v1/applications", { method: "POST", body: body.data });
}
```

```ts
// app/api/applications/[id]/route.ts → /api/applications/7
export async function PATCH(request: Request, ctx: RouteContext<"/api/applications/[id]">) {
  const { id } = await ctx.params;                     // params are a Promise in Next.js 15+
  if (!/^\d+$/.test(id)) return Response.json({ error: { code: "invalid_id" } }, { status: 400 });
  const body = await readJson(request);
  if (!body.ok) return body.response;
  return forwardToFlask(`/api/v1/applications/${id}`, { method: "PATCH", body: body.data });
}
```

`RouteContext<'/api/applications/[id]'>` is a global helper type generated by Next.js (`next dev`/`next build`/`next typegen`). In the exercise we write the type by hand.

:::warning[Route Handlers are public]
Like Server Actions, every `route.ts` is reachable by anyone. Authenticate (and authorize) in each handler. `GET` handlers are **not cached** by default — keep it that way for per-user data.
:::

### 5. The browser client

```ts
// lib/applications-client.ts — imported by Client Components
async function request<T>(path: string, method: string, body?: unknown): Promise<T> {
  const response = await fetch(path, {
    method,
    headers: body === undefined ? { Accept: "application/json" } : { Accept: "application/json", "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (response.status === 204) return null as T;
  const json = await response.json().catch(() => null);          // error pages may be HTML
  if (!response.ok) throw new ApiError(response.status, json?.error?.code ?? "unknown_error");
  return json as T;
}

export const applicationsClient = {
  list: (status?: string) => request<Application[]>(status ? `/api/applications?status=${encodeURIComponent(status)}` : "/api/applications", "GET"),
  create: (input: NewApplication) => request<Application>("/api/applications", "POST", input),
  update: (id: number, patch: ApplicationPatch) => request<Application>(`/api/applications/${id}`, "PATCH", patch),
  remove: (id: number) => request<null>(`/api/applications/${id}`, "DELETE"),
};
```

Cookies are sent automatically on same-origin `fetch`. Plug these functions into TanStack Query's `queryFn`/`mutationFn` (W4 L7).

```mermaid
sequenceDiagram
    participant C as Client Component
    participant R as Route Handler (Next.js)
    participant F as Flask API
    C->>R: PATCH /api/applications/7 {status:"offer"} + session cookie
    R->>R: getSession() → accessToken; validate id; parse JSON
    R->>F: PATCH /api/v1/applications/7 Authorization: Bearer …
    F-->>R: 200 {…} or 422 {error…}
    R-->>C: same status + body
```

## ⚖️ Trade-offs

| | ✅ | ❌ |
|---|---|---|
| Browser → Flask directly | fewer hops, simple | token must be JS-readable, CORS, API exposed |
| BFF Route Handlers | token stays server-side, same-origin, can reshape data | extra hop/latency, more code to maintain |
| Catch-all proxy (`rewrites` / `[...path]`) | little code | easy to expose unintended endpoints; auth header injection needs care |
| Server Actions for mutations | no route code, revalidation built in | POST only, sequential, not for external clients |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ BFF handlers for interactive client features that need the user's token.
- ✅ Route Handlers for webhooks (Midtrans in RevoShop-style apps), file downloads, RSS/sitemaps.
- 🚫 Don't call your own Route Handler **from a Server Component** — call the data function directly (an extra HTTP hop for nothing).
- 🚫 Don't build a generic proxy that forwards any path and method.

## 🏆 Best practices

- [ ] Use methods by meaning: GET reads, POST creates, PATCH updates partially, DELETE removes.
- [ ] Return `201` for creates, `204` with no body for deletes, and keep error bodies consistent (`{ error: { code, message?, fields? } }`).
- [ ] Authenticate in every handler; forward only allow-listed paths.
- [ ] Validate route params and JSON before calling upstream.
- [ ] Never leak upstream error details or internal hostnames; log them server-side.
- [ ] `cache: "no-store"` for per-user upstream requests.
- [ ] Set timeouts on upstream calls (`AbortSignal.timeout(10_000)`).
- [ ] Only send `Content-Type: application/json` when there's a body.
- [ ] Use `encodeURIComponent` / `URLSearchParams` for query strings.

## 🏭 How it's used in industry

- The BFF pattern is common at companies with many backend services (Netflix, SoundCloud popularised it): each frontend gets a tailored API layer.
- Next.js Route Handlers often wrap internal microservices so browsers only ever talk to one origin.
- Public APIs document methods and status codes with OpenAPI (Module 2 W5), and frontends generate typed clients from it.

## ⚠️ Common mistakes

- `await response.json()` on a `204` → "Unexpected end of JSON input".
- Building `/api/v1/applications/${id}` without validating `id` (`../admin/users`).
- Forgetting that `params` is a Promise → `id` is `undefined`.
- Returning `NextResponse.json(error)` with status `200` for errors.
- Sending `GET` requests with a body.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain the receptionist analogy for the BFF, then explain to a teammate why retrying a timed-out `DELETE` is safe but retrying a `POST` might not be.

## 📐 Design it

CareerPilot's **notes editor** autosaves while typing, lets users pin a note, reorder notes by drag and drop, and delete notes. Design the Route Handlers (paths, methods, request bodies, success and error status codes) and the matching Flask endpoints. Mark which operations are idempotent.

:::quiz
Show a possible design

| Next.js route | Method | Body | Flask | Success | Errors | Idempotent |
|---|---|---|---|---|---|---|
| `/api/applications/[id]/notes` | GET | — | `GET /api/v1/applications/{id}/notes` | 200 `Note[]` | 401, 404 | ✅ |
| `/api/applications/[id]/notes` | POST | `{ body }` | `POST …/notes` | **201** `Note` + `Location` | 401, 404, 422 | ❌ (send `Idempotency-Key` from a client-generated UUID to make autosave-create safe) |
| `/api/notes/[noteId]` | PATCH | `{ body?, pinned? }` | `PATCH /api/v1/notes/{noteId}` | 200 `Note` | 401, 404, 409 (version conflict with `If-Match`/`version`), 422 | ✅ in practice (same body → same state) |
| `/api/applications/[id]/notes/order` | PUT | `{ noteIds: number[] }` | `PUT …/notes/order` | 204 | 401, 404, 422 (ids don't match) | ✅ (full replacement) |
| `/api/notes/[noteId]` | DELETE | — | `DELETE /api/v1/notes/{noteId}` | 204 | 401, 404 | ✅ |

- Autosave: debounce 800 ms, `PATCH` with a `version` to avoid overwriting edits from another tab (409 → show "updated elsewhere").
- Reorder uses **PUT** of the full order rather than many PATCHes — one request, idempotent.
- Every handler validates ids and authenticates; Flask checks ownership.
:::

### 📝 Self-review checklist

- [ ] Status codes match the method semantics
- [ ] Conflicts and validation errors are distinguishable
- [ ] No catch-all proxy

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w5/05-route-handlers" ai="no-ai" title="A BFF for applications"}
Write a forwarding helper, collection and item Route Handlers for GET/POST/PATCH/DELETE (with id validation, invalid JSON handling, 204 passthrough and 502 on network errors), and a typed browser client.
:::

:::hints
- `new URL(request.url).search` keeps the query string (including `?`).
- `await request.json()` throws on invalid JSON — catch it.
- Test the `204` path: `new Response(null, { status: 204 })`.
:::

## ✅ Quick check

:::quiz
A Server Component needs the applications list. Should it `fetch("/api/applications")`?

No. Call the server data function (DAL) directly. Route Handlers are for the browser and external callers; calling them from the server adds an HTTP hop and needs an absolute URL and forwarded cookies.
:::

:::quiz
What's the difference between PUT and PATCH for `{ "status": "offer" }`?

PATCH changes only `status`. PUT means "this is the whole resource" — fields you omit would be cleared or rejected.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| HTTP method | Metode HTTP (kata kerja request) |
| Idempotent | Hasil sama walau diulang |
| Route Handler | Endpoint API di Next.js (`route.ts`) |
| Backend-for-Frontend | Lapisan backend khusus untuk frontend |
| Upstream | Server tujuan di belakang proxy |
| Status code | Kode status respons |

## 📚 Keep learning

- Next.js docs (bundled): Backend for Frontend guide; `route.js` file convention; Route Handlers
- [MDN: HTTP request methods](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods)
- [MDN: HTTP response status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
