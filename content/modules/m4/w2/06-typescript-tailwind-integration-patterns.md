---
title: "TypeScript + Tailwind: Integration Patterns"
summary: Combine types and Tailwind classes into reusable building blocks — the cn() helper, typed variant tables, class-variance-authority (CVA), safe class overrides, and where to keep these files.
type: lesson
source: core
sourceRef: "M3 · W2 · L5"
roles: { be: optional, fe: core, fs: core, ai: recommended, ops: none }
durationMinutes: 120
tags: [typescript, tailwind, variants, cva, tailwind-merge, design-system]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Adding classes only when a condition is true (`clsx`)
- Letting the **last** class win when two classes conflict (`tailwind-merge`)
- The `cn()` helper that combines both
- Typed **variants** like `variant: "primary" | "danger"`
- CVA, the library shadcn/ui uses for the same idea
- Where to put tokens, helpers and components

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Variant** | A named style option of a component: primary, danger, small… | Varian tampilan |
| **`clsx`** | A helper that joins class names and skips false ones | Penggabung class |
| **`tailwind-merge`** | A helper that removes conflicting Tailwind classes; the last one wins | Pengatasi bentrok class |
| **`cn()`** | Your small helper = `clsx` + `tailwind-merge` | Helper class |
| **Override** | The caller replaces a default style (`px-8` instead of `px-4`) | Menimpa |
| **Design system** | A shared set of components and styles the whole team uses | Sistem desain |

## 🧠 The big idea

A design system is like a **restaurant menu, not a buffet**. Instead of every developer mixing any classes they like, a component offers a small menu — `variant: "primary" | "danger"`, `size: "sm" | "md"` — and TypeScript refuses orders that aren't on the menu. Tailwind supplies the ingredients; TypeScript guards the menu.

## ❓ Why it matters

After a few weeks with Tailwind, every project asks the same questions:
- "How do I add a class only when the button is disabled?"
- "Why doesn't my `px-8` replace the component's `px-4`?"
- "How do I stop people from using `size='xl'` when it doesn't exist?"

The simple approach fails:

```ts
const classes = "px-4 py-2 bg-indigo-600 " + (danger ? "bg-red-600 " : "") + props.className;
// "px-4 py-2 bg-indigo-600 bg-red-600 px-8" — which bg and px win? Depends on CSS order, not class order!
```

Both `bg-indigo-600` and `bg-red-600` are in the class list. Which one wins depends on their order **inside the generated CSS file**, not their order in your string (remember "which rule wins" from Week 1). So the danger button may stay indigo. And a typo like `variant="dagner"` passes silently.

## 📖 Step by step

### 1. `clsx`: add classes on conditions

```ts
clsx("px-4", isActive && "bg-indigo-50", { "opacity-50": disabled }, ["mt-2", null])
// "px-4 bg-indigo-50 opacity-50 mt-2" (falsy values dropped)
```

Like packing a bag with a checklist: "umbrella — only if it rains". False items are skipped.

### 2. `tailwind-merge`: the last one wins

```ts
twMerge("px-4 py-2 bg-indigo-600", "px-8 bg-red-600")
// "py-2 px-8 bg-red-600"
```

It knows which Tailwind classes do the same job (padding, background color…) and keeps only the **last** one — like updating a delivery address: the newest address replaces the old one.

### 3. `cn()` = both together

```ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

This tiny helper is in almost every modern React + Tailwind project.

### 4. Typed variant tables

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

- The tables contain **complete** class names, so Tailwind can find them.
- `satisfies` checks every variant has a style. Add `"warning"` to the type but forget the style → error.
- `className` goes **last**, so the caller's classes win (`buttonClasses({ className: "px-8" })`).

### 5. CVA: the same idea as a library

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

- `variants` — the menu.
- `compoundVariants` — extra styles for a combination ("danger **and** small").
- `defaultVariants` — what you get when you don't choose.
- `VariantProps` — builds the props type from the menu, so you don't write it twice.

shadcn/ui (Week 5) builds its components exactly like this. Because you wrote the manual version first, CVA won't feel like magic.

### 6. Where files live

```text
src/
├── app.css                     ← @import "tailwindcss" + @theme tokens
├── lib/utils.ts                ← cn()
└── components/ui/
    ├── button.tsx              ← variants + component
    ├── badge.tsx               ← STATUS_BADGE satisfies Record<Status, string>
    └── card.tsx
```

The `Status` type comes from your API model file. If the backend adds a status, the badge table fails to compile until you give it a style.

## ⚠️ Common mistakes

- Joining strings and expecting the last class to win — without `twMerge`, the CSS file order decides.
- Forgetting `satisfies`, so a new variant quietly shows no style.
- Putting `className` first, so the component's defaults beat the caller.
- Building class names from strings (`` `bg-${color}` ``) that Tailwind never creates.
- Making a variant system for a one-off layout — just write the classes.

## 🏆 Best practices

- [ ] One `cn()` helper, used everywhere.
- [ ] Variants as typed unions with complete tables (`satisfies Record<…>`).
- [ ] Put `className` **last** so the caller's classes win.
- [ ] Build prop types from variants (`VariantProps`) instead of writing them twice.
- [ ] Put focus and disabled styles in the base classes, so every variant gets them.
- [ ] Connect domain unions (like `Status`) to style tables, so new values can't be forgotten.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain why `"px-4 px-8"` doesn't always give `px-8` without `tailwind-merge`. Use what you learned about "which rule wins" in Week 1.

## 📐 Design it

Design the typed variant API for CareerPilot's **`Alert`** component: tones success, info, warning and error; `default` or `compact` size; optionally dismissible; an icon per tone. Include the types, the tables and a note about screen reader roles.

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

- Errors use `role="alert"` (read aloud immediately); others use `role="status"` (read politely).
- Icons are `aria-hidden`; the title carries the meaning, so color is not the only signal.
- The dismiss button has a clear name ("Dismiss error: Couldn't save").
- If `onDismiss` is given, the alert is dismissible. There's no separate `dismissible` flag that could disagree with it.
:::

### 📝 Self-review checklist

- [ ] Typed unions with complete tables
- [ ] Caller can override with `cn(…, className)`
- [ ] Roles and non-color signals considered

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w2/06-integration-patterns" ai="no-ai" title="Typed button and badge variants"}
Write `cn()` with clsx + tailwind-merge, complete typed variant and size tables with `satisfies`, and `buttonClasses` / `badgeClasses` helpers where the caller's classes override the defaults. The tests check exact outputs, conflict handling, and that unknown variants don't compile.
:::

:::hints
- `twMerge(clsx(inputs))` — pass the array to clsx.
- Order in `buttonClasses`: base, variant, size, `fullWidth && "w-full"`, `className`.
- `satisfies Record<ButtonVariant, string>` goes after the object.
:::

## ✅ Quick check

:::quiz
What does `tailwind-merge` do that `clsx` doesn't?

It removes conflicting Tailwind classes so the last one wins (`px-4 px-8` → `px-8`). `clsx` only joins classes and skips false ones.
:::

:::quiz
Why must variant tables contain complete class names?

Tailwind only creates CSS for class names it finds written in full in your files.
:::

## 📚 Keep learning

- [tailwind-merge docs](https://github.com/dcastil/tailwind-merge)
- [class-variance-authority docs](https://cva.style/docs)
- [shadcn/ui: Installation (see the cn() helper)](https://ui.shadcn.com/docs/installation)
