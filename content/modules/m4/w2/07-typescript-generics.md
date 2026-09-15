---
title: "🔥 TypeScript Generics"
summary: Write functions and types that work with any data while keeping the exact type — type parameters, constraints, keyof, generic API responses and stores, and when generics make code worse.
type: lesson
source: original
roles: { be: optional, fe: recommended, fs: recommended, ai: optional, ops: none }
durationMinutes: 120
tags: [typescript, generics, type-parameters, keyof]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What a type parameter (`T`) is, and how TypeScript fills it in
- Limiting `T` with `extends`, and safe field access with `keyof`
- Generic types like `Result<T>` and `Paginated<T>`
- A generic store (the idea behind React state)
- When generics are too much

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Generic** | A function or type that works with many types but keeps the exact one | Generik |
| **Type parameter (`T`)** | A placeholder for a type, filled in when the function is used | Parameter tipe |
| **Inference** | TypeScript figures out what `T` is from your arguments | Tebakan tipe |
| **Constraint (`extends`)** | A rule for what `T` is allowed to be: `T extends { length: number }` | Batasan |
| **`keyof T`** | The field names of `T` | Nama-nama field |
| **Wrapper type** | A type that wraps other data: `ApiResponse<Job>` | Tipe pembungkus |

## 🧠 The big idea

A generic is like a **labeled container at a warung**: the jar says "contains: T". Put kerupuk in, and you know kerupuk comes out — without making a separate "kerupuk jar", "peanut jar" and "candy jar". Without generics you either copy the same code for each type, or use `any` and lose the label completely.

## ❓ Why it matters

Helpers like `groupBy` or `paginate`, API response wrappers, stores and React hooks all work with **any** data. Generics keep the link between what goes in and what comes out: `paginate(jobs)` returns `Paginated<Job>`, so autocomplete works on `result.data[0].title`.

Without generics:

```ts
function first(items: any[]): any { return items[0]; }
const job = first(jobs);
job.titel.toUpperCase();          // compiles 😬 crashes at runtime

function firstJob(items: Job[]): Job | undefined { ... }
function firstCompany(items: Company[]): Company | undefined { ... }   // duplication forever
```

## 📖 Step by step

### 1. Type parameters

```ts
function firstOrNull<T>(items: readonly T[]): T | null {
  return items.length > 0 ? items[0]! : null;
}

const job = firstOrNull(jobs);       // T inferred as Job → Job | null
const n = firstOrNull([1, 2, 3]);    // number | null
```

- `<T>` declares the placeholder.
- When you call `firstOrNull(jobs)`, TypeScript sees an array of `Job` and fills in `T = Job`.
- You almost never write `firstOrNull<Job>(…)` yourself.

### 2. Constraints: rules for `T`

```ts
function longest<T extends { length: number }>(a: T, b: T): T {
  return a.length >= b.length ? a : b;
}

function pick<T extends object, K extends keyof T>(obj: T, keys: readonly K[]): Pick<T, K> { ... }
pick(job, ["title", "salaryMax"]);   // Pick<Job, "title" | "salaryMax">
pick(job, ["company"]);              // ❌ "company" is not a key of Job
```

- `T extends { length: number }` = "T can be anything **that has a length**" (a string, an array). Like a parking spot that fits any vehicle — as long as it's shorter than 5 meters.
- `K extends keyof T` = "K must be one of T's field names". You can't ask for a field that doesn't exist.

### 3. Callbacks keep the types flowing

```ts
function groupBy<T, K extends PropertyKey>(items: readonly T[], keyOf: (item: T) => K): Partial<Record<K, T[]>> { ... }

groupBy(applications, (app) => app.status);   // Partial<Record<Status, Application[]>>
```

TypeScript knows `app` is an `Application` (from the array) and that the key is a `Status` (from what your callback returns). No types written by hand.

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

- `Result<T, E = Error>` — a success with a value, or a failure with an error. `E = Error` is a **default**.
- `Paginated<T>` — one "page" shape for any list: jobs, companies, notes.

:::warning[Generics don't validate]
`getJson<ApiList<Application>>()` is just a label on the jar — nobody checked what's inside. The response is not checked. In Week 5, combine this with a runtime schema (`schema.parse(json)`) so the type is really true.
:::

### 5. A generic store (preview of React state)

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

A store holds one value and tells listeners when it changes — like a WhatsApp group that notifies all members when someone posts. `useState<T>` in React and Zustand's `create<T>()` use exactly this pattern.

### 6. Going further (just a taste)

```ts
type Nullable<T> = { [K in keyof T]: T[K] | null };        // mapped type
type ElementType<T> = T extends readonly (infer U)[] ? U : never;   // conditional type with infer
```

Libraries use these advanced types a lot. In app code you rarely need more than `Partial`, `Pick`, `Omit` and friends.

## ⚠️ Common mistakes

- `function f<T>(x: any): T` — returning a `T` nobody checked is lying.
- A type parameter used only once (`function f<T>(x: T): void`) — just use `unknown`.
- Limiting too much (`T extends Job` when any object works) or too little (then you can't access fields).
- Complicated type puzzles in app code that nobody on the team can read.
- Using generics to "pretend" external data was validated.

## 🏆 Best practices

- [ ] Let TypeScript fill in type parameters; write them only when it can't.
- [ ] Use clear names when there are several (`TData`, `TError`, `K`).
- [ ] Limit `T` with `extends` to exactly what the function needs.
- [ ] Use `keyof` for helpers that work with field names.
- [ ] Give useful defaults (`Result<T, E = Error>`).
- [ ] Use generics when the output type depends on the input type — otherwise keep it simple.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain generics with the labeled jar analogy, then show how `paginate(jobs, 1, 20)` "knows" that `result.data` contains jobs.

## 📐 Design it

Design a generic data loader in plain TypeScript (no React yet) for CareerPilot. It loads data with a `fetcher`, has an `idle / loading / success / error` state as a discriminated union, supports `reload()`, and lets the caller change the data with a `select` function. Write the types.

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

- Two type parameters: `TRaw` (what the network returns) and `TData` (what the page wants).
- `TData` is filled in automatically from what `select` returns.
- `previous` keeps the old data on screen while reloading or after an error, so the page doesn't flash empty.
- This is a small version of TanStack Query's `useQuery` (Week 4).
:::

### 📝 Self-review checklist

- [ ] The output type comes from `select` automatically
- [ ] The state is a discriminated union
- [ ] Cancelling and subscribing are typed

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w2/07-generics" ai="no-ai" title="Generic utilities: groupBy, pick, Result, paginate and a store"}
Replace helpers typed with `unknown` by generics, so types flow from inputs to outputs: `groupBy`, `pick` with `keyof`, a `Result` type with `tryCatch`, `paginate`, a store you can subscribe to, and `firstOrNull`. Type tests check the exact types TypeScript figures out.
:::

:::hints
- `(groups[key] ??= []).push(item)` builds the groups in one line.
- In `pick`, start with `const result = {} as Pick<T, K>` and copy each key.
- `typeof next === "function"` tells an updater function apart from a plain value (cast it once).
:::

## ✅ Quick check

:::quiz
What does `K extends keyof T` guarantee?

That `K` is one of `T`'s field names, so `obj[key]` is valid and has the type `T[K]`.
:::

:::quiz
When is a type parameter unnecessary?

When it appears only once and doesn't connect an input to an output. Use `unknown` or a concrete type instead.
:::

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
