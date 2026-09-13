# M4 · W1 · 02 — Style a Job Card with Design Tokens

> 🚫🤖 **No-AI** · ⏱️ ~45 min

`index.html` (provided, don't edit) shows a list of job cards. Write **`styles.css`** from scratch. Open `index.html` in a browser as you go.

Rules checked by the tests:

| Area | Requirement |
|---|---|
| Design tokens | `:root` defines `--color-primary`, `--color-text`, `--color-muted`, `--color-surface`, `--radius`, `--space-1`, `--space-2`, `--space-4` |
| Reset | `*, *::before, *::after { box-sizing: border-box; }` |
| Body | `font-family` with **at least one fallback** ending in a generic family (`sans-serif`/`system-ui`); `line-height` without units (e.g. `1.5`); `color: var(--color-text)` |
| `.card` | `background` uses `var(--color-surface)`, `padding` uses a `--space-*` variable, `border-radius: var(--radius)` |
| `.card__title` | `font-size` in `rem` |
| `.card__meta` | `color: var(--color-muted)` |
| `.badge` and `.badge--remote` | `.badge` has `display: inline-block` and padding; the modifier `.badge--remote` changes `background` using `--color-primary` |
| States | `.button:hover` exists, and `.button:focus-visible` has an `outline` (never `outline: none` without a replacement) |
| Hygiene | no `#id` selectors, no `!important`, no `px` font sizes |

```bash
cd exercises/web
npx vitest run m4/w1/02-css-fundamentals
```
