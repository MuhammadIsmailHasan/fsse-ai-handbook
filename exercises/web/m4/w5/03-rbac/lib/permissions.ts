// RBAC policy. See README.md.
export type Role = "member" | "mentor" | "admin";
export type Permission =
  | "applications:read:own"
  | "applications:write:own"
  | "applications:read:mentees"
  | "notes:comment"
  | "companies:manage"
  | "users:manage";

export type NavItem = { href: string; label: string; requires?: Permission };

export const NAV_ITEMS: readonly NavItem[] = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/applications", label: "My applications", requires: "applications:read:own" },
  { href: "/mentees", label: "Mentees", requires: "applications:read:mentees" },
  { href: "/admin/companies", label: "Companies", requires: "companies:manage" },
  { href: "/admin/users", label: "Users", requires: "users:manage" },
];

export const ROLE_PERMISSIONS: Record<Role, readonly Permission[]> = { member: [], mentor: [], admin: [] };

type Actor = { id: number; role: Role; menteeIds?: number[] };

export function can(user: { role: Role } | null, permission: Permission): boolean {
  return false;
}

export function canViewApplication(user: Actor, application: { ownerId: number }): boolean {
  return false;
}

export function canEditApplication(user: Actor, application: { ownerId: number }): boolean {
  return false;
}

export function navFor(user: { role: Role } | null): NavItem[] {
  return [];
}
