---
title: "TypeScript + Tailwind: Integration Patterns"
summary: Combine types and utilities into reusable UI building blocks — the cn() helper, typed variant maps, class-variance-authority, safe class composition, and project structure for a typed design system.
type: lesson
source: core
sourceRef: "M3 · W2 · L5"
roles: { be: optional, fe: core, fs: core, ai: recommended, ops: none }
durationMinutes: 120
tags: [typescript, tailwind, variants, cva, tailwind-merge, design-system]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- `clsx` for conditional classes and `tailwind-merge` for conflict resolution → the `cn()` helper
- Typed **variant maps** with `satisfies Record<Variant, string>`
- `class-variance-authority` (CVA) and `VariantProps`
- Letting callers override styles safely with `className`
- Organizing tokens, helpers and components in a project

## 🧠 The big idea

A design system is a **menu, not a buffet**. Instead of every developer mixing arbitrary classes, components offer a small typed menu — `variant: "primary" | "danger"`, `size: "sm" | "md"` — and TypeScript refuses orders that aren't on it. Tailwind supplies the ingredients; TypeScript enforces the menu.

## ❓ Why does this exist?

After a few weeks of Tailwind, every project reinvents: "how do I add a class only when `disabled`?", "why doesn't my `px-8` override the component's `px-4`?", "how do I stop people using a `size='xl'` that doesn't exist?". These patterns are the standard answers — used by shadcn/ui, which you'll adopt in Week 5.

## 💥 What happens if we DON'T?

```ts
const classes = "px-4 py-2 bg-indigo-600 " + (danger ? "bg-red-600 " : "") + props.className;
// "px-4 py-2 bg-indigo-600 bg-red-600 px-8" — which bg and px win? Depends on CSS order, not class order!
```

In the generated stylesheet, `bg-indigo-600` might come **after** `bg-red-600`, so the danger button stays indigo. And `variant="dagner"` compiles fine in untyped code.

## 📖 How it works, step by step

### 1. `clsx`: conditional class strings

```ts
clsx("px-4", isActive && "bg-indigo-50", { "opacity-50": disabled }, ["mt-2", null])
// "px-4 bg-indigo-50 opacity-50 mt-2" (falsy values dropped)
```

### 2. `tailwind-merge`: later classes win

```ts
twMerge("px-4 py-2 bg-indigo-600", "px-8 bg-red-600")
// "py-2 px-8 bg-red-600"
```

It understands Tailwind's groups (padding, background color, rounded…) and keeps the **last** conflicting class.

### 3. `cn()` = both

```ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

This tiny helper appears in almost every modern React + Tailwind codebase.

### 4. Typed variant maps

```ts
export type ButtonVariant = "primary" | "secondary" | "danger" | "ghost";
export type ButtonSize = "sm" | "md" | "lg";

const VARIANTS = {
  primary: "bg-indigo-600 text-white hover:bg-indigo-500",
  secondary: "bg-white text-slate-900 ring-1 ring-slate-300 hover:bg-slate-50",
  danger: "bg-red-600 text-white hover:bg-red-500",
  ghost: "bg-transparent text-slate-700 hover:bg-slate-100",
} satisfies Record<ButtonVariant, string>;

const SIZES = { sm: "px-2.5 py-1.5 text-sm", md: "px-4 py-2 text-sm", lg: "px-5 py-3 text-base" } satisfies Record<ButtonSize, string>;

export function buttonClasses({ variant = "primary", size = "md", fullWidth = false, className }: {
  variant?: ButtonVariant; size?: ButtonSize; fullWidth?: boolean; className?: string;
} = {}) {
  return cn(BASE, VARIANTS[variant], SIZES[size], fullWidth && "w-full", className);
}
```

- Complete class strings in a lookup table → Tailwind can find them.
- `satisfies` → adding a variant to the union without styling it is a compile error.
- `className` last → callers can override (`buttonClasses({ className: "px-8" })`) and `twMerge` resolves conflicts.

### 5. CVA: the same idea, packaged

```ts
import { cva, type VariantProps } from "class-variance-authority";

export const button = cva("inline-flex items-center justify-center rounded-lg font-semibold", {
  variants: {
    variant: { primary: "bg-indigo-600 text-white", danger: "bg-red-600 text-white" },
    size: { sm: "px-2.5 py-1.5 text-sm", md: "px-4 py-2 text-sm" },
  },
  compoundVariants: [{ variant: "danger", size: "sm", class: "font-bold" }],
  defaultVariants: { variant: "primary", size: "md" },
});

export type ButtonProps = VariantProps<typeof button>;   // { variant?: "primary" | "danger" | null; size?: … }
// usage: cn(button({ variant: "danger" }), className)
```

shadcn/ui components are built exactly like this (Week 5). Knowing the hand-written version means CVA holds no magic.

### 6. Where things live

```text
src/
├── app.css                     ← @import "tailwindcss" + @theme tokens
├── lib/utils.ts                ← cn()
└── components/ui/
    ├── button.tsx              ← variants + component
    ├── badge.tsx               ← STATUS_BADGE satisfies Record<Status, string>
    └── card.tsx
```

Domain types (`Status`) come from the API model module, so a new backend status forces the badge map to be updated.

## ⚖️ Trade-offs

| Choice | ✅ | ❌ |
|---|---|---|
| Hand-written variant maps | zero dependencies, fully typed | reinvent compound variants |
| CVA | standard API, compound variants, `VariantProps` | small dependency |
| `tailwind-merge` | predictable overrides | runtime cost (small); must match your Tailwind version |
| Allowing `className` overrides | flexible | can break design consistency if abused |
| Strict props only (no `className`) | enforced consistency | escape hatches become forks |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ Any component with visual variants used in more than one place.
- ✅ `cn()` wherever classes are conditional or overridable.
- 🚫 Variant systems for one-off layouts — just write the classes.
- 🚫 Building class names from strings (`` `bg-${color}` ``).

## 🏆 Best practices

- [ ] One `cn()` helper, imported everywhere.
- [ ] Variants as typed unions with complete lookup tables (`satisfies Record<…>`).
- [ ] Put `className` **last** so caller overrides win.
- [ ] Derive prop types from variants (`VariantProps`) instead of duplicating them.
- [ ] Keep base classes accessible (focus-visible, disabled states) so every variant inherits them.
- [ ] Tie domain unions (status) to style maps so new values fail to compile until styled.

## 🏭 How it's used in industry

- shadcn/ui, a popular way to build React design systems, uses `cn()` + CVA in every component.
- Design-system teams publish variant APIs mirroring Figma component properties (variant, size, state).
- Code generation tools (v0, etc.) emit the same `cn()`/CVA patterns — you'll recognize them immediately.

## ⚠️ Common mistakes

- Concatenating strings and expecting the last class to win (CSS order decides without `twMerge`).
- Forgetting `satisfies`, so a new variant silently renders unstyled.
- Putting `className` first, so component defaults override the caller.
- Dynamic class names that Tailwind never generates.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain why `"px-4 px-8"` doesn't reliably produce `px-8` without `tailwind-merge`, using what you know about the cascade from Week 1.

## 📐 Design it

Design the typed variant API for CareerPilot's **`Alert`** component used for success, info, warning and error messages, in `default` or `compact` density, optionally dismissible, with an icon per tone. Include types, maps and an accessibility note on roles.

:::quiz
Show a possible design

```ts
export type AlertTone = "success" | "info" | "warning" | "error";
export type AlertDensity = "default" | "compact";

const TONE = {
  success: "border-green-200 bg-green-50 text-green-900",
  info: "border-blue-200 bg-blue-50 text-blue-900",
  warning: "border-amber-200 bg-amber-50 text-amber-900",
  error: "border-red-200 bg-red-50 text-red-900",
} satisfies Record<AlertTone, string>;

const DENSITY = { default: "gap-3 p-4 text-sm", compact: "gap-2 px-3 py-2 text-xs" } satisfies Record<AlertDensity, string>;

const ICON = { success: CheckCircleIcon, info: InfoIcon, warning: TriangleIcon, error: XCircleIcon } satisfies Record<AlertTone, IconComponent>;

// errors interrupt (assertive); others are polite status messages
const ROLE = { success: "status", info: "status", warning: "status", error: "alert" } as const satisfies Record<AlertTone, "status" | "alert">;

export interface AlertProps {
  tone?: AlertTone;
  density?: AlertDensity;
  title: string;
  children?: React.ReactNode;
  onDismiss?: () => void;          // dismissible iff provided — no separate boolean that can disagree
  className?: string;
}

export const alertClasses = ({ tone = "info", density = "default", className }: Pick<AlertProps, "tone" | "density" | "className">) =>
  cn("flex items-start rounded-lg border", TONE[tone], DENSITY[density], className);
```

- Icons are `aria-hidden`; the title carries meaning (color isn't the only signal).
- The dismiss button has an accessible name ("Dismiss error: Couldn't save").
- `onDismiss` presence decides dismissibility — an impossible "dismissible without handler" state can't exist.
:::

### 📝 Self-review checklist

- [ ] Typed unions with complete maps
- [ ] Caller overrides via `cn(…, className)`
- [ ] Roles and non-color signals considered

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w2/06-integration-patterns" ai="no-ai" title="Typed button and badge variants"}
Write `cn()` with clsx + tailwind-merge, complete typed variant and size maps with `satisfies`, and `buttonClasses`/`badgeClasses` helpers where caller classes override defaults. Tests check exact outputs, conflict resolution and that unknown variants don't compile.
:::

:::hints
- `twMerge(clsx(inputs))` — pass the array to clsx.
- Order in `buttonClasses`: base, variant, size, `fullWidth && "w-full"`, `className`.
- `satisfies Record<ButtonVariant, string>` goes after the object literal.
:::

## ✅ Quick check

:::quiz
What does `tailwind-merge` do that `clsx` doesn't?

It removes conflicting Tailwind classes so the last one wins (`px-4 px-8` → `px-8`); clsx only joins conditional classes.
:::

:::quiz
Why must variant maps contain complete class names?

Tailwind generates CSS only for class names it finds literally in the source files.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Variant | Varian tampilan komponen |
| Class merging | Penggabungan kelas (mengatasi konflik) |
| Design system | Sistem desain |
| Lookup table | Tabel pencarian (peta nilai) |
| Override | Menimpa gaya bawaan |

## 📚 Keep learning

- [tailwind-merge docs](https://github.com/dcastil/tailwind-merge)
- [class-variance-authority docs](https://cva.style/docs)
- [shadcn/ui: Installation (see the cn() helper)](https://ui.shadcn.com/docs/installation)
