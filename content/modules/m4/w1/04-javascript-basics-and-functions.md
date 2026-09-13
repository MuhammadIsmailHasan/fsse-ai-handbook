---
title: "JavaScript Basics & Functions"
summary: JavaScript for Python developers — values and types, equality and truthiness, const/let, strings and template literals, functions, arrow functions, closures, modules, and the quirks that cause real bugs.
type: lesson
source: core
sourceRef: "M3 · W1 · L3"
roles: { be: recommended, fe: core, fs: core, ai: core, ops: optional }
durationMinutes: 180
tags: [javascript, functions, closures, types, modules]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Where JavaScript runs (browser, Node.js) and how it differs from Python
- `const` / `let`, primitive types, objects and arrays
- `===` vs `==`, **truthiness**, `??` vs `||`, optional chaining `?.`
- Strings, template literals, numbers (and their gotchas)
- Function declarations, **arrow functions**, default and rest parameters
- **Closures** and functions as values (callbacks, debounce)
- ES modules: `import` / `export`

## 🧠 The big idea

You already know how to program. JavaScript is **a new dialect, not a new language of thought**: variables, functions, loops and objects work much like Python. The danger is in the small differences that *look* familiar — `==`, truthiness, `this`, numbers — so this lesson focuses there.

## ❓ Why does this exist?

JavaScript is the only language browsers run natively, so every interactive web page — and React, Next.js, and the UI of your CareerPilot app — is JavaScript (or TypeScript compiled to it). With Node.js it also runs servers, build tools, and CLIs.

## 💥 What happens if we DON'T learn the quirks?

```js
if (salaryMax) { showSalary() }          // 🐛 salary 0 is hidden
const count = input.value + 1            // 🐛 "5" + 1 === "51"
if (status == 0) { ... }                 // 🐛 "" == 0 is true
0.1 + 0.2 === 0.3                        // false (same as Python!)
```

## 📖 How it works, step by step

### 1. Python ↔ JavaScript cheat sheet

| Python | JavaScript |
|---|---|
| `name = "Siti"` | `const name = "Siti"` (can't reassign) / `let count = 0` |
| `None` | `null` (intentional empty) and `undefined` (not set) |
| `True`, `False` | `true`, `false` |
| `f"Hi {name}"` | `` `Hi ${name}` `` |
| `len(items)` | `items.length` |
| `dict` | object `{ key: value }` or `Map` |
| `list` | array `[1, 2, 3]` |
| `def add(a, b=1):` | `function add(a, b = 1) {}` or `const add = (a, b = 1) => a + b` |
| `and / or / not` | `&& / \|\| / !` |
| `for x in items:` | `for (const x of items) {}` |
| `raise ValueError()` | `throw new Error()` |
| `try/except` | `try/catch` |
| `import x from y` | `import { x } from "./y.js"` |
| indentation blocks | `{ }` blocks (semicolons optional but common) |

Never use `var` (function-scoped, hoisted, confusing). `const` by default; `let` when you must reassign.

### 2. Types

Primitives: `string`, `number` (one type for ints and floats), `bigint`, `boolean`, `null`, `undefined`, `symbol`. Everything else is an **object** (arrays, functions, dates…).

```js
typeof "hi"        // "string"
typeof 42          // "number"
typeof null        // "object"  ← historic bug; check null with === null
Array.isArray([])  // true
Number("12abc")    // NaN  (Not a Number — and NaN !== NaN; use Number.isNaN)
```

Money: numbers are floats. Store rupiah as **integers** (like your Flask API), never do currency math with fractions of units.

### 3. Equality and truthiness

```js
0 == ""            // true   ← coercion
0 === ""           // false  ✅ always use === and !==
```

**Falsy** values: `false`, `0`, `-0`, `0n`, `""`, `null`, `undefined`, `NaN`. Everything else is truthy — including `"0"`, `[]` and `{}` (unlike Python, where empty lists are falsy!).

```js
const salary = job.salaryMax || "Not disclosed"   // 🐛 0 → "Not disclosed"
const salary = job.salaryMax ?? "Not disclosed"   // ✅ only null/undefined fall back
const city = job.company?.address?.city           // undefined instead of a crash
```

### 4. Strings

```js
const title = "  Backend Engineer ";
title.trim().toLowerCase()                // "backend engineer"
title.includes("End")                     // false (case-sensitive)
`Rp ${min / 1_000_000}–${max / 1_000_000} juta`
"a-b-c".split("-")                        // ["a", "b", "c"]
"backend engineer".replace(/\s+/g, "-")    // regex with g flag = replace all
```

### 5. Functions

```js
// declaration: hoisted, has its own `this`
function slugify(title) {
  return title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
}

// arrow function: concise, inherits `this` from outside — the default in modern code
const double = (n) => n * 2;
const toCard = (job) => ({ id: job.id, label: job.title });   // returning an object: wrap in ()

// defaults, rest parameters, destructuring
function salaryLabel({ min = null, max = null } = {}) { ... }
const sum = (...numbers) => numbers.reduce((a, b) => a + b, 0);
```

Functions are values: pass them around (`button.addEventListener("click", onSave)`), return them, store them.

### 6. Closures

A function remembers the variables of the scope where it was created:

```js
function createCounter(start = 0) {
  let count = start;                  // private
  return {
    increment: () => ++count,
    value: () => count,
  };
}
const saved = createCounter();
saved.increment();                    // 1 — nobody else can touch `count`
```

Closures power event handlers, React hooks (Week 3), and utilities like **debounce**:

```js
function debounce(fn, waitMs) {
  let timer;                          // shared by every call of the returned function
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), waitMs);
  };
}
const onSearch = debounce((text) => fetchJobs(text), 300);   // one request after typing stops
```

### 7. Objects, spread and destructuring

```js
const job = { id: 1, title: "Backend Engineer", salary: { min: 9e6, max: 14e6 } };
const { title, salary: { max } } = job;          // destructuring
const updated = { ...job, title: "Senior Backend Engineer" };   // copy + change (shallow!)
const [first, ...rest] = ["python", "sql", "docker"];
```

Objects and arrays are **references** (like Python): `const copy = job` doesn't copy. Spread makes a **shallow** copy; `structuredClone(job)` makes a deep one.

### 8. Modules

```js
// format.js
export function slugify(title) { ... }
export const CURRENCY = "IDR";

// app.js
import { slugify, CURRENCY } from "./format.js";
```

In the browser: `<script type="module" src="app.js"></script>`. In Node: `"type": "module"` in `package.json`. Each module has its own scope — no accidental globals.

## ⚖️ Trade-offs

| Choice | ✅ | ❌ |
|---|---|---|
| Arrow functions | short, predictable `this` | can't be constructors; no `arguments` |
| Function declarations | hoisted, clear names in stack traces | `this` depends on how they're called |
| `==` | shorter | coercion bugs — avoid |
| `\|\|` for defaults | works for strings | wrong for `0`, `""`, `false` → use `??` |
| Plain JS | no build step | no type safety → TypeScript next week |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ `const` + arrow functions + `===` + `??` + `?.` as defaults.
- ✅ Closures for private state and callbacks.
- 🚫 `var`, `==`, modifying built-in prototypes, global variables.
- 🚫 Number math for money with decimals.

## 🏆 Best practices

- [ ] `const` by default, `let` only when reassigning, never `var`.
- [ ] `===`/`!==` always; `??` for defaults; `?.` for optional data.
- [ ] Small pure functions with clear names; avoid hidden global state.
- [ ] Template literals instead of string concatenation.
- [ ] Use ES modules; one responsibility per module.
- [ ] Format with Prettier and lint with ESLint (they catch `==`, unused variables, shadowing).
- [ ] Learn to use the browser **Console** and **debugger** breakpoints — `debugger;` works like Python's `breakpoint()`.

## 🏭 How it's used in industry

- Nearly every frontend is JavaScript/TypeScript; many backends and tools use Node.js, Deno or Bun.
- Code reviews routinely flag `==`, `||` defaults on numbers and mutation of shared objects.
- Debounce/throttle are standard for search boxes and scroll handlers (TanStack, lodash, custom hooks).

## ⚠️ Common mistakes

- `"5" + 1` string concatenation from form inputs → convert with `Number()`.
- Checking emptiness with `if (list)` — `[]` is truthy; use `list.length === 0`.
- Forgetting `return` in multi-line arrow functions with `{ }`.
- Mutating objects passed in (surprises callers — and breaks React later).

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a Python developer why `if (job.salaryMax)` is a bug in JavaScript when salary can be `0`, and which operator fixes the "default value" case.

## 📐 Design it

CareerPilot's job search box calls the API as the user types. Design the functions (names, inputs, outputs) that: normalize the query, debounce requests, ignore responses that arrive out of order (an old slow response must not overwrite newer results), and cache the last 20 queries.

:::quiz
Show a possible design

```js
export const normalizeQuery = (text) => text.trim().replace(/\s+/g, " ").toLowerCase();

export function createSearch({ fetchJobs, render, waitMs = 300, cacheSize = 20 }) {
  const cache = new Map();          // query → results (Map keeps insertion order → simple LRU)
  let latestRequestId = 0;          // closure state

  async function run(rawText) {
    const query = normalizeQuery(rawText);
    if (query === "") return render([]);
    if (cache.has(query)) {
      const results = cache.get(query);
      cache.delete(query); cache.set(query, results);   // refresh recency
      return render(results);
    }
    const requestId = ++latestRequestId;
    const results = await fetchJobs(query);
    if (requestId !== latestRequestId) return;          // an older response arrived late → ignore
    cache.set(query, results);
    if (cache.size > cacheSize) cache.delete(cache.keys().next().value);   // evict oldest
    render(results);
  }

  return debounce(run, waitMs);
}
```

- Pure `normalizeQuery` is trivially testable.
- Closures hold the cache and request counter privately.
- Dependencies (`fetchJobs`, `render`) are injected → testable with fakes.
- Later, `AbortController` can cancel outdated requests instead of ignoring them (lesson 07), and TanStack Query does most of this for you (Week 4).
:::

### 📝 Self-review checklist

- [ ] Out-of-order responses handled
- [ ] State kept private in closures
- [ ] Dependencies injected

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w1/04-js-basics-functions" ai="no-ai" title="Slugs, salary labels, closures and debounce"}
Implement string cleanup, a salary label with several optional-value cases, a blank check that doesn't trust truthiness, a closure-based counter and a debounce function tested with fake timers — using modern syntax only.
:::

:::hints
- `slugify`: two regex replaces — non-alphanumerics to `-`, then trim leading/trailing `-`.
- `salaryLabel`: compare with `=== null || === undefined` (or `== null` — but the tests forbid `==`, so write it out).
- `Math.round(x * 10) / 10` rounds to one decimal; `String(9)` is `"9"` and `String(9.5)` is `"9.5"`.
- `debounce`: keep `timer` outside the returned function.
:::

## ✅ Quick check

:::quiz
What's the difference between `null` and `undefined`?

`undefined` means a value was never set (missing property, missing argument); `null` is an intentional "no value". Both are falsy and both trigger `??`.
:::

:::quiz
What does a closure capture?

The variables of the scope where the function was created, which stay alive as long as the function exists.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Truthy / falsy | Nilai yang dianggap benar / salah dalam kondisi |
| Strict equality | Kesamaan ketat (`===`) |
| Arrow function | Fungsi panah |
| Closure | Penutupan — fungsi yang mengingat variabel di sekitarnya |
| Callback | Fungsi yang dipanggil kembali oleh fungsi lain |
| Debounce | Menunda eksekusi sampai input berhenti |

## 📚 Keep learning

- [MDN: JavaScript Guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide)
- [javascript.info — The Modern JavaScript Tutorial](https://javascript.info/)
- [MDN: Closures](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Closures)
