---
title: "🔥 shadcn/ui: Accessible Components You Own"
summary: Use the most popular React component approach of the Tailwind era — how shadcn/ui copies Radix-based components into your repo, cva variants, the cn helper, theming with CSS variables, AlertDialog confirmations, and customizing safely.
type: lesson
source: original
roles: { be: none, fe: core, fs: recommended, ai: optional, ops: none }
durationMinutes: 120
tags: [shadcn-ui, radix, tailwind, cva, design-system, accessibility]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What shadcn/ui is (and isn't): a **code distribution** tool, not an npm component library
- `npx shadcn@latest init` / `add`, `components.json`, and where files land
- **Radix primitives** for accessibility (focus trap, keyboard, ARIA)
- **cva** variants and the **`cn()`** helper (`clsx` + `tailwind-merge`)
- Theming with CSS variables and Tailwind v4
- Building a **destructive confirmation** with AlertDialog and pending state
- Owning and updating copied components responsibly

## 🧠 The big idea

Most UI libraries are like **renting furniture**: it arrives assembled, you can pick colors from a catalog, but you can't saw off a leg. shadcn/ui is like **IKEA plans plus quality parts**: you get well-designed pieces (built on Radix's accessible hardware) delivered **into your house** (your repo). They're yours — change anything.

## ❓ Why does this exist?

Building accessible components from scratch is hard. A correct modal dialog needs: focus trap, return focus on close, `Escape` to close, scroll locking, `aria-modal`, labelled title and description, portal rendering, and screen-reader testing. Traditional libraries (MUI, Ant Design) solve this but come with their own styling systems that fight Tailwind and are hard to customize deeply.

shadcn/ui combines **headless accessible primitives** (Radix) with **Tailwind styles you own**.

## 💥 What happens if we DON'T?

```tsx
// ❌ a hand-rolled "modal"
{open && (
  <div className="fixed inset-0 bg-black/50" onClick={() => setOpen(false)}>
    <div className="bg-white p-6">
      <p>Delete this application?</p>
      <div onClick={handleDelete}>Delete</div>          {/* not a button: no keyboard, no role */}
    </div>
  </div>
)}
```

Keyboard users can tab **behind** the modal, screen readers don't announce it, `Escape` does nothing, focus is lost after closing, and a mis-click on the backdrop cancels a destructive action halfway.

## 📖 How it works, step by step

### 1. Setup

```bash
npx shadcn@latest init            # detects Next.js + Tailwind v4, writes components.json, lib/utils.ts, theme CSS variables
npx shadcn@latest add button alert-dialog badge form
```

```text
components/
  ui/
    button.tsx          ← copied source, edit freely
    alert-dialog.tsx
    badge.tsx
lib/
  utils.ts              ← cn()
components.json         ← aliases, style, base color, icon library
```

Components import primitives from the `radix-ui` package and icons from `lucide-react`. Recent CLI versions can also scaffold with other primitive libraries — the ideas in this lesson are the same.

### 2. `cn()` — merging classes safely

```ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

cn("px-4 bg-red-600", isActive && "ring-2", "bg-purple-600");   // → "px-4 ring-2 bg-purple-600"
```

`clsx` handles conditionals; `tailwind-merge` resolves conflicts so a `className` prop can **override** a default.

### 3. Variants with `cva`

```tsx
import { cva, type VariantProps } from "class-variance-authority";

export const badgeVariants = cva("inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium", {
  variants: {
    tone: {
      neutral: "bg-slate-100 text-slate-700",
      info: "bg-blue-100 text-blue-800",
      warning: "bg-amber-100 text-amber-800",
      success: "bg-green-100 text-green-800",
      danger: "bg-red-100 text-red-800",
    },
  },
  defaultVariants: { tone: "neutral" },
});

export function Badge({ tone, className, ...props }: React.ComponentProps<"span"> & VariantProps<typeof badgeVariants>) {
  return <span data-slot="badge" className={cn(badgeVariants({ tone }), className)} {...props} />;
}
```

Then map **domain** values to **design** variants in one place:

```tsx
const STATUS_BADGE = {
  applied: { tone: "info", label: "Applied" },
  interview: { tone: "warning", label: "Interview" },
  offer: { tone: "success", label: "Offer 🎉" },
  rejected: { tone: "danger", label: "Rejected" },
} as const;
```

### 4. `asChild` and Slot

```tsx
<Button asChild variant="outline">
  <Link href="/applications/new">New application</Link>
</Button>
```

`asChild` renders the **child element** (a real `<a>`) with the button's styles and props — no invalid `<button><a/></button>` nesting.

### 5. AlertDialog for destructive actions

| Component | Closes on outside click? | Role | Use for |
|---|---|---|---|
| `Dialog` | yes | `dialog` | forms, details |
| `AlertDialog` | **no** | `alertdialog` | confirm destructive/irreversible actions |

```tsx
export function DeleteApplicationDialog({ role, onConfirm }: Props) {
  const [open, setOpen] = useState(false);
  const [pending, setPending] = useState(false);
  const [failed, setFailed] = useState(false);

  async function handleConfirm(event: React.MouseEvent<HTMLButtonElement>) {
    event.preventDefault();                 // don't auto-close; wait for the result
    setPending(true);
    setFailed(false);
    try {
      await onConfirm();
      setOpen(false);
    } catch {
      setFailed(true);
    } finally {
      setPending(false);
    }
  }

  return (
    <AlertDialog open={open} onOpenChange={(next) => !pending && setOpen(next)}>
      <AlertDialogTrigger asChild><Button variant="destructive">Delete</Button></AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{`Delete "${role}"?`}</AlertDialogTitle>
          <AlertDialogDescription>This removes the application and its notes. This can't be undone.</AlertDialogDescription>
        </AlertDialogHeader>
        {failed && <p role="alert">Couldn't delete. Try again.</p>}
        <AlertDialogFooter>
          <AlertDialogCancel disabled={pending}>Cancel</AlertDialogCancel>
          <AlertDialogAction disabled={pending} onClick={handleConfirm}>{pending ? "Deleting…" : "Delete application"}</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
```

Radix wires up: focus moves into the dialog (to Cancel — the safe choice), `Tab` is trapped, `Escape` closes, focus returns to the trigger, title/description are linked with ARIA.

### 6. Theming

`init` adds CSS variables (`--background`, `--primary`, `--destructive`, `--radius` …) and maps them to Tailwind utilities (`bg-primary`, `text-destructive`). Change the brand by editing variables, and support dark mode with a `.dark` class — without touching components.

## ⚖️ Trade-offs

| | ✅ | ❌ |
|---|---|---|
| shadcn/ui (copied code) | full control, Tailwind-native, accessible primitives, no version lock | **you** maintain updates; copies can drift; many files in your repo |
| npm component library (MUI, Mantine, Chakra) | updates via `npm update`, big component sets | styling system to learn, harder deep customization |
| Headless only (Radix, React Aria, Base UI) | maximum freedom | you write all styles |
| From scratch | total control | accessibility bugs, lots of time |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ Tailwind + React/Next.js apps that want a custom look with solid accessibility.
- ✅ Starting a design system you'll grow.
- 🚫 If your company already has a design system package — use that.
- 🚫 Don't copy a component and then never read it — you own the bugs too.

## 🏆 Best practices

- [ ] Treat `components/ui` as **your** code: read it, test critical behavior, review diffs when re-adding.
- [ ] Customize through variants and CSS variables before editing internals.
- [ ] Keep domain mapping (status → tone) outside `ui/` primitives.
- [ ] Use `AlertDialog` for destructive confirmations; keep it open until the action finishes; show errors inside.
- [ ] Use `asChild` for links styled as buttons.
- [ ] Always give dialogs a title (visually hidden if needed) and description.
- [ ] Test with the keyboard and a screen reader (VoiceOver/NVDA) at least once per component type.
- [ ] Pin `radix-ui`, `cva`, `tailwind-merge` versions; update deliberately.

## 🏭 How it's used in industry

- shadcn/ui is one of the most starred React UI projects and widely used in Next.js SaaS starters, dashboards and AI app templates (including many generated by AI tools like v0).
- Companies often fork shadcn/ui components into an internal design system, adding brand tokens and Storybook docs.
- Radix primitives also power other libraries and design systems, so the accessibility patterns you learn transfer.

## ⚠️ Common mistakes

- Wrapping `<Link>` in `<Button>` instead of `asChild`.
- Class conflicts because `cn` wasn't used (`className="bg-purple-600"` doesn't override `bg-red-600` without `tailwind-merge`).
- Closing the confirm dialog immediately, then failing silently.
- Using `Dialog` for "Delete account" so a stray click outside cancels it.
- Forgetting `"use client"` in components that use Radix state.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain the "rented furniture vs IKEA plans with quality parts" analogy, and one real downside of owning the component code.

## 📐 Design it

Plan a small **CareerPilot design system** on top of shadcn/ui: which components you'd add first for the applications board, which variants each needs (e.g. `Button`: default/outline/ghost/destructive, sizes), which domain components wrap them (`StatusBadge`, `ApplicationCard`), and how you'd document and test them.

:::quiz
Show a possible plan

- **Primitives (`components/ui`)**: Button (default, secondary, outline, ghost, destructive × sm/default/icon), Badge (tones), Card, Input, Textarea, Select, Form (RHF integration), Dialog, AlertDialog, DropdownMenu, Tabs, Tooltip, Skeleton, Sonner/Toast.
- **Domain components (`components/careerpilot`)**: `StatusBadge` (status → tone), `ApplicationCard` (Card + StatusBadge + DropdownMenu actions), `MoveStatusMenu`, `DeleteApplicationDialog`, `SalaryRange`, `EmptyState`.
- **Tokens**: brand colors and radius in CSS variables; dark mode via `.dark`.
- **Docs**: Storybook stories for every variant + accessibility addon; a short `components/README.md` with "which component when".
- **Tests**: Vitest + Testing Library for behavior (dialog pending/error, menu keyboard), visual snapshots in Storybook/Chromatic or Playwright screenshots for key states; axe checks in CI.
- **Updates**: re-run `npx shadcn@latest add <component> --diff`-style review (or compare with upstream) quarterly; changes go through PR review.
:::

### 📝 Self-review checklist

- [ ] Primitives stay generic; domain logic lives in wrappers
- [ ] Destructive actions use AlertDialog
- [ ] Accessibility is tested, not assumed

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w5/08-shadcn-ui" ai="ai-allowed" title="Badge variants and a delete confirmation"}
With provided shadcn-style `Button` and `AlertDialog`, build a `cva` badge with tones, a `StatusBadge` mapping, and a `DeleteApplicationDialog` that stays open while deleting, blocks Escape during the request and shows errors inside.
:::

:::hints
- `cn(badgeVariants({ tone }), className)` lets `className` override the tone background.
- Call `event.preventDefault()` in the action's `onClick` so Radix doesn't close the dialog.
- Ignore `onOpenChange(false)` while pending.
:::

## ✅ Quick check

:::quiz
Why does shadcn/ui use `tailwind-merge` inside `cn()`?

Tailwind classes don't override by order in the `class` attribute — CSS order decides. `tailwind-merge` removes conflicting classes (`bg-red-600` vs `bg-purple-600`) so the last one intended wins.
:::

:::quiz
`npx shadcn@latest add button` releases a fix. How do you get it?

It isn't automatic — the code is yours. Re-run `add` (review the diff before overwriting your customizations) or apply the change manually.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Headless component | Komponen tanpa gaya bawaan (hanya perilaku) |
| Variant | Varian tampilan komponen |
| Design system | Sistem desain (komponen + aturan visual) |
| Focus trap | Menahan fokus keyboard di dalam dialog |
| Destructive action | Aksi yang menghapus/merusak data |
| Design token | Nilai desain (warna, radius) sebagai variabel |

## 📚 Keep learning

- [shadcn/ui docs](https://ui.shadcn.com/docs) — Installation (Next.js), Theming, AlertDialog, Form
- [Radix Primitives: Alert Dialog](https://www.radix-ui.com/primitives/docs/components/alert-dialog)
- [cva docs](https://cva.style/docs)
