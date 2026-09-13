"use client";
// See README.md.
import type { ReactNode } from "react";

export function createStrictContext<T>(name: string) {
  const Provider = (props: { value: T; children: ReactNode }) => null;
  const useValue = (): T => {
    throw new Error("TODO");
  };
  return [Provider, useValue] as const;
}

export type Filters = { status: "all" | "applied" | "interview" | "offer" | "rejected"; query: string };
export type FiltersAction = { type: "setStatus"; status: Filters["status"] } | { type: "setQuery"; query: string } | { type: "reset" };

export function filtersReducer(state: Filters, action: FiltersAction): Filters {
  return state;
}

export function FiltersProvider(props: { initial?: Filters; children: ReactNode }) {
  return null;
}

export function useFilters(): Filters {
  throw new Error("TODO");
}

export function useFiltersDispatch(): (action: FiltersAction) => void {
  throw new Error("TODO");
}

export function ToastProvider(props: { children: ReactNode }) {
  return null;
}

export function useToast(): { show(message: string): void; dismiss(id: number): void } {
  throw new Error("TODO");
}
