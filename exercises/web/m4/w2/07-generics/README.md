# M4 · W2 · 07 — Generics: Reusable, Type-Safe Helpers

> 🚫🤖 **No-AI** · ⏱️ ~75 min · edit **`generic-utils.ts`**

| Export | Signature and behavior |
|---|---|
| `groupBy` | `<T, K extends PropertyKey>(items: readonly T[], keyOf: (item: T) => K) => Partial<Record<K, T[]>>` |
| `pick` | `<T extends object, K extends keyof T>(obj: T, keys: readonly K[]) => Pick<T, K>` — a new object with only those keys |
| `type Result<T, E = Error>` | `{ ok: true; value: T } \| { ok: false; error: E }` |
| `tryCatch` | `<T>(fn: () => Promise<T>) => Promise<Result<T>>` — never throws; non-`Error` throws are wrapped in `new Error(String(thrown))` |
| `type Paginated<T>` | `{ data: T[]; meta: { page: number; perPage: number; total: number; totalPages: number } }` |
| `paginate` | `<T>(items: readonly T[], page: number, perPage: number) => Paginated<T>` — 1-based pages; out-of-range pages return empty `data`; `totalPages` is at least 1 |
| `createStore` | `<T>(initial: T) => { get(): T; set(next: T \| ((previous: T) => T)): void; subscribe(listener: (value: T) => void): () => void }` — `set` notifies listeners only if the value changed (`Object.is`); `subscribe` returns an unsubscribe function |
| `firstOrNull` | `<T>(items: readonly T[]) => T \| null` |

`generic-utils.types.ts` checks that types flow through (e.g. `pick(job, ["title"])` is exactly `{ title: string }`).

```bash
cd exercises/web
npx vitest run m4/w2/07-generics
```
