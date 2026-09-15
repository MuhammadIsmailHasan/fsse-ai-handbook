---
title: "Props & TypeScript Interfaces"
summary: Design how components are used — typed props, default values, children and slots, accepting normal HTML attributes, callback props, and simple rules that keep components easy to use.
type: lesson
source: core
sourceRef: "M3 · W3 · L2"
roles: { be: optional, fe: core, fs: core, ai: recommended, ops: none }
durationMinutes: 150
tags: [react, props, typescript, component-api]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Typing props, optional props and default values
- `children` and "slots" for flexible content
- Letting your `Button` accept every normal `<button>` attribute
- Callback props like `onToggle`
- `useId` for connecting labels and inputs
- Rules for props that are easy to use and hard to misuse

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Props** | The inputs a component receives from its parent | Input komponen |
| **Default value** | The value used when the parent doesn't pass a prop | Nilai bawaan |
| **`ReactNode`** | The type for "anything React can show": text, elements, lists, `null` | Apa pun yang bisa ditampilkan |
| **Slot** | A prop that accepts content, like `actions={<Button />}` | Tempat konten |
| **Rest / spread (`...rest`)** | Collect the remaining props and pass them on | Sisa props diteruskan |
| **Callback prop** | A function prop the child calls: `onToggle` | Props berupa fungsi |
| **`useId`** | A React hook that makes a unique id for labels and inputs | Pembuat id unik |

## 🧠 The big idea

Props are a component's **contract**, like the menu and order form at a coffee shop: it lists what you can order (size, sugar level) and rejects nonsense ("extra large small"). TypeScript makes the editor check this contract every time someone uses the component.

## ❓ Why it matters

Components are used by many people in many places. Without typed props, mistakes only show up in the browser:

```tsx
function Button(props: any) {
  return <button className={props.big ? "text-lg" : ""} onClick={props.click}>{props.text}</button>;
}
<Button text="Save" onClick={save} />         // onClick ignored (prop is called click) — silent bug
<Button text="Delete" big small danger />     // contradictory booleans
<Button text="Submit" type="submit" />        // type isn't forwarded → the form never submits
```

- `onClick` is silently ignored (the prop is called `click`).
- `big small danger` together makes no sense, but it's allowed.
- `type="submit"` is thrown away, so the form never submits.

With typed props, autocomplete shows the options and these mistakes become red lines.

## 📖 Step by step

### 1. Typed props and defaults

```tsx
interface StatusBadgeProps {
  status: Status;                    // required
  size?: "sm" | "md";                // optional
}

export function StatusBadge({ status, size = "md" }: StatusBadgeProps) {
  return <span data-status={status} className={size === "sm" ? "text-xs" : "text-sm"}>{STATUS_LABELS[status]}</span>;
}
```

- `status` is required; `size?` is optional.
- `size = "md"` gives a default value right where you unpack the props.

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

- A **slot** is a named place for content, like the photo space on a certificate template.
- `useId()` creates an id that is unique even if the card appears 10 times on a page. Here it connects the section to its heading for screen readers.

### 3. Accepting normal HTML attributes

Your `Button` should work like a real `<button>`, plus your extras — like a **phone case**: the phone still has all its buttons, the case just adds protection and style.

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

- `ComponentPropsWithoutRef<"button">` = "all the props a normal button accepts".
- `...rest` collects everything you didn't unpack (onClick, aria-label…) and passes it to the real button.
- `{...rest}` goes **first**, then your controlled props, so callers can't accidentally break them.
- `type = "button"` by default, because a button inside a form submits the form unless told otherwise.

### 4. Callback props

```tsx
interface SaveButtonProps {
  saved: boolean;
  onToggle: () => void;              // "on" + event, called by the child
  jobTitle: string;
}
```

The parent gives a function; the child calls it when something happens — like giving a waiter your phone number: "call me when the table is ready". Naming habit: props are `onSomething`, the parent's functions are `handleSomething`. To send data back, use arguments: `onSelect: (id: number) => void`.

### 5. Rules for good props

| Instead of | Prefer | Why |
|---|---|---|
| `primary secondary danger` booleans | `variant: "primary" \| "secondary" \| "danger"` | nonsense combinations are impossible |
| `titleText`, `titleColor`, `titleSize` | one `title: ReactNode` slot | fewer props, more flexible |
| 15 optional props | smaller components used together | easier to read |
| `data={job}` when only two fields are used | `title`, `company` | clearer, easier to reuse |
| mixed names like `isOpen` + `setIsOpen` | `open` + `onOpenChange` | same style as popular libraries |

### 6. `ref` is a normal prop

A **ref** gives direct access to the real DOM element (for example, to focus an input). In React 19 you pass it like any other prop:

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

### 7. Server → Client props must be simple data

When a Server Component uses a Client Component, the props travel over the network — like sending a package by courier. Strings, numbers, booleans, plain objects and arrays can be packed. **Functions can't** be sent (except Server Actions — Week 5). So callbacks like `onToggle` are created inside client code.

## ⚠️ Common mistakes

- `props: any` or props without types.
- Not passing `className` and `aria-*` through, so others can't style or label the component.
- A button inside a form without `type="button"` that submits by accident.
- Hardcoded ids in a reusable component, so two copies on one page have the same id.
- Adding a new prop for every design request instead of composing smaller components.

## 🏆 Best practices

- [ ] Type every component's props; export the props type for reusable components.
- [ ] Put defaults where you unpack props; buttons default to `type="button"`.
- [ ] For wrappers around HTML elements, extend `ComponentPropsWithoutRef<"element">` and pass `...rest` on.
- [ ] Use unions for variants, not many booleans.
- [ ] Name callbacks `onX`; send only the data needed.
- [ ] Use `useId` for label and description ids.
- [ ] Keep props simple data when crossing from Server to Client Components.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Using the coffee-shop order form idea, explain why `<Button primary danger small large />` is a worse design than `<Button variant="danger" size="sm" />`.

## 📐 Design it

Design the props for CareerPilot's **`TextField`**, used in every form: a label, hint text, an error message, a required marker, an optional prefix (like "Rp"), and it must still accept every normal input attribute (type, name, autoComplete, onChange…). Write the interface and explain the accessibility attributes.

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

- Normal input props pass straight through (`name`, `type`, `autoComplete`, `onChange`, `value`).
- The `id` is created with `useId` (and removed from the props), so the label always connects, even with many fields.
- `aria-describedby` connects the hint and the error to the input; `aria-invalid` marks the error state.
- The visual "Rp" is `aria-hidden`, so write the currency in the label too ("Maximum salary (Rp)").
:::

### 📝 Self-review checklist

- [ ] Normal input props still work
- [ ] Label, hint and error are connected with ids
- [ ] The error state is available to screen readers

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w3/02-props-typescript" ai="no-ai" title="A small typed UI kit"}
Build `Button` (accepts normal button props, safe `type` default, loading state), `Avatar` (image or initials), `StatusBadge` and a labelled `Card` with optional actions using `useId`. The tests check behavior and prop forwarding; type tests make unknown variants, statuses and missing children fail to compile.
:::

:::hints
- Unpack what you control and collect the rest: `({ variant = "primary", loading = false, type = "button", disabled, children, ...rest })`.
- `aria-busy={loading || undefined}` leaves the attribute out when not loading.
- Initials: `name.trim().split(/\s+/).slice(0, 2).map((w) => w[0]?.toUpperCase() ?? "").join("")`.
:::

## ✅ Quick check

:::quiz
Why extend `ComponentPropsWithoutRef<"button">` for a Button component?

So it accepts every normal button prop (onClick, aria-*, form, name…) with correct types, and you can pass them to the real `<button>`.
:::

:::quiz
Why can't a Server Component pass an `onClick` function to a Client Component?

Props sent from server to browser must be simple data. A normal function can't be sent over the network.
:::

## 📚 Keep learning

- [React docs: Passing Props to a Component](https://react.dev/learn/passing-props-to-a-component)
- [React docs: useId](https://react.dev/reference/react/useId)
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)
