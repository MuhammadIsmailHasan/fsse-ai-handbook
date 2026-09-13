import type { ReactNode } from "react";
import { can, type Permission, type Role } from "../lib/permissions";

// UI convenience only — the server still checks.
export function Can({ user, permission, children, fallback = null }: { user: { role: Role } | null; permission: Permission; children: ReactNode; fallback?: ReactNode }) {
  return <>{can(user, permission) ? children : fallback}</>;
}
