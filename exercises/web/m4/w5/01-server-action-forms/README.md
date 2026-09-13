# M4 · W5 · 01 — Forms with Server Actions, `useActionState` and Zod

> 🚫🤖 **No-AI** · ⏱️ ~90 min

Build the "New application" form so it works **without client-side JavaScript** (progressive enhancement), validates on the server with **Zod**, and maps the Flask API's `422` field errors back onto the form.

Provided: `lib/api.ts` with `createApplication(input)` which calls Flask and throws `ApiError(status, code, fields?)`.

## 1. `app/applications/new/schema.ts`
`applicationSchema` (Zod 4) for the raw `FormData` values:
- `company_id`: string → positive integer (`z.coerce.number().int().positive()`, message `"Choose a company"`)
- `role`: trimmed string, 1–200 chars (`"Role is required"`)
- `salary_min`, `salary_max`: optional — empty string → `undefined`, otherwise a non-negative integer
- refinement: when both salaries exist, `salary_min <= salary_max` → error on `salary_max`: `"Maximum must be at least the minimum"`

## 2. `app/applications/new/actions.ts` — a `"use server"` file
`export type FormState = { message: string | null; fieldErrors: Partial<Record<"company_id" | "role" | "salary_min" | "salary_max", string[]>> }`

`createApplicationAction(previousState: FormState, formData: FormData): Promise<FormState>`:
1. validate with `safeParse`; on failure return `{ message: "Please fix the errors below", fieldErrors: z.flattenError(error).fieldErrors }`
2. call `createApplication(data)`; on `ApiError` with status `422` return its `fields` as `fieldErrors` with the same message; `409` → `{ message: "You already have an application for this role", fieldErrors: {} }`; anything else → rethrow
3. on success: `updateTag("applications")` then `redirect("/applications/{id}")` (both from Next.js)

## 3. `app/applications/new/application-form.tsx` — Client Component
- `useActionState(createApplicationAction, { message: null, fieldErrors: {} })`
- `<form action={formAction}>` with named inputs: a `<select name="company_id">` (label `Company`, options from the `companies` prop plus `Choose a company` with value `""`), `role`, `salary_min`, `salary_max` (labels `Role`, `Minimum salary`, `Maximum salary`)
- each field with errors gets `aria-invalid` and `aria-describedby="{name}-error"` and a `<p id="{name}-error">` with the **first** message
- `state.message` in `<p role="alert">`
- a separate `SubmitButton` component using `useFormStatus()`: text `Saving…` and `disabled` while pending, otherwise `Save application`

```bash
cd exercises/web
npx vitest run m4/w5/01-server-action-forms
```
