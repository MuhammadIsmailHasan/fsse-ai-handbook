---
title: "🔥 Component Tests with Vitest + Testing Library"
summary: Test React components the way users use them — Vitest setup for Next.js, Testing Library queries, user-event, async UI, mocking modules and fetch, testing hooks, what not to test, and measuring test quality with mutation testing.
type: lesson
source: original
roles: { be: none, fe: core, fs: core, ai: optional, ops: none }
durationMinutes: 150
tags: [vitest, testing-library, react, component-testing, mocking, mutation-testing]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Why component tests are the **best value** tests for a React UI
- Vitest + jsdom + Testing Library setup in a Next.js project
- Query priority: `getByRole` → `getByLabelText` → `getByText` → `getByTestId`
- `getBy` vs `queryBy` vs `findBy`
- `userEvent` for realistic interactions
- Testing async states (pending, success, error) with controllable Promises
- Mocking: modules (`vi.mock`), `fetch`, Next.js navigation, timers
- Testing custom hooks with `renderHook`
- What **not** to test, and how mutation testing measures test quality

## 🧠 The big idea

Testing Library's guiding principle: **the more your tests resemble the way your software is used, the more confidence they give you.** A user doesn't know your component has a `useState` called `deletingId` — they see a button that says "Deleting…" and can't be clicked twice. Test **that**.

Component tests are a **flight simulator**: realistic enough to practice every emergency (errors, slow networks, empty states) in milliseconds, without the cost of flying the real plane (E2E).

## ❓ Why does this exist?

E2E tests are slow and need a running app, API and database. Unit tests of pure functions miss UI wiring. Component tests render a real React tree in jsdom (a simulated DOM), click and type like a user, and run hundreds of cases per second — perfect for tables, forms, dialogs, conditional rendering and accessibility.

## 💥 What happens if we DON'T (or test the wrong way)?

```tsx
// ❌ implementation-detail tests
expect(wrapper.state("deletingId")).toBe(13);                 // breaks on refactor to useReducer
expect(container.querySelector(".btn-danger")).toBeTruthy();  // breaks on a CSS change, misses a11y
expect(asFragment()).toMatchSnapshot();                       // 400-line snapshot nobody reads; "update snapshot" on every change
```

These tests fail when you refactor correctly and pass when behavior breaks — the worst of both.

## 📖 How it works, step by step

### 1. Setup in a Next.js project

```bash
npm install -D vitest @vitejs/plugin-react jsdom @testing-library/react @testing-library/dom @testing-library/user-event @testing-library/jest-dom vite-tsconfig-paths
```

```ts
// vitest.config.mts
import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [tsconfigPaths(), react()],
  test: { environment: "jsdom", setupFiles: ["./vitest.setup.ts"], restoreMocks: true },
});
```

```ts
// vitest.setup.ts
import "@testing-library/jest-dom/vitest";   // toBeInTheDocument, toBeDisabled, toHaveAccessibleDescription…
```

Async **Server Components** aren't supported by Vitest rendering yet — test their data functions as units, their client children as components, and whole pages with E2E.

### 2. Queries

| Query | No match | Many matches | Async? | Use for |
|---|---|---|---|---|
| `getBy…` | throws | throws | no | elements that must be there |
| `queryBy…` | `null` | throws | no | asserting something is **absent** |
| `findBy…` | rejects after timeout | rejects | **yes** | elements that appear later |
| `getAllBy…` / `queryAllBy…` / `findAllBy…` | — | array | — | lists |

Priority: `getByRole("button", { name: "Delete Backend Engineer" })` → `getByLabelText("Search")` → `getByText("No applications match your filters")` → `getByTestId` as a last resort. Use `within(row)` to scope to one part of the UI, and `screen.debug()` / `screen.logTestingPlaygroundURL()` when stuck.

### 3. Interactions with `userEvent`

```tsx
const user = userEvent.setup();
render(<ApplicationsTable applications={rows} onDelete={onDelete} />);

await user.type(screen.getByLabelText("Search"), "  FRONTEND ");
await user.selectOptions(screen.getByLabelText("Status"), "offer");
await user.click(screen.getByRole("button", { name: "Applied on" }));
await user.keyboard("{Escape}");
```

`userEvent` fires the full event sequence a browser would (focus, keydown, input, keyup, click) — `fireEvent` fires just one event; use it only when you need that control (e.g. with fake timers).

### 4. Async states with a controllable Promise

```tsx
test("deletes by id with a pending state", async () => {
  let finish!: () => void;
  const onDelete = vi.fn(() => new Promise<void>((resolve) => (finish = resolve)));
  const user = userEvent.setup();
  render(<ApplicationsTable applications={rows} onDelete={onDelete} />);

  await user.click(screen.getByRole("button", { name: "Delete Frontend Developer" }));
  expect(onDelete).toHaveBeenCalledWith(13);
  const button = screen.getByRole("button", { name: "Delete Frontend Developer" });
  expect(button).toBeDisabled();
  expect(button).toHaveTextContent("Deleting…");

  finish();                                              // now let the request complete
  await vi.waitFor(() => expect(button).toBeEnabled());
});
```

Resolving the Promise **yourself** lets you assert the in-between state deterministically — no sleeps.

### 5. Mocking

```tsx
// Next.js navigation
const push = vi.fn();
vi.mock("next/navigation", () => ({ useRouter: () => ({ push, replace: vi.fn(), refresh: vi.fn() }), usePathname: () => "/jobs" }));

// A module your component imports
vi.mock("./lib/applications-client", () => ({ applicationsClient: { remove: vi.fn().mockResolvedValue(null) } }));

// fetch
vi.stubGlobal("fetch", vi.fn().mockResolvedValue(Response.json([{ id: 1 }])));

// timers
vi.useFakeTimers(); act(() => vi.advanceTimersByTime(4000));
```

- Mock at **boundaries** (network, router, time, browser APIs), not your own child components.
- For many API-driven components, **MSW (Mock Service Worker)** intercepts requests at the network level and can be shared between tests, Storybook and local development.
- Wrap components that need providers (TanStack Query, context) in a custom `renderWithProviders` helper; create a **new QueryClient per test** with `retry: false`.

### 6. Hooks

```tsx
const { result, rerender } = renderHook(({ value }) => useDebouncedValue(value, 300), { initialProps: { value: "d" } });
```

Prefer testing hooks through a component that uses them; use `renderHook` for reusable hooks with many cases.

### 7. What not to test

- Internal state, private functions, CSS class names.
- Third-party library behavior (Radix already tests its focus trap — test **your** usage: title, confirm action, pending state).
- Large snapshots. Small inline snapshots of stable, meaningful output are fine.

### 8. Are the tests any good? Mutants again

The exercise gives you a finished component and 9 mutants. A test suite with 100% coverage can still let most of them survive:

```tsx
test("renders", () => {
  render(<ApplicationsTable applications={rows} onDelete={vi.fn()} />);
  expect(screen.getByRole("table")).toBeInTheDocument();       // covers most lines, kills almost nothing
});
```

For real projects, **Stryker** runs mutation testing on Vitest suites; use it on critical modules (permissions, pricing, validation).

## ⚖️ Trade-offs

| | ✅ | ❌ |
|---|---|---|
| Component tests (jsdom) | fast, realistic interactions, a11y-oriented queries | no real layout/CSS, no real browser APIs |
| Vitest Browser Mode / Playwright component testing | real browser rendering | slower, more setup |
| E2E | full confidence for journeys | slow, flaky if overused |
| Snapshots | quick to write | brittle, rarely reviewed |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ Forms, tables, filters, dialogs, conditional rendering, loading/error/empty states, accessibility names.
- ✅ Regression tests for UI bugs found in production.
- 🚫 Visual layout (use visual regression/E2E screenshots).
- 🚫 Async Server Components and full routing (use E2E).

## 🏆 Best practices

- [ ] Query by role/label/text; `within` to scope; `getByTestId` last.
- [ ] `userEvent.setup()` per test; `await` every interaction.
- [ ] `findBy` / `vi.waitFor` for async; controllable Promises for pending states; never `setTimeout` sleeps.
- [ ] Test the three states of async UI: pending, success, error — plus empty.
- [ ] Mock boundaries (network, router, timers), not children; reset mocks between tests (`restoreMocks`).
- [ ] New providers/clients per test; no shared mutable state.
- [ ] Each test: one behavior, named like a spec sentence.
- [ ] Run tests in CI on every PR; check test quality with mutations on critical code.

## 🏭 How it's used in industry

- Testing Library is the de facto standard for React component testing, and Vitest has become a popular default for Vite and many Next.js projects (Jest remains common in older codebases).
- Teams combine component tests with Storybook stories (interaction tests, accessibility checks) and a small E2E layer.
- Frontend interviews often include "write tests for this component" — role-based queries and async testing are what reviewers look for.

## ⚠️ Common mistakes

- `getBy` to assert absence (throws) → use `queryBy` + `not.toBeInTheDocument()`.
- Forgetting `await` on `user.click` → assertions run before updates.
- Expecting instant updates after async work → use `findBy`.
- "not wrapped in act(...)" warnings ignored — they usually mean an update happened after the test finished; await the final state.
- Test data that accidentally matches multiple rows (e.g. searching "data" matches both a role and a company).

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a teammate why `expect(screen.getByRole("table")).toBeInTheDocument()` can give 90% coverage and almost no confidence, using the flight simulator analogy.

## 📐 Design it

List the component tests for CareerPilot's **ApplicationForm** from W5 (React Hook Form + Zod, company select loaded from the API, dynamic skills rows, server errors, pending state). For each test: arrange, act, assert — and what you mock.

:::quiz
Show a possible list

| Test | Arrange / mock | Act | Assert |
|---|---|---|---|
| loads companies | `fetch`/MSW returns 2 companies | render | "Loading companies…" then options appear (`findAllByRole("option")`) |
| company load error | MSW returns 500 | render | alert "Couldn't load companies" + Retry button refetches |
| required fields | companies loaded | click Save | messages for role/company, `aria-invalid`, `onSubmit` not called |
| skills rows | — | Add skill ×2, type, remove first | remaining row keeps its typed value; Add disabled at max |
| salary refinement | — | min 20, max 10, blur | "Maximum must be at least the minimum" on max |
| pending | `onSubmit` returns a controllable Promise | fill valid + Save | button disabled "Saving…"; resolve → enabled |
| server field error | `onSubmit` resolves `{ fieldErrors: { role: "Already applied" } }` | submit | message under Role, focus moves to Role |
| success | `onSubmit` resolves `undefined` | submit | status "Application saved", form reset (not dirty) |

Mocks: network via MSW (or `fetch` stub), `next/navigation` router if the form redirects. Not mocked: RHF, Zod, child inputs.
:::

### 📝 Self-review checklist

- [ ] Pending, success, error and empty states covered
- [ ] Only boundaries mocked
- [ ] Every assertion is user-visible

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w6/06-component-tests" ai="no-ai" title="Tests that kill 9 mutants"}
Write Vitest + Testing Library tests for a finished applications table (sorting, search, status filter, empty state, delete pending and error). The grader runs your tests against the real component and 9 mutants.
:::

:::hints
- Read each rule in the README and ask: "what would a user see if this were broken?"
- Choose test data where a search matches **only** role or **only** company.
- A pending-state assertion needs a Promise you resolve yourself.
:::

## ✅ Quick check

:::quiz
When do you use `queryByText` instead of `getByText`?

When asserting that something is **not** there: `expect(screen.queryByText("Error")).not.toBeInTheDocument()`. `getBy` would throw before the assertion.
:::

:::quiz
Why create a new TanStack `QueryClient` for every test?

The cache would otherwise leak data between tests, making results depend on test order.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Component test | Tes komponen |
| Query (Testing Library) | Cara mencari elemen di DOM |
| Mock | Tiruan untuk dependensi |
| jsdom | DOM simulasi di Node.js |
| Coverage | Cakupan kode yang dijalankan tes |
| Mutation testing | Pengujian mutasi (menilai kualitas tes) |

## 📚 Keep learning

- Next.js docs (bundled): Testing → Vitest
- [Testing Library: Guiding principles](https://testing-library.com/docs/guiding-principles) · [Which query should I use?](https://testing-library.com/docs/queries/about#priority)
- [Kent C. Dodds: Common mistakes with React Testing Library](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
- [MSW docs](https://mswjs.io/docs)
