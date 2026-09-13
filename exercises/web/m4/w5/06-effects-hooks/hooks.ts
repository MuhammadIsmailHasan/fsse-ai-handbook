"use client";
// Custom hooks. See README.md.

export function useDebouncedValue<T>(value: T, delayMs: number): T {
  return value;
}

export function useOnlineStatus(): boolean {
  return true;
}

export type FetchState<T> = { status: "idle" | "loading" | "success" | "error"; data: T | null; error: string | null };

export function useFetchJson<T>(url: string | null): FetchState<T> {
  return { status: "idle", data: null, error: null };
}

export function useLocalStorage<T>(key: string, initial: T): [T, (value: T) => void] {
  return [initial, () => {}];
}
