---
title: "Week 5 Placement Check"
summary: Server Actions and form states, session-based authentication, RBAC, Context, Route Handlers, useEffect, React Hook Form + Zod, shadcn/ui and Zustand — check what you can skip.
type: placement-check
source: original
roles: { be: optional, fe: core, fs: core, ai: recommended, ops: none }
durationMinutes: 20
tags: [placement, forms, authentication, rbac, react, nextjs]
---

::::placement{id="modules/m4/w5"}
:::quiz
1 · A Server Action validates a form and returns field errors. Which hooks show those errors and a "Saving…" button, and why must you still validate on the server if the client validates too?

`useActionState(action, initialState)` returns `[state, formAction, isPending]`; `useFormStatus()` inside the form gives `pending` for the submit button. Server Actions are public POST endpoints — anyone can call them without your client code, so the server is the only validation you can trust.
:::

:::quiz
2 · Where should a Next.js app keep the Flask access token after login, and which cookie flags matter?

In an encrypted/signed session cookie set on the server: `httpOnly` (JavaScript can't read it), `secure` (HTTPS only), `sameSite: "lax"` (CSRF protection for most cross-site requests), `path: "/"` and an expiry. Not in `localStorage`.
:::

:::quiz
3 · You check authentication in `proxy.ts` and hide the admin link for non-admins. Is the admin Server Action safe?

No. Proxy checks are optimistic and UI hiding is cosmetic. The Server Action (and the Flask API) must verify the session and the permission themselves.
:::

:::quiz
4 · A context holds `{ filters, setFilters }` created inline in the provider. What performance problem does that cause, and one fix?

A new object every render re-renders every consumer, even ones that only call `setFilters`. Fixes: `useMemo` the value, or split into a state context and a dispatch context.
:::

:::quiz
5 · Name two bugs in `useEffect(() => { fetch(url).then(r => r.json()).then(setData) }, [url])`.

No cancellation/ignore flag → a slow old response can overwrite a newer one (race condition), and it sets state after unmount. Also no error or loading handling. Use an `AbortController` cleanup — or TanStack Query / Server Components.
:::

:::quiz
6 · When would you pick React Hook Form + Zod over a plain Server Action form, and when Zustand over Context?

RHF + Zod: rich client forms (instant validation, dynamic field arrays, many fields). Zustand: client UI state shared by distant components that changes often, where you want selector-based subscriptions without provider re-renders. Server data stays in Server Components / TanStack Query.
:::
::::

:::tip[Scoring yourself]
Pass with **5 of 6**. Questions 2 and 3 are security questions — if you missed either, do lessons 02 and 03 anyway.
:::
