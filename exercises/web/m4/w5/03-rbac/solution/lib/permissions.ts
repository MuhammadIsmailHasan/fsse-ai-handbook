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

const MEMBER: readonly Permission[] = ["applications:read:own", "applications:write:own"];
const ALL_PERMISSIONS: readonly Permission[] = [...MEMBER, "applications:read:mentees", "notes:comment", "companies:manage", "users:manage"];

// One table = one place to review who can do what.
export const ROLE_PERMISSIONS: Record<Role, readonly Permission[]> = {
  member: MEMBER,
  mentor: [...MEMBER, "applications:read:mentees", "notes:comment"],
  admin: ALL_PERMISSIONS,
};

type Actor = { id: number; role: Role; menteeIds?: number[] };

export function can(user: { role: Role } | null, permission: Permission): boolean {
  if (!user) return false;
  // Object.hasOwn guards against roles like "toString" coming from untrusted data.
  if (!Object.hasOwn(ROLE_PERMISSIONS, user.role)) return false;
  return ROLE_PERMISSIONS[user.role].includes(permission);
}

export function canViewApplication(user: Actor, application: { ownerId: number }): boolean {
  if (user.role === "admin") return true;
  if (application.ownerId === user.id) return can(user, "applications:read:own");
  return can(user, "applications:read:mentees") && (user.menteeIds ?? []).includes(application.ownerId);
}

export function canEditApplication(user: Actor, application: { ownerId: number }): boolean {
  if (user.role === "admin") return true;
  return application.ownerId === user.id && can(user, "applications:write:own");
}

export function navFor(user: { role: Role } | null): NavItem[] {
  return NAV_ITEMS.filter((item) => !item.requires || can(user, item.requires));
}
