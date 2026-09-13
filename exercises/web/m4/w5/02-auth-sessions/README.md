# M4 · W5 · 02 — Authentication: sessions, DAL and `proxy.ts`

> 🚫🤖 **No-AI** · ⏱️ ~2 h

CareerPilot's Flask API issues an access token on login. The browser must **never** see that token in JavaScript. We keep it inside an **encrypted, httpOnly session cookie** managed by Next.js, and check it in three layers.

Provided: `lib/flask-auth.ts` → `loginWithFlask(email, password)` returns `{ accessToken, user: { id, name, role } }` or throws `InvalidCredentials`.

## 1. `lib/session.ts` (starts with `import "server-only"`)
Session payload: `{ userId: number; role: "member" | "admin"; accessToken: string; expiresAt: string }` (ISO date).
- `encrypt(payload)` → a JWT signed with **HS256** using `process.env.SESSION_SECRET` (jose `SignJWT`), `iat` set, expires in **7 days**
- `decrypt(token?)` → the payload, or `null` for missing / tampered / expired tokens (never throws)
- `createSession(user, accessToken)` → sets cookie **`session`**: `httpOnly: true`, `secure: true`, `sameSite: "lax"`, `path: "/"`, `expires` = 7 days from now
- `deleteSession()` → deletes the `session` cookie

## 2. `lib/safe-redirect.ts`
`safeNextPath(value: unknown)` → the value only if it is a **relative path** (starts with a single `/`, not `//`, no backslash, no `:` before the first `/`… keep it simple: must match `^/(?![/\\])`). Otherwise `"/dashboard"`. Prevents **open redirects** (`?next=https://evil.example`).

## 3. `app/login/actions.ts` (`"use server"`)
- `login(prev: LoginState, formData)` → validate `email` (email) and `password` (min 1) with Zod; on failure `{ message: "Enter your email and password" }`. Call Flask; `InvalidCredentials` → `{ message: "Invalid email or password" }` (same message for unknown email and wrong password!). Success → `createSession`, then `redirect(safeNextPath(formData.get("next")))`.
- `logout()` → `deleteSession()` then `redirect("/login")`

## 4. `lib/dal.ts` — Data Access Layer (`server-only`)
- `verifySession` — wrapped in React `cache()`: reads the cookie via `cookies()`, decrypts; no valid session → `redirect("/login")`; else `{ userId, role, accessToken }`
- `getCurrentUser()` → calls `verifySession()` and returns a **DTO** `{ id, role }` — never the token

## 5. `proxy.ts` — optimistic checks only
`export default async function proxy(request: NextRequest)`:
- protected prefixes `/dashboard`, `/applications` without a valid session → redirect to `/login?next=<original path + search>`
- `/login` **with** a valid session → redirect to `/dashboard`
- otherwise `NextResponse.next()`
- export `config.matcher` that skips `api`, `_next/static`, `_next/image` and `favicon.ico`

```bash
cd exercises/web
npx vitest run m4/w5/02-auth-sessions
```
