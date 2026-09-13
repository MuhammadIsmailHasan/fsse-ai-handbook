// Generic helpers. See README.md. Replace the `unknown`s with generics.

export function groupBy(items: unknown[], keyOf: (item: unknown) => string): Record<string, unknown[]> {
  throw new Error("TODO");
}

export function pick(obj: object, keys: string[]): object {
  throw new Error("TODO");
}

export type Result = unknown;

export async function tryCatch(fn: () => Promise<unknown>): Promise<unknown> {
  throw new Error("TODO");
}

export type Paginated = unknown;

export function paginate(items: unknown[], page: number, perPage: number): unknown {
  throw new Error("TODO");
}

export function createStore(initial: unknown): unknown {
  throw new Error("TODO");
}

export function firstOrNull(items: unknown[]): unknown {
  throw new Error("TODO");
}
