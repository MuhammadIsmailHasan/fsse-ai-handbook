import { useCallback, useEffect, useRef, useState } from "react";

export function useControllableState<T>({ value, defaultValue, onChange }: { value?: T; defaultValue: T; onChange?: (value: T) => void }): [T, (next: T | ((prev: T) => T)) => void] {
  const [internal, setInternal] = useState(defaultValue);
  const isControlled = value !== undefined;
  const current = isControlled ? value : internal;

  // Refs keep setValue stable while always seeing the latest props.
  const latest = useRef({ current, isControlled, onChange });
  useEffect(() => {
    latest.current = { current, isControlled, onChange };
  });

  const setValue = useCallback((next: T | ((prev: T) => T)) => {
    const { current: prev, isControlled: controlled, onChange: notify } = latest.current;
    const resolved = typeof next === "function" ? (next as (prev: T) => T)(prev) : next;
    if (Object.is(resolved, prev)) return;
    if (!controlled) setInternal(resolved);
    latest.current = { ...latest.current, current: resolved };
    notify?.(resolved);
  }, []);

  return [current, setValue];
}
