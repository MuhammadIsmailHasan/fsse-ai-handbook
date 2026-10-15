---
title: "JavaScript Basics & Functions"
summary: JavaScript for Python developers — values and types, comparing values, const/let, strings, functions, arrow functions, closures and modules, plus the small differences that cause real bugs.
type: lesson
source: core
roles: { be: recommended, fe: core, fs: core, ai: core, ops: optional }
durationMinutes: 180
tags: [javascript, functions, closures, types, modules]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- How JavaScript compares to Python
- `const` and `let`, types, objects and arrays
- Comparing values safely (`===`), and "empty-ish" values
- Strings and template literals
- Functions, arrow functions and closures
- Splitting code into files with `import` / `export`

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **`const` / `let`** | Ways to create a variable: `const` can't be reassigned, `let` can | Konstanta / variabel |
| **Truthy / falsy** | Values JavaScript treats as true or false inside an `if` | Dianggap benar / salah |
| **`===`** | Strict comparison: same value **and** same type | Sama persis |
| **`??`** | "Use this default only if the value is `null` or `undefined`" | Nilai cadangan |
| **Arrow function** | A short way to write a function: `(a) => a * 2` | Fungsi ringkas |
| **Closure** | A function that remembers variables from where it was created | Fungsi yang mengingat |
| **Module** | One file that shares code with `export` and uses code with `import` | Modul |

## 🧠 The big idea

You already know how to program. Learning JavaScript after Python is like **moving from Jakarta to Bandung**: most things work the same (roads, shops, money), but a few local rules surprise you. This lesson focuses on those surprises — `==`, empty values and numbers — because that's where bugs come from.

## ❓ Why it matters

JavaScript is the only language browsers run directly. Every interactive page, React and Next.js — including your CareerPilot app — is JavaScript (or TypeScript turned into JavaScript).

The small differences cause real bugs:

```js
if (salaryMax) { showSalary() }          // 🐛 salary 0 is hidden
const count = input.value + 1            // 🐛 "5" + 1 === "51"
if (status == 0) { ... }                 // 🐛 "" == 0 is true
0.1 + 0.2 === 0.3                        // false (same as Python!)
```

## 📖 Step by step

### 1. Python ↔ JavaScript

| Python | JavaScript |
|---|---|
| `name = "Siti"` | `const name = "Siti"` (can't reassign) / `let count = 0` |
| `None` | `null` (empty on purpose) and `undefined` (never set) |
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
| indentation blocks | `{ }` blocks (semicolons are optional but common) |

Use `const` by default and `let` only when the value must change. Never use `var` (it's the old way and behaves strangely).

### 2. Types

Simple types: `string`, `number` (one type for whole and decimal numbers), `boolean`, `null`, `undefined` (and the rare `bigint`, `symbol`). Everything else is an **object** — arrays, functions, dates.

```js
typeof "hi"        // "string"
typeof 42          // "number"
typeof null        // "object"  ← historic bug; check null with === null
Array.isArray([])  // true
Number("12abc")    // NaN  (Not a Number — and NaN !== NaN; use Number.isNaN)
```

Money tip: store rupiah as **whole numbers** (like your Flask API). Decimal math with money gives rounding errors.

### 3. Comparing values and "empty" values

`==` tries to convert types before comparing — like a cashier who accepts a photo of money as real money. `===` checks the value **and** the type. Always use `===`.

```js
0 == ""            // true   ← coercion
0 === ""           // false  ✅ always use === and !==
```

These values count as **false** in an `if` (falsy): `false`, `0`, `""`, `null`, `undefined`, `NaN`. Everything else counts as true — **including `[]` and `{}`**. (In Python, an empty list is false. In JavaScript it's true!)

```js
const salary = job.salaryMax || "Not disclosed"   // 🐛 0 → "Not disclosed"
const salary = job.salaryMax ?? "Not disclosed"   // ✅ only null/undefined fall back
const city = job.company?.address?.city           // undefined instead of a crash
```

- `||` uses the default for **any** false-ish value, including `0`.
- `??` uses the default **only** for `null` or `undefined`. Better for numbers.
- `?.` (optional chaining) stops safely when something is missing, instead of crashing — like checking if a door exists before opening it.

### 4. Strings

```js
const title = "  Backend Engineer ";
title.trim().toLowerCase()                // "backend engineer"
title.includes("End")                     // false (case-sensitive)
`Rp ${min / 1_000_000}–${max / 1_000_000} juta`
"a-b-c".split("-")                        // ["a", "b", "c"]
"backend engineer".replace(/\s+/g, "-")    // regex with g flag = replace all
```

Template literals (with backticks `` ` ``) work like Python f-strings: `${...}` puts a value inside the text.

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

- An **arrow function** is a shorter way to write a function. Most modern code uses them.
- `...numbers` collects all arguments into an array (like Python's `*args`).
- Functions are values: you can pass them to other functions, like `button.addEventListener("click", onSave)`. A function passed like this is called a **callback** — "call me back when something happens".

### 6. Closures

A closure is a function that **remembers** the variables from the place it was created — like a **backpack** the function carries with it.

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

`count` lives in the backpack. Only `increment` and `value` can reach it.

A common use is **debounce**: wait until the user stops typing, then search once. It works like an elevator door that waits until people stop coming in before it closes.

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

React hooks (Week 3) are built on closures too.

### 7. Objects and copies

```js
const job = { id: 1, title: "Backend Engineer", salary: { min: 9e6, max: 14e6 } };
const { title, salary: { max } } = job;          // destructuring
const updated = { ...job, title: "Senior Backend Engineer" };   // copy + change (shallow!)
const [first, ...rest] = ["python", "sql", "docker"];
```

- **Destructuring** takes values out of an object or array into variables.
- `{ ...job }` (spread) makes a copy. It is a **shallow** copy: the outer box is new, but boxes inside (like `salary`) are still shared. Use `structuredClone(job)` for a full copy.
- `const copy = job` does **not** copy — both names point to the same object (same as Python).

### 8. Modules

```js
// format.js
export function slugify(title) { ... }
export const CURRENCY = "IDR";

// app.js
import { slugify, CURRENCY } from "./format.js";
```

`export` shares code from a file; `import` uses it in another file. In the browser: `<script type="module" src="app.js"></script>`. Each module has its own variables, so files don't overwrite each other.

## ⚠️ Common mistakes

- `"5" + 1` from a form input gives `"51"` — convert with `Number()` first.
- Checking an empty list with `if (list)` — `[]` is true. Use `list.length === 0`.
- `||` for numeric defaults (breaks on `0`) — use `??`.
- Forgetting `return` in an arrow function that uses `{ }`.
- Changing an object that was passed in — it surprises the caller (and breaks React later).

## 🏆 Best practices

- [ ] `const` by default, `let` when needed, never `var`.
- [ ] Always `===` and `!==`; `??` for defaults; `?.` for data that may be missing.
- [ ] Small functions with clear names; avoid global variables.
- [ ] Template literals instead of joining strings with `+`.
- [ ] One job per module (file).
- [ ] Use Prettier (formatting) and ESLint (catches `==`, unused variables).
- [ ] Learn the browser **Console** and breakpoints — `debugger;` works like Python's `breakpoint()`.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a Python developer why `if (job.salaryMax)` is a bug in JavaScript when a salary can be `0`, and which operator fixes the default value.

## 📐 Design it

CareerPilot's job search box calls the API while the user types. Plan the functions (name, input, output) that: clean up the search text, wait until typing stops (debounce), ignore old answers that arrive late, and remember the last 20 searches.

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

- `normalizeQuery` has no side effects, so it's easy to test.
- The cache and the request counter live in the closure "backpack" — nobody else can change them.
- Each request gets a number. If an older number answers last, its result is ignored — like a waiter ignoring an order you already changed.
- `fetchJobs` and `render` are passed in, so tests can use fake versions.
:::

### 📝 Self-review checklist

- [ ] Late, old answers are ignored
- [ ] Private state is kept in a closure
- [ ] Things the function needs are passed in (easy to test)

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w1/04-js-basics-functions" ai="no-ai" title="Slugs, salary labels, closures and debounce"}
Write small functions: clean up a string into a URL slug, build a salary label for several "missing value" cases, check for blank text without trusting truthiness, make a counter with a closure, and write a debounce function (tested with fake timers) — using modern syntax only.
:::

:::hints
- `slugify`: two regex replaces — non-letters/numbers become `-`, then remove `-` at the start and end.
- `salaryLabel`: compare with `=== null || === undefined` (the tests forbid `==`, so write it out).
- `Math.round(x * 10) / 10` rounds to one decimal; `String(9)` is `"9"` and `String(9.5)` is `"9.5"`.
- `debounce`: keep `timer` outside the returned function.
:::

## ✅ Quick check

:::quiz
What's the difference between `null` and `undefined`?

`undefined` means a value was never set (a missing property or argument). `null` means "empty on purpose". Both trigger `??`.
:::

:::quiz
What does a closure remember?

The variables from the place where the function was created. They stay alive as long as the function exists.
:::

## 📚 Keep learning

- [MDN: JavaScript Guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide)
- [javascript.info — The Modern JavaScript Tutorial](https://javascript.info/)
- [MDN: Closures](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Closures)
