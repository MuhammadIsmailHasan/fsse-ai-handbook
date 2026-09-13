# M4 · W1 · 04 — JavaScript Basics & Functions

> 🚫🤖 **No-AI** · ⏱️ ~60 min · edit **`basics.js`**

| Function | Behavior |
|---|---|
| `slugify(title)` | `"  Senior Backend Engineer (Python) "` → `"senior-backend-engineer-python"`: lower-case; runs of anything that isn't `a-z`/`0-9` become one `-`; no leading/trailing `-` |
| `salaryLabel(min, max)` | `null`/`undefined` mean "not given". Both → `"Rp 9–14 juta"`; only max → `"Up to Rp 14 juta"`; only min → `"From Rp 9 juta"`; neither → `"Not disclosed"`; equal → `"Rp 10 juta"`. Amounts are in rupiah; show juta with up to 1 decimal (`9500000` → `9.5`). `min > max` → throw a `RangeError` |
| `isBlank(value)` | `true` for `null`, `undefined`, `""` and whitespace-only strings; `false` for everything else — including `0` and `false` (don't rely on truthiness!) |
| `createCounter(start = 0)` | returns `{ increment, decrement, reset, value }` functions sharing a private count (a **closure**); `reset()` goes back to `start` |
| `debounce(fn, waitMs)` | returns a function that calls `fn` with the **latest** arguments only after `waitMs` ms without new calls |

Use `const`/`let` (no `var`) and strict equality (`===`, never `==`) — a test checks.

```bash
cd exercises/web
npx vitest run m4/w1/04-js-basics-functions
```
