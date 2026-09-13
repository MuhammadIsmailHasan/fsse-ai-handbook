---
title: "🔥 Accessibility Basics"
summary: Build interfaces everyone can use — WCAG principles, keyboard access and focus management, accessible names, ARIA patterns done right, accessible forms and errors, and testing with tools and screen readers.
type: lesson
source: original
roles: { be: optional, fe: core, fs: core, ai: recommended, ops: none }
durationMinutes: 150
tags: [accessibility, a11y, wcag, aria, keyboard, forms]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Who accessibility is for, and **WCAG**'s four principles (POUR)
- Keyboard access: focus order, visible focus, **roving tabindex**, focus management
- Accessible names, roles and states — the accessibility tree
- The first rule of ARIA, and implementing a real ARIA pattern (tabs)
- Accessible form errors with `aria-invalid` and `aria-describedby`
- Testing: axe, Lighthouse, keyboard-only, screen readers, Testing Library's role queries

## 🧠 The big idea

Accessibility is a **ramp next to the stairs**: built for wheelchair users, used daily by parents with strollers, travelers with luggage and delivery workers. Captions help people in noisy trains; keyboard shortcuts help power users; clear error messages help everyone. Designing for the edges improves the product for all.

## ❓ Why does this exist?

- People use the web with screen readers, keyboards, switch devices, voice control, zoom, and high-contrast modes — permanently, temporarily (broken arm) or situationally (bright sunlight).
- Laws and procurement rules require it (WCAG 2.2 AA is the common target).
- Accessible markup is what automated tests, search engines and AI agents rely on too.

## 💥 What happens if we DON'T?

- A job seeker using VoiceOver can't find the "Apply" button because it's a `<div>`.
- A keyboard user tabs into a modal… and focus goes behind it.
- "Invalid input" appears in red above the form, but a screen reader never announces it and it isn't linked to the field.
- Custom tabs look great but the arrow keys do nothing and the reader announces "clickable, clickable, clickable".

## 📖 How it works, step by step

### 1. WCAG's POUR principles

| Principle | Examples |
|---|---|
| **Perceivable** | text alternatives, captions, contrast ≥ 4.5:1, don't rely on color alone |
| **Operable** | everything works with a keyboard, visible focus, no keyboard traps, enough time, target size |
| **Understandable** | clear labels and errors, predictable navigation, language set |
| **Robust** | valid semantic markup that assistive tech can interpret |

### 2. The accessibility tree: role, name, state

Every interactive element needs:
- a **role** (button, link, tab, checkbox),
- an **accessible name** (visible text, `<label>`, `aria-label`, `aria-labelledby`),
- **state** when relevant (`aria-pressed`, `aria-expanded`, `aria-selected`, `aria-invalid`, `disabled`).

Native elements provide these for free. Inspect them in DevTools → Elements → **Accessibility** panel.

### 3. Keyboard access

- `Tab` / `Shift+Tab` move between interactive elements in **DOM order**.
- `Enter` activates links and buttons; `Space` activates buttons and checkboxes.
- Composite widgets (tabs, menus, listboxes) are **one Tab stop**; arrow keys move inside them — the **roving tabindex** technique:

```js
buttons.forEach((button, i) => {
  button.tabIndex = i === selectedIndex ? 0 : -1;   // only the active tab is in the Tab order
});
```

- Never use positive `tabindex` values (they break the natural order).
- **Manage focus** when context changes: open a dialog → focus inside it; close → return focus to the button that opened it; submit an invalid form → focus the first error; navigate in a single-page app → focus the new page heading.

### 4. The first rule of ARIA

> If a native HTML element or attribute gives you the semantics and behavior you need, **use it instead of ARIA**.

ARIA changes what's **announced**, not how things **behave** — `role="button"` on a `div` doesn't make it focusable or respond to Enter. When you do need ARIA (tabs, comboboxes, live regions), follow the WAI-ARIA Authoring Practices patterns exactly.

### 5. A real pattern: tabs

```html
<div role="tablist">
  <button role="tab" id="tab-saved" aria-controls="panel-saved" aria-selected="true" tabindex="0">Saved</button>
  <button role="tab" id="tab-applied" aria-controls="panel-applied" aria-selected="false" tabindex="-1">Applied</button>
</div>
<div role="tabpanel" id="panel-saved" aria-labelledby="tab-saved">…</div>
<div role="tabpanel" id="panel-applied" aria-labelledby="tab-applied" hidden>…</div>
```

Keyboard: `ArrowRight`/`ArrowLeft` move (wrapping), `Home`/`End` jump. Selection follows focus.

### 6. Accessible form errors

```html
<label for="email">Email</label>
<input id="email" type="email" aria-invalid="true" aria-describedby="email-error" />
<p id="email-error">Enter a valid email address</p>
```

- Errors next to fields, in text (not only red borders), linked with `aria-describedby`.
- `aria-invalid="true"` on invalid fields; remove it when fixed.
- Move focus to the first invalid field (or to an error summary that links to fields).
- Announce async results ("Application saved") with a polite live region.

### 7. Visual accessibility

- Contrast: 4.5:1 normal text, 3:1 large text and UI component borders/focus indicators.
- Don't convey meaning with color alone (status badges show text or icons too).
- Support zoom to 200% and text resizing; respect `prefers-reduced-motion`.
- Target size: at least 24×24 CSS px (WCAG 2.2), ideally ~44×44 on touch.

### 8. Testing accessibility

| Method | Catches |
|---|---|
| **Keyboard only** (unplug the mouse) | traps, missing focus styles, unreachable controls |
| **Screen reader** (VoiceOver `Cmd+F5`, NVDA on Windows, TalkBack on Android) | names, announcements, reading order |
| **axe DevTools / Lighthouse** | ~30–50% of issues automatically (contrast, missing labels, ARIA errors) |
| **Testing Library `getByRole`** | tests fail if elements lack roles/names — accessibility baked into tests |
| **`jest-axe` / Playwright + axe** | automated checks in CI (Week 6) |

Automated tools can't judge whether alt text is meaningful or focus order makes sense — manual checks still matter.

## ⚖️ Trade-offs

| Choice | ✅ | ❌ |
|---|---|---|
| Native elements | accessible by default | styling some (select, date) is limited |
| Custom widgets + ARIA | full design control | must implement keyboard, focus and states exactly |
| Headless accessible libraries (Radix, React Aria) | patterns done right, you style them | a dependency |
| Automated checks only | cheap, in CI | miss many real issues |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ From the first line of HTML — retrofitting is expensive.
- ✅ Use proven accessible component libraries for complex widgets (Week 5: shadcn/ui on Radix).
- 🚫 Don't add ARIA to "fix" non-semantic markup when a native element exists.
- 🚫 Don't hide focus outlines or disable zoom (`user-scalable=no`).

## 🏆 Best practices

- [ ] Semantic HTML first; ARIA only for patterns HTML lacks, following the ARIA Authoring Practices.
- [ ] Every control reachable and operable by keyboard, with a visible `:focus-visible` style.
- [ ] Manage focus on dialogs, route changes and validation errors.
- [ ] Every input has a label; errors are text, linked via `aria-describedby`, with `aria-invalid`.
- [ ] Contrast and color-independence checked; respect reduced motion.
- [ ] Use role-based queries in tests (`getByRole`) and run axe in CI.
- [ ] Do a 5-minute keyboard + screen reader pass before merging UI changes.

## 🏭 How it's used in industry

- Many companies include accessibility in their Definition of Done and run axe checks in CI.
- Government and education sites (and their vendors) must meet WCAG 2.x AA; the European Accessibility Act applies to many digital products and services sold in the EU since June 2025.
- Testing Library's philosophy ("test the way users use your app") made role-based queries the default in React teams.

## ⚠️ Common mistakes

- Placeholder as label; icon-only buttons with no accessible name.
- `tabindex="0"` on everything, or positive tabindex values.
- Modals without focus trapping and return focus.
- `aria-label` that contradicts visible text (voice control users say what they see).

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a product manager why "it passed Lighthouse 100" doesn't mean the job application flow is accessible, and what two manual checks you'd do before release.

## 📐 Design it

Design the accessibility requirements for CareerPilot's **"Move application" dialog** (opened from a card on the board): it shows the current status, radio options for the next statuses, an optional note, and Save/Cancel. Cover roles, names, keyboard behavior, focus management, errors and announcements.

:::quiz
Show a possible spec

- **Trigger**: `<button aria-haspopup="dialog">Move "Backend Engineer at Kopi Data"</button>` (a specific accessible name, not just "Move").
- **Dialog**: native `<dialog>` opened with `showModal()` (focus trap + Escape for free) or a role="dialog" with `aria-modal="true"`; `aria-labelledby` → the dialog's `<h2>Move application</h2>`; `aria-describedby` → "Currently: Applied".
- **Focus**: on open, focus the first radio (or the heading if content is long); Tab cycles inside; Escape and Cancel close; on close, **return focus to the trigger**.
- **Options**: `<fieldset><legend>Next status</legend>` with native radios (arrow keys work natively); disallowed transitions are simply not listed (not just greyed out) — or `disabled` with an explanation.
- **Note**: labeled `<textarea>`; character counter announced politely only when near the limit.
- **Errors**: if no status is chosen, `aria-invalid` on the fieldset, message linked with `aria-describedby`, focus moves to the first radio. Server error (409 invalid_transition) shown in an alert region inside the dialog (`role="alert"`).
- **Success**: close the dialog, return focus, and announce "Moved to Interview" in the page's polite live region; the card's new column is reflected without moving focus unexpectedly.
- **Visuals**: focus rings visible, contrast checked, status never by color alone; works at 200% zoom and on mobile.
- **Tests**: Testing Library `getByRole("dialog", { name: "Move application" })`, keyboard flows with user-event, axe check in the component test.
:::

### 📝 Self-review checklist

- [ ] Names, roles and states for every control
- [ ] Focus in, trapped, and returned
- [ ] Errors linked and announced
- [ ] Success announced without stealing focus

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w1/08-accessibility" ai="no-ai" title="Accessible tabs and form errors"}
Implement the ARIA tabs pattern (roles, ids, roving tabindex, arrow/Home/End keys, hidden panels) and form validation that marks invalid fields, links error messages with `aria-describedby` and focuses the first error. Tests find elements by role and accessible name — inaccessible markup can't pass.
:::

:::hints
- Write `select(index, { focus })` that updates `aria-selected`, `tabIndex` and `hidden` for all tabs at once.
- Listen for `keydown` on the tablist; use `document.activeElement` to find the current tab; call `event.preventDefault()` for handled keys.
- `firstInvalid ??= input` remembers only the first invalid field.
:::

## ✅ Quick check

:::quiz
What is the first rule of ARIA?

Don't use ARIA if a native HTML element or attribute already provides the semantics and behavior you need.
:::

:::quiz
What does roving tabindex achieve?

A composite widget (tabs, toolbar, menu) takes one Tab stop; arrow keys move focus within it, by keeping `tabindex="0"` only on the active item and `-1` on the rest.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Accessibility (a11y) | Aksesibilitas |
| WCAG | Pedoman aksesibilitas konten web |
| Accessible name | Nama yang diumumkan teknologi bantu |
| Focus management | Pengelolaan fokus keyboard |
| Assistive technology | Teknologi bantu (pembaca layar, kontrol suara) |
| Keyboard trap | Jebakan keyboard — fokus tidak bisa keluar |

## 📚 Keep learning

- [W3C: WCAG 2.2 at a glance](https://www.w3.org/WAI/standards-guidelines/wcag/glance/)
- [ARIA Authoring Practices Guide — Tabs pattern](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/)
- [Testing Library: Which query should I use?](https://testing-library.com/docs/queries/about/#priority)
- [axe DevTools browser extension](https://www.deque.com/axe/devtools/)

## 📣 End of Week 1 — share your progress

:::linkedin{type="weekly"}
🌐 Week 1 of frontend, coming from a Python backend background.

- Rebuilt a "div soup" page with semantic HTML — then tried it with a screen reader. Eye-opening.
- Mobile-first layouts with Grid and Flexbox (one line: `repeat(auto-fill, minmax(16rem, 1fr))` 🤯)
- JavaScript for Python devs: `??` vs `||`, closures, and why `fetch` doesn't throw on a 500
- Built accessible tabs with keyboard navigation — tested with role-based queries

Biggest surprise: [your answer].

Next: TypeScript and Tailwind. 🚀

#Frontend #JavaScript #Accessibility #LearningInPublic
:::
