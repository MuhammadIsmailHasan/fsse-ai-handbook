---
title: "RBAC & Conditional Rendering"
summary: Show the right UI to each role and enforce it where it matters — permission policies instead of role checks, ownership rules, filtered navigation, a Can component, and server-side authorization.
type: lesson
source: core
sourceRef: "M3 · W5 · L3"
roles: { be: recommended, fe: core, fs: core, ai: optional, ops: none }
durationMinutes: 150
tags: [rbac, authorization, permissions, conditional-rendering, security, nextjs]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Roles vs **permissions**, and why code should ask "can this user do X?" instead of "is this user an admin?"
- A single **policy module** (`can`, `canEditApplication`) shared by UI and server code
- **Ownership** and relationship rules (my data, my mentees' data)
- Conditional rendering patterns: filtered navigation, a `<Can>` component, disabled vs hidden controls
- **Enforcing** authorization in Server Actions, pages (`notFound`, `redirect`) and the API
- 403 vs 404 for resources a user may not see

## 🧠 The big idea

In an office building, your **access card** (role) opens certain doors (permissions). The lobby screen might only show the floors you can visit — that's convenient (conditional rendering). But the **door locks** still check your card. If someone takes the stairs, the lock is what stops them.

UI hiding = lobby screen. Server authorization = door locks. You need both, but only one is security.

## ❓ Why does this exist?

Apps have different users: CareerPilot has **members** (job seekers), **mentors** who review mentees' applications, and **admins** who manage companies and users. Without a clear model, checks spread everywhere:

```tsx
{user.role === "admin" || user.role === "mentor" ? <MenteesLink /> : null}
```

…and when you add a "career coach" role, you hunt through 40 files.

## 💥 What happens if we DON'T?

- A member hides the "Delete company" button in the UI — but the Server Action has no check, so calling it from DevTools deletes the company.
- `GET /applications/15` shows another user's application because the page only checked "logged in".
- Different screens disagree ("mentors can comment" in one place, not in another).

## 📖 How it works, step by step

### 1. Roles map to permissions

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

Code asks about **permissions**. Adding a role means editing one table.

### 2. Ownership and relationships

Permissions alone can't answer "can Sari edit **this** application?".

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

This is **RBAC + ownership** — what most apps actually need. When rules depend on many attributes (department, time, plan tier), teams move to **ABAC** or policy engines.

### 3. Conditional rendering in the UI

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

| Situation | Hide or disable? |
|---|---|
| User will **never** have access (member → admin panel) | **hide** |
| User could get access (upgrade plan, needs verification) | **disable + explain** |
| Temporarily unavailable (form invalid, already applied) | **disable + reason** |

Rendering patterns you'll use: `&&` for show/hide (watch out for `0 && …` rendering `0`), ternary for either/or, early `return` for whole-page states, lookup objects for many variants.

### 4. Enforce on the server — every entry point

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

And the **Flask API** checks again (Module 2 W5 RBAC lesson). The Next.js checks give good UX and protect the BFF; the API check protects data from every client (mobile app, scripts).

### 5. 401, 403 or 404?

| Case | Response |
|---|---|
| Not logged in | **401** / redirect to login |
| Logged in, action not allowed, resource existence isn't secret (admin page) | **403** "You don't have permission" |
| Resource belongs to someone else (application #15) | **404** — don't leak that it exists |

:::note[forbidden() and unauthorized()]
Next.js has `forbidden()` and `unauthorized()` helpers with `forbidden.tsx`/`unauthorized.tsx` files, but in Next.js 16 they're still **experimental** (`experimental.authInterrupts`). Returning a result or calling `notFound()`/`redirect()` works today.
:::

## ⚖️ Trade-offs

| Model | ✅ | ❌ |
|---|---|---|
| Role checks (`role === "admin"`) | quick for 2 roles | scattered, breaks when roles grow |
| RBAC permission table | one place, testable, readable | awkward for per-object rules alone |
| RBAC + ownership functions | covers most SaaS apps | functions grow with features |
| ABAC / policy engine (OPA, Cedar, Casbin, Oso) | complex rules, audits, central management | more infrastructure and learning |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ A permission table + ownership helpers for apps with a handful of roles.
- ✅ The same policy module for UI hints and server enforcement (when the frontend is TypeScript).
- 🚫 Don't trust role or permission data coming from the client (`formData.get("role")`).
- 🚫 Don't build a policy engine for two roles.

## 🏆 Best practices

- [ ] Ask about **permissions**, not role names, in feature code.
- [ ] **Deny by default**: unknown roles and missing users get nothing.
- [ ] Enforce in every Server Action, Route Handler, page with private data — and in the API.
- [ ] Hide what users can never use; disable with an explanation when they could.
- [ ] Return 404 for other users' resources; 403 when existence isn't secret.
- [ ] Unit-test the policy as a table (role × permission) — it's pure and fast.
- [ ] Read the role from the verified session, and re-check sensitive roles from the API/database when they can change.
- [ ] Log denied attempts for admin actions.

## 🏭 How it's used in industry

- GitHub, Google Workspace and most SaaS products use role → permission mappings with resource ownership ("repo admin", "org owner").
- Policy-as-code tools (Open Policy Agent, AWS Cedar/Verified Permissions, Oso) are common in larger companies to keep authorization consistent across services.
- OWASP lists **Broken Access Control** as the #1 web application risk — usually missing server-side checks.

## ⚠️ Common mistakes

- `{count && <Badge />}` renders `0` when `count` is 0 → use `count > 0 &&`.
- Checking permissions in the page but not in the Server Action it uses.
- Storing permissions in the session forever — a demoted admin keeps access until the cookie expires.
- `ROLE_PERMISSIONS[user.role]` with an untrusted role like `"toString"` → returns a function, not `undefined`.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a product manager why "we hid the button" is not enough to stop a member deleting companies, using the office access-card analogy.

## 📐 Design it

CareerPilot adds a **"recruiter"** role: recruiters can post jobs for **their own company**, view applications submitted to those jobs (read-only), and add notes visible only to other recruiters of the same company. Update the permission list, write the ownership functions you'd need, and list every server entry point that must check them.

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

**Entry points that must check:** `createJobAction`, `updateJobAction`, `closeJobAction`; `app/(recruiter)/jobs/[id]/applicants/page.tsx` (404 for other companies); `addCompanyNoteAction`; Route Handler `GET /api/jobs/[id]/applicants` (if the board uses TanStack Query); the Flask endpoints for all of the above (the real source of truth). Note: `companyId` must come from the database, not the form. Members must never see recruiter notes on their own application — test that explicitly.
:::

### 📝 Self-review checklist

- [ ] New role added in one table
- [ ] Every mutation re-checks on the server
- [ ] Cross-company access returns 404

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w5/03-rbac" ai="no-ai" title="Permissions policy, <Can> and a protected action"}
Build the role → permission table, ownership rules for mentors and admins, filtered navigation, a `<Can>` component, and a Server Action that refuses members and mentors before calling the API.
:::

:::hints
- `Object.hasOwn(ROLE_PERMISSIONS, role)` avoids surprises from inherited object keys.
- Handle the admin shortcut first, then ownership, then relationships.
- In the action, call `verifySession()` before anything else.
:::

## ✅ Quick check

:::quiz
A mentor opens `/applications/15`, which belongs to someone who isn't their mentee. What should the page do, and why that status?

Call `notFound()` (404). Revealing "403 Forbidden" confirms that application #15 exists and belongs to someone else.
:::

:::quiz
Why keep `lib/permissions.ts` free of Next.js and database imports?

So the same pure policy runs in Server Components, Server Actions, Client Components (UI hints) and unit tests without mocks.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Role-Based Access Control | Kontrol akses berbasis peran |
| Permission | Izin / hak akses |
| Ownership | Kepemilikan data |
| Conditional rendering | Menampilkan UI berdasarkan kondisi |
| Deny by default | Tolak secara default |
| Broken access control | Kontrol akses yang rusak (celah keamanan) |

## 📚 Keep learning

- Next.js docs (bundled): Authentication guide → Authorization; Data Security guide
- [OWASP Top 10: Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
