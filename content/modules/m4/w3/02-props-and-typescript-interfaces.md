---
title: "Props & TypeScript Interfaces"
summary: Design component APIs — typed props, defaults, optional and children props, extending native HTML props, forwarding attributes, callbacks, and patterns that keep components flexible without becoming confusing.
type: lesson
source: core
sourceRef: "M3 · W3 · L2"
roles: { be: optional, fe: core, fs: core, ai: recommended, ops: none }
durationMinutes: 150
tags: [react, props, typescript, component-api]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Typing props with interfaces/types; required vs optional; defaults with destructuring
- `children` and `ReactNode`, render slots (`actions`, `icon`)
- Extending native element props with `ComponentPropsWithoutRef<"button">` and forwarding the rest
- Callback props (`onToggle`, `onSelect`) and naming conventions
- `useId` for accessible id relationships
- Designing component APIs: variants vs booleans, avoiding prop explosion
- Refs as props in React 19

## 🧠 The big idea

Props are a component's **contract** — like the function signature of an API endpoint you designed in Module 2. A good contract is small, typed, hard to misuse, and consistent. TypeScript turns that contract into something the editor enforces at every usage.

## ❓ Why does this exist?

Components are reused by many people in many places. Without typed props, a teammate passes `variant="dagner"`, forgets a required `title`, or passes a string where a callback belongs — and finds out in the browser. With typed props, autocomplete shows what's possible and mistakes are red lines.

## 💥 What happens if we DON'T?

```tsx
function Button(props: any) {
  return <button className={props.big ? "text-lg" : ""} onClick={props.click}>{props.text}</button>;
}
<Button text="Save" onClick={save} />         // onClick ignored (prop is called click) — silent bug
<Button text="Delete" big small danger />     // contradictory booleans
<Button text="Submit" type="submit" />        // type isn't forwarded → the form never submits
```

## 📖 How it works, step by step

### 1. Typed props with defaults

```tsx
interface StatusBadgeProps {
  status: Status;                    // required
  size?: "sm" | "md";                // optional
}

export function StatusBadge({ status, size = "md" }: StatusBadgeProps) {
  return <span data-status={status} className={size === "sm" ? "text-xs" : "text-sm"}>{STATUS_LABELS[status]}</span>;
}
```

Destructuring defaults are the modern way (the old `defaultProps` is deprecated for function components).

### 2. `children` and slots

```tsx
interface CardProps {
  title: string;
  actions?: React.ReactNode;         // a "slot": any renderable content
  children: React.ReactNode;
}

export function Card({ title, actions, children }: CardProps) {
  const titleId = useId();           // unique, stable, SSR-safe id
  return (
    <section aria-labelledby={titleId}>
      <header className="flex justify-between">
        <h2 id={titleId}>{title}</h2>
        {actions}
      </header>
      {children}
    </section>
  );
}

<Card title="Notes" actions={<Button>Add note</Button>}>…</Card>
```

`ReactNode` accepts elements, strings, numbers, arrays, `null` — anything React can render.

### 3. Extending native props

A `Button` should behave like a `<button>` plus your additions:

```tsx
import type { ComponentPropsWithoutRef } from "react";

interface ButtonProps extends ComponentPropsWithoutRef<"button"> {
  variant?: "primary" | "secondary" | "danger";
  loading?: boolean;
}

export function Button({ variant = "primary", loading = false, type = "button", disabled, className, children, ...rest }: ButtonProps) {
  return (
    <button
      {...rest}                                  // onClick, aria-*, data-*, form, name… all work
      type={type}                                // safe default: not "submit"
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      className={cn(buttonClasses({ variant }), className)}
    >
      {loading ? "Loading…" : children}
    </button>
  );
}
```

Order matters: spread `...rest` **first**, then the props you control, so callers can't accidentally break them (or spread last if overriding should be allowed — decide deliberately).

### 4. Callback props

```tsx
interface SaveButtonProps {
  saved: boolean;
  onToggle: () => void;              // "on" + event, called by the child
  jobTitle: string;
}
```

The parent passes a function; the child calls it. Naming: props `onSomething`, handlers in the parent `handleSomething`. Pass data up with arguments: `onSelect: (id: number) => void`.

### 5. API design guidelines

| Instead of | Prefer | Why |
|---|---|---|
| `primary secondary danger` booleans | `variant: "primary" \| "secondary" \| "danger"` | impossible combinations can't exist |
| `titleText`, `titleColor`, `titleSize` | a `title: ReactNode` slot or composition | fewer props, more flexibility |
| 15 optional props | smaller components composed together | readable call sites |
| `data={job}` for a component that uses two fields | `title`, `company` | clearer dependencies, easier reuse |
| `isOpen` + `setIsOpen` mixed naming | `open` + `onOpenChange` | consistent with popular libraries |

### 6. Refs are props now

React 19 passes `ref` like a normal prop to function components (no `forwardRef` needed):

```tsx
function TextField({ label, ref, ...props }: { label: string; ref?: React.Ref<HTMLInputElement> } & ComponentPropsWithoutRef<"input">) {
  const id = useId();
  return (
    <>
      <label htmlFor={id}>{label}</label>
      <input id={id} ref={ref} {...props} />
    </>
  );
}
```

### 7. Server → Client props must be serializable

When a Server Component renders a Client Component, props cross the network: strings, numbers, booleans, plain objects/arrays, `Date`… are fine; **functions are not** (except Server Actions — Week 5). So `onToggle` callbacks are created inside client code.

## ⚖️ Trade-offs

| Choice | ✅ | ❌ |
|---|---|---|
| Extending native props | behaves like HTML, fewer surprises | larger prop surface to document |
| Strict, minimal props | consistent design | escape hatches needed eventually |
| Slots (`ReactNode`) | flexible layouts | less control over what's rendered |
| Passing whole objects | fewer props | tight coupling to data shape |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ Extend native props for every wrapper around an HTML element (Button, Input, Link).
- ✅ Variants as unions; slots for flexible regions.
- 🚫 Don't forward props blindly to components that aren't DOM elements.
- 🚫 Don't add a prop for every design request — compose instead.

## 🏆 Best practices

- [ ] Type every component's props; export the props type for reusable components.
- [ ] Defaults in destructuring; `type="button"` default for buttons.
- [ ] Extend `ComponentPropsWithoutRef<"element">` and forward `...rest` for DOM wrappers.
- [ ] Use unions for variants, not multiple booleans.
- [ ] Name callbacks `onX`; pass the minimum data needed.
- [ ] Use `useId` for label/description relationships; never hardcode ids in reusable components.
- [ ] Keep props serializable across the Server → Client boundary.

## 🏭 How it's used in industry

- Design-system components (shadcn/ui, Radix, MUI) extend native props and forward refs so they work with forms, tooltips and tests.
- Storybook documents components straight from their TypeScript props.
- API consistency (`open`/`onOpenChange`, `value`/`onChange`, `disabled`) is a common code review topic.

## ⚠️ Common mistakes

- `props: any` or untyped props.
- Forgetting to forward `className`/`aria-*`, so consumers can't style or label the component.
- Default button `type` submitting forms accidentally.
- Duplicate ids when a component is rendered twice.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a teammate why `<Button primary danger small large />` is a worse API than `<Button variant="danger" size="sm" />`.

## 📐 Design it

Design the props for CareerPilot's **`TextField`** used across all forms: label, hint text, error message, required indicator, optional prefix (e.g. "Rp"), and it must still accept every native input prop (type, name, autoComplete, onChange…). Write the interface and describe the rendered markup's accessibility attributes.

:::quiz
Show a possible design

```tsx
interface TextFieldProps extends Omit<ComponentPropsWithoutRef<"input">, "id" | "prefix"> {
  label: string;
  hint?: string;
  error?: string;              // presence = invalid
  prefix?: React.ReactNode;     // e.g. "Rp"
  ref?: React.Ref<HTMLInputElement>;
}

export function TextField({ label, hint, error, prefix, required, ref, className, ...inputProps }: TextFieldProps) {
  const id = useId();
  const hintId = hint ? `${id}-hint` : undefined;
  const errorId = error ? `${id}-error` : undefined;
  return (
    <div className={className}>
      <label htmlFor={id}>
        {label} {required && <span aria-hidden="true">*</span>}
      </label>
      {hint && <p id={hintId}>{hint}</p>}
      <div className="flex">
        {prefix && <span aria-hidden="true">{prefix}</span>}
        <input
          {...inputProps}
          id={id}
          ref={ref}
          required={required}
          aria-invalid={error ? true : undefined}
          aria-describedby={[hintId, errorId].filter(Boolean).join(" ") || undefined}
        />
      </div>
      {error && <p id={errorId}>{error}</p>}
    </div>
  );
}
```

- Native props flow through (`name`, `type`, `autoComplete`, `onChange`, controlled `value`).
- `id` is generated (omitted from props) so labels always connect, even with many fields.
- The visual prefix is `aria-hidden`; mention the currency in the label ("Maximum salary (Rp)") so screen readers get it.
- `required` sets both the native attribute and the visual asterisk.
:::

### 📝 Self-review checklist

- [ ] Native input props preserved
- [ ] Label, hint and error connected with ids
- [ ] Invalid state exposed to assistive tech

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w3/02-props-typescript" ai="no-ai" title="A small typed UI kit"}
Build `Button` (extends native button props, safe `type` default, loading state), `Avatar` (image or initials), `StatusBadge` and a labelled `Card` with optional actions using `useId`. Tests check behavior and forwarding; type tests make unknown variants, statuses and missing children fail to compile.
:::

:::hints
- Destructure what you control and collect the rest: `({ variant = "primary", loading = false, type = "button", disabled, children, ...rest })`.
- `aria-busy={loading || undefined}` omits the attribute when not loading.
- Initials: `name.trim().split(/\s+/).slice(0, 2).map((w) => w[0]?.toUpperCase() ?? "").join("")`.
:::

## ✅ Quick check

:::quiz
Why extend `ComponentPropsWithoutRef<"button">` for a Button component?

So it accepts every native button prop (onClick, aria-*, form, name…) with correct types, and you can forward them to the real `<button>`.
:::

:::quiz
Why can't a Server Component pass an `onClick` function prop to a Client Component?

Props crossing the server/client boundary must be serializable; regular functions can't be sent over the network.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Prop forwarding | Meneruskan props ke elemen di dalamnya |
| Slot | Tempat konten fleksibel dalam komponen |
| Callback prop | Props berupa fungsi yang dipanggil anak |
| Default value | Nilai bawaan |
| Serializable | Bisa diubah menjadi data (JSON-like) untuk dikirim |

## 📚 Keep learning

- [React docs: Passing Props to a Component](https://react.dev/learn/passing-props-to-a-component)
- [React docs: useId](https://react.dev/reference/react/useId)
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)
