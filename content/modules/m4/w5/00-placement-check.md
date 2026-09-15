---
title: "Week 5 Placement Check"
summary: Server Actions and form states, session-based login, roles and permissions, Context, Route Handlers, useEffect, React Hook Form + Zod, shadcn/ui and Zustand — check what you can skip.
type: placement-check
source: original
roles: { be: optional, fe: core, fs: core, ai: recommended, ops: none }
durationMinutes: 20
tags: [placement, forms, authentication, rbac, react, nextjs]
---

::::placement{id="modules/m4/w5"}
Answer from memory. If a word is new to you, that's a sign to study the lesson.

:::quiz
1 · A Server Action checks a form and returns field errors. Which hooks show those errors and a "Saving…" button? And why must the server still check the form if the browser already did?

`useActionState(action, initialState)` returns `[state, formAction, isPending]`; `useFormStatus()` inside the form gives `pending` for the submit button. A Server Action is a public POST endpoint — anyone can call it without your page — so the server's check is the only one you can trust.
:::

:::quiz
2 · After login, where should a Next.js app keep the Flask access token, and which cookie settings matter?

In a signed or encrypted session cookie set by the server: `httpOnly` (JavaScript can't read it), `secure` (HTTPS only), `sameSite: "lax"` (blocks most requests from other sites), `path: "/"` and an expiry time. Not in `localStorage`.
:::

:::quiz
3 · You check login in `proxy.ts` and hide the admin link from non-admins. Is the admin Server Action safe?

No. The proxy check is only a quick first check, and hiding a link is only cosmetic. The Server Action (and the Flask API) must check the session and the permission themselves.
:::

:::quiz
4 · A context provides `{ filters, setFilters }` as a new object created in the provider. What performance problem does that cause, and one fix?

A new object on every render redraws every component that uses the context, even ones that only call `setFilters`. Fixes: wrap the value in `useMemo`, or split it into a state context and a setter context.
:::

:::quiz
5 · Name two bugs in `useEffect(() => { fetch(url).then(r => r.json()).then(setData) }, [url])`.

No cancelling → a slow old response can overwrite a newer one (race condition), and it can set state after the component is gone. Also no loading or error handling. Add an `AbortController` cleanup — or use TanStack Query / Server Components.
:::

:::quiz
6 · When would you choose React Hook Form + Zod over a simple Server Action form, and Zustand over Context?

React Hook Form + Zod: big browser forms with instant checks, repeating field groups, many fields. Zustand: browser UI state shared by components far apart that changes often, where you want each component to subscribe only to the part it uses. Server data stays in Server Components or TanStack Query.
:::
::::

:::tip[Scoring yourself]
Pass with **5 of 6**. Questions 2 and 3 are about security — if you missed either one, do lessons 02 and 03 anyway.
:::
