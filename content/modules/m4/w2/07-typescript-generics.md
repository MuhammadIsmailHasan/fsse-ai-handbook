---
title: "🔥 TypeScript Generics"
summary: Write functions, types and components that work with any data while keeping exact types — type parameters, constraints, keyof, generic API responses and stores, and when generics make code worse.
type: lesson
source: original
roles: { be: optional, fe: recommended, fs: recommended, ai: optional, ops: none }
durationMinutes: 120
tags: [typescript, generics, type-parameters, keyof]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What a type parameter is, and how TypeScript infers it
- Constraints with `extends`, and `keyof` for type-safe property access
- Generic types: `Result<T, E>`, `Paginated<T>`, `ApiResponse<T>`
- Generic stores and callbacks
- Defaults for type parameters
- A first look at conditional and mapped types — and when not to go there

## 🧠 The big idea

A generic is a **labeled container**: a lunchbox that says "contains: T". When you put rice in, TypeScript knows you get rice out — without writing a separate `RiceBox`, `NoodleBox` and `SushiBox`. Without generics you'd either duplicate code or use `any` and lose the label entirely.

## ❓ Why does this exist?

Utilities (`groupBy`, `paginate`), data wrappers (API responses, pagination, results), stores and React hooks all work with **any** data type. Generics keep the connection between input and output types, so `paginate(jobs)` returns `Paginated<Job>` — and autocomplete works on `result.data[0].title`.

## 💥 What happens if we DON'T?

```ts
function first(items: any[]): any { return items[0]; }
const job = first(jobs);
job.titel.toUpperCase();          // compiles 😬 crashes at runtime

function firstJob(items: Job[]): Job | undefined { ... }
function firstCompany(items: Company[]): Company | undefined { ... }   // duplication forever
```

## 📖 How it works, step by step

### 1. Type parameters

```ts
function firstOrNull<T>(items: readonly T[]): T | null {
  return items.length > 0 ? items[0]! : null;
}

const job = firstOrNull(jobs);       // T inferred as Job → Job | null
const n = firstOrNull([1, 2, 3]);    // number | null
```

`T` is a placeholder filled in at each call. Usually it's **inferred** from arguments; you rarely write `firstOrNull<Job>(…)`.

### 2. Constraints

```ts
function longest<T extends { length: number }>(a: T, b: T): T {
  return a.length >= b.length ? a : b;
}

function pick<T extends object, K extends keyof T>(obj: T, keys: readonly K[]): Pick<T, K> { ... }
pick(job, ["title", "salaryMax"]);   // Pick<Job, "title" | "salaryMax">
pick(job, ["company"]);              // ❌ "company" is not a key of Job
```

`K extends keyof T` means "K must be one of T's property names" — safe dynamic property access.

### 3. Grouping and callbacks

```ts
function groupBy<T, K extends PropertyKey>(items: readonly T[], keyOf: (item: T) => K): Partial<Record<K, T[]>> { ... }

groupBy(applications, (app) => app.status);   // Partial<Record<Status, Application[]>>
```

The callback's parameter type flows from the array; the return type flows from the callback.

### 4. Generic types

```ts
type Result<T, E = Error> = { ok: true; value: T } | { ok: false; error: E };

type Paginated<T> = {
  data: T[];
  meta: { page: number; perPage: number; total: number; totalPages: number };
};

type ApiResponse<T> = { data: T };                       // matches your Flask envelope
type ApiList<T> = ApiResponse<T[]> & { meta: Paginated<T>["meta"] };

async function getJson<T>(url: string): Promise<T> { ... }
const page = await getJson<ApiList<Application>>("/api/v1/applications");
```

:::warning[Generics don't validate]
`getJson<ApiList<Application>>()` is an assertion in disguise — nothing checks the response. Pair generic fetchers with a runtime schema (`schema.parse(json)`) in Week 5 so the type is earned.
:::

### 5. Generic stores (and a preview of React hooks)

```ts
function createStore<T>(initial: T) {
  let value = initial;
  const listeners = new Set<(value: T) => void>();
  return {
    get: () => value,
    set(next: T | ((previous: T) => T)) { ... },
    subscribe(listener: (value: T) => void) { listeners.add(listener); return () => listeners.delete(listener); },
  };
}

const filters = createStore({ status: null as Status | null, q: "" });
filters.set((prev) => ({ ...prev, q: "python" }));
```

`useState<T>`, `useQuery<TData>` and Zustand's `create<T>()` are exactly this pattern.

### 6. Beyond: mapped and conditional types (just a taste)

```ts
type Nullable<T> = { [K in keyof T]: T[K] | null };        // mapped type
type ElementType<T> = T extends readonly (infer U)[] ? U : never;   // conditional type with infer
```

Libraries use these heavily; application code rarely needs more than the built-in utility types.

## ⚖️ Trade-offs

| Choice | ✅ | ❌ |
|---|---|---|
| Generic function | reusable, exact types | harder to read with many parameters |
| Overloads / specific functions | simple signatures | duplication |
| `any` | quick | loses all type information |
| Advanced type-level code | powerful library APIs | cryptic errors; slows compilation |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ Utilities over collections, response wrappers, stores, hooks, reusable components (`<Select<T>>`).
- ✅ When the output type depends on the input type.
- 🚫 A type parameter used only once (`function f<T>(x: T): void`) — just use `unknown`.
- 🚫 "Type gymnastics" in app code when a simple union or overload is clearer.

## 🏆 Best practices

- [ ] Let TypeScript infer type arguments; write them explicitly only when inference can't.
- [ ] Name parameters meaningfully when there are several (`TData`, `TError`, `K`).
- [ ] Constrain type parameters (`extends`) to what the function actually needs.
- [ ] Use `keyof` constraints for property-based utilities.
- [ ] Give defaults where useful (`Result<T, E = Error>`).
- [ ] Don't use generics to fake validation of external data.

## 🏭 How it's used in industry

- React (`useState<T>`), TanStack Query (`useQuery<TData, TError>`), Zod (`z.infer<typeof schema>`) and Prisma/Drizzle ORMs are generics-heavy.
- Teams wrap their API clients in generic request functions typed from OpenAPI schemas.
- Senior frontend interviews often include "write a typed `groupBy`/`debounce`/`pick`".

## ⚠️ Common mistakes

- `function f<T>(x: any): T` — returning an unchecked `T` is lying.
- Over-constraining (`T extends Job`) when any object would do, or under-constraining so property access fails.
- Deeply nested conditional types that nobody on the team can maintain.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain generics with the labeled lunchbox analogy, then show how `paginate(jobs, 1, 20)` "knows" `result.data` contains jobs.

## 📐 Design it

Design a generic **`useResource`-style** data loader (plain TypeScript, no React yet) for CareerPilot: it loads a resource with a `fetcher`, exposes `idle/loading/success/error` state as a discriminated union, supports `reload()`, and lets the caller transform data with a `select` function. Write the types.

:::quiz
Show a possible design

```ts
type ResourceState<TData, TError = Error> =
  | { status: "idle" }
  | { status: "loading"; previous?: TData }
  | { status: "success"; data: TData; loadedAt: number }
  | { status: "error"; error: TError; previous?: TData };

interface ResourceOptions<TRaw, TData = TRaw> {
  fetcher: (signal: AbortSignal) => Promise<TRaw>;
  select?: (raw: TRaw) => TData;          // e.g. envelope → data, sort, filter
  clock?: () => number;
}

interface Resource<TData> {
  getState(): ResourceState<TData>;
  load(): Promise<void>;                  // aborts an in-flight load first
  reload(): Promise<void>;
  subscribe(listener: (state: ResourceState<TData>) => void): () => void;
}

declare function createResource<TRaw, TData = TRaw>(options: ResourceOptions<TRaw, TData>): Resource<TData>;

// usage — TData inferred from select:
const applications = createResource({
  fetcher: (signal) => api.get<ApiList<Application>>("/api/v1/applications", { signal }),
  select: (res) => res.data.toSorted((a, b) => b.updatedAt.localeCompare(a.updatedAt)),
});
// Resource<Application[]>
```

- Two type parameters: what the network returns vs what the UI wants.
- `previous` data keeps the UI stable while reloading or after an error.
- This is a small version of TanStack Query's `useQuery` (Week 4).
:::

### 📝 Self-review checklist

- [ ] Output type inferred from `select`
- [ ] State is a discriminated union
- [ ] Cancellation and subscriptions typed

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w2/07-generics" ai="no-ai" title="Generic utilities: groupBy, pick, Result, paginate and a store"}
Replace `unknown`-typed helpers with generics so types flow from inputs to outputs: `groupBy`, `pick` with `keyof` constraints, a `Result` type with `tryCatch`, `paginate`, a subscribable store and `firstOrNull`. Type tests check the exact inferred types.
:::

:::hints
- `(groups[key] ??= []).push(item)` builds groups in one line.
- In `pick`, start with `const result = {} as Pick<T, K>` and assign each key.
- `typeof next === "function"` distinguishes an updater function from a value (cast it once).
:::

## ✅ Quick check

:::quiz
What does `K extends keyof T` guarantee?

That `K` is a union of property names of `T`, so `obj[key]` is valid and typed as `T[K]`.
:::

:::quiz
When is a generic parameter unnecessary?

When it appears only once in the signature and doesn't relate inputs to outputs — use `unknown` or a concrete type instead.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Generic | Generik — tipe dengan parameter |
| Type parameter | Parameter tipe (`T`) |
| Constraint | Batasan (`extends`) |
| Type argument | Argumen tipe (`<Job>`) |
| Mapped type | Tipe terpetakan |

## 📚 Keep learning

- [TypeScript Handbook: Generics](https://www.typescriptlang.org/docs/handbook/2/generics.html)
- [TypeScript Handbook: Keyof Type Operator](https://www.typescriptlang.org/docs/handbook/2/keyof-types.html)

## 📣 End of Week 2 — share your progress

:::linkedin{type="weekly"}
🔷 Week 2: TypeScript + Tailwind CSS.

- Modeled job applications with discriminated unions — an "offer without an amount" now fails to compile
- Learned that TypeScript types disappear at runtime (so API data still needs validation)
- Set up Tailwind CSS v4 with design tokens in CSS, and built responsive cards with utilities
- Wrote typed button variants with cn(), tailwind-merge and satisfies — the pattern behind shadcn/ui

What clicked for me: [your answer].

Next: React with Next.js. 🚀

#TypeScript #TailwindCSS #Frontend #LearningInPublic
:::
