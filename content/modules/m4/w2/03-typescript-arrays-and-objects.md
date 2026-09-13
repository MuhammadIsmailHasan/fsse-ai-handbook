---
title: "TypeScript Arrays & Objects"
summary: Type collections and lookup tables precisely — readonly arrays, tuples, `as const`, `keyof` and indexed access, `Record` and index signatures, `satisfies`, and immutable updates that TypeScript can verify.
type: lesson
source: core
sourceRef: "M3 · W2 · L3"
split: true
roles: { be: optional, fe: core, fs: core, ai: recommended, ops: none }
durationMinutes: 120
tags: [typescript, arrays, objects, as-const, satisfies, keyof]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- `T[]`, `readonly T[]` and tuples
- `as const` and deriving union types from values
- `keyof`, `typeof`, indexed access types
- `Record<K, V>` vs index signatures, and `noUncheckedIndexedAccess`
- `satisfies`: check a value against a type without losing literal types
- Typing immutable updates (spread, `map`, `toSorted`)

## 🧠 The big idea

Often you already **have** the data (a list of statuses, a label map) and you want the types to **follow the data**, not the other way around. Write the list once with `as const`, derive the union from it, and let `satisfies` verify the lookup tables are complete. Change the list → every dependent type and table updates or errors.

## ❓ Why does this exist?

Front-ends are full of configuration objects: status labels, colors per status, route tables, feature flags, select options. Without precise types, a missing key (`STATUS_LABELS.interview` undefined) shows as an empty badge in production.

## 💥 What happens if we DON'T?

```ts
const STATUSES = ["saved", "applied", "interview"];      // string[]
type Status = "saved" | "applied" | "interview";          // typed again by hand → drifts
const LABELS: Record<string, string> = { saved: "Saved", aplied: "Applied" };  // typo compiles
LABELS["interview"].toUpperCase();                        // 💥 undefined at runtime
```

## 📖 How it works, step by step

### 1. Arrays and tuples

```ts
const skills: string[] = ["python", "sql"];
function render(items: readonly string[]) { ... }      // accepts mutable AND readonly arrays; can't push
const range: [min: number, max: number] = [9, 14];      // fixed length, typed positions
```

Function parameters should usually be `readonly` — it documents that you won't mutate them and accepts more inputs.

### 2. `as const`

```ts
const STATUSES = ["saved", "applied", "interview", "offer", "rejected"] as const;
// type: readonly ["saved", "applied", "interview", "offer", "rejected"]

type Status = (typeof STATUSES)[number];
// "saved" | "applied" | "interview" | "offer" | "rejected"
```

- `typeof STATUSES` — the type of a value
- `[number]` — the type of any element (indexed access)

Now `STATUSES.map(...)` renders the select options and `Status` types the model — one source of truth.

### 3. `keyof` and indexed access

```ts
interface Job { id: number; title: string; salaryMax: number | null }
type JobKey = keyof Job;                    // "id" | "title" | "salaryMax"
type Salary = Job["salaryMax"];             // number | null

function sortBy(jobs: readonly Job[], key: "id" | "title") { ... }   // or K extends keyof Job (generics lesson)
```

### 4. `Record` vs index signatures

```ts
const counts: Record<Status, number> = { saved: 0, applied: 2, interview: 0, offer: 1, rejected: 0 };   // every key required
const cache: { [jobId: string]: Job } = {};                                                             // any string key
```

With `noUncheckedIndexedAccess`, `cache["42"]` is `Job | undefined` — honest about missing keys. `Record<Status, …>` over a finite union is complete, so reads are safe.

### 5. `satisfies`

```ts
const STATUS_LABELS = {
  saved: "Saved",
  applied: "Applied",
  interview: "Interview",
  offer: "Offer",
  rejected: "Rejected",
} satisfies Record<Status, string>;
```

- Missing or misspelled keys → error (like an annotation).
- But the value keeps its **precise** type (unlike `: Record<Status, string>`), so e.g. `keyof typeof STATUS_LABELS` stays exact and extra helpful inference remains.

Great for config tables, route maps, and theme tokens.

### 6. Immutable updates, typed

```ts
function moveItem(items: readonly BoardItem[], id: number, status: Status): BoardItem[] {
  return items.map((item) => (item.id === id ? { ...item, status } : item));
}
```

- `readonly` input prevents accidental `items[0].status = ...` on the array (fields need their own `readonly`).
- Spreading keeps untouched items identical (`===`) — React uses this to skip re-rendering them.
- `Readonly<T>` / `readonly` are compile-time only; `Object.freeze` enforces at runtime.

### 7. Narrowing unknown strings

```ts
function isStatus(value: unknown): value is Status {
  return typeof value === "string" && (STATUSES as readonly string[]).includes(value);
}
const fromUrl = new URLSearchParams(location.search).get("status");
const status: Status = isStatus(fromUrl) ? fromUrl : "saved";
```

(The `as readonly string[]` widens the tuple so `includes` accepts any string.)

## ⚖️ Trade-offs

| Choice | ✅ | ❌ |
|---|---|---|
| `as const` + derived unions | one source of truth | readonly tuples need widening for `includes` |
| Type annotation `: Record<…>` | checks completeness | loses literal value types |
| `satisfies` | checks + keeps precision | newer syntax some teams don't know |
| Index signatures | flexible keys | every read may be `undefined` |
| `readonly` everywhere | safer | noisy in small scripts |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ `as const` for fixed option lists and config; `satisfies` for lookup tables.
- ✅ `readonly` parameters for arrays you only read.
- 🚫 Don't use index signatures when the keys are a known finite set — use `Record<Union, …>`.

## 🏆 Best practices

- [ ] Derive unions from `as const` arrays instead of retyping them.
- [ ] Use `satisfies Record<Union, V>` for complete lookup tables.
- [ ] Enable `noUncheckedIndexedAccess`; handle `undefined` from dynamic lookups.
- [ ] Accept `readonly T[]` in functions; return new arrays/objects.
- [ ] Guard values coming from URLs, storage and APIs before treating them as unions.

## 🏭 How it's used in industry

- Design systems type variant tables with `satisfies` (e.g. button variants → classes — lesson 06).
- Routing libraries (TanStack Router, typed Next.js routes) derive route param types from route definitions.
- i18n libraries check translation keys against a typed dictionary.

## ⚠️ Common mistakes

- Losing literal types by annotating config objects too loosely.
- Mutating props/state arrays in place (`sort`, `push`).
- `obj[key]` on `Record<string, T>` assuming it exists.
- Duplicating a union type and the runtime array that lists the same values.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain the difference between `const LABELS: Record<Status, string> = …` and `const LABELS = { … } satisfies Record<Status, string>` to a teammate.

## 📐 Design it

Design the typed configuration for CareerPilot's application **filters bar**: status options with labels and colors, sort options (`newest`, `oldest`, `company A–Z`) mapped to API query parameters, and reading/writing these to the URL query string safely.

:::quiz
Show a possible design

```ts
export const STATUSES = ["saved", "applied", "interview", "offer", "rejected"] as const;
export type Status = (typeof STATUSES)[number];

export const STATUS_META = {
  saved: { label: "Saved", badge: "bg-slate-100 text-slate-700" },
  applied: { label: "Applied", badge: "bg-blue-50 text-blue-700" },
  interview: { label: "Interview", badge: "bg-amber-50 text-amber-800" },
  offer: { label: "Offer", badge: "bg-green-50 text-green-700" },
  rejected: { label: "Rejected", badge: "bg-red-50 text-red-700" },
} satisfies Record<Status, { label: string; badge: string }>;

export const SORTS = {
  newest: { label: "Newest", query: { order_by: "created_at", direction: "desc" } },
  oldest: { label: "Oldest", query: { order_by: "created_at", direction: "asc" } },
  company: { label: "Company A–Z", query: { order_by: "company", direction: "asc" } },
} as const satisfies Record<string, { label: string; query: { order_by: string; direction: "asc" | "desc" } }>;
export type SortKey = keyof typeof SORTS;

export interface Filters { status: Status | null; sort: SortKey; q: string }

const isStatus = (v: unknown): v is Status => typeof v === "string" && (STATUSES as readonly string[]).includes(v);
const isSort = (v: unknown): v is SortKey => typeof v === "string" && Object.hasOwn(SORTS, v);

export function readFilters(params: URLSearchParams): Filters {
  const status = params.get("status");
  const sort = params.get("sort");
  return { status: isStatus(status) ? status : null, sort: isSort(sort) ? sort : "newest", q: params.get("q") ?? "" };
}

export function writeFilters(filters: Filters): URLSearchParams {
  const params = new URLSearchParams();
  if (filters.status) params.set("status", filters.status);
  if (filters.sort !== "newest") params.set("sort", filters.sort);
  if (filters.q.trim()) params.set("q", filters.q.trim());
  return params;
}
```

Untrusted URL values are narrowed with guards; tables are complete by construction; defaults are omitted from the URL to keep links short.
:::

### 📝 Self-review checklist

- [ ] One source of truth for statuses and sorts
- [ ] Tables checked for completeness
- [ ] URL values validated before use

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w2/03-arrays-objects" ai="no-ai" title="A typed application board"}
Derive a `Status` union from an `as const` array, build a complete label table with `satisfies`, and write immutable board functions — counts with zeros, moving items, adding tags and sorting — accepting readonly arrays. Type tests check readonly fields, invalid statuses and keys.
:::

:::hints
- `Object.fromEntries(STATUSES.map((s) => [s, 0])) as Record<Status, number>` starts counts at zero (one justified assertion).
- `items.map((item) => (item.id === id ? { ...item, status } : item))` keeps untouched items identical.
- For status order, `STATUSES.indexOf(a.status) - STATUSES.indexOf(b.status)`.
:::

## ✅ Quick check

:::quiz
How do you get a union of the element values of `const X = ["a", "b"] as const`?

`type T = (typeof X)[number]` → `"a" | "b"`.
:::

:::quiz
What does `noUncheckedIndexedAccess` change?

Index access like `arr[0]` or `record[key]` (with an index signature) includes `undefined` in the type, forcing you to handle missing values.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Tuple | Tupel — larik dengan panjang dan tipe per posisi tetap |
| `as const` | Menjadikan nilai literal dan readonly |
| Indexed access type | Tipe akses indeks (`T["key"]`) |
| Index signature | Tanda indeks (kunci dinamis) |
| `satisfies` | Operator pengecek kecocokan tipe tanpa mengubah tipe nilai |

## 📚 Keep learning

- [TypeScript Handbook: Indexed Access Types](https://www.typescriptlang.org/docs/handbook/2/indexed-access-types.html)
- [TypeScript 4.9 release notes: the satisfies operator](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html)
