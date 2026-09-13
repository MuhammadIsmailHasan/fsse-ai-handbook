// <Can> helper. See README.md.
import type { ReactNode } from "react";
import type { Permission, Role } from "../lib/permissions";

export function Can(props: { user: { role: Role } | null; permission: Permission; children: ReactNode; fallback?: ReactNode }) {
  return null;
}
