---
title: "Controlled Inputs & Forms"
summary: Build forms React can manage — controlled inputs of every type, one state object per form, validation users can find, converting input text into clean data, refs for focus, and when uncontrolled inputs are better.
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
- Controlling text, number, select, checkbox, radio and textarea
- One state object for the whole form
- Turning form text into clean data for your API (numbers, `null`)
- Validation with accessible error messages
- `useRef` to move focus
- Submitting safely (no double submits)

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Controlled input** | An input whose value comes from React state | Input yang dikendalikan state |
| **Uncontrolled input** | An input that keeps its own value in the browser; you read it on submit | Input yang menyimpan nilainya sendiri |
| **`onChange`** | The event that fires on every change (each key press) | Saat nilai berubah |
| **Payload** | The clean data you send to the API | Data kiriman |
| **Validation** | Checking the values are correct before sending | Pengecekan data |
| **Ref (`useRef`)** | A box that holds something (like a DOM element) without redrawing | Referensi |
| **`FormData`** | A browser object that reads all values of a form at once | Pembaca data form |

## 🧠 The big idea

A controlled input is like a **shop display that only the shopkeeper arranges**: what you see in the box is always exactly what's in React state, and every key press goes through your code first. Because the truth lives in one place, validation, formatting and "show this field only if…" become simple.

## ❓ Why it matters

Forms are where users give data to your API. You often need a live character counter, fields that appear depending on other fields, checks before calling Flask, and clean typed data.

Common problems when forms are careless:

```tsx
<input type="number" onChange={(e) => setSalary(e.target.value)} />   // salary is "9000000" (a string!)
<input value={role} />                                                 // read-only: no onChange → can't type
<input value={maybeUndefined} onChange={…} />                          // "changing an uncontrolled input to be controlled" warning
```

- Even a number input gives you **text**.
- `value` without `onChange` makes an input you can't type in.
- Starting with `undefined` causes a React warning.

And sending `{ salary_min: "", salary_max: "9000000" }` makes your Flask API return 422 — or save wrong data.

## 📖 Step by step

### 1. Controlled inputs

```tsx
const [role, setRole] = useState("");
<input id="role" value={role} onChange={(e) => setRole(e.target.value)} />
```

The loop: you type → `onChange` → `setRole` → React redraws → the box shows the new `role`.

| Input | Set its value with | Read the new value from |
|---|---|---|
| text, email, search, textarea | `value={string}` | `e.target.value` |
| number | `value={string}` (keep it as text while typing) | `e.target.value` → convert on submit |
| select | `value={string}` on `<select>` | `e.target.value` |
| checkbox | `checked={boolean}` | `e.target.checked` |
| radio group | `checked={value === option}` | `e.target.value` |

Start with `""` or `false`, never `undefined`.

### 2. One state object for the form

```tsx
type Values = { companyId: string; role: string; salaryMin: string; salaryMax: string; remote: boolean; notes: string };
const EMPTY: Values = { companyId: "", role: "", salaryMin: "", salaryMax: "", remote: false, notes: "" };

const [values, setValues] = useState<Values>(EMPTY);
const set = <K extends keyof Values>(key: K, value: Values[K]) => setValues((prev) => ({ ...prev, [key]: value }));

<input value={values.role} onChange={(e) => set("role", e.target.value)} />
<input type="checkbox" checked={values.remote} onChange={(e) => set("remote", e.target.checked)} />
```

Like one **registration form** with all fields, instead of loose notes. The small `set` helper uses a generic (Week 2), so `set("remote", "yes")` is a type error.

### 3. From form values to clean data

Keep two separate shapes — like a **draft** you're still writing and the **final letter** you send:
- **Form values**: text, exactly as typed.
- **Payload**: cleaned data with real numbers and `null`.

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

`toNumber` turns an empty field into `null`, not `0` (`Number("")` is `0`!).

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

- Check **when the user submits** first. Don't show errors while they're still typing the first letter.
- After an error is shown, you can re-check that field as they fix it.
- Frontend checks are for **a nice experience**. The Flask API's checks are for **safety**. Keep both — like a shop assistant who helps you fill the form, and the bank teller who checks it again.

### 5. Refs and focus

```tsx
const roleRef = useRef<HTMLInputElement>(null);
<input ref={roleRef} … />
roleRef.current?.focus();       // after validation fails
```

A ref is like a **bookmark** to a real element: you can jump to it (focus it) without redrawing the page. Don't read or change `ref.current` while rendering — only in event handlers or effects.

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

- Disable the button while saving, so people can't submit twice (like double-tapping "Pay").
- Clear the form only after **success**. If the API fails, keep what the user typed.
- Add `noValidate` to the `<form>` if you show your own messages, but keep `type="email"`, `required` and `min` for mobile keyboards.

### 7. Uncontrolled inputs (sometimes simpler)

```tsx
<form onSubmit={(e) => { e.preventDefault(); const data = new FormData(e.currentTarget); … }}>
  <input name="role" defaultValue="" />
</form>
```

The browser keeps the value, and you read everything at once on submit with `FormData`. Good for simple forms with no live behavior. React 19 **form actions** build on this — Week 5 covers them with React Hook Form + Zod.

## ⚠️ Common mistakes

- `value` without `onChange` (you can't type).
- Reading `"on"` from a checkbox instead of using `checked`.
- `Number("")` → `0`, silently turning an empty salary into zero.
- Converting number inputs on every key press (empty and half-typed values break) — convert on submit.
- Clearing the form when the API returned an error.
- No labels, or errors not connected to their fields.

## 🏆 Best practices

- [ ] Every input has a label; errors use `aria-describedby` + `aria-invalid`; focus the first error.
- [ ] Start controlled values with `""` / `false`, never `undefined`.
- [ ] Keep form values (text) separate from the payload; trim and convert on submit.
- [ ] Validate on submit first; the server's validation is still the final check.
- [ ] Disable submit and show progress while saving.
- [ ] Reset after success; keep values after failure.
- [ ] Use the right input `type` and `autoComplete`.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a backend teammate, with the shop-assistant-and-bank-teller idea, why the frontend checks the salary range even though the Flask API already does — and why the API must still check it.

## 📐 Design it

Design an **"Add note with reminder"** form: note text (required, max 1000 characters), a "remind me" toggle that shows a date-time field (required when on, must be in the future), and a priority choice (low / normal / high, default normal). Describe the form values type, the payload type, the checks, and the accessibility attributes.

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

- The note: `<textarea id="note" maxLength={1000} aria-describedby="note-count note-error">` with a live counter `<p id="note-count">120/1000</p>`.
- The toggle: `<input type="checkbox" id="remind" aria-controls="reminder-fields">`. The date field only appears when it's on (and its error is cleared when it's turned off).
- The date: `<input type="datetime-local" id="remindAt" min={nowLocalString}>`, with `aria-invalid` and `aria-describedby` when there's an error.
- Priority: `<fieldset><legend>Priority</legend>` with three normal radio buttons.
- `validate` receives `now` as a parameter, so tests don't need to fake the clock.
:::

### 📝 Self-review checklist

- [ ] Form values and payload are separate types
- [ ] The extra field is checked only when it's shown
- [ ] Time checks are testable (`now` passed in)
- [ ] Grouped radios and connected errors

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w3/05-controlled-inputs" ai="no-ai" title="A controlled application form"}
Build a fully controlled form with select, text, number, checkbox and textarea inputs, a live character counter, accessible validation that focuses the first error, a typed payload with number conversion, and a reset after success — plus a controlled search box whose Clear button puts focus back in the input using a ref.
:::

:::hints
- One `values` object + a `set(key, value)` helper keeps the handlers tiny.
- Keep refs in an object by field name, so you can focus `refs[firstInvalid]`.
- An `<option>` value is always text — convert with `Number()` in the payload.
:::

## ✅ Quick check

:::quiz
What makes an input "controlled"?

Its value comes from React state through `value` (or `checked`), and it changes only through an `onChange` handler that updates that state.
:::

:::quiz
Why keep number inputs as text in the form state?

While typing, the field can be empty or half-written. Converting on every key press turns empty into 0 or NaN. Convert once, on submit.
:::

## 📚 Keep learning

- [React docs: Reacting to Input with State](https://react.dev/learn/reacting-to-input-with-state)
- [React docs: `<input>` (controlled inputs)](https://react.dev/reference/react-dom/components/input)
- [React docs: Manipulating the DOM with Refs](https://react.dev/learn/manipulating-the-dom-with-refs)
