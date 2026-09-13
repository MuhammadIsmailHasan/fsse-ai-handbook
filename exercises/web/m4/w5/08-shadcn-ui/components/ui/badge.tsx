// Badge with cva variants. See README.md.
import type { ComponentProps } from "react";

export const badgeVariants = (options?: { tone?: "neutral" | "info" | "warning" | "success" | "danger" | null }) => "";

export function Badge(props: ComponentProps<"span"> & { tone?: "neutral" | "info" | "warning" | "success" | "danger" }) {
  return null;
}

export function StatusBadge(props: { status: "applied" | "interview" | "offer" | "rejected" }) {
  return null;
}
