---
title: "🔥 Accessibility Basics"
summary: Build pages everyone can use — the four WCAG principles, keyboard use and focus, names and roles, ARIA done right, form errors people can find, and how to test with tools and screen readers.
type: lesson
source: original
roles: { be: optional, fe: core, fs: core, ai: recommended, ops: none }
durationMinutes: 150
tags: [accessibility, a11y, wcag, aria, keyboard, forms]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Who accessibility helps, and the four WCAG principles
- Making everything work with a keyboard, and moving focus correctly
- Giving every control a role, a name and a state
- When to use ARIA — and when not to
- Form errors that screen reader users can find
- Testing with tools, the keyboard and a screen reader

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Accessibility (a11y)** | Making a page usable for everyone, including people with disabilities | Aksesibilitas |
| **WCAG** | The international rulebook for web accessibility | Pedoman aksesibilitas web |
| **Focus** | The element that keyboard keys currently act on | Fokus |
| **Screen reader** | Software that reads the page aloud (VoiceOver, NVDA, TalkBack) | Pembaca layar |
| **Accessible name** | The name a screen reader says for an element ("Save, button") | Nama yang dibacakan |
| **ARIA** | Extra HTML attributes that tell screen readers what something is | Atribut penjelas |
| **Live region** | An area whose changes are read aloud automatically | Area yang diumumkan |

## 🧠 The big idea

Accessibility is like a **ramp next to the stairs**. It is built for wheelchair users, but parents with strollers, travelers with suitcases and delivery drivers use it every day too. Captions help people on noisy trains; clear error messages help everyone. Building for people at the edges makes the product better for all.

## ❓ Why it matters

- People use the web with screen readers, only a keyboard, voice control or zoom — some permanently, some for a while (a broken arm), some in a moment (bright sunlight on a phone).
- Many laws and companies require it (WCAG 2.2 level AA is the usual target).
- Automated tests, Google and AI agents also rely on accessible HTML.

What goes wrong without it:

- A job seeker using VoiceOver can't find "Apply" because it's a `<div>`.
- A keyboard user opens a popup, but focus stays **behind** it.
- "Invalid input" appears in red, but a screen reader never says it.
- Custom tabs look nice, but arrow keys do nothing.

## 📖 Step by step

### 1. The four WCAG principles (POUR)

| Principle | Means | Examples |
|---|---|---|
| **Perceivable** | People can see or hear the content | alt text, captions, enough contrast, not only color |
| **Operable** | People can use it | works with a keyboard, visible focus, big enough buttons |
| **Understandable** | People understand it | clear labels and errors, predictable navigation |
| **Robust** | Tools can read it | correct HTML that assistive tools understand |

### 2. Role, name and state

A screen reader describes each control with three things — like a **name badge** at an event: *who you are* (role), *your name* (name), *what you're doing now* (state).

- **Role**: button, link, tab, checkbox.
- **Name**: from visible text, a `<label>`, `aria-label` or `aria-labelledby`.
- **State**: pressed, expanded, selected, invalid, disabled (`aria-pressed`, `aria-expanded`, `aria-selected`, `aria-invalid`, `disabled`).

Real HTML elements give you these for free. Check them in DevTools → Elements → **Accessibility**.

### 3. Keyboard use and focus

- `Tab` / `Shift+Tab` move between controls in HTML order.
- `Enter` presses links and buttons; `Space` presses buttons and checkboxes.
- A group like tabs or a menu is **one Tab stop**. Inside it, the arrow keys move. This is called **roving tabindex** — like a microphone passed around a table: only the person holding it (`tabindex="0"`) can be reached with Tab.

```js
buttons.forEach((button, i) => {
  button.tabIndex = i === selectedIndex ? 0 : -1;   // only the active tab is in the Tab order
});
```

- Never use `tabindex` greater than 0 — it breaks the natural order.
- **Move focus** when the page changes, like a guide walking you to the next room:
  - open a dialog → focus inside it;
  - close it → focus back on the button that opened it;
  - a form has errors → focus the first error;
  - go to a new page in a single-page app → focus the new page's heading.

### 4. The first rule of ARIA

> If a normal HTML element already does what you need, **use it instead of ARIA**.

ARIA only changes what is **announced**, not how it **behaves**. Putting `role="button"` on a `div` is like putting a "door" sticker on a wall: people are told it's a door, but it still doesn't open. The `div` still can't be focused or pressed with Enter.

Use ARIA only for patterns HTML doesn't have (tabs, comboboxes, live regions), and follow the official WAI-ARIA patterns exactly.

### 5. Example: tabs

```html
<div role="tablist">
  <button role="tab" id="tab-saved" aria-controls="panel-saved" aria-selected="true" tabindex="0">Saved</button>
  <button role="tab" id="tab-applied" aria-controls="panel-applied" aria-selected="false" tabindex="-1">Applied</button>
</div>
<div role="tabpanel" id="panel-saved" aria-labelledby="tab-saved">…</div>
<div role="tabpanel" id="panel-applied" aria-labelledby="tab-applied" hidden>…</div>
```

- `aria-selected` says which tab is active; `aria-controls` connects a tab to its panel.
- Keyboard: `ArrowRight`/`ArrowLeft` move to the next tab (and wrap around), `Home`/`End` jump to the first/last.

### 6. Form errors people can find

```html
<label for="email">Email</label>
<input id="email" type="email" aria-invalid="true" aria-describedby="email-error" />
<p id="email-error">Enter a valid email address</p>
```

- Put the error **text** next to the field (not only a red border).
- `aria-describedby` connects the message to the field, so the screen reader reads it — like a sticky note attached to the right box.
- `aria-invalid="true"` marks the field as wrong; remove it when fixed.
- Move focus to the first wrong field.
- For messages like "Application saved", use a polite live region so it's read aloud.

### 7. Things people see

- Contrast: at least 4.5:1 for normal text; 3:1 for large text, icons and focus rings.
- Don't use color alone to show meaning (status badges also show text).
- The page must work at 200% zoom; respect `prefers-reduced-motion`.
- Buttons at least 24×24 px (about 44×44 px is better on touch screens).

### 8. Testing

| How | Finds |
|---|---|
| **Keyboard only** (put the mouse away) | controls you can't reach, missing focus rings, focus traps |
| **Screen reader** (VoiceOver `Cmd+F5` on Mac, NVDA on Windows, TalkBack on Android) | wrong names, missing announcements, strange reading order |
| **axe DevTools / Lighthouse** | about 30–50% of problems automatically (contrast, missing labels) |
| **Testing Library `getByRole`** | tests fail if elements have no role or name |
| **Playwright + axe** | automatic checks in CI (Week 6) |

Tools can't judge whether alt text is useful or whether the focus order makes sense. You still need a quick manual check.

## ⚠️ Common mistakes

- Placeholder instead of a label; icon-only buttons with no name.
- `tabindex="0"` on everything, or values above 0.
- Popups (modals) that don't keep focus inside and don't return it when closed.
- `aria-label` that says something different from the visible text (voice control users say what they see).
- Hiding focus outlines or turning off zoom (`user-scalable=no`).
- Adding ARIA to "fix" a `div` when a real `<button>` exists.

## 🏆 Best practices

- [ ] Real HTML elements first; ARIA only for patterns HTML doesn't have.
- [ ] Everything works with the keyboard, with a visible `:focus-visible` style.
- [ ] Move focus for dialogs, page changes and form errors.
- [ ] Every input has a label; errors are text, connected with `aria-describedby`, with `aria-invalid`.
- [ ] Check contrast; never show meaning with color alone.
- [ ] Use `getByRole` in tests and run axe in CI.
- [ ] Before merging a UI change, spend 5 minutes with only the keyboard and a screen reader.
- [ ] For complex widgets, use a tested library (Radix / shadcn/ui — Week 5).

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a product manager why "Lighthouse gave us 100" doesn't prove the job application flow is accessible, and which two manual checks you'd do before release.

## 📐 Design it

Plan the accessibility of CareerPilot's **"Move application" dialog** (opened from a card on the board). It shows the current status, radio options for the next status, an optional note, and Save/Cancel. Cover roles, names, keyboard, focus, errors and announcements.

:::quiz
Show a possible plan

- **Button that opens it**: `<button aria-haspopup="dialog">Move "Backend Engineer at Kopi Data"</button>` — a specific name, not just "Move".
- **Dialog**: the native `<dialog>` opened with `showModal()` (keeps focus inside and closes with Escape for free). `aria-labelledby` points to its heading "Move application"; `aria-describedby` points to "Currently: Applied".
- **Focus**: when it opens, focus the first radio; Tab stays inside; Escape and Cancel close it; when it closes, **focus goes back to the button that opened it**.
- **Options**: `<fieldset><legend>Next status</legend>` with normal radio buttons (arrow keys work automatically). Moves that aren't allowed are not listed.
- **Note**: a `<textarea>` with a label.
- **Errors**: no status chosen → the message is connected with `aria-describedby`, and focus moves to the first radio. A server error (409) is shown inside the dialog with `role="alert"`.
- **Success**: close the dialog, return focus, and announce "Moved to Interview" in the page's polite live region.
- **Visual**: visible focus rings, enough contrast, status not shown by color alone, works at 200% zoom and on phones.
- **Tests**: `getByRole("dialog", { name: "Move application" })`, keyboard flows with user-event, and an axe check.
:::

### 📝 Self-review checklist

- [ ] Every control has a role, a name and (if needed) a state
- [ ] Focus goes in, stays in, and comes back
- [ ] Errors are connected to fields and read aloud
- [ ] Success is announced without jumping focus around

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w1/08-accessibility" ai="no-ai" title="Accessible tabs and form errors"}
Build the ARIA tabs pattern (roles, ids, roving tabindex, arrow/Home/End keys, hidden panels) and form validation that marks wrong fields, connects error messages with `aria-describedby` and focuses the first error. The tests find elements by role and name — markup that isn't accessible can't pass.
:::

:::hints
- Write `select(index, { focus })` that updates `aria-selected`, `tabIndex` and `hidden` for all tabs at once.
- Listen for `keydown` on the tablist; use `document.activeElement` to find the current tab; call `event.preventDefault()` for keys you handle.
- `firstInvalid ??= input` remembers only the first wrong field.
:::

## ✅ Quick check

:::quiz
What is the first rule of ARIA?

Don't use ARIA if a normal HTML element or attribute already gives the meaning and behavior you need.
:::

:::quiz
What does roving tabindex do?

A group like tabs takes only one Tab stop; arrow keys move inside it. Only the active item has `tabindex="0"`, the rest have `-1`.
:::

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
