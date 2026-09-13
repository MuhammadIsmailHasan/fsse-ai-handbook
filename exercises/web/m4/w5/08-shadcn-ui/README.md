# M4 · W5 · 08 — shadcn/ui: own your components

> 🤖✅ **AI-allowed** · ⏱️ ~75 min

shadcn/ui isn't a dependency you import — its CLI **copies component source into your repo** (`components/ui/*`), built on **Radix** primitives (accessibility) + **Tailwind** + **cva** (variants). You own and edit that code.

Provided (as `npx shadcn@latest add button alert-dialog` would generate, simplified): `lib/utils.ts` (`cn`), `components/ui/button.tsx`, `components/ui/alert-dialog.tsx`.

## 1. `components/ui/badge.tsx`
- `badgeVariants` with **cva**: base `"inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"`, variants `tone`:
  - `neutral` → `bg-slate-100 text-slate-700` (**default**)
  - `info` → `bg-blue-100 text-blue-800`
  - `warning` → `bg-amber-100 text-amber-800`
  - `success` → `bg-green-100 text-green-800`
  - `danger` → `bg-red-100 text-red-800`
- `Badge({ tone, className, ...props })` → `<span data-slot="badge">`, merging classes with `cn` (so `className="bg-purple-100"` **replaces** the tone background)
- `StatusBadge({ status })` for `"applied" | "interview" | "offer" | "rejected"` → tones info / warning / success / danger and labels `Applied`, `Interview`, `Offer 🎉`, `Rejected`

## 2. `components/delete-application-dialog.tsx` (`"use client"`)
`<DeleteApplicationDialog role="Data Engineer" onConfirm={async () => {...}} />`
- trigger: `<Button variant="destructive">` text `Delete`
- an **AlertDialog** (not Dialog: destructive confirmations must not close on outside click) with title `Delete "Data Engineer"?`, description `This removes the application and its notes. This can't be undone.`
- `Cancel` and `Delete application` buttons
- controlled `open` state; clicking `Delete application` calls `event.preventDefault()` (keep dialog open), shows `Deleting…` and disables both buttons while pending
- success → close; failure → keep open and show `<p role="alert">Couldn't delete. Try again.</p>`

```bash
cd exercises/web
npx vitest run m4/w5/08-shadcn-ui
```
