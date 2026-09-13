# M4 · W1 · 08 — Accessible Tabs and Form Errors

> 🚫🤖 **No-AI** · ⏱️ ~75 min · edit **`a11y-widgets.js`**

The tests use Testing Library queries like `getByRole("tab", { name: "Saved" })` — they find elements the way assistive technology does. If your markup isn't accessible, the tests can't find it.

## 1. `createTabs(root, tabs)`
`tabs` is `[{ id, label, content }]`. Build the [ARIA tabs pattern](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/):
- a container with `role="tablist"`; each tab is a `<button role="tab" id="tab-{id}" aria-controls="panel-{id}">`
- each panel is `<div role="tabpanel" id="panel-{id}" aria-labelledby="tab-{id}">` with the content as text
- the first tab starts selected: `aria-selected="true"`, `tabindex="0"`; others `aria-selected="false"`, `tabindex="-1"` (**roving tabindex**); non-selected panels have the `hidden` attribute
- clicking a tab selects it; with focus on a tab, `ArrowRight`/`ArrowLeft` move selection **and focus** to the next/previous tab (wrapping around), `Home`/`End` go to first/last

## 2. `validateSignup(form)`
The form (provided in the test) has `#email` and `#password` inputs, each followed by an empty `<p id="{field}-error">`. Return `true` if valid. Otherwise:
- set `aria-invalid="true"` on invalid inputs (and remove it from valid ones)
- link each invalid input to its message with `aria-describedby="{field}-error"` and put the message text in that `<p>` (`"Enter a valid email address"`, `"Password must be at least 8 characters"`); clear messages of valid fields
- move focus to the **first** invalid field
- email is valid if it matches `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`

```bash
cd exercises/web
npx vitest run m4/w1/08-accessibility
```
