# M4 · W1 · 03 — A Responsive Jobs Page (mobile first)

> 🚫🤖 **No-AI** · ⏱️ ~60 min

`index.html` (provided) has a header, a filter sidebar, a job list and a footer. Write **`layout.css`** mobile first: the base styles are for phones; `@media (min-width: …)` rules add columns on bigger screens. Resize your browser (or DevTools device mode) while you work.

| Selector | Requirement |
|---|---|
| `.container` | `max-width` in `rem` (e.g. `72rem`), `margin-inline: auto`, horizontal padding |
| `.site-header` | Flexbox: `display: flex`, `justify-content: space-between`, `align-items: center`, `flex-wrap: wrap`, a `gap` |
| `.page` | Grid: `display: grid` with a `gap` (one column on phones — no `grid-template-columns` in the base rule) |
| `@media (min-width: 48rem)` | `.page` gets two columns: a sidebar and flexible content, e.g. `grid-template-columns: 16rem 1fr` |
| `.jobs` | `display: grid`, `gap`, and a responsive column rule `grid-template-columns: repeat(auto-fill, minmax(<n>rem, 1fr))` |
| `img` | `max-width: 100%` and `height: auto` |
| Rules | media queries use `min-width` in `em`/`rem` (mobile first), no fixed `width` in `px` anywhere |

```bash
cd exercises/web
npx vitest run m4/w1/03-layout-responsive
```
