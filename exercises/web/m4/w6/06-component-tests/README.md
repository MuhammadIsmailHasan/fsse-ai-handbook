# M4 · W6 · 06 — Component tests with Vitest + Testing Library

> 🚫🤖 **No-AI** · ⏱️ ~90 min · 🧪 **graded by 9 mutants**

`applications-table.tsx` is finished. Your job is to write `applications-table.test.tsx` so that it **passes** on the real component and **fails** on each of the 9 copies in `mutants/` (each has one bug). Don't open the mutants until you're done — test the behavior below like a user would.

## Behavior
Props: `applications` (rows with `id, role, company, status, appliedOn` as `YYYY-MM-DD`) and `onDelete(id): Promise<void>`.

- The table's caption (accessible name) is **"{n} applications"** — and **"1 application"** for one row
- Rows are sorted by **Applied on, newest first**; the column header has `aria-sort="descending"`
- Clicking the **Applied on** header button reverses the order and updates `aria-sort`
- **Search** (label "Search") matches **role or company**, **case-insensitive**, ignoring surrounding spaces
- **Status** select filters rows (`All`, `Applied`, …)
- When nothing matches: **"No applications match your filters"** and a **Clear filters** button that resets **both** search and status
- Each row has a button labelled **"Delete {role}"**: it calls `onDelete` with that row's **id**; while waiting it's **disabled** and shows **"Deleting…"**; if `onDelete` rejects, an alert says **"Couldn't delete {role}"**

## Testing Library habits
- Query like a user: `getByRole`, `getByLabelText`, `getByText`; `within(row)` for one row
- `userEvent.setup()` + `await user.click/type/selectOptions`
- `findBy…` / `vi.waitFor` for async results; a manually-resolved Promise to test pending states
- Test behavior, not implementation (no state, no class names)

```bash
cd exercises/web
npx vitest m4/w6/06-component-tests/applications-table.test.tsx   # watch your tests
npx vitest run m4/w6/06-component-tests                             # tests + grader
```
