# Architecture G · 03 — Compound components: accessible Tabs

> 🚫🤖 **No-AI** · ⏱️ ~90 min

A `<Tabs>` component with 12 props (`tabs`, `labels`, `renderPanel`, `activeClassName`, …) breaks every time a designer wants an icon in one tab. **Compound components** share state through context and let the caller compose the markup:

```tsx
<Tabs defaultValue="notes" onValueChange={track}>
  <Tabs.List aria-label="Application sections">
    <Tabs.Trigger value="notes">Notes</Tabs.Trigger>
    <Tabs.Trigger value="history">History</Tabs.Trigger>
    <Tabs.Trigger value="files" disabled>Files</Tabs.Trigger>
  </Tabs.List>
  <Tabs.Panel value="notes">…</Tabs.Panel>
  <Tabs.Panel value="history">…</Tabs.Panel>
</Tabs>
```

## `tabs.tsx` (`"use client"`)
- `Tabs` supports **uncontrolled** (`defaultValue`) and **controlled** (`value` + `onValueChange`) use — `onValueChange` is called when the user selects a tab
- `Tabs.List` → `role="tablist"`, passes other props (like `aria-label`) through
- `Tabs.Trigger` → `<button type="button" role="tab">` with `aria-selected`, `aria-controls` (its panel id), an `id`, and a **roving tabindex**: `0` on the selected tab, `-1` on the others; `disabled` supported
- `Tabs.Panel` → `role="tabpanel"`, `aria-labelledby` (its trigger id), `tabIndex={0}`; only the selected panel is rendered
- ids are unique per `Tabs` instance (`useId`) — two Tabs on one page must not clash
- keyboard on a tab (WAI-ARIA Tabs pattern, automatic activation): **ArrowRight/ArrowLeft** move focus **and** selection to the next/previous **enabled** tab, wrapping around; **Home/End** go to the first/last enabled tab
- using `Tabs.Trigger` or `Tabs.Panel` outside `Tabs` throws `"Tabs.Trigger must be used inside <Tabs>"` (or `Tabs.Panel`)

```bash
cd exercises/web
npx vitest run architecture/g-frontend-patterns/03-compound-components
```
