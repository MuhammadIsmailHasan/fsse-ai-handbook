---
title: "JWT Authentication"
summary: Stateless auth for a FastAPI service — how a signed JWT carries the user's identity, why the server trusts it by checking the signature (no DB lookup), how expiry works, and how a get_current_user dependency turns a token into a user.
type: lesson
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: optional }
durationMinutes: 120
tags: [fastapi, jwt, authentication, security, tokens]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What a **JWT** is and its three parts
- Why a **signature** lets the server trust a token without a database
- The login → token → `Authorization: Bearer` flow
- **Expiry** and why short-lived tokens matter
- Turning a token into a user with a `get_current_user` dependency
- The honest trade-off: JWTs are hard to revoke

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **JWT** | A signed token carrying claims (data) | Token bertanda tangan |
| **Claim** | A piece of data in the token (e.g. user id) | Data di dalam token |
| **Signature** | Proof the token wasn't tampered with | Bukti token tak diubah |
| **Secret** | The key used to sign/verify | Kunci penanda tangan |
| **Stateless** | The server keeps no session store | Tanpa penyimpanan sesi |
| **Bearer** | The header scheme carrying the token | Skema header pembawa token |
| **exp** | Expiry time claim | Waktu kedaluwarsa |

## 🧠 The big idea

A JWT is a **festival wristband**. At the gate (login) you prove who you are once and get a tamper-evident wristband stamped by the organizer (the **signature**). Inside, every stall just glances at the wristband — they don't call the front gate to check, because a fake or altered band is obvious. The wristband itself carries who you are and when it expires.

## ❓ Why it matters

APIs need to know *who* is calling on every request, but re-checking a password each time is impossible and slow. A JWT solves this: after one login, the client carries a signed token that proves its identity. The server verifies the **signature** with its **secret** — no database lookup — so auth scales cheaply and statelessly. You used JWT + RBAC in RevoShop (Flask); the concepts are identical in FastAPI, wired through a dependency.

## 📖 Step by step

### 1. What's inside a JWT

Three dot-separated parts: `header.payload.signature`.

- **Header**: the algorithm (e.g. `HS256`).
- **Payload**: the **claims** — `sub` (subject/user id), `exp` (expiry), maybe `role`.
- **Signature**: `HMAC(header.payload, secret)` — proves the first two parts weren't changed.

The payload is only **base64-encoded, not encrypted** — anyone can read it. So never put secrets (passwords) in a JWT; it proves identity, it doesn't hide data.

### 2. The signature is the trust

The server signs with a **secret** only it knows. To verify, it recomputes the signature over the received `header.payload` and compares. If someone changes the payload (say, `role: admin`), the signature won't match and the token is rejected. That's why the server can **trust the claims without a database lookup** — the signature guarantees integrity.

### 3. The login flow

```
1. POST /login {email, password}  → server checks credentials (once)
2. server signs a JWT: {"sub": user_id, "exp": now+15min}  → returns access_token
3. client stores the token, then on each request sends:
   Authorization: Bearer <token>
4. server verifies signature + exp, reads sub → knows the user
```

### 4. Expiry (exp) and refresh

Tokens carry an **`exp`** claim and are checked on every request; an expired token is rejected. Keep access tokens **short-lived** (minutes) so a stolen token is useful only briefly. Longer sessions use a separate long-lived **refresh token** to get new access tokens (RevoShop's pattern).

### 5. Wire it with a dependency

Exactly the `get_current_user` from the DI lesson, now decoding a JWT:

```python
def get_current_user(authorization: str | None = Header(default=None)):
    token = _bearer(authorization)                 # 401 if missing/malformed
    payload = decode_and_verify(token, SECRET)     # 401 if bad signature or expired
    return load_user(payload["sub"])
```

Protected endpoints add `user = Depends(get_current_user)` — one place for all auth.

### 6. The honest trade-off: revocation

Because the server keeps no session store, it can't easily **revoke** a token before it expires (logout everywhere, ban a user instantly). Mitigations: short expiry, a small deny-list of revoked token ids, or checking a "token version" per user. Statelessness is the benefit *and* the cost.

### Choosing your auth setup

| Need | Do this |
|---|---|
| Identify the caller cheaply per request | JWT verified by signature |
| Limit damage of a stolen token | short `exp` (minutes) |
| Longer sessions | refresh token flow |
| Instant logout/ban | deny-list or token-version check |
| Hide data | ❌ not JWT — it's readable; use HTTPS + don't put secrets in it |

- ✅ Sign with a strong secret; verify signature and `exp` every request.
- ✅ Keep access tokens short-lived; centralize auth in a dependency.
- 🚫 Never store passwords/secrets in the payload; never trust an unverified token.

## ⚠️ Common mistakes

- Putting sensitive data in the payload (it's readable — only base64-encoded).
- Not checking `exp`, so old tokens work forever.
- A weak or leaked secret — anyone with it can forge tokens.
- Trusting the payload without verifying the signature.
- Assuming you can instantly revoke a JWT (you can't, without extra machinery).

:::revoshop
RevoShop uses flask-jwt-extended (JWT + RBAC). (1) Find where it issues a token at login and where it protects routes — in FastAPI these become a `/login` endpoint and `get_current_user`. (2) What claims does RevoShop put in the token (user id, role)? (3) How does RevoShop handle expiry/refresh, and what would it do to force a logout despite JWT statelessness?
:::

## 🏆 Best practices

- [ ] Sign tokens with a strong, secret key stored in config/secrets, never in code.
- [ ] Verify the signature and `exp` on every request (via `get_current_user`).
- [ ] Keep access tokens short-lived; use refresh tokens for longer sessions.
- [ ] Put only non-sensitive claims (user id, role) in the payload.
- [ ] Have a revocation strategy (short exp + deny-list or token-version) if you need instant logout.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain a JWT with the festival-wristband analogy, including why stalls don't call the gate (the signature). Then say why you must never put a password in the payload.

## 📐 Design it

Design authentication for CareerPilot's API: the `/login` endpoint, what goes in the token, how protected endpoints check it, the expiry choice, and how you'd support "log out of all devices" despite JWT being stateless.

:::quiz
Show a possible design

- **`POST /login`**: verify email+password once; on success sign a JWT `{"sub": user_id, "role": ..., "exp": now+15min}` and return `access_token` (plus a longer-lived refresh token).
- **Token contents**: `sub` (user id) and `role` for RBAC — no password or sensitive data (the payload is readable).
- **Protected endpoints**: `user = Depends(get_current_user)`, which verifies the signature and `exp` and loads the user; role checks via a `require_admin` dependency.
- **Expiry**: short access token (15 min) limits a stolen token's window; a refresh token issues new ones.
- **Log out everywhere**: since JWTs are stateless, keep a per-user **token version** (or `tokens_valid_after` timestamp) in the DB; include it in the token and reject tokens whose version is stale. Bumping the version instantly invalidates all existing tokens.

**Rule shown:** stateless JWT verified by signature + short expiry for cheap auth, plus a token-version/deny-list when you genuinely need instant revocation.
:::

### 📝 Self-review checklist

- [ ] Login issues a signed, short-lived token with only safe claims
- [ ] Every protected route verifies signature + expiry via a dependency
- [ ] Role checks handled by a dependency
- [ ] A revocation strategy exists for instant logout

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m3/w2/04-jwt" ai="no-ai" title="Sign and verify a token by hand"}
Build a minimal JWT-style token with Python's standard library: `sign(payload, secret)` produces `base64(payload).base64(hmac)`, and `verify(token, secret, now)` recomputes the signature (rejecting tampering) and checks the `exp` claim (rejecting expired). The tests tamper with a token, use a wrong secret, and expire a token — all must be rejected.
:::

:::hints
- Use `json`, `hmac`, `hashlib`, `base64` (urlsafe, strip `=` padding), and pass `now` in for determinism.
- `sign`: `body = b64(json(payload))`; `sig = b64(hmac_sha256(secret, body))`; return `f"{body}.{sig}"`.
- `verify`: split on `.`; recompute the sig with `hmac.compare_digest`; raise on mismatch; decode payload; if `payload["exp"] <= now` raise; return payload.
- Raise a clear exception (e.g. `ValueError`) for tampered/expired/wrong-secret tokens.
:::

## ✅ Quick check

:::quiz
Why can a server trust a JWT's claims without looking the token up in a database?

Because the token is signed with a secret only the server knows. The server recomputes the signature over the received header+payload; if they match, the token is authentic and unaltered, so it trusts the claims (like the user id) directly — no database round-trip needed.
:::

:::quiz
Why must you never put a password or secret in a JWT payload?

The payload is only base64-encoded, not encrypted — anyone holding the token can read it. A JWT proves identity via its signature; it does not hide its contents. Put only non-sensitive claims (user id, role) in it.
:::

## 📚 Keep learning

- [jwt.io — introduction to JSON Web Tokens](https://jwt.io/introduction)
- [FastAPI: OAuth2 with JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [OWASP: JWT security cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
