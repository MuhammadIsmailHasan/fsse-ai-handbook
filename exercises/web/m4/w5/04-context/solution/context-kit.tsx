"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useReducer, useRef, useState, type Dispatch, type ReactNode } from "react";

export function createStrictContext<T>(name: string) {
  // undefined means "no provider" — so falsy values like 0 still count as provided.
  const Context = createContext<T | undefined>(undefined);
  Context.displayName = name;

  function Provider({ value, children }: { value: T; children: ReactNode }) {
    return <Context.Provider value={value}>{children}</Context.Provider>;
  }

  function useValue(): T {
    const value = useContext(Context);
    if (value === undefined) throw new Error(`use${name} must be used inside <${name}Provider>`);
    return value;
  }

  return [Provider, useValue] as const;
}

// ---------- Filters ----------
export type Filters = { status: "all" | "applied" | "interview" | "offer" | "rejected"; query: string };
export type FiltersAction = { type: "setStatus"; status: Filters["status"] } | { type: "setQuery"; query: string } | { type: "reset" };

const DEFAULT_FILTERS: Filters = { status: "all", query: "" };

export function filtersReducer(state: Filters, action: FiltersAction): Filters {
  switch (action.type) {
    case "setStatus":
      return { ...state, status: action.status };
    case "setQuery":
      return { ...state, query: action.query };
    case "reset":
      return DEFAULT_FILTERS;
  }
}

const [FiltersStateProvider, useFiltersState] = createStrictContext<Filters>("Filters");
const [FiltersDispatchProvider, useFiltersDispatchValue] = createStrictContext<Dispatch<FiltersAction>>("FiltersDispatch");

export function FiltersProvider({ initial = DEFAULT_FILTERS, children }: { initial?: Filters; children: ReactNode }) {
  const [state, dispatch] = useReducer(filtersReducer, initial);
  // Two contexts: components that only dispatch don't re-render when state changes.
  return (
    <FiltersDispatchProvider value={dispatch}>
      <FiltersStateProvider value={state}>{children}</FiltersStateProvider>
    </FiltersDispatchProvider>
  );
}

export const useFilters = useFiltersState;
export const useFiltersDispatch = useFiltersDispatchValue;

// ---------- Toasts ----------
type Toast = { id: number; message: string };
type ToastApi = { show(message: string): void; dismiss(id: number): void };

const [ToastApiProvider, useToastApi] = createStrictContext<ToastApi>("Toast");

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const nextId = useRef(1);
  const timers = useRef(new Map<number, ReturnType<typeof setTimeout>>());

  const dismiss = useCallback((id: number) => {
    clearTimeout(timers.current.get(id));
    timers.current.delete(id);
    setToasts((current) => current.filter((toast) => toast.id !== id));
  }, []);

  const show = useCallback(
    (message: string) => {
      const id = nextId.current++;
      setToasts((current) => [...current, { id, message }]);
      timers.current.set(id, setTimeout(() => dismiss(id), 4000));
    },
    [dismiss],
  );

  useEffect(() => {
    const activeTimers = timers.current;
    return () => activeTimers.forEach((timer) => clearTimeout(timer));
  }, []);

  const api = useMemo(() => ({ show, dismiss }), [show, dismiss]);

  return (
    <ToastApiProvider value={api}>
      {children}
      <div role="status" aria-live="polite">
        {toasts.map((toast) => (
          <p key={toast.id}>
            {toast.message}
            <button type="button" aria-label="Dismiss notification" onClick={() => dismiss(toast.id)}>
              ×
            </button>
          </p>
        ))}
      </div>
    </ToastApiProvider>
  );
}

export const useToast = useToastApi;
