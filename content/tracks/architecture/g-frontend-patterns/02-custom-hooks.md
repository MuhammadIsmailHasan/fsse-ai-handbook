---
title: "Custom Hooks as Reusable Behavior"
summary: Share behavior instead of markup — designing custom hooks with clear inputs and outputs, pure logic outside React, stable callbacks, the controlled/uncontrolled pattern, headless components, and testing hooks.
type: lesson
source: original
roles: { be: none, fe: core, fs: recommended, ai: optional, ops: none }
durationMinutes: 90
tags: [architecture, react, hooks, headless-ui, controlled-components, testing]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- When logic deserves a custom hook — and when a plain function is better
- Designing a hook's **API**: inputs, outputs, naming
- Keeping **pure logic** (pagination math, validation) in plain functions the hook calls
- **Stable callbacks** (`useCallback`, refs) and why consumers care
- The **controlled vs uncontrolled** pattern with `useControllableState`
- **Headless** components: behavior in hooks, markup chosen by the caller
- Testing hooks with `renderHook`

## 🧠 The big idea

Components are **LEGO bricks you can see**; hooks are the **motors and gears inside**. The same motor can drive a car, a crane or a windmill — each with a different body. `usePagination` can power a numbered pager, a "Load more" button or a mobile swipe view.

## ❓ Why does this exist?

Before hooks, sharing stateful logic meant higher-order components or render props (wrapper hell). Hooks let you extract "open/close", "pagination", "value with optional control", "debounced search" into functions that any component can call — each call with its **own** state.

## 💥 What happens if we DON'T?

- Five pagers in the app, five slightly different page-number algorithms, three with off-by-one bugs.
- Every dialog re-implements `isOpen/open/close`, and some create new functions each render, breaking memoized children.
- A `Select` component that only works uncontrolled; the form library needs it controlled → a fork.

## 📖 How it works, step by step

### 1. Pure first, hook second

```ts
// pagination.ts — pure, testable with a table of cases
export function getPageItems({ page, totalPages, siblings = 1 }: Options): (number | "…")[] { … }

// the hook adds React concerns only: memoization and callbacks
export function usePagination({ total, pageSize, page, onPageChange }: Args) {
  const totalPages = Math.max(0, Math.ceil(total / pageSize));
  const items = useMemo(() => getPageItems({ page, totalPages }), [page, totalPages]);
  const goTo = (target: number) => { const p = clamp(target, 1, totalPages); if (p !== page) onPageChange(p); };
  return { totalPages, items, hasPrevious: page > 1, hasNext: page < totalPages, previous: () => goTo(page - 1), next: () => goTo(page + 1), goTo };
}
```

If a function doesn't call any hook, it isn't a hook — don't name it `useX`.

### 2. Design the API

| Question | Good answer |
|---|---|
| Name | what it provides: `useDisclosure`, `usePagination`, `useOnlineStatus` — not `useEffectOnce` |
| Inputs | one options object (easy to extend) |
| Outputs | an object for many values; a tuple `[value, setValue]` only for `useState`-like hooks |
| Side effects | explicit and cleaned up |
| Where state lives | inside (uncontrolled), outside (controlled), or both |

### 3. Stable callbacks

```ts
export function useDisclosure(initial = false) {
  const [isOpen, setIsOpen] = useState(initial);
  const open = useCallback(() => setIsOpen(true), []);
  const close = useCallback(() => setIsOpen(false), []);
  const toggle = useCallback(() => setIsOpen((v) => !v), []);
  return { isOpen, open, close, toggle };
}
```

Stable functions can be passed to memoized children and used in effect dependencies without re-running effects. (The React Compiler can memoize automatically — library hooks should still be explicit.)

### 4. Controlled or uncontrolled — support both

```ts
export function useControllableState<T>({ value, defaultValue, onChange }: Options<T>) {
  const [internal, setInternal] = useState(defaultValue);
  const isControlled = value !== undefined;
  const current = isControlled ? value : internal;

  const latest = useRef({ current, isControlled, onChange });
  useEffect(() => { latest.current = { current, isControlled, onChange }; });

  const setValue = useCallback((next: T | ((prev: T) => T)) => {
    const { current: prev, isControlled: controlled, onChange: notify } = latest.current;
    const resolved = typeof next === "function" ? (next as (p: T) => T)(prev) : next;
    if (Object.is(resolved, prev)) return;
    if (!controlled) setInternal(resolved);
    notify?.(resolved);
  }, []);

  return [current, setValue] as const;
}
```

```tsx
<Tabs defaultValue="notes" />                          // uncontrolled: the component remembers
<Tabs value={tab} onValueChange={setTab} />            // controlled: the parent decides (URL, form, store)
```

This is exactly how Radix and shadcn/ui components accept both `value` and `defaultValue`.

### 5. Headless components

```tsx
function Pager({ total, page, onPageChange }: Props) {
  const { items, hasPrevious, hasNext, previous, next, goTo } = usePagination({ total, pageSize: 20, page, onPageChange });
  return (
    <nav aria-label="Pagination">
      <button onClick={previous} disabled={!hasPrevious}>Previous</button>
      {items.map((item, i) => item === "…" ? <span key={`gap-${i}`}>…</span> : (
        <button key={item} aria-current={item === page ? "page" : undefined} onClick={() => goTo(item)}>{item}</button>
      ))}
      <button onClick={next} disabled={!hasNext}>Next</button>
    </nav>
  );
}
```

The hook owns behavior; each product surface owns its markup and styles.

### 6. Testing

```ts
test.each([[{ page: 5, totalPages: 10 }, [1, "…", 4, 5, 6, "…", 10]]])("%o", (input, expected) => {
  expect(getPageItems(input)).toEqual(expected);
});

const { result, rerender } = renderHook((page) => usePagination({ total: 95, pageSize: 20, page, onPageChange }), { initialProps: 1 });
act(() => result.current.next());
```

## ⚖️ Trade-offs

| | ✅ | ❌ |
|---|---|---|
| Custom hook | reuse behavior across different UIs; testable | indirection; hooks rules (top level only) |
| Plain function | simplest, framework-free | no state/effects |
| Headless component library | accessible behavior for free | learning its API; less control |
| Copy-paste | fast today | divergence and bugs tomorrow |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ The same stateful behavior in 2+ components, or complex behavior worth testing alone.
- ✅ Wrapping browser APIs and subscriptions.
- 🚫 Code with no hooks inside — make it a function.
- 🚫 "God hooks" returning 20 values for one page — split them or keep code in the component.

## 🏆 Best practices

- [ ] Extract pure logic into functions; hooks only add React concerns.
- [ ] Name hooks by what they provide; one options object in, an object out.
- [ ] Return stable callbacks; document which values are stable.
- [ ] Support controlled and uncontrolled use for reusable UI state.
- [ ] Keep hooks focused; compose small hooks into bigger ones.
- [ ] Test pure functions with tables of cases and hooks with `renderHook`.
- [ ] Don't return JSX from hooks — return data and handlers.

## 🏭 How it's used in industry

- UI libraries are built as hooks + headless primitives: React Aria (`useButton`, `useTabs`), Downshift, TanStack Table, Radix's internal `useControllableState`.
- Teams keep a `hooks/` folder of shared behavior (`useDebouncedValue`, `useMediaQuery`, `useDisclosure`) with tests.
- Interview exercises often ask candidates to implement `useDebounce`, `usePrevious` or a pagination hook.

## ⚠️ Common mistakes

- Calling hooks conditionally or inside loops.
- Returning new functions each render and breaking memoized consumers.
- Switching a component between controlled and uncontrolled after mount (`value` from `undefined` to a string).
- Hooks that secretly depend on a context without a helpful error when the provider is missing.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain the "motors inside LEGO" analogy, then explain to a teammate why `useControllableState` lets the same `Tabs` be driven by internal state, the URL or a form library.

## 📐 Design it

CareerPilot needs a reusable **multi-select** used for skills (in a form), statuses (in URL filters) and compare jobs (in Zustand). Design `useMultiSelect`: inputs, outputs, controlled/uncontrolled support, keyboard behavior you'd expose, and the pure functions you'd test separately.

:::quiz
Show a possible design

```ts
type UseMultiSelectOptions<T> = {
  options: T[];
  getKey: (option: T) => string;
  value?: string[];                    // controlled (URL, RHF, Zustand)
  defaultValue?: string[];             // uncontrolled
  onValueChange?: (keys: string[]) => void;
  max?: number;                        // e.g. 3 for compare
};

type UseMultiSelectResult<T> = {
  selectedKeys: string[];
  isSelected: (key: string) => boolean;
  toggle: (key: string) => "added" | "removed" | "full";
  clear: () => void;
  getOptionProps: (option: T) => { role: "option"; "aria-selected": boolean; onClick: () => void; id: string };
  getListboxProps: () => { role: "listbox"; "aria-multiselectable": true; onKeyDown: (e: KeyboardEvent) => void };
};
```

- Built on `useControllableState<string[]>`.
- Pure helpers: `toggleKey(keys, key, max)` → `{ keys, result }`, `moveActive(index, key, length)` for Arrow/Home/End — tested with tables.
- Prop getters (`getOptionProps`) keep ARIA wiring consistent while callers choose markup (chips, checkboxes, cards).
:::

### 📝 Self-review checklist

- [ ] Pure logic separated from the hook
- [ ] Controlled and uncontrolled supported
- [ ] Stable, documented outputs

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/architecture/g-frontend-patterns/02-custom-hooks" ai="no-ai" title="Pagination, disclosure and controllable state"}
Write a pure page-number algorithm with a `usePagination` hook on top, a `useDisclosure` hook with stable callbacks, and `useControllableState` supporting controlled and uncontrolled use with updater functions.
:::

:::hints
- Collect the wanted pages in a `Set`, sort them, then insert `"…"` only for gaps bigger than one page.
- Keep the latest props in a ref so `setValue` can stay stable.
- Test your algorithm on paper with page 1, the last page and the middle.
:::

## ✅ Quick check

:::quiz
Two components call `useDisclosure()`. Do they share `isOpen`?

No. Hooks share logic, not state — each call has its own state. To share state, lift it up, use context or a store.
:::

:::quiz
Why should `setValue` from `useControllableState` not change identity when `onChange` changes?

Consumers put it in effect dependencies or pass it to memoized children; a new function each render would re-run effects and re-render children needlessly.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Custom hook | Hook buatan sendiri |
| Headless component | Komponen tanpa tampilan bawaan |
| Controlled component | Komponen yang nilainya dikendalikan induk |
| Uncontrolled component | Komponen yang menyimpan nilainya sendiri |
| Stable reference | Referensi yang tidak berubah antar render |
| Prop getter | Fungsi pemberi props siap pakai |

## 📚 Keep learning

- [React docs: Reusing Logic with Custom Hooks](https://react.dev/learn/reusing-logic-with-custom-hooks)
- [React Aria hooks](https://react-spectrum.adobe.com/react-aria/hooks.html)
- [Kent C. Dodds: Inversion of Control](https://kentcdodds.com/blog/inversion-of-control)
