"use client";

import { useCallback, useEffect, useState, useSyncExternalStore } from "react";

export function useDebouncedValue<T>(value: T, delayMs: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(timer); // value changed again → restart the wait
  }, [value, delayMs]);
  return debounced;
}

function subscribeOnline(callback: () => void) {
  window.addEventListener("online", callback);
  window.addEventListener("offline", callback);
  return () => {
    window.removeEventListener("online", callback);
    window.removeEventListener("offline", callback);
  };
}

export function useOnlineStatus(): boolean {
  return useSyncExternalStore(
    subscribeOnline,
    () => navigator.onLine,
    () => true, // server snapshot: assume online, no hydration mismatch
  );
}

export type FetchState<T> = { status: "idle" | "loading" | "success" | "error"; data: T | null; error: string | null };

const IDLE = { status: "idle", data: null, error: null } as const;

export function useFetchJson<T>(url: string | null): FetchState<T> {
  const [state, setState] = useState<FetchState<T> & { url: string | null }>({ ...IDLE, url: null });

  useEffect(() => {
    if (!url) return;
    const controller = new AbortController();
    setState({ status: "loading", data: null, error: null, url });

    fetch(url, { signal: controller.signal })
      .then(async (response) => {
        if (!response.ok) throw new Error(`Request failed with status ${response.status}`);
        const data = (await response.json()) as T;
        if (!controller.signal.aborted) setState({ status: "success", data, error: null, url });
      })
      .catch((error: unknown) => {
        if (controller.signal.aborted) return; // superseded or unmounted
        setState({ status: "error", data: null, error: error instanceof Error ? error.message : "Request failed", url });
      });

    return () => controller.abort();
  }, [url]);

  if (!url) return IDLE;
  // Before the effect runs for a new url, don't show the previous url's data.
  if (state.url !== url) return { status: "loading", data: null, error: null };
  return { status: state.status, data: state.data, error: state.error };
}

function readStorage<T>(key: string, fallback: T): T {
  try {
    const raw = window.localStorage.getItem(key);
    return raw === null ? fallback : (JSON.parse(raw) as T);
  } catch {
    return fallback; // invalid JSON or storage blocked
  }
}

export function useLocalStorage<T>(key: string, initial: T): [T, (value: T) => void] {
  const [value, setStateValue] = useState(initial);

  useEffect(() => {
    // After mount only: the server has no localStorage, so the first render must match it.
    setStateValue(readStorage(key, initial));
    const onStorage = (event: StorageEvent) => {
      if (event.key === key) setStateValue(readStorage(key, initial));
    };
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
    // eslint-disable-next-line react-hooks/exhaustive-deps -- initial is only a fallback
  }, [key]);

  const setValue = useCallback(
    (next: T) => {
      setStateValue(next);
      try {
        window.localStorage.setItem(key, JSON.stringify(next));
      } catch {
        // quota exceeded / private mode: keep the in-memory value
      }
    },
    [key],
  );

  return [value, setValue];
}
