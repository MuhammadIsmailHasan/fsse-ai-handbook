---
title: "Tailwind: Typography, Responsive Design & Components"
summary: Build real interfaces with utilities — typography scale, spacing, color and states, mobile-first responsive prefixes, dark mode, and turning repeated class lists into components.
type: lesson
source: core
sourceRef: "M3 · W2 · L4"
roles: { be: optional, fe: core, fs: core, ai: optional, ops: none }
durationMinutes: 150
tags: [tailwind, responsive, typography, components, dark-mode]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Reading and writing utility classes fluently: spacing, sizing, typography, colors, borders, shadows
- Layout utilities: flex, grid, gap, container patterns
- **Variants**: `hover:`, `focus-visible:`, `disabled:`, `group-hover:`, `aria-*`, `data-*`
- **Responsive** prefixes (mobile first) and container queries
- Dark mode with `dark:`
- Extracting components instead of repeating classes
- Keeping it accessible and avoiding class soup

## 🧠 The big idea

Tailwind classes are a **vocabulary**. At first you look up every word; after a week you "speak" layout: `flex items-center justify-between gap-4` reads like a sentence. The CSS knowledge from Week 1 doesn't go away — each utility is one CSS declaration with a design-system value.

## ❓ Why does this exist?

Most UI work is combining the same few properties with consistent values. Utilities let you do that without switching files, and variants (`md:`, `hover:`, `dark:`) express responsive and interactive states inline, next to the element they affect.

## 💥 What happens if we DON'T use it well?

```html
<div class="mt-[13px] ml-[7px] text-[15px] text-[#4b5563] w-[437px]">…</div>
<button class="bg-indigo-600 text-white">Save</button>   <!-- no hover, focus or disabled states -->
```

Arbitrary values break consistency and responsiveness; missing states hurt keyboard users. And a 40-class `<button>` copy-pasted in 30 places means 30 edits for a design change.

## 📖 How it works, step by step

### 1. The scales

| Category | Examples | CSS |
|---|---|---|
| Spacing (0.25rem steps) | `p-4`, `px-2`, `mt-6`, `gap-3`, `space-y-2` | `padding: 1rem` … |
| Sizing | `w-full`, `max-w-5xl`, `h-12`, `size-10`, `min-h-dvh` | widths/heights |
| Typography | `text-sm`, `text-2xl`, `font-semibold`, `leading-relaxed`, `tracking-tight`, `line-clamp-2`, `truncate` | font properties |
| Color | `bg-white`, `text-slate-600`, `border-slate-200`, `bg-indigo-600/90` (opacity) | colors from `@theme` |
| Borders & effects | `border`, `rounded-xl`, `ring-1`, `shadow-sm`, `outline-2` | borders, shadows |
| Layout | `flex`, `grid`, `grid-cols-3`, `items-center`, `justify-between`, `hidden`, `sr-only` | display, alignment |

`sr-only` hides content visually but keeps it for screen readers — great for icon buttons.

### 2. States and variants

```html
<button class="rounded-lg bg-indigo-600 px-4 py-2 text-white
               hover:bg-indigo-500
               focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600
               disabled:cursor-not-allowed disabled:opacity-50">
  Save
</button>

<a class="group flex items-center gap-2">
  <span class="group-hover:underline">View job</span>
  <svg class="transition group-hover:translate-x-1" aria-hidden="true">…</svg>
</a>

<button aria-pressed="true" class="aria-pressed:bg-indigo-50 aria-pressed:text-indigo-700">Saved</button>
<div data-state="open" class="data-[state=open]:block hidden">…</div>
```

Style **from accessibility state** (`aria-pressed:`, `aria-invalid:`) so visuals and semantics can't drift apart.

### 3. Responsive (mobile first)

```html
<ul class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">…</ul>
<h1 class="text-2xl sm:text-3xl lg:text-4xl">Jobs for you</h1>
<aside class="hidden md:block">Filters</aside>
```

| Prefix | Min width |
|---|---|
| `sm:` | 40rem (640px) |
| `md:` | 48rem (768px) |
| `lg:` | 64rem (1024px) |
| `xl:` | 80rem (1280px) |
| `2xl:` | 96rem (1536px) |

Unprefixed = all sizes; a prefix means "**from this width up**". `max-md:` targets below a breakpoint when needed.

Container queries are built in:

```html
<div class="@container">
  <article class="flex flex-col @md:flex-row">…</article>
</div>
```

### 4. Dark mode

```html
<article class="bg-white text-slate-900 dark:bg-slate-900 dark:text-slate-100">…</article>
```

By default `dark:` follows the OS (`prefers-color-scheme`); with the custom variant from lesson 04 it follows a `.dark` class you toggle.

### 5. Typography for content

For Markdown/CMS content, the official Typography plugin gives beautiful defaults with one class:

```css
@plugin "@tailwindcss/typography";
```

```html
<article class="prose dark:prose-invert max-w-none">…rendered markdown…</article>
```

(This handbook renders lessons with `prose`.)

### 6. Components, not copy-paste

When the same class list repeats, extract a **component** (React, Week 3) or a **class helper** (lesson 06):

```tsx
function Badge({ children }: { children: React.ReactNode }) {
  return <span className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium">{children}</span>;
}
```

`@apply` inside CSS exists, but overusing it rebuilds the CSS-naming problem Tailwind solved — reserve it for third-party markup you can't add classes to.

### 7. Reading long class lists

Group mentally: **layout → box → typography → color → states → responsive**. Prettier's Tailwind plugin sorts classes in a consistent order so diffs stay clean.

## ⚖️ Trade-offs

| Choice | ✅ | ❌ |
|---|---|---|
| Utilities in markup | local, fast, consistent | verbose markup |
| Components for repeated UI | one place to change | need a component system (React) |
| `@apply` | shorter HTML for third-party markup | reintroduces custom class naming |
| Arbitrary values | pixel-perfect one-offs | erode the design system |
| `dark:` everywhere | explicit | doubles color classes → semantic CSS variables can reduce it |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ Utilities for layout and component styling; `prose` for content.
- ✅ Extract components after the second or third repetition.
- 🚫 Arbitrary values unless there's a real reason (third-party size constraint).
- 🚫 Hiding focus rings or relying on color alone for state.

## 🏆 Best practices

- [ ] Mobile first: base classes for phones, prefixes for larger screens.
- [ ] Every interactive element: `hover:`, `focus-visible:`, `disabled:` states.
- [ ] Use `sr-only` labels for icon-only buttons; style from `aria-*` states.
- [ ] Stay on the scale; add missing values to `@theme` rather than using `[…]`.
- [ ] Extract components/class helpers for repeated combinations.
- [ ] Sort classes with Prettier; keep class lists readable.
- [ ] Test dark mode and 200% zoom.

## 🏭 How it's used in industry

- Tailwind UI, shadcn/ui and many design systems ship components as React + Tailwind code you own and customize.
- Product teams prototype directly in code with Tailwind, often from AI-generated starting points, then refine.
- Code reviews focus on consistency (scale usage), states and accessibility rather than CSS architecture.

## ⚠️ Common mistakes

- `md:` thinking it means "only medium" (it means "medium and up").
- Forgetting `min-w-0` on flex children, so long text overflows (`truncate` needs it).
- Missing `focus-visible:` styles.
- Copy-pasting 30-class buttons instead of creating a component.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain mobile-first responsive prefixes to a designer: what `grid-cols-1 md:grid-cols-2 xl:grid-cols-4` means at 375px, 800px and 1440px.

## 📐 Design it

Write the Tailwind markup (classes only) for CareerPilot's **application card** used on the board: company logo, role title (truncate on one line), company + location (muted), status badge, "updated 2 days ago", a menu icon button (accessible), hover elevation, focus ring when the whole card is a link, and a compact layout inside narrow columns using container queries.

:::quiz
Show possible markup

```html
<li class="@container">
  <article class="group relative flex gap-3 rounded-xl border border-slate-200 bg-white p-3 shadow-sm transition
                  hover:shadow-md focus-within:ring-2 focus-within:ring-indigo-600
                  dark:border-slate-800 dark:bg-slate-900">
    <img src="…" alt="" class="size-10 shrink-0 rounded-lg object-cover" />
    <div class="min-w-0 flex-1">
      <h3 class="truncate text-sm font-semibold text-slate-900 dark:text-white">
        <a href="/applications/12" class="outline-none after:absolute after:inset-0">Senior Backend Engineer</a>
      </h3>
      <p class="truncate text-xs text-slate-500 dark:text-slate-400">Kopi Data · Jakarta</p>
      <div class="mt-2 flex flex-col gap-1 @xs:flex-row @xs:items-center @xs:justify-between">
        <span class="inline-flex w-fit items-center rounded-full bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-800">Interview</span>
        <time datetime="2026-09-12" class="text-xs text-slate-500">Updated 2 days ago</time>
      </div>
    </div>
    <button type="button" class="relative z-10 self-start rounded-md p-1 text-slate-500 hover:bg-slate-100 focus-visible:outline-2 focus-visible:outline-indigo-600">
      <span class="sr-only">Actions for Senior Backend Engineer</span>
      <svg aria-hidden="true" class="size-4">…</svg>
    </button>
  </article>
</li>
```

Notes: `min-w-0` makes `truncate` work in flex; the link's `after:absolute after:inset-0` makes the whole card clickable while keeping one focusable link; the menu button sits above it with `relative z-10`; `alt=""` because the company name is already in text; `sr-only` names the icon button specifically.
:::

### 📝 Self-review checklist

- [ ] Truncation works (`min-w-0`)
- [ ] One clear link target, accessible icon button
- [ ] Focus visible, dark mode considered
- [ ] Narrow-column layout handled

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w2/05-tailwind-components" ai="no-ai" title="Responsive job cards with utilities only"}
Style a job list page using only Tailwind utilities: container, responsive heading and grid, cards with dark mode, clamped descriptions, badges and a button with hover, focus-visible and disabled states. Tests check the classes, forbid arbitrary values and inline styles, and compile Tailwind to catch typos.
:::

:::hints
- `flex flex-col` on the card + `mt-auto` on the button pushes it to the bottom.
- `w-fit` stops the badge from stretching in a flex column.
- If a class "doesn't exist", check the Tailwind docs spelling (e.g. `grid-cols-2`, not `grid-col-2`).
:::

## ✅ Quick check

:::quiz
What does `md:hidden` do?

Hides the element from the `md` breakpoint (48rem) and up; it stays visible on smaller screens.
:::

:::quiz
Why style with `aria-pressed:` instead of a separate "active" class?

The visual state follows the accessibility state automatically, so they can't get out of sync.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Responsive prefix | Awalan responsif (sm:, md:, lg:) |
| State variant | Varian status (hover:, focus-visible:) |
| Container query | Kueri wadah |
| Screen-reader only | Hanya untuk pembaca layar (`sr-only`) |
| Line clamp | Membatasi jumlah baris teks |

## 📚 Keep learning

- [Tailwind CSS docs: Responsive design](https://tailwindcss.com/docs/responsive-design)
- [Tailwind CSS docs: Hover, focus, and other states](https://tailwindcss.com/docs/hover-focus-and-other-states)
- [Tailwind CSS docs: Dark mode](https://tailwindcss.com/docs/dark-mode)
