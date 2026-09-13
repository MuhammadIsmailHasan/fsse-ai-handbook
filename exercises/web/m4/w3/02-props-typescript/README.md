# M4 · W3 · 02 — Typed Props: Building a Small UI Kit

> 🚫🤖 **No-AI** · ⏱️ ~60 min · edit **`ui-kit.tsx`**

| Component | Props and behavior |
|---|---|
| `Button` | `interface ButtonProps extends ComponentPropsWithoutRef<"button">` + `variant?: "primary" \| "secondary" \| "danger"` (default `"primary"`) + `loading?: boolean`. Renders a `<button>` with **`type="button"` by default** (callers may pass `type="submit"`), forwards every other prop (`onClick`, `aria-*`, `disabled`…), adds `data-variant={variant}`. When `loading`: disabled, `aria-busy="true"`, and the text `Loading…` instead of `children` |
| `Avatar` | `{ name: string; src?: string; size?: number }` (size default `40`). With `src`: `<img src alt={name} width height>`; without: `<span role="img" aria-label={name}>` showing **initials** (first letter of the first two words, upper-case: `"siti rahma"` → `"SR"`, `"Budi"` → `"B"`) |
| `StatusBadge` | `{ status: Status }` where `type Status = "saved" \| "applied" \| "interview" \| "offer" \| "rejected"`; renders `<span data-status={status}>` with the label from `STATUS_LABELS` (e.g. `"Interview"`) |
| `Card` | `{ title: string; actions?: ReactNode; children: ReactNode }` — `<section aria-labelledby>` whose `<h2>` has a generated id (use React's `useId`); `actions` render in a `<div>` next to the title only when provided |

Types are checked too: an unknown `variant` or `status`, or a `Card` without `children`, must not compile.

```bash
cd exercises/web
npx vitest run m4/w3/02-props-typescript
```
