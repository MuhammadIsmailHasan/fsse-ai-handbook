# M4 · W5 · 07 — React Hook Form + Zod

> 🤖✅ **AI-allowed** (after you've done exercise 01 yourself) · ⏱️ ~90 min

Server Actions + `useActionState` are great for simple forms. For **rich client forms** (instant validation, dynamic rows, many fields) the industry standard is **React Hook Form (RHF) + Zod**, with the **same schema** re-checked on the server.

## `profile-schema.ts`
`profileSchema` (Zod 4):
- `name`: trimmed, min 2 → `"Name must be at least 2 characters"`
- `email`: `z.email("Enter a valid email")`
- `headline`: trimmed, max 120 → `"Keep your headline under 120 characters"`
- `links`: array (max 5) of `{ label: min 1 "Label is required", url: z.url("Enter a full URL, e.g. https://…") }`
Export `type ProfileValues = z.infer<typeof profileSchema>`.

## `profile-form.tsx` (`"use client"`)
`<ProfileForm defaultValues={...} onSubmit={async (values) => result} />` where the result is `void` or `{ fieldErrors?: Partial<Record<"name" | "email" | "headline", string>>; message?: string }` (errors from the server).

- `useForm<ProfileValues>({ resolver: zodResolver(profileSchema), defaultValues, mode: "onTouched" })`
- inputs **Name**, **Email**, **Headline** via `register`; each error shown in `<p id="{field}-error">` + `aria-invalid` + `aria-describedby`
- `useFieldArray` for links: each row has inputs labelled `Link {n} label` and `Link {n} URL` and a `Remove link {n}` button; `Add link` button appends `{ label: "", url: "" }` and is **disabled at 5**; show row errors in the same way (`id="links.{i}.url-error"`)
- submit button `Save profile`, disabled while `isSubmitting`
- on server `fieldErrors` → `setError(field, { type: "server", message })`; on `message` → `setError("root.server", …)` shown in `role="alert"`
- on success → `<p role="status">Profile saved</p>` and `reset(values)` so the form isn't dirty anymore

```bash
cd exercises/web
npx vitest run m4/w5/07-react-hook-form-zod
```
