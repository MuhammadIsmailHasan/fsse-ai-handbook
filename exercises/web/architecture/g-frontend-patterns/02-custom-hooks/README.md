# Architecture G · 02 — Custom hooks as reusable behavior

> 🚫🤖 **No-AI** · ⏱️ ~75 min

Hooks let components **share behavior, not markup**. Build three hooks that component libraries (Radix, Headless UI, shadcn/ui) are built on — keeping the pure logic separate so it's testable without React.

## 1. `pagination.ts`
- `getPageItems({ page, totalPages, siblings = 1 })` → an array of page numbers and `"…"`:
  - always the first and last page, the current page, and `siblings` pages on each side
  - a gap of **one** page is shown as the page itself, not `"…"`
  - `totalPages <= 0` → `[]`; `page` is clamped into range
  - examples (page, totalPages): `(1, 1)` → `[1]` · `(5, 10)` → `[1, "…", 4, 5, 6, "…", 10]` · `(3, 10)` → `[1, 2, 3, 4, "…", 10]` · with `siblings: 2`, `(1, 5)` → `[1, 2, 3, 4, 5]` (the gap is only page 4, so it is shown)
- `usePagination({ total, pageSize, page, onPageChange })` → `{ totalPages, items, hasPrevious, hasNext, previous(), next(), goTo(n) }`; `goTo` clamps and doesn't call `onPageChange` if the page wouldn't change

## 2. `use-disclosure.ts`
`useDisclosure(initial = false)` → `{ isOpen, open, close, toggle }` — the three functions are **referentially stable** across renders.

## 3. `use-controllable-state.ts`
The pattern behind `value`/`defaultValue` props:
`useControllableState<T>({ value, defaultValue, onChange })` → `[current, setValue]`
- **controlled** (`value !== undefined`): returns `value`; `setValue(next)` only calls `onChange(next)`
- **uncontrolled**: keeps its own state starting at `defaultValue`; `setValue` updates it and calls `onChange`
- `setValue` accepts a value or an updater function `(prev) => next`
- `onChange` is **not** called when the value doesn't change (`Object.is`)
- `setValue` is stable across renders even if `onChange` is a new inline function each time

```bash
cd exercises/web
npx vitest run architecture/g-frontend-patterns/02-custom-hooks
```
