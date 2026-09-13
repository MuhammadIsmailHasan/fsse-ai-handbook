# M4 · W2 · 06 — Typed Variants: TypeScript + Tailwind Together

> 🚫🤖 **No-AI** · ⏱️ ~60 min · edit **`ui-classes.ts`**

Build the class-name helpers that component libraries (and shadcn/ui, Week 5) are made of.

| Export | Requirement |
|---|---|
| `cn(...inputs)` | `twMerge(clsx(inputs))` — conditional classes **and** conflict resolution (`"px-4 px-8"` → `"px-8"`) |
| `type ButtonVariant` | `"primary" \| "secondary" \| "danger" \| "ghost"` |
| `type ButtonSize` | `"sm" \| "md" \| "lg"` |
| `BUTTON_VARIANTS` | `satisfies Record<ButtonVariant, string>`: primary `"bg-indigo-600 text-white hover:bg-indigo-500"`, secondary `"bg-white text-slate-900 ring-1 ring-slate-300 hover:bg-slate-50"`, danger `"bg-red-600 text-white hover:bg-red-500"`, ghost `"bg-transparent text-slate-700 hover:bg-slate-100"` |
| `BUTTON_SIZES` | `satisfies Record<ButtonSize, string>`: sm `"px-2.5 py-1.5 text-sm"`, md `"px-4 py-2 text-sm"`, lg `"px-5 py-3 text-base"` |
| `buttonClasses(options?)` | `options: { variant?: ButtonVariant; size?: ButtonSize; fullWidth?: boolean; className?: string }` (defaults `primary`, `md`, `false`). Returns `cn(BASE, BUTTON_VARIANTS[variant], BUTTON_SIZES[size], fullWidth && "w-full", className)` where `BASE = "inline-flex items-center justify-center rounded-lg font-semibold focus-visible:outline-2 focus-visible:outline-offset-2 disabled:pointer-events-none disabled:opacity-50"` |
| `type Status` / `STATUS_BADGE` | `"saved" \| "applied" \| "interview" \| "offer" \| "rejected"`, with badge colors `satisfies Record<Status, string>` (any colors you like, each must include a `bg-` and a `text-` class) |
| `badgeClasses(status, className?)` | `cn("inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium", STATUS_BADGE[status], className)` |

```bash
cd exercises/web
npx vitest run m4/w2/06-integration-patterns
```
