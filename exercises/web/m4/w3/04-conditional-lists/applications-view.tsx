// Conditional rendering and lists. See README.md.
import { useState } from "react";

export type Status = "saved" | "applied" | "interview" | "offer" | "rejected";
export const STATUS_ORDER: readonly Status[] = ["saved", "applied", "interview", "offer", "rejected"];
export const STATUS_LABELS: Record<Status, string> = { saved: "Saved", applied: "Applied", interview: "Interview", offer: "Offer", rejected: "Rejected" };

export type Application = { id: number; role: string; company: string; status: Status; unread: number };

export type RequestState<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "success"; data: T };

export function ApplicationsView(props: { state: RequestState<Application[]>; onRetry: () => void }) {
  return null;
}
