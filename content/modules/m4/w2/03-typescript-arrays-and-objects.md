---
title: "TypeScript Arrays & Objects"
summary: Type lists and lookup tables precisely — readonly arrays, tuples, `as const`, `keyof`, `Record`, `satisfies`, and updating data without changing the original, all checked by TypeScript.
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

- Typing arrays, readonly arrays and tuples
- `as const`: making types **follow your data**
- `keyof` and `Type["field"]`
- `Record` for lookup tables, and why missing keys are dangerous
- `satisfies`: checking a table is complete
- Updating arrays and objects without changing the original

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **`readonly` array** | An array your code promises not to change | Array hanya-baca |
| **Tuple** | An array with a fixed length and a type per position: `[min, max]` | Tupel |
| **`as const`** | "Treat these values as exact and unchangeable" | Nilai pasti |
| **`typeof` (in types)** | Get the type of an existing value | Ambil tipe dari nilai |
| **`keyof`** | The list of field names of a type: `"id" \| "title"` | Daftar nama field |
| **`Record<K, V>`** | An object type with keys K and values V | Tabel kunci-nilai |
| **`satisfies`** | "Check this value matches a type, but keep its exact type" | Cek kecocokan |

## 🧠 The big idea

Often you already **have** the data — a list of statuses, a table of labels. Instead of typing the same list twice (once as data, once as a type), let the type **follow the data**. It's like a **master price list** at a shop: change the price in one place, and every receipt uses the new price automatically.

## ❓ Why it matters

Frontends are full of small config tables: labels per status, colors per status, dropdown options. If a key is missing, the page shows an empty badge — and nobody notices until a user does.

```ts
const STATUSES = ["saved", "applied", "interview"];      // string[]
type Status = "saved" | "applied" | "interview";          // typed again by hand → drifts
const LABELS: Record<string, string> = { saved: "Saved", aplied: "Applied" };  // typo compiles
LABELS["interview"].toUpperCase();                        // 💥 undefined at runtime
```

- The list and the type are written twice, so they drift apart.
- The typo `aplied` compiles.
- A missing key crashes only when the app runs.

## 📖 Step by step

### 1. Arrays and tuples

```ts
const skills: string[] = ["python", "sql"];
function render(items: readonly string[]) { ... }      // accepts mutable AND readonly arrays; can't push
const range: [min: number, max: number] = [9, 14];      // fixed length, typed positions
```

- For function inputs, prefer `readonly string[]`: it says "I will only read this", like borrowing a library book — you read it, you don't write in it.
- A **tuple** has fixed positions, like a date written as `[day, month, year]`.

### 2. `as const` — the type follows the data

```ts
const STATUSES = ["saved", "applied", "interview", "offer", "rejected"] as const;
// type: readonly ["saved", "applied", "interview", "offer", "rejected"]

type Status = (typeof STATUSES)[number];
// "saved" | "applied" | "interview" | "offer" | "rejected"
```

Read the last line like this:
- `typeof STATUSES` — "the type of this array",
- `[number]` — "the type of any item inside it".

Now the same list feeds the dropdown options **and** the `Status` type. Add a status to the list → the type updates too.

### 3. `keyof` and `Type["field"]`

```ts
interface Job { id: number; title: string; salaryMax: number | null }
type JobKey = keyof Job;                    // "id" | "title" | "salaryMax"
type Salary = Job["salaryMax"];             // number | null

function sortBy(jobs: readonly Job[], key: "id" | "title") { ... }   // or K extends keyof Job (generics lesson)
```

- `keyof Job` = the names of all fields, like the column headers of a spreadsheet.
- `Job["salaryMax"]` = the type of one field.

### 4. `Record` and missing keys

```ts
const counts: Record<Status, number> = { saved: 0, applied: 2, interview: 0, offer: 1, rejected: 0 };   // every key required
const cache: { [jobId: string]: Job } = {};                                                             // any string key
```

- `Record<Status, number>` = one entry for **every** status. Forget one → error.
- `{ [jobId: string]: Job }` = any string can be a key, so a key may not exist. With the `noUncheckedIndexedAccess` setting, `cache["42"]` has the type `Job | undefined`, which reminds you to handle "not found".

### 5. `satisfies` — check a table is complete

```ts
const STATUS_LABELS = {
  saved: "Saved",
  applied: "Applied",
  interview: "Interview",
  offer: "Offer",
  rejected: "Rejected",
} satisfies Record<Status, string>;
```

`satisfies` is like a **teacher checking your homework** without rewriting it: it reports missing or misspelled keys, but your values keep their exact types. (Writing `: Record<Status, string>` instead also checks, but it replaces the exact types with the general ones.)

Use it for config tables, route maps and theme settings.

### 6. Updating without changing the original

```ts
function moveItem(items: readonly BoardItem[], id: number, status: Status): BoardItem[] {
  return items.map((item) => (item.id === id ? { ...item, status } : item));
}
```

- `map` builds a new array; the changed item is a new object (`{ ...item, status }`).
- Items that didn't change stay the **exact same objects**. React uses this to skip redrawing them (Week 3).
- `readonly` is only checked while you write code. `Object.freeze` blocks changes while the app runs.

### 7. Checking strings from outside

```ts
function isStatus(value: unknown): value is Status {
  return typeof value === "string" && (STATUSES as readonly string[]).includes(value);
}
const fromUrl = new URLSearchParams(location.search).get("status");
const status: Status = isStatus(fromUrl) ? fromUrl : "saved";
```

A value from the URL, localStorage or an API can be anything. Check it before treating it as a `Status` — like checking a ticket before letting someone in. (`as readonly string[]` is needed so `includes` accepts any string.)

## ⚠️ Common mistakes

- Writing the list of values twice (array + type) — they drift apart.
- Annotating config objects too loosely (`Record<string, string>`), so typos compile.
- Assuming `obj[key]` exists on a `Record<string, T>`.
- Changing props or state arrays directly (`sort`, `push`).
- Using a URL or storage value as a `Status` without checking it.

## 🏆 Best practices

- [ ] Build unions from `as const` arrays instead of typing them again.
- [ ] Use `satisfies Record<Union, V>` for lookup tables that must be complete.
- [ ] Turn on `noUncheckedIndexedAccess`; handle "not found".
- [ ] Accept `readonly T[]` in functions; return new arrays and objects.
- [ ] Check values from URLs, storage and APIs with a type guard before using them.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Using the homework-checking analogy, explain the difference between `const LABELS: Record<Status, string> = …` and `const LABELS = { … } satisfies Record<Status, string>`.

## 📐 Design it

Design the typed settings for CareerPilot's **filters bar**: status options with labels and colors, sort options (`newest`, `oldest`, `company A–Z`) that map to API query parameters, and safely reading and writing them in the URL.

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

- The status list and sort table are the single source of truth.
- `satisfies` guarantees every status has a label and a color.
- Values from the URL are checked with guards before use.
- Default values are left out of the URL, so links stay short.
:::

### 📝 Self-review checklist

- [ ] One source of truth for statuses and sorts
- [ ] Tables are checked for missing keys
- [ ] URL values are checked before use

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w2/03-arrays-objects" ai="no-ai" title="A typed application board"}
Build a `Status` union from an `as const` array, create a complete label table with `satisfies`, and write board functions that never change their input — counts that include zeros, moving items, adding tags and sorting — accepting readonly arrays. Type tests check readonly fields, wrong statuses and wrong keys.
:::

:::hints
- `Object.fromEntries(STATUSES.map((s) => [s, 0])) as Record<Status, number>` starts all counts at zero (one assertion you can justify).
- `items.map((item) => (item.id === id ? { ...item, status } : item))` keeps unchanged items identical.
- For status order: `STATUSES.indexOf(a.status) - STATUSES.indexOf(b.status)`.
:::

## ✅ Quick check

:::quiz
How do you get a union of the values in `const X = ["a", "b"] as const`?

`type T = (typeof X)[number]` → `"a" | "b"`.
:::

:::quiz
What does `noUncheckedIndexedAccess` change?

Reading `arr[0]` or `record[key]` (with dynamic keys) includes `undefined` in the type, so you must handle "not found".
:::

## 📚 Keep learning

- [TypeScript Handbook: Indexed Access Types](https://www.typescriptlang.org/docs/handbook/2/indexed-access-types.html)
- [TypeScript 4.9 release notes: the satisfies operator](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html)
