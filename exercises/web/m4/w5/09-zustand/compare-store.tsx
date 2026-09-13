"use client";
// Zustand store + provider. See README.md.
import type { ReactNode } from "react";

export type CompareState = {
  jobIds: number[];
  isTrayOpen: boolean;
  toggleJob: (id: number) => "added" | "removed" | "full";
  clear: () => void;
  setTrayOpen: (open: boolean) => void;
};

export function createCompareStore(initial?: Partial<Pick<CompareState, "jobIds" | "isTrayOpen">>): {
  getState: () => CompareState;
  subscribe: (listener: (state: CompareState) => void) => () => void;
} {
  throw new Error("TODO");
}

export function CompareStoreProvider(props: { initial?: Partial<Pick<CompareState, "jobIds" | "isTrayOpen">>; children: ReactNode }) {
  return null;
}

export function useCompareStore<T>(selector: (state: CompareState) => T): T {
  throw new Error("TODO");
}

export const selectCount = (state: CompareState): number => 0;
export const selectIsSelected = (id: number) => (state: CompareState): boolean => false;

export function CompareButton(props: { jobId: number }) {
  return null;
}

export function CompareTray() {
  return null;
}
