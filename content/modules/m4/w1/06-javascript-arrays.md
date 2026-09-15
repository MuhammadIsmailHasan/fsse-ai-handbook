---
title: "JavaScript Arrays & Data Transformation"
summary: Turn API data into what the page needs — map, filter, reduce, find, some/every, flatMap, sorting without changing the original, grouping and Sets — explained with Python comparisons.
type: lesson
source: core
sourceRef: "M3 · W1 · L5"
roles: { be: recommended, fe: core, fs: core, ai: core, ops: optional }
durationMinutes: 150
tags: [javascript, arrays, functional-programming, immutability]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Which array methods **change** the original array, and which make a new one
- `map`, `filter`, `reduce`, `find`, `some`, `every`
- Sorting numbers and text correctly
- Removing duplicates and grouping data
- Writing readable chains of steps
- The Python version of each method

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **`map`** | Change every item and get a new array of the same length | Ubah setiap item |
| **`filter`** | Keep only the items that pass a test | Saring |
| **`reduce`** | Combine all items into one value (a total, a count, an object) | Gabungkan jadi satu |
| **Mutate** | Change the original data in place | Mengubah data asli |
| **Immutable** | Don't change the original — make a new copy instead | Tidak mengubah asli |
| **Comparator** | A small function that tells `sort` which of two items goes first | Fungsi pembanding |
| **`Set`** | A collection with no duplicates | Himpunan tanpa duplikat |

## 🧠 The big idea

Array methods work like a **laundry line**: dirty clothes go in, one station sorts them, the next washes, the next folds, and clean folded clothes come out. Each station does one job. And the original pile isn't destroyed — every station makes a new pile.

In code: raw jobs from the API → keep remote jobs (`filter`) → turn each into card data (`map`) → sort by salary → show on the page.

## ❓ Why it matters

Frontends reshape data all the time: your Flask API returns applications, the dashboard needs counts per status, the board needs them grouped by column. Array methods say **what** you want in a few clear lines, are easy to test, and don't change data React depends on (Week 3).

The old way easily creates bugs:

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

## 📖 Step by step

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

### 2. Changes the original vs makes a new array

Some methods write on the original paper; others make a photocopy first.

| Changes the original ⚠️ | Makes a new array ✅ |
|---|---|
| `push`, `pop`, `shift`, `unshift`, `splice` | `concat`, `slice`, spread `[...a, x]` |
| `sort`, `reverse` | `toSorted`, `toReversed` |
| `arr[i] = x` | `arr.with(i, x)` |
| `fill`, `copyWithin` | `map`, `filter`, `flatMap` |

In page code — especially React state — use the right column.

### 3. The big three: `map`, `filter`, `reduce`

```js
const remote = jobs.filter((job) => job.remote);
const cards = remote.map((job) => ({ id: job.id, label: `${job.title} · ${job.company}` }));
const total = jobs.reduce((sum, job) => sum + (job.salaryMax ?? 0), 0);
```

- `filter` = a sieve: only what passes stays.
- `map` = a stamp: every item gets changed the same way.
- `reduce` = a piggy bank: you drop in items one by one and end with one total. The `0` at the end is the starting amount — always give one.

`reduce` can also build an object, like counting votes:

```js
const countsByStatus = applications.reduce((counts, app) => {
  counts[app.status] = (counts[app.status] ?? 0) + 1;
  return counts;
}, {});
// { saved: 2, applied: 5, interview: 1 }
```

### 4. Finding and checking

```js
jobs.find((job) => job.id === id)          // first match or undefined
jobs.findIndex((job) => job.id === id)     // index or -1
jobs.some((job) => job.city === "Bandung") // at least one
jobs.every((job) => job.salaryMax !== null)
skills.includes("python")                  // uses === (NaN-safe)
```

- `some` = "is there **at least one**?"
- `every` = "do **all** of them pass?"

### 5. Sorting correctly

```js
[10, 9, 100].sort()                                // [10, 100, 9] 🐛 compares as strings
[10, 9, 100].toSorted((a, b) => a - b)             // [9, 10, 100]
jobs.toSorted((a, b) => (b.salaryMax ?? -1) - (a.salaryMax ?? -1) || a.id - b.id)   // salary desc, then id
jobs.toSorted((a, b) => a.title.localeCompare(b.title, "id"))                        // text, locale-aware
```

Without a comparator, JavaScript sorts numbers **like words** ("100" comes before "9", like in a dictionary). The comparator answers "who goes first?":
- negative number → `a` first,
- positive number → `b` first,
- `0` → same.

`||` adds a tie-breaker: if salaries are equal, sort by id.

### 6. Flattening, removing duplicates, grouping

```js
const allSkills = jobs.flatMap((job) => job.skills);            // [["py","sql"],["py"]] → ["py","sql","py"]
const unique = [...new Set(allSkills)].sort();                   // de-duplicate
const byCity = Object.groupBy(jobs, (job) => job.city);          // { Jakarta: [...], Bandung: [...] }
const titlesByCity = Object.fromEntries(
  Object.entries(byCity).map(([city, group]) => [city, group.map((j) => j.title)]),
);
```

- `flatMap` = `map`, then open the small bags into one big bag.
- `new Set(...)` = keep each value once, like a guest list where duplicate names are removed.
- `Object.groupBy` = sort items into boxes by a label (city, status).

### 7. Readable chains

```js
const topRemoteSalaries = jobs
  .filter((job) => job.remote && job.salaryMax !== null)
  .toSorted((a, b) => b.salaryMax - a.salaryMax)
  .slice(0, 5)
  .map(({ title, salaryMax }) => ({ title, salary: formatRupiah(salaryMax) }));
```

One step per line, like a recipe. If a step is complicated, give it a name (`const isRemote = (job) => ...`). For huge data (tens of thousands of items) or very frequent code, one simple `for...of` loop can be clearer and faster.

## ⚠️ Common mistakes

- `.sort()` on numbers without a comparator.
- Changing props or state with `push` or `sort`.
- Forgetting `return` in `map` with braces: `map((j) => { j.title })` gives `undefined`s.
- Using `map` just to loop (use `forEach` or `for...of`).
- Very clever nested `reduce` calls that nobody can read.
- `includes` inside a loop over a big array (slow) — use a `Set`.

## 🏆 Best practices

- [ ] Don't change inputs or state: use `toSorted`, spread, `map`, `filter`.
- [ ] Always give `sort` a comparator; use `localeCompare` for text.
- [ ] Always give `reduce` a starting value.
- [ ] Handle empty arrays (an average of nothing, `Math.max(...[])` is `-Infinity`).
- [ ] Use `??` for missing numbers, not `||`.
- [ ] Name complex callbacks (`const isAffordable = (job) => ...`).
- [ ] Use `Set` or `Map` for fast "is it in here?" checks.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a teammate why `applications.sort(...)` inside a component can cause bugs that `toSorted` doesn't, even if the screen looks the same. Use the "write on the original vs photocopy" idea.

## 📐 Design it

CareerPilot's dashboard gets `applications: [{ id, status, company: { name }, appliedOn, updatedAt, salaryMax }]`. Plan functions (name + chain of steps) for: (1) the count for every status, including statuses with zero, (2) board columns in order, newest update first, (3) the top 5 companies by number of applications, (4) the response rate = applications that moved past `applied` ÷ applications that reached `applied`.

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

- Every status is always present, so the page never has to check for `undefined`.
- Ties are broken by name, so the order never jumps around.
- Division by zero is handled.
- Dates in ISO format (`2026-09-01T…`) can be compared as text.
- "Does a rejection without a screening call count as a response?" is a **product** decision — write it down.
:::

### 📝 Self-review checklist

- [ ] No function changes its input
- [ ] Empty data is handled
- [ ] The order is always the same (tie-breakers)

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w1/06-array-methods" ai="no-ai" title="Transform job data with array methods"}
Write nine small data functions — filter, average, count, sort without changing the input, group, `every`/`some`, unique skills and lookup — using frozen input data. The tests fail if you use loops or change the input.
:::

:::hints
- The test data is frozen with `Object.freeze`: calling `sort` on it throws an error — use `toSorted`.
- For `skillCounts`, use `flatMap` first, then `reduce` into an object.
- `jobs.map((j) => j.salaryMax).filter((s) => s !== null)` before calculating the average.
:::

## ✅ Quick check

:::quiz
What does `[3, 20, 100].sort()` return, and why?

`[100, 20, 3]` — without a comparator, the numbers are compared as text ("100" < "20" < "3").
:::

:::quiz
`map` or `forEach`?

`map` returns a new array with the changed values. `forEach` returns nothing — use it only to do something for each item.
:::

## 📚 Keep learning

- [MDN: Array](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array)
- [MDN: Object.groupBy()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/groupBy)
