"use client";
// Container component. See README.md.
import type { Item } from "./applications-view";

export function ApplicationsContainer(props: { loadApplications: (status: string, signal: AbortSignal) => Promise<Item[]> }) {
  return null;
}
