# M4 · W1 · 05 — An Interactive Job Board with the DOM

> 🚫🤖 **No-AI** · ⏱️ ~75 min · edit **`job-board.js`**

`mountJobBoard(root, jobs)` builds this UI inside `root` (no frameworks):

```html
<form role="search">
  <label for="job-search">Search jobs</label>
  <input id="job-search" type="search">
</form>
<p aria-live="polite">3 jobs · 0 saved</p>
<ul>
  <li data-id="1">
    <h2>Backend Engineer</h2>
    <p>Kopi Data · Jakarta</p>
    <button type="button" aria-pressed="false">Save</button>
  </li>
  …
</ul>
```

| Behavior | Requirement |
|---|---|
| Rendering | one `<li data-id>` per job with the title in `<h2>` and `"{company} · {city}"` in `<p>`. Use `textContent` / `createElement` — job data must **never** be parsed as HTML (a test uses a malicious title) |
| Search | typing in the input (the `input` event) shows only jobs whose title or company contains the text, case-insensitive; the status becomes `"{shown} jobs · {saved} saved"` |
| Empty state | when nothing matches, the list is empty and a `<p class="empty">No jobs match "{text}"</p>` is shown (removed again when results return) |
| Save | clicking a job's button toggles `aria-pressed` and its text between `Save` / `Saved`, and updates the saved count. Saved state survives searching |
| Submit | pressing Enter in the search must not reload the page (`preventDefault`) |
| Event delegation | exactly **one** click listener, on the `<ul>` — not one per button (a test checks) |
| Return | `mountJobBoard` returns a function that removes everything it added (cleanup) |

```bash
cd exercises/web
npx vitest run m4/w1/05-dom-events
```
