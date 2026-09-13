---
title: "Controlled Inputs & Forms"
summary: Build forms React can reason about — controlled inputs of every type, one state object per form, accessible validation, typed payloads, refs for focus, and when uncontrolled inputs are better.
type: lesson
source: core
sourceRef: "M3 · W3 · L5"
roles: { be: optional, fe: core, fs: core, ai: recommended, ops: none }
durationMinutes: 180
tags: [react, forms, controlled-components, validation, refs]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Controlled vs uncontrolled inputs
- Controlling every input type: text, number, select, checkbox, radio, textarea
- One state object for a form, with a typed generic setter
- Converting input strings into a typed payload (numbers, `null`)
- Validation on submit, accessible error messages and focusing the first error
- Refs with `useRef` for focus and DOM access
- Resetting forms, disabling submit while submitting
- A preview of React 19 form actions and React Hook Form + Zod (Week 5)

## 🧠 The big idea

A controlled input is a **puppet whose strings React holds**: what you see in the box is always exactly what's in state, and every keystroke goes through your code first. That makes validation, formatting and conditional fields simple — because the truth lives in one place.

## ❓ Why does this exist?

Forms are where users give your API data. You need live character counters, dependent fields ("show salary only if disclosed"), validation before hitting Flask, and a clean typed payload. When React controls the values, all of these are just render logic.

## 💥 What happens if we DON'T?

```tsx
<input type="number" onChange={(e) => setSalary(e.target.value)} />   // salary is "9000000" (a string!)
<input value={role} />                                                 // read-only: no onChange → can't type
<input value={maybeUndefined} onChange={…} />                          // "changing an uncontrolled input to be controlled" warning
```

And payloads like `{ salary_min: "", salary_max: "9000000" }` make your Flask validation return 422 or, worse, store wrong data.

## 📖 How it works, step by step

### 1. Controlled inputs

```tsx
const [role, setRole] = useState("");
<input id="role" value={role} onChange={(e) => setRole(e.target.value)} />
```

| Input | Value prop | Read from |
|---|---|---|
| text, email, search, textarea | `value={string}` | `e.target.value` |
| number | `value={string}` (keep as string while typing) | `e.target.value` → convert on submit |
| select | `value={string}` on `<select>` | `e.target.value` |
| checkbox | `checked={boolean}` | `e.target.checked` |
| radio group | `checked={value === option}` | `e.target.value` |

Initial values must never be `undefined` (use `""`, `false`).

### 2. One state object + a generic setter

```tsx
type Values = { companyId: string; role: string; salaryMin: string; salaryMax: string; remote: boolean; notes: string };
const EMPTY: Values = { companyId: "", role: "", salaryMin: "", salaryMax: "", remote: false, notes: "" };

const [values, setValues] = useState<Values>(EMPTY);
const set = <K extends keyof Values>(key: K, value: Values[K]) => setValues((prev) => ({ ...prev, [key]: value }));

<input value={values.role} onChange={(e) => set("role", e.target.value)} />
<input type="checkbox" checked={values.remote} onChange={(e) => set("remote", e.target.checked)} />
```

The generic `K extends keyof Values` (Week 2!) makes `set("remote", "yes")` a compile error.

### 3. From form values to a typed payload

Keep **form values** (strings, as typed) separate from the **domain payload** (numbers, nulls):

```tsx
const toNumber = (value: string) => (value.trim() === "" ? null : Number(value));

const payload: ApplicationPayload = {
  companyId: Number(values.companyId),
  role: values.role.trim(),
  salaryMin: toNumber(values.salaryMin),
  salaryMax: toNumber(values.salaryMax),
  remote: values.remote,
  notes: values.notes,
};
```

### 4. Validation with accessible errors

```tsx
function validate(values: Values): Partial<Record<"company" | "role" | "salaryMax", string>> {
  const errors: Partial<Record<…>> = {};
  if (values.companyId === "") errors.company = "Choose a company";
  if (values.role.trim() === "") errors.role = "Role is required";
  const min = toNumber(values.salaryMin), max = toNumber(values.salaryMax);
  if (min !== null && max !== null && min > max) errors.salaryMax = "Maximum must be at least the minimum";
  return errors;
}
```

```tsx
<input
  id="role"
  aria-invalid={errors.role ? true : undefined}
  aria-describedby={errors.role ? "role-error" : undefined}
  …
/>
{errors.role && <p id="role-error">{errors.role}</p>}
```

When to validate: **on submit** first; then optionally re-validate a field on blur/change after it has shown an error. Don't yell at users while they're still typing the first character. And remember: **client validation is UX; the Flask API's validation is security** — keep both.

### 5. Refs and focus

```tsx
const roleRef = useRef<HTMLInputElement>(null);
<input ref={roleRef} … />
roleRef.current?.focus();       // after validation fails
```

Refs hold values that don't trigger re-renders (DOM nodes, timers). Don't read or write `ref.current` during render.

### 6. Submitting

```tsx
async function handleSubmit(event: FormEvent<HTMLFormElement>) {
  event.preventDefault();
  const found = validate(values);
  setErrors(found);
  if (Object.keys(found).length > 0) return focusFirstError(found);
  setSubmitting(true);
  try {
    await onSubmit(toPayload(values));
    setValues(EMPTY);
  } catch (error) {
    setServerError(messageFor(error));    // map API 422 field errors back to fields (Week 5)
  } finally {
    setSubmitting(false);
  }
}

<button type="submit" disabled={submitting}>{submitting ? "Saving…" : "Save application"}</button>
```

Use `noValidate` on the `<form>` if you render your own messages (so native bubbles don't duplicate them), but keep `type="email"`, `required`, `min` for mobile keyboards and semantics.

### 7. Uncontrolled inputs (sometimes better)

```tsx
<form onSubmit={(e) => { e.preventDefault(); const data = new FormData(e.currentTarget); … }}>
  <input name="role" defaultValue="" />
</form>
```

The DOM keeps the value; you read it on submit. Fine for simple forms without live behavior. React 19 **form actions** (`<form action={serverAction}>`, `useActionState`) build on this with progressive enhancement — Week 5 covers them together with React Hook Form + Zod.

## ⚖️ Trade-offs

| Choice | ✅ | ❌ |
|---|---|---|
| Controlled | live validation, dependent fields, single source of truth | re-render per keystroke (fine for normal forms), more code |
| Uncontrolled + FormData | little code, works with native forms/actions | harder to do live behavior |
| Hand-rolled validation | no dependencies, full control | repetitive at scale → schema libraries |
| React Hook Form + Zod | less boilerplate, shared schemas | libraries to learn (Week 5) |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ Controlled for forms with live counters, conditional fields, formatting, or instant feedback.
- ✅ Uncontrolled/`FormData` for simple forms and server actions.
- 🚫 Don't convert `type="number"` values to numbers on every keystroke (you'll fight empty and partial input) — convert on submit.

## 🏆 Best practices

- [ ] Every input has a label; errors are linked with `aria-describedby` + `aria-invalid`; focus the first error.
- [ ] Initialize controlled values with `""`/`false`, never `undefined`.
- [ ] Keep form values (strings) separate from the typed payload; convert and trim on submit.
- [ ] Validate on submit first; keep server-side validation as the source of truth.
- [ ] Disable submit and show progress while submitting; prevent double submits.
- [ ] Reset the form (or navigate away) after success; keep values after failures.
- [ ] Use the right input types and `autoComplete` attributes.

## 🏭 How it's used in industry

- Most production React apps use React Hook Form (performance, less code) with Zod schemas shared with API clients.
- Next.js apps increasingly use Server Actions for mutations with `useActionState` for pending/error states.
- Form accessibility is one of the most common audit findings — labels, errors and focus are checked first.

## ⚠️ Common mistakes

- `value` without `onChange` (read-only input).
- Using the string `"false"` or `"on"` from a checkbox instead of `checked`.
- `Number("")` → `0` silently turning empty salaries into zero.
- Clearing the form when the API returned an error.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a backend teammate why the frontend validates a salary range even though the Flask API already does — and why the API must still validate.

## 📐 Design it

Design the **"Add note with reminder"** form for an application: note text (required, max 1000), an optional reminder toggle that reveals a date and time input (required when the toggle is on, must be in the future), and a priority radio group (low/normal/high, default normal). Describe the form values type, the payload type, validation rules, and the rendered accessibility attributes.

:::quiz
Show a possible design

```ts
type NoteValues = { text: string; remind: boolean; remindAt: string; priority: "low" | "normal" | "high" };  // remindAt: "2026-09-20T09:00" from datetime-local
type NotePayload = { text: string; priority: NoteValues["priority"]; remindAt: string | null };                // ISO string in UTC or null

function validate(v: NoteValues, now: Date) {
  const errors: Partial<Record<"text" | "remindAt", string>> = {};
  if (v.text.trim() === "") errors.text = "Write a note";
  else if (v.text.length > 1000) errors.text = "Keep it under 1000 characters";
  if (v.remind) {
    if (v.remindAt === "") errors.remindAt = "Pick a reminder time";
    else if (new Date(v.remindAt) <= now) errors.remindAt = "Reminder must be in the future";
  }
  return errors;
}

const toPayload = (v: NoteValues): NotePayload => ({
  text: v.text.trim(),
  priority: v.priority,
  remindAt: v.remind ? new Date(v.remindAt).toISOString() : null,   // hidden field ignored when toggle is off
});
```

Markup notes:
- `<textarea id="note" maxLength={1000} aria-describedby="note-count note-error">` with a live counter `<p id="note-count">120/1000</p>`.
- Toggle: `<input type="checkbox" id="remind" aria-controls="reminder-fields">`; the date field is rendered only when checked (and its error cleared when unchecked).
- `<input type="datetime-local" id="remindAt" min={nowLocalString}>` with `aria-invalid`/`aria-describedby` on error.
- Priority: `<fieldset><legend>Priority</legend>` with three native radios `checked={values.priority === "high"}`.
- `validate` receives `now` as a parameter → testable without mocking the clock.
:::

### 📝 Self-review checklist

- [ ] Values vs payload types separated
- [ ] Conditional field validated only when shown
- [ ] Time logic testable (injected `now`)
- [ ] Accessible grouping and error links

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w3/05-controlled-inputs" ai="no-ai" title="A controlled application form"}
Build a fully controlled form with a select, text, number, checkbox and textarea inputs, a live character counter, accessible validation that focuses the first error, a typed payload with number conversion, and a reset after success — plus a controlled search box whose Clear button refocuses the input with a ref.
:::

:::hints
- One `values` object + `set(key, value)` helper keeps handlers tiny.
- Store refs in an object keyed by field so you can focus `refs[firstInvalid]`.
- The `<option>` `value` is always a string — convert with `Number()` in the payload.
:::

## ✅ Quick check

:::quiz
What makes an input "controlled"?

Its current value comes from React state via `value` (or `checked`) and changes only through an `onChange` handler that updates that state.
:::

:::quiz
Why keep number inputs as strings in form state?

While typing, inputs can be empty or partial; converting on every keystroke turns empty into 0 or NaN. Convert once on submit.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Controlled input | Input terkontrol (nilainya dari state) |
| Uncontrolled input | Input tidak terkontrol (nilainya di DOM) |
| Ref | Referensi ke elemen/nilai tanpa memicu render |
| Payload | Data yang dikirim ke API |
| Validation | Validasi |

## 📚 Keep learning

- [React docs: Reacting to Input with State](https://react.dev/learn/reacting-to-input-with-state)
- [React docs: `<input>` (controlled inputs)](https://react.dev/reference/react-dom/components/input)
- [React docs: Manipulating the DOM with Refs](https://react.dev/learn/manipulating-the-dom-with-refs)
