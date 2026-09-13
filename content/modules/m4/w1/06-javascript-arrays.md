---
title: "JavaScript Arrays & Data Transformation"
summary: Transform data like a professional — map, filter, reduce, find, some/every, flatMap, sorting without mutation, grouping and Sets — the everyday toolkit for turning API responses into UI.
type: lesson
source: core
sourceRef: "M3 · W1 · L5"
roles: { be: recommended, fe: core, fs: core, ai: core, ops: optional }
durationMinutes: 150
tags: [javascript, arrays, functional-programming, immutability]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Array basics and which methods **mutate**
- `map`, `filter`, `reduce`, `find`, `some`, `every`, `includes`
- `flatMap`, `Set`, `Object.groupBy`, `Object.entries/fromEntries`
- Sorting with comparators — and non-mutating `toSorted`, `toReversed`, `with`
- Chaining transformations readably, and when a plain loop is better
- Python equivalents for everything

## 🧠 The big idea

Array methods are a **factory conveyor belt**: raw API data enters, each station does one job (keep the remote jobs, turn them into card data, sort by salary), and finished UI-ready data comes out — without anyone changing the original parts.

## ❓ Why does this exist?

Frontends constantly reshape data: your Flask API returns applications; the dashboard needs counts per status, the board needs them grouped by column, the chart needs averages. Declarative array methods say **what** you want, are easy to test, and don't mutate data that React relies on to detect changes (Week 3).

## 💥 What happens if we DON'T?

```js
function topJobs(jobs) {
  jobs.sort((a, b) => b.salary - a.salary);   // 🐛 mutates the caller's array (and React state!)
  return jobs.slice(0, 3);
}

const titles = [];
for (let i = 0; i <= jobs.length; i++) {       // 🐛 off-by-one → undefined
  if (jobs[i].remote == true) titles.push(jobs[i].title);
}
```

## 📖 How it works, step by step

### 1. Python ↔ JavaScript

| Python | JavaScript |
|---|---|
| `[j["title"] for j in jobs]` | `jobs.map((j) => j.title)` |
| `[j for j in jobs if j["remote"]]` | `jobs.filter((j) => j.remote)` |
| `functools.reduce` / `sum(...)` | `jobs.reduce((sum, j) => sum + j.salary, 0)` |
| `next((j for j in jobs if j["id"] == 2), None)` | `jobs.find((j) => j.id === 2)` → `undefined` if none |
| `any(...)` / `all(...)` | `some(...)` / `every(...)` |
| `sorted(jobs, key=...)` | `jobs.toSorted((a, b) => ...)` |
| `set(skills)` | `new Set(skills)` |
| `itertools.groupby` / defaultdict | `Object.groupBy(jobs, (j) => j.city)` |
| `enumerate(items)` | `items.map((item, index) => ...)` / `items.entries()` |

### 2. Mutating vs non-mutating

| Mutates ⚠️ | Returns a new array ✅ |
|---|---|
| `push`, `pop`, `shift`, `unshift`, `splice` | `concat`, `slice`, spread `[...a, x]` |
| `sort`, `reverse` | `toSorted`, `toReversed` |
| `arr[i] = x` | `arr.with(i, x)` |
| `fill`, `copyWithin` | `map`, `filter`, `flatMap` |

In UI code, prefer the right column — especially for state.

### 3. The big three

```js
const remote = jobs.filter((job) => job.remote);
const cards = remote.map((job) => ({ id: job.id, label: `${job.title} · ${job.company}` }));
const total = jobs.reduce((sum, job) => sum + (job.salaryMax ?? 0), 0);
```

`reduce(callback, initialValue)` — always pass the initial value.

```js
const countsByStatus = applications.reduce((counts, app) => {
  counts[app.status] = (counts[app.status] ?? 0) + 1;
  return counts;
}, {});
// { saved: 2, applied: 5, interview: 1 }
```

### 4. Searching and testing

```js
jobs.find((job) => job.id === id)          // first match or undefined
jobs.findIndex((job) => job.id === id)     // index or -1
jobs.some((job) => job.city === "Bandung") // at least one
jobs.every((job) => job.salaryMax !== null)
skills.includes("python")                  // uses === (NaN-safe)
```

### 5. Sorting correctly

```js
[10, 9, 100].sort()                                // [10, 100, 9] 🐛 compares as strings
[10, 9, 100].toSorted((a, b) => a - b)             // [9, 10, 100]
jobs.toSorted((a, b) => (b.salaryMax ?? -1) - (a.salaryMax ?? -1) || a.id - b.id)   // salary desc, then id
jobs.toSorted((a, b) => a.title.localeCompare(b.title, "id"))                        // text, locale-aware
```

The comparator returns negative (a first), positive (b first) or 0. `||` chains tie-breakers.

### 6. Flattening, uniqueness, grouping

```js
const allSkills = jobs.flatMap((job) => job.skills);            // [["py","sql"],["py"]] → ["py","sql","py"]
const unique = [...new Set(allSkills)].sort();                   // de-duplicate
const byCity = Object.groupBy(jobs, (job) => job.city);          // { Jakarta: [...], Bandung: [...] }
const titlesByCity = Object.fromEntries(
  Object.entries(byCity).map(([city, group]) => [city, group.map((j) => j.title)]),
);
```

`Object.groupBy` is ES2024 (all modern browsers and Node 21+).

### 7. Readable chains

```js
const topRemoteSalaries = jobs
  .filter((job) => job.remote && job.salaryMax !== null)
  .toSorted((a, b) => b.salaryMax - a.salaryMax)
  .slice(0, 5)
  .map(({ title, salaryMax }) => ({ title, salary: formatRupiah(salaryMax) }));
```

One step per line, named helper functions for non-trivial callbacks. Each step creates a new array — fine for hundreds or thousands of items; for huge data or hot loops, a single `for...of` can be clearer and faster.

## ⚖️ Trade-offs

| Choice | ✅ | ❌ |
|---|---|---|
| Method chains | declarative, testable, immutable | intermediate arrays; long chains get cryptic |
| `for...of` loop | early `break`, one pass, familiar | more mutable variables |
| `reduce` for everything | one pass | often harder to read than `filter`+`map` or a loop |
| `sort` in place | no copy | mutates shared data |
| `Object` as map | JSON-friendly | keys become strings; prototype keys — `Map` for arbitrary keys |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ Shaping API responses into UI data; derived state (counts, groups, totals).
- ✅ `find`/`some` instead of manual search loops.
- 🚫 `map` just to loop for side effects — use `forEach` or `for...of`.
- 🚫 Deeply nested `reduce` gymnastics — write a named function or a loop.

## 🏆 Best practices

- [ ] Never mutate inputs or state: `toSorted`, spread, `map`/`filter`.
- [ ] Always give `sort` a comparator; use `localeCompare` for text.
- [ ] Always give `reduce` an initial value.
- [ ] Handle empty arrays (averages, `Math.max(...[])` is `-Infinity`).
- [ ] Use `??` for missing numbers, not `||`.
- [ ] Name complex callbacks (`const isAffordable = (job) => ...`).
- [ ] Choose `Set`/`Map` for membership and lookups instead of `includes` in loops (O(n²)).

## 🏭 How it's used in industry

- Every React component that renders a list uses `map`; filters and sorting UIs are `filter` + `toSorted`.
- Redux/Zustand reducers and TanStack Query `select` functions transform data immutably.
- Data dashboards compute aggregates client-side with `reduce`/`groupBy` for small datasets (server-side SQL for big ones — Module 2).

## ⚠️ Common mistakes

- `.sort()` on numbers without a comparator.
- Mutating props/state with `push`/`sort`.
- Forgetting to `return` inside `map` with braces: `map((j) => { j.title })` → `undefined`s.
- Using `includes` inside a loop over large arrays.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a teammate why `applications.sort(...)` inside a component can cause bugs that `toSorted` doesn't, even if the result looks the same on screen.

## 📐 Design it

CareerPilot's dashboard receives `applications: [{ id, status, company: { name }, appliedOn, updatedAt, salaryMax }]`. Design pure functions (signatures + method chain sketch) for: (1) counts per status with all statuses present, (2) the pipeline board columns in order, each sorted by `updatedAt` newest first, (3) top 5 companies by number of applications, (4) response rate = applications that moved past `applied` ÷ applications that reached `applied`.

:::quiz
Show a possible design

```js
const STATUSES = ["saved", "applied", "screening", "interview", "offer", "accepted", "rejected", "withdrawn"];

export const countsByStatus = (apps) =>
  Object.fromEntries(STATUSES.map((s) => [s, apps.filter((a) => a.status === s).length]));
// one filter per status: O(8n) — fine; a single reduce also works

export const boardColumns = (apps) => {
  const groups = Object.groupBy(apps, (a) => a.status);
  return STATUSES.map((status) => ({
    status,
    items: (groups[status] ?? []).toSorted((a, b) => b.updatedAt.localeCompare(a.updatedAt)), // ISO strings sort lexically
  }));
};

export const topCompanies = (apps, n = 5) =>
  Object.entries(Object.groupBy(apps, (a) => a.company.name))
    .map(([name, group]) => ({ name, count: group.length }))
    .toSorted((a, b) => b.count - a.count || a.name.localeCompare(b.name))
    .slice(0, n);

const PAST_APPLIED = new Set(["screening", "interview", "offer", "accepted", "rejected"]);
export const responseRate = (apps) => {
  const reachedApplied = apps.filter((a) => a.appliedOn !== null);
  if (reachedApplied.length === 0) return 0;
  return reachedApplied.filter((a) => PAST_APPLIED.has(a.status)).length / reachedApplied.length;
};
```

Decisions to note: every status present (UI never checks `undefined`), explicit tie-breaks, division-by-zero guard, ISO timestamps compared as strings. (Whether "rejected without screening" counts as a response is a **product** question — write it down.)
:::

### 📝 Self-review checklist

- [ ] Pure functions, no mutation
- [ ] Empty data handled
- [ ] Deterministic ordering with tie-breaks

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w1/06-array-methods" ai="no-ai" title="Transform job data with array methods"}
Implement nine small data functions — filtering, averaging, counting, sorting without mutation, grouping, `every`/`some`, unique skills and lookup — over frozen input data. Tests fail if you use loops or mutate the input.
:::

:::hints
- The test data is frozen with `Object.freeze`: `sort` on it throws — use `toSorted`.
- For `skillCounts`, `flatMap` first, then `reduce` into an object.
- `jobs.map((j) => j.salaryMax).filter((s) => s !== null)` before averaging.
:::

## ✅ Quick check

:::quiz
What does `[3, 20, 100].sort()` return and why?

`[100, 20, 3]` — without a comparator, elements are compared as strings ("100" < "20" < "3").
:::

:::quiz
`map` vs `forEach`?

`map` returns a new array of transformed values; `forEach` returns `undefined` and is only for side effects.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Immutable | Tidak diubah (membuat salinan baru) |
| Callback | Fungsi yang diberikan ke fungsi lain |
| Comparator | Fungsi pembanding untuk pengurutan |
| Accumulator | Akumulator — nilai yang dibawa `reduce` |
| Derived data | Data turunan (dihitung dari data lain) |

## 📚 Keep learning

- [MDN: Array](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array)
- [MDN: Object.groupBy()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/groupBy)
