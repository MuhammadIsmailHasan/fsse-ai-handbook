# M4 · W5 · 09 — Zustand for shared client UI state

> 🤖✅ **AI-allowed** · ⏱️ ~75 min · ⚪ optional

Server data belongs in **TanStack Query** / Server Components. Zustand is for **client-only UI state** shared by distant components — here: the "compare jobs" tray (pick up to 3 jobs anywhere on the page).

In Next.js, don't use a **module-level global store** for anything that could differ between users during server rendering. Use the recommended pattern: **create the store per provider** and read it with `useStore(store, selector)`.

## `compare-store.tsx` (`"use client"`)
1. `createCompareStore(initial?: Partial<{ jobIds: number[]; isTrayOpen: boolean }>)` → a vanilla store (`createStore` from `zustand/vanilla`) with state
   - `jobIds: number[]` (default `[]`), `isTrayOpen: boolean` (default `false`)
   - `toggleJob(id): "added" | "removed" | "full"` — removes if selected; otherwise adds if fewer than **3** (and opens the tray); otherwise returns `"full"` without changing state
   - `clear()` — empties `jobIds` and closes the tray
   - `setTrayOpen(open)`
   - wrapped in **`persist`** middleware: name `"careerpilot-compare"`, `localStorage` via `createJSONStorage`, **`partialize` to persist only `jobIds`**
2. `<CompareStoreProvider initial?>` creates the store **once** (`useState(() => createCompareStore(initial))`)
3. `useCompareStore(selector)` → `useStore(store, selector)`; throws `"useCompareStore must be used inside <CompareStoreProvider>"` without a provider
4. selectors: `selectCount(state)`, `selectIsSelected(id)(state)`
5. components:
   - `CompareButton({ jobId })` → `<button aria-pressed>` text `Compare`; subscribes **only** to whether this job is selected (so toggling job 2 doesn't re-render job 1's button). If the result is `"full"`, show `<span role="status">You can compare up to 3 jobs</span>`.
   - `CompareTray()` → when open, `<aside aria-label="Compare jobs">` with heading `Compare ({count}/3)` and a `Clear` button

```bash
cd exercises/web
npx vitest run m4/w5/09-zustand
```
