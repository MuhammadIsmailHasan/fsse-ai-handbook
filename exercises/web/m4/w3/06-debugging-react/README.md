# M4 · W3 · 06 — Bug Hunt: Five Real React Bugs

> 🚫🤖 **No-AI** · ⏱️ ~75 min · edit **`buggy-components.tsx`**

Each component in `buggy-components.tsx` matches a bug report from QA. Reproduce the bug (run the tests, or render the component in a small app), find the cause with **React DevTools** and `console.log`, and fix it with the smallest correct change. Keep the component's props and output the same.

| Component | Bug report |
|---|---|
| `SavedList` | "I click **Save**, nothing appears in the list. After I type in another field, suddenly it shows up." |
| `Stopwatch` | "The timer goes 0 → 1 and then stops. After closing the dialog, the console shows a warning / it keeps ticking in the background." |
| `NotesEditor` | "I have notes A, B, C. I delete A — now the text boxes show A and B instead of B and C." |
| `FiltersPanel` | "The page freezes as soon as the filters panel appears." (React: *Maximum update depth exceeded*) |
| `ProfileHeader` | "The page crashes when a user is promoted to admin while it's open." (React: *Rendered more hooks than during the previous render*) |

Write a one-line comment above each fix: **cause → fix** (you'll reuse these for the lesson's quick check and interviews).

```bash
cd exercises/web
npx vitest run m4/w3/06-debugging-react
```
