export function groupBy<T, K extends PropertyKey>(items: readonly T[], keyOf: (item: T) => K): Partial<Record<K, T[]>> {
  const groups: Partial<Record<K, T[]>> = {};
  for (const item of items) {
    const key = keyOf(item);
    (groups[key] ??= []).push(item);
  }
  return groups;
}

export function pick<T extends object, K extends keyof T>(obj: T, keys: readonly K[]): Pick<T, K> {
  const result = {} as Pick<T, K>;
  for (const key of keys) result[key] = obj[key];
  return result;
}

export type Result<T, E = Error> = { ok: true; value: T } | { ok: false; error: E };

export async function tryCatch<T>(fn: () => Promise<T>): Promise<Result<T>> {
  try {
    return { ok: true, value: await fn() };
  } catch (thrown) {
    return { ok: false, error: thrown instanceof Error ? thrown : new Error(String(thrown)) };
  }
}

export type Paginated<T> = {
  data: T[];
  meta: { page: number; perPage: number; total: number; totalPages: number };
};

export function paginate<T>(items: readonly T[], page: number, perPage: number): Paginated<T> {
  const start = (page - 1) * perPage;
  return {
    data: page < 1 ? [] : items.slice(start, start + perPage),
    meta: { page, perPage, total: items.length, totalPages: Math.max(1, Math.ceil(items.length / perPage)) },
  };
}

export interface Store<T> {
  get(): T;
  set(next: T | ((previous: T) => T)): void;
  subscribe(listener: (value: T) => void): () => void;
}

export function createStore<T>(initial: T): Store<T> {
  let value = initial;
  const listeners = new Set<(value: T) => void>();
  return {
    get: () => value,
    set(next) {
      const resolved = typeof next === "function" ? (next as (previous: T) => T)(value) : next;
      if (Object.is(resolved, value)) return;
      value = resolved;
      listeners.forEach((listener) => listener(value));
    },
    subscribe(listener) {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
  };
}

export function firstOrNull<T>(items: readonly T[]): T | null {
  return items.length > 0 ? (items[0] as T) : null;
}
