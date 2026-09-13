# M4 · W3 · 05 — Controlled Inputs: An Application Form

> 🚫🤖 **No-AI** · ⏱️ ~90 min · edit **`application-form.tsx`**

`ApplicationForm({ onSubmit, companies })` — every field is **controlled** (`value` + `onChange` from state).

| Field (label) | Element | Rules |
|---|---|---|
| `Company` | `<select>` with a first option `Choose a company` (value `""`) then one option per company (`value={id}`) | required |
| `Role` | text input | required (trimmed) |
| `Minimum salary` / `Maximum salary` | `type="number"` inputs, `min="0"` | optional; if both are filled, minimum ≤ maximum |
| `Remote` | checkbox | — |
| `Notes` | textarea, max 500 characters | shows a live counter `"{n}/500"` |

Submit (`<button type="submit">Save application</button>`):
- `event.preventDefault()`
- validate; for each problem show `<p id="{field}-error">` with the message **and** set `aria-invalid` + `aria-describedby` on that field: `company` → `"Choose a company"`, `role` → `"Role is required"`, `salaryMax` → `"Maximum must be at least the minimum"`. Focus the first invalid field. Errors of fixed fields disappear on the next submit
- if valid, call `onSubmit(payload)` with `{ companyId: number; role: string; salaryMin: number | null; salaryMax: number | null; remote: boolean; notes: string }` (numbers converted from strings, empty → `null`, role trimmed), then **reset** the form

Separately, `SearchBox({ value, onChange })` is a controlled `type="search"` input labelled `Search applications` plus a `Clear` button that appears only when `value` isn't empty and calls `onChange("")` and puts focus back in the input (use a **ref**).

```bash
cd exercises/web
npx vitest run m4/w3/05-controlled-inputs
```
