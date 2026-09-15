---
title: "Tailwind: Typography, Responsive Design & Components"
summary: Build real screens with utility classes — text sizes, spacing, colors, hover and focus states, mobile-first prefixes, dark mode, and turning repeated class lists into components.
type: lesson
source: core
sourceRef: "M3 · W2 · L4"
roles: { be: optional, fe: core, fs: core, ai: optional, ops: none }
durationMinutes: 150
tags: [tailwind, responsive, typography, components, dark-mode]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- The most common Tailwind classes: spacing, size, text, color, borders
- Classes for states: `hover:`, `focus-visible:`, `disabled:`, `group-hover:`, `aria-*`
- Mobile-first prefixes (`sm:`, `md:`, `lg:`) and container queries
- Dark mode with `dark:`
- Styling long articles with `prose`
- Making a component instead of copying long class lists

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Scale** | Tailwind's fixed list of sizes: `p-1`, `p-2`, `p-4`… | Skala ukuran |
| **Variant / prefix** | A condition before a class: `hover:bg-blue-500` works only on hover | Awalan kondisi |
| **Responsive prefix** | `md:` = "from medium screens **and bigger**" | Awalan ukuran layar |
| **`group`** | Mark a parent so children can react to its hover: `group-hover:` | Kelompok |
| **`sr-only`** | Hidden on screen, but read by screen readers | Hanya pembaca layar |
| **Arbitrary value** | A one-off value in brackets: `mt-[13px]` | Nilai sembarang |

## 🧠 The big idea

Tailwind classes are like **learning a new language's vocabulary**. The first days you look up every word. After a week you "speak layout": `flex items-center justify-between gap-4` reads like a sentence — "put these in a row, centered vertically, spread out, with space between". Your CSS knowledge from Week 1 still applies: each class is one CSS rule with a value from the design scale.

## ❓ Why it matters

Most UI work is combining the same few properties with consistent values. Tailwind lets you do that right next to the element, and prefixes like `md:`, `hover:` and `dark:` handle screen sizes and states in the same place.

Used badly, it becomes hard to maintain:

```html
<div class="mt-[13px] ml-[7px] text-[15px] text-[#4b5563] w-[437px]">…</div>
<button class="bg-indigo-600 text-white">Save</button>   <!-- no hover, focus or disabled states -->
```

- Random values break the consistent look and don't adapt to screens.
- No hover or focus style: keyboard users can't see where they are.
- A 40-class button copied into 30 places = 30 edits for one design change.

## 📖 Step by step

### 1. The common classes

| Group | Examples | Does |
|---|---|---|
| Spacing (steps of 0.25rem) | `p-4`, `px-2`, `mt-6`, `gap-3`, `space-y-2` | padding, margin, gaps |
| Size | `w-full`, `max-w-5xl`, `h-12`, `size-10`, `min-h-dvh` | width and height |
| Text | `text-sm`, `text-2xl`, `font-semibold`, `leading-relaxed`, `tracking-tight`, `line-clamp-2`, `truncate` | font size, weight, lines |
| Color | `bg-white`, `text-slate-600`, `border-slate-200`, `bg-indigo-600/90` | colors (`/90` = 90% opacity) |
| Borders & shadows | `border`, `rounded-xl`, `ring-1`, `shadow-sm`, `outline-2` | edges and depth |
| Layout | `flex`, `grid`, `grid-cols-3`, `items-center`, `justify-between`, `hidden`, `sr-only` | placing things |

- `truncate` cuts long text with "…" on one line; `line-clamp-2` allows 2 lines.
- `sr-only` hides text visually but screen readers still read it — perfect for icon-only buttons.

### 2. States

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

- `hover:` — when the mouse is over it. `focus-visible:` — when reached by keyboard. `disabled:` — when the button is disabled.
- `group` + `group-hover:` — hovering the **parent** changes a **child**, like one light switch controlling several lamps.
- `aria-pressed:` — style from the accessibility state. The look and the meaning always match, because they come from the same attribute.

### 3. Mobile first

```html
<ul class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">…</ul>
<h1 class="text-2xl sm:text-3xl lg:text-4xl">Jobs for you</h1>
<aside class="hidden md:block">Filters</aside>
```

| Prefix | From width |
|---|---|
| `sm:` | 40rem (640px) |
| `md:` | 48rem (768px) |
| `lg:` | 64rem (1024px) |
| `xl:` | 80rem (1280px) |
| `2xl:` | 96rem (1536px) |

A class **without** a prefix applies to all screens. A prefix means "**from this width and bigger**" — like an age rule "17+": it doesn't mean "only 17". Use `max-md:` if you need "smaller than md".

Container queries are built in, so a card can adapt to the box it's in:

```html
<div class="@container">
  <article class="flex flex-col @md:flex-row">…</article>
</div>
```

### 4. Dark mode

```html
<article class="bg-white text-slate-900 dark:bg-slate-900 dark:text-slate-100">…</article>
```

`dark:` classes apply in dark mode. By default this follows the phone or computer setting; with the custom variant from lesson 04, it follows a `.dark` class you switch on.

### 5. Long articles: `prose`

For Markdown or blog content, the Typography plugin styles everything with one class:

```css
@plugin "@tailwindcss/typography";
```

```html
<article class="prose dark:prose-invert max-w-none">…rendered markdown…</article>
```

(This handbook uses `prose` for its lessons.)

### 6. Components, not copy-paste

When the same long class list appears again and again, make a **component** (React, Week 3) — like saving a recipe instead of remembering the ingredients every time:

```tsx
function Badge({ children }: { children: React.ReactNode }) {
  return <span className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium">{children}</span>;
}
```

`@apply` in CSS also exists, but using it everywhere brings back the naming problems Tailwind solved. Use it only for HTML you can't add classes to (from a third-party library).

### 7. Reading long class lists

Read them in groups: **layout → box → text → color → states → screen sizes**. The Prettier Tailwind plugin sorts classes in this kind of order automatically.

## ⚠️ Common mistakes

- Thinking `md:` means "only medium screens" (it means medium **and bigger**).
- Forgetting `min-w-0` on a flex child, so `truncate` doesn't work and long text overflows.
- No `focus-visible:` style on buttons and links.
- Random values like `mt-[13px]` instead of the scale.
- Copy-pasting a 30-class button instead of creating a component.
- Showing a state only with color.

## 🏆 Best practices

- [ ] Mobile first: base classes for phones, prefixes for bigger screens.
- [ ] Every interactive element has `hover:`, `focus-visible:` and `disabled:` styles.
- [ ] Icon-only buttons have an `sr-only` label; style from `aria-*` states.
- [ ] Stay on the scale; add missing values to `@theme` instead of `[…]`.
- [ ] Turn repeated class groups into components.
- [ ] Sort classes with Prettier.
- [ ] Test dark mode and 200% zoom.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain mobile-first prefixes to a designer: what does `grid-cols-1 md:grid-cols-2 xl:grid-cols-4` show on a 375px phone, an 800px tablet and a 1440px laptop?

## 📐 Design it

Write the Tailwind classes for CareerPilot's **application card** on the board: company logo, job title (one line, cut with "…"), company + location (gray), status badge, "updated 2 days ago", an accessible menu icon button, a shadow on hover, a focus ring when the card link is focused, and a compact layout in narrow columns using container queries.

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

- `min-w-0` lets `truncate` work inside flex.
- `after:absolute after:inset-0` on the link stretches its click area over the whole card, while keeping only one link to focus.
- The menu button sits above that area with `relative z-10`.
- `alt=""` because the company name is already written as text.
- `sr-only` gives the icon button a specific name.
:::

### 📝 Self-review checklist

- [ ] Long text is cut correctly (`min-w-0`)
- [ ] One clear link, and an accessible icon button
- [ ] Visible focus, dark mode handled
- [ ] Works in a narrow column

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w2/05-tailwind-components" ai="no-ai" title="Responsive job cards with utilities only"}
Style a job list page using only Tailwind classes: a container, a responsive heading and grid, cards with dark mode, descriptions limited to a few lines, badges and a button with hover, focus-visible and disabled states. The tests check your classes, forbid arbitrary values and inline styles, and build Tailwind to catch typos.
:::

:::hints
- `flex flex-col` on the card + `mt-auto` on the button pushes the button to the bottom.
- `w-fit` stops the badge from stretching in a flex column.
- If a class "doesn't exist", check the spelling in the Tailwind docs (e.g. `grid-cols-2`, not `grid-col-2`).
:::

## ✅ Quick check

:::quiz
What does `md:hidden` do?

It hides the element from the `md` width (48rem) and bigger. On smaller screens it stays visible.
:::

:::quiz
Why style with `aria-pressed:` instead of a separate "active" class?

The look follows the accessibility state automatically, so they can never disagree.
:::

## 📚 Keep learning

- [Tailwind CSS docs: Responsive design](https://tailwindcss.com/docs/responsive-design)
- [Tailwind CSS docs: Hover, focus, and other states](https://tailwindcss.com/docs/hover-focus-and-other-states)
- [Tailwind CSS docs: Dark mode](https://tailwindcss.com/docs/dark-mode)
