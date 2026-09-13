# M4 · W2 · 04 — Set Up Tailwind CSS v4 with Your Design Tokens

> 🤖✅ **AI-allowed** (explain every line) · ⏱️ ~45 min · edit **`app.css`**

Tailwind v4 is configured **in CSS** (no `tailwind.config.js` needed). `index.html` (provided) already uses the classes below. Write `app.css` so they all exist:

| Needed | How |
|---|---|
| Tailwind itself | `@import "tailwindcss";` |
| Class scanning | `@source "./index.html";` (explicit sources are clearer than relying on auto-detection) |
| `bg-brand-500`, `hover:bg-brand-600`, `text-brand-50` | brand colors in `@theme`: `--color-brand-50`, `--color-brand-500`, `--color-brand-600` |
| `font-display` | `--font-display: "Plus Jakarta Sans", ui-sans-serif, system-ui, sans-serif;` in `@theme` |
| `3xl:grid-cols-4` | a custom breakpoint `--breakpoint-3xl: 120rem;` |
| `dark:bg-slate-900` | class-based dark mode: `@custom-variant dark (&:where(.dark, .dark *));` |
| `container-page` | a custom utility with `@utility container-page { … }` setting `max-width: 72rem`, `margin-inline: auto` and `padding-inline: 1rem` |
| Base styles | in `@layer base`, give `body` the classes' equivalents: `background-color: var(--color-slate-50)` and `color: var(--color-slate-900)` |

The test compiles your CSS with Tailwind (like Vite/Next.js would) and inspects the generated stylesheet.

```bash
cd exercises/web
npx vitest run m4/w2/04-tailwind-setup
```
