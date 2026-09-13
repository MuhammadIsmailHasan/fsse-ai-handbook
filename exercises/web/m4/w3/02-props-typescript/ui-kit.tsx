// Typed props. See README.md.
import type { ComponentPropsWithoutRef, ReactNode } from "react";

export type Status = "saved" | "applied" | "interview" | "offer" | "rejected";
export const STATUS_LABELS: Record<Status, string> = { saved: "Saved", applied: "Applied", interview: "Interview", offer: "Offer", rejected: "Rejected" };

export function Button(props: any) {
  return null;
}

export function Avatar(props: any) {
  return null;
}

export function StatusBadge(props: any) {
  return null;
}

export function Card(props: any) {
  return null;
}
