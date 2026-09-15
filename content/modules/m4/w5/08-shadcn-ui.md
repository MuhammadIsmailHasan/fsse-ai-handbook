---
title: "🔥 shadcn/ui: Accessible Components You Own"
summary: How shadcn/ui copies accessible Radix-based components into your project — cva variants, the cn helper, theming with CSS variables, safe delete confirmations, and owning the code.
type: lesson
source: original
roles: { be: none, fe: core, fs: recommended, ai: optional, ops: none }
durationMinutes: 120
tags: [shadcn-ui, radix, tailwind, cva, design-system, accessibility]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What shadcn/ui is — and isn't: it copies code into your project; it's not an npm component library
- `npx shadcn@latest init` / `add`, and where the files go
- **Radix primitives**: the accessibility built in (focus, keyboard, ARIA)
- **cva** variants and the **`cn()`** helper (you met both in Week 2)
- Theming with CSS variables
- A **delete confirmation** with AlertDialog and a "Deleting…" state
- Owning and updating copied components responsibly

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **shadcn/ui** | A tool that copies ready-made, accessible components into your code | Komponen yang disalin ke proyekmu |
| **Radix** | A library of unstyled components that handle keyboard, focus and ARIA | Komponen tanpa gaya |
| **Headless component** | Behavior only, no styles — you add the look | Komponen tanpa tampilan |
| **Primitive** | A basic building block like Dialog, Menu, Tabs | Balok dasar |
| **Focus trap** | Keeping keyboard focus inside a dialog while it's open | Mengunci fokus |
| **AlertDialog** | A dialog for dangerous actions; a click outside doesn't close it | Dialog konfirmasi |
| **`asChild`** | Give a component's styles to its child element (like a real link) | Pakai elemen anak |
| **Design token** | A design value (color, radius) stored as a CSS variable | Token desain |

## 🧠 The big idea

Most UI libraries are like **renting furniture**: it arrives assembled, you pick colors from a catalog, but you can't cut off a leg. shadcn/ui is like **IKEA plans plus quality parts**: you get well-designed pieces (built on Radix's accessible hardware) delivered **into your house** (your project). They're yours — change anything.

## ❓ Why it matters

Building accessible components yourself is hard. A correct popup dialog needs: keeping focus inside, returning focus when closed, `Escape` to close, stopping the page behind from scrolling, a labelled title and description, and testing with screen readers. Traditional libraries (MUI, Ant Design) solve this, but come with their own styling systems that fight Tailwind.

shadcn/ui combines **accessible behavior** (Radix) with **Tailwind styles you own**.

A hand-made "modal" usually breaks:

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

- Keyboard users can Tab to things **behind** the modal.
- Screen readers don't announce it; `Escape` does nothing.
- Focus is lost after closing.
- A mis-click on the dark background cancels a dangerous action halfway.

## 📖 Step by step

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

- `init` sets up the project; `add` copies components into `components/ui`.
- The components use the `radix-ui` package for behavior and `lucide-react` for icons.

### 2. `cn()` — combining classes safely

```ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

cn("px-4 bg-red-600", isActive && "ring-2", "bg-purple-600");   // → "px-4 ring-2 bg-purple-600"
```

Same helper as Week 2 lesson 06: `clsx` adds classes on conditions, `tailwind-merge` removes conflicts so a `className` prop can **override** a default.

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

Then connect your **business** values to **design** variants in one place:

```tsx
const STATUS_BADGE = {
  applied: { tone: "info", label: "Applied" },
  interview: { tone: "warning", label: "Interview" },
  offer: { tone: "success", label: "Offer 🎉" },
  rejected: { tone: "danger", label: "Rejected" },
} as const;
```

The generic `Badge` knows only colors ("tones"). A small table says "interview → warning". That way the design stays reusable, and business words stay in your app code.

### 4. `asChild`

```tsx
<Button asChild variant="outline">
  <Link href="/applications/new">New application</Link>
</Button>
```

`asChild` means "don't make your own `<button>` — put your styles on my child". The result is a real link (`<a>`) that looks like a button, without invalid `<button><a/></button>` nesting. Like putting a uniform on a staff member instead of building a new person.

### 5. AlertDialog for dangerous actions

| Component | Closes on outside click? | Role | Use for |
|---|---|---|---|
| `Dialog` | yes | `dialog` | forms, details |
| `AlertDialog` | **no** | `alertdialog` | confirming dangerous or permanent actions |

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

- `event.preventDefault()` stops the dialog from closing immediately; it closes only **after** the delete succeeds.
- While deleting, `Escape` and outside clicks are ignored (`!pending && setOpen(next)`).
- If it fails, the error shows **inside** the dialog.
- Radix does the rest: focus goes to **Cancel** (the safe choice), Tab stays inside, `Escape` closes, focus returns to the Delete button, and the title and description are connected for screen readers.

Like an ATM asking "Are you sure you want to transfer?" — it waits for the bank's answer before printing the receipt.

### 6. Theming

`init` adds CSS variables (`--background`, `--primary`, `--destructive`, `--radius`…) and connects them to Tailwind classes (`bg-primary`, `text-destructive`). Change your brand by editing the variables; add dark mode with a `.dark` class — without touching the components.

## ⚠️ Common mistakes

- Putting `<Link>` inside `<Button>` instead of using `asChild`.
- Not using `cn`, so `className="bg-purple-600"` doesn't override `bg-red-600`.
- Closing the confirm dialog right away, then failing silently.
- Using `Dialog` for "Delete account", so a stray click outside cancels it.
- Forgetting `"use client"` in components that use Radix state.
- Copying a component and never reading it — you own its bugs too.
- Using shadcn/ui when your company already has its own design system package.

## 🏆 Best practices

- [ ] Treat `components/ui` as **your** code: read it, test important behavior, review changes when you add it again.
- [ ] Customize with variants and CSS variables before editing the insides.
- [ ] Keep business mapping (status → tone) outside the `ui/` components.
- [ ] Use `AlertDialog` for dangerous actions; keep it open until the action finishes; show errors inside.
- [ ] Use `asChild` for links that look like buttons.
- [ ] Always give dialogs a title (visually hidden if needed) and a description.
- [ ] Test each type of component with the keyboard and a screen reader at least once.
- [ ] Pin the versions of `radix-ui`, `cva` and `tailwind-merge`; update on purpose.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain the "rented furniture vs IKEA plans with quality parts" idea, and one real downside of owning the component code.

## 📐 Design it

Plan a small **CareerPilot design system** on top of shadcn/ui: which components to add first for the applications board, which variants each needs (for example `Button`: default/outline/ghost/destructive, with sizes), which app-specific components wrap them (`StatusBadge`, `ApplicationCard`), and how to document and test them.

:::quiz
Show a possible plan

- **Basic components (`components/ui`)**: Button (default, secondary, outline, ghost, destructive × sm/default/icon), Badge (tones), Card, Input, Textarea, Select, Form (React Hook Form), Dialog, AlertDialog, DropdownMenu, Tabs, Tooltip, Skeleton, Sonner/Toast.
- **App components (`components/careerpilot`)**: `StatusBadge` (status → tone), `ApplicationCard` (Card + StatusBadge + DropdownMenu actions), `MoveStatusMenu`, `DeleteApplicationDialog`, `SalaryRange`, `EmptyState`.
- **Tokens**: brand colors and radius as CSS variables; dark mode with `.dark`.
- **Docs**: Storybook stories for every variant, with the accessibility add-on, plus a short `components/README.md` saying "which component when".
- **Tests**: Vitest + Testing Library for behavior (dialog saving/error, menu keyboard); screenshots of key states (Storybook or Playwright); axe checks in CI.
- **Updates**: every few months, compare your copies with the latest shadcn/ui versions and apply changes through a reviewed pull request.
:::

### 📝 Self-review checklist

- [ ] Basic components stay generic; business logic lives in wrappers
- [ ] Dangerous actions use AlertDialog
- [ ] Accessibility is tested, not assumed

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w5/08-shadcn-ui" ai="ai-allowed" title="Badge variants and a delete confirmation"}
Using the provided shadcn-style `Button` and `AlertDialog`, build a `cva` badge with tones, a `StatusBadge` mapping, and a `DeleteApplicationDialog` that stays open while deleting, ignores Escape during the request, and shows errors inside.
:::

:::hints
- `cn(badgeVariants({ tone }), className)` lets `className` override the tone's background.
- Call `event.preventDefault()` in the action button's `onClick` so Radix doesn't close the dialog.
- Ignore `onOpenChange(false)` while pending.
:::

## ✅ Quick check

:::quiz
Why does shadcn/ui use `tailwind-merge` inside `cn()`?

Tailwind classes don't override each other by their order in the `class` attribute — the CSS file order decides. `tailwind-merge` removes the conflicting class (`bg-red-600` vs `bg-purple-600`) so the one you meant wins.
:::

:::quiz
shadcn/ui releases a fix for the button. How do you get it?

Not automatically — the code is yours. Run `add` again (and review the changes before overwriting your customizations), or apply the fix by hand.
:::

## 📚 Keep learning

- [shadcn/ui docs](https://ui.shadcn.com/docs) — Installation (Next.js), Theming, AlertDialog, Form
- [Radix Primitives: Alert Dialog](https://www.radix-ui.com/primitives/docs/components/alert-dialog)
- [cva docs](https://cva.style/docs)
