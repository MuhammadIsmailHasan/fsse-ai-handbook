---
title: "RBAC & Conditional Rendering"
summary: Show the right screens to each role and enforce it where it matters — permission tables instead of role checks, ownership rules, filtered menus, a Can component, and checks on the server.
type: lesson
source: core
sourceRef: "M3 · W5 · L3"
roles: { be: recommended, fe: core, fs: core, ai: optional, ops: none }
durationMinutes: 150
tags: [rbac, authorization, permissions, conditional-rendering, security, nextjs]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Roles vs **permissions**: ask "can this user do X?", not "is this user an admin?"
- One **policy file** used by both the screens and the server
- **Ownership** rules: my data, my mentees' data
- Showing or hiding UI: filtered menus, a `<Can>` component, hide vs disable
- **Enforcing** permissions in Server Actions, pages and the API
- When to answer 403 vs 404

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Role** | A group of users: member, mentor, admin | Peran |
| **Permission** | One thing a user may do: "manage companies" | Izin |
| **RBAC** | Role-Based Access Control: roles give permissions | Kontrol akses berbasis peran |
| **Ownership** | "This application belongs to user 7" | Kepemilikan |
| **Policy** | The functions that decide yes/no for an action | Aturan izin |
| **Enforce** | Actually block the action on the server | Menegakkan aturan |
| **Deny by default** | If a rule doesn't say yes, the answer is no | Tolak kalau tidak jelas |
| **403 / 404** | "Not allowed" / "Not found" | Dilarang / tidak ditemukan |

## 🧠 The big idea

In an office building, your **access card** (role) opens certain doors (permissions). The screen in the lobby may only show the floors you can visit — that's convenient (conditional rendering). But the **door locks** still check your card. If someone takes the stairs, the lock is what stops them.

- Hiding UI = the lobby screen (comfort).
- Server authorization = the door locks (security).

You need both, but only the locks are security.

## ❓ Why it matters

CareerPilot has **members** (job seekers), **mentors** who review their mentees' applications, and **admins** who manage companies and users. Without a clear model, checks spread everywhere:

```tsx
{user.role === "admin" || user.role === "mentor" ? <MenteesLink /> : null}
```

When you add a "career coach" role, you have to search 40 files.

Worse problems:
- A member can't see the "Delete company" button — but the Server Action has no check, so calling it from DevTools deletes the company.
- `/applications/15` shows someone else's application because the page only checked "logged in".
- Screens disagree ("mentors can comment" in one place but not another).

## 📖 Step by step

### 1. Roles give permissions

```ts
// lib/permissions.ts — pure TypeScript, usable on server and client
export type Role = "member" | "mentor" | "admin";
export type Permission =
  | "applications:read:own" | "applications:write:own"
  | "applications:read:mentees" | "notes:comment"
  | "companies:manage" | "users:manage";

const MEMBER = ["applications:read:own", "applications:write:own"] as const;

export const ROLE_PERMISSIONS: Record<Role, readonly Permission[]> = {
  member: MEMBER,
  mentor: [...MEMBER, "applications:read:mentees", "notes:comment"],
  admin: [...MEMBER, "applications:read:mentees", "notes:comment", "companies:manage", "users:manage"],
};

export function can(user: { role: Role } | null, permission: Permission) {
  return !!user && Object.hasOwn(ROLE_PERMISSIONS, user.role) && ROLE_PERMISSIONS[user.role].includes(permission);
}
```

- One **table** says which role has which permissions — like a list of which doors each access card opens.
- Feature code asks about **permissions** (`can(user, "companies:manage")`), never role names.
- Adding a role = editing one table.
- `can` says **no** when there's no user or the role is unknown (deny by default).

### 2. Ownership and relationships

A permission alone can't answer "can Sari edit **this** application?".

```ts
export function canEditApplication(user: Actor, app: { ownerId: number }) {
  if (user.role === "admin") return true;
  return app.ownerId === user.id && can(user, "applications:write:own");
}

export function canViewApplication(user: Actor, app: { ownerId: number }) {
  if (user.role === "admin") return true;
  if (app.ownerId === user.id) return can(user, "applications:read:own");
  return can(user, "applications:read:mentees") && (user.menteeIds ?? []).includes(app.ownerId);
}
```

Like a hotel: your key card works for **floors** your room type allows (permission), but it only opens **your own room** (ownership). Most apps need exactly this: **RBAC + ownership**. When rules depend on many details (department, time, subscription plan), teams move to policy engines.

### 3. Showing and hiding UI

```tsx
// Navigation derived from the same policy
export const navFor = (user: User | null) => NAV_ITEMS.filter((item) => !item.requires || can(user, item.requires));

// Declarative helper
export function Can({ user, permission, children, fallback = null }: CanProps) {
  return <>{can(user, permission) ? children : fallback}</>;
}

<Can user={user} permission="companies:manage" fallback={<p>Ask an admin to edit companies.</p>}>
  <DeleteCompanyButton companyId={company.id} />
</Can>
```

- The menu is built from the same `can` function, so screens can't disagree.
- `<Can>` shows its children only when allowed, otherwise a `fallback`.

| Situation | Hide or disable? |
|---|---|
| The user will **never** have access (member → admin panel) | **hide** |
| The user **could** get access (upgrade plan, verify account) | **disable + explain how** |
| Temporarily unavailable (form invalid, already applied) | **disable + give the reason** |

### 4. Enforce on the server — at every door

```ts
// Server Action
"use server";
export async function deleteCompanyAction(companyId: number) {
  const session = await verifySession();                       // authentication
  if (!can(session, "companies:manage")) {                     // authorization
    return { ok: false, message: "You don't have permission to do that" } as const;
  }
  await deleteCompany(companyId);
  return { ok: true } as const;
}
```

```tsx
// Page for a single resource
export default async function ApplicationPage({ params }: PageProps<"/applications/[id]">) {
  const user = await getCurrentUser();
  const app = await getApplication(Number((await params).id));
  if (!app || !canViewApplication(user, app)) notFound();       // 404: don't reveal it exists
  return <ApplicationDetail app={app} canEdit={canEditApplication(user, app)} />;
}
```

- Every Server Action: first check the session, then the permission.
- Every page with private data: check before showing anything.
- The **Flask API** checks again (Module 2 Week 5). The Next.js checks give a good experience; the API checks protect the data from every kind of client (mobile app, scripts).

### 5. 401, 403 or 404?

| Case | Answer |
|---|---|
| Not logged in | **401** / redirect to login |
| Logged in but not allowed, and it's no secret the page exists (admin page) | **403** "You don't have permission" |
| The item belongs to someone else (application #15) | **404** — don't reveal it exists |

Like a hotel receptionist: if you ask about another guest's room, they say "no such booking", not "that's someone else's room".

:::note[forbidden() and unauthorized()]
Next.js has `forbidden()` and `unauthorized()` helpers with `forbidden.tsx` / `unauthorized.tsx` files, but in Next.js 16 they are still **experimental** (`experimental.authInterrupts`). Returning a result, or calling `notFound()` / `redirect()`, works today.
:::

## ⚠️ Common mistakes

- `{count && <Badge />}` shows `0` when `count` is 0 → use `count > 0 &&`.
- Checking permission in the page but not in the Server Action it calls.
- Trusting a role or permission sent from the browser (`formData.get("role")`).
- Keeping permissions in the session forever — a removed admin keeps access until the cookie expires.
- `ROLE_PERMISSIONS[user.role]` with an untrusted role like `"toString"` → returns a function, not `undefined`. Use `Object.hasOwn`.
- Building a big policy engine for just two roles.

## 🏆 Best practices

- [ ] Feature code asks about **permissions**, not role names.
- [ ] **Deny by default**: unknown roles and missing users get nothing.
- [ ] Check permissions in every Server Action, Route Handler and private page — and in the API.
- [ ] Hide what users can never use; disable with an explanation when they could.
- [ ] 404 for other users' items; 403 when it's no secret the page exists.
- [ ] Test the policy as a table (role × permission) — it's pure and fast.
- [ ] Read the role from the verified session; re-check important roles from the API when they can change.
- [ ] Log denied attempts at admin actions.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Using the access-card idea, explain to a product manager why "we hid the button" is not enough to stop a member from deleting companies.

## 📐 Design it

CareerPilot adds a **"recruiter"** role. Recruiters can post jobs for **their own company**, see (but not change) applications to those jobs, and add notes only other recruiters of the same company can see. Update the permissions, write the ownership functions you need, and list every server entry point that must check them.

:::quiz
Show a possible design

```ts
type Role = "member" | "mentor" | "recruiter" | "admin";
type Permission =
  | ... existing
  | "jobs:write:company"
  | "applications:read:company"
  | "notes:company";

ROLE_PERMISSIONS.recruiter = ["jobs:write:company", "applications:read:company", "notes:company"];

type Actor = { id: number; role: Role; companyId?: number; menteeIds?: number[] };

const canManageJob = (u: Actor, job: { companyId: number }) =>
  u.role === "admin" || (can(u, "jobs:write:company") && u.companyId === job.companyId);

const canViewCandidateApplication = (u: Actor, app: { job: { companyId: number } }) =>
  u.role === "admin" || (can(u, "applications:read:company") && u.companyId === app.job.companyId);

const canSeeNote = (u: Actor, note: { visibility: "private" | "company"; authorId: number; companyId?: number }) =>
  note.authorId === u.id || (note.visibility === "company" && can(u, "notes:company") && u.companyId === note.companyId);
```

**Entry points that must check:**
- `createJobAction`, `updateJobAction`, `closeJobAction`
- `app/(recruiter)/jobs/[id]/applicants/page.tsx` (404 for other companies)
- `addCompanyNoteAction`
- the Route Handler `GET /api/jobs/[id]/applicants` (if the board uses TanStack Query)
- the Flask endpoints for all of the above (the real source of truth)

`companyId` must come from the database, never from the form. Members must never see recruiter notes on their own application — write a test for exactly that.
:::

### 📝 Self-review checklist

- [ ] The new role is added in one table
- [ ] Every change is checked again on the server
- [ ] Access to another company's data returns 404

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w5/03-rbac" ai="no-ai" title="Permissions policy, <Can> and a protected action"}
Build the role → permission table, ownership rules for mentors and admins, a filtered menu, a `<Can>` component, and a Server Action that refuses members and mentors before calling the API.
:::

:::hints
- `Object.hasOwn(ROLE_PERMISSIONS, role)` avoids surprises from built-in object keys.
- Check the admin shortcut first, then ownership, then relationships.
- In the action, call `verifySession()` before anything else.
:::

## ✅ Quick check

:::quiz
A mentor opens `/applications/15`, which belongs to someone who isn't their mentee. What should the page do, and why that status?

Call `notFound()` (404). Answering "403 Forbidden" would confirm that application #15 exists and belongs to someone else.
:::

:::quiz
Why keep `lib/permissions.ts` free of Next.js and database imports?

So the same pure rules run in Server Components, Server Actions, Client Components (to show or hide UI) and unit tests, without fakes.
:::

## 📚 Keep learning

- Next.js docs (bundled): Authentication guide → Authorization; Data Security guide
- [OWASP Top 10: Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
