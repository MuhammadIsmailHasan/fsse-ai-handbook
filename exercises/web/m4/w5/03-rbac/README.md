# M4 · W5 · 03 — Role-Based Access Control (RBAC)

> 🚫🤖 **No-AI** · ⏱️ ~75 min

CareerPilot has three roles: **member** (job seeker), **mentor** (reviews mentees' applications) and **admin**. Hide UI the user can't use — but **enforce on the server**, because anyone can call a Server Action or API directly.

Provided: `lib/dal.ts` (`verifySession()` → `{ userId, role }`), `lib/companies-api.ts`.

## 1. `lib/permissions.ts` (pure, no Next.js imports)
```ts
export type Role = "member" | "mentor" | "admin";
export type Permission = "applications:read:own" | "applications:write:own" | "applications:read:mentees" | "notes:comment" | "companies:manage" | "users:manage";
```
- `ROLE_PERMISSIONS: Record<Role, readonly Permission[]>`
  - member → read:own, write:own
  - mentor → everything a member has + read:mentees + notes:comment
  - admin → **every** permission
- `can(user: { role: Role } | null, permission)` → boolean (null user → false; unknown role → false)
- `canViewApplication(user: { id, role, menteeIds?: number[] }, application: { ownerId })` → owner with `read:own`; mentor with `read:mentees` and `ownerId` in `menteeIds`; or admin
- `canEditApplication(user, application)` → owner with `write:own`, or admin
- `navFor(user)` → filter `NAV_ITEMS` (provided in the starter) by `requires` (items without `requires` are always visible)

## 2. `components/can.tsx`
`<Can user={user} permission="companies:manage" fallback={...}>children</Can>` → children when allowed, else `fallback` (default `null`).

## 3. `app/admin/companies/actions.ts` (`"use server"`)
`deleteCompanyAction(companyId: number): Promise<{ ok: true } | { ok: false; message: string }>`
- `verifySession()` **first**; without `companies:manage` → `{ ok: false, message: "You don't have permission to do that" }` and **don't** call the API
- otherwise `deleteCompany(companyId)` then `{ ok: true }`

```bash
cd exercises/web
npx vitest run m4/w5/03-rbac
```
