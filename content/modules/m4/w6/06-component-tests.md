---
title: "🔥 Component Tests with Vitest + Testing Library"
summary: Test React components the way users use them — Vitest setup for Next.js, Testing Library queries, user-event, loading and error states, mocking modules and fetch, testing hooks, what not to test, and checking test quality with mutants.
type: lesson
source: original
roles: { be: none, fe: core, fs: core, ai: optional, ops: none }
durationMinutes: 150
tags: [vitest, testing-library, react, component-testing, mocking, mutation-testing]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Why component tests give the **best value** for a React UI
- Vitest + jsdom + Testing Library setup in a Next.js project
- Query priority: `getByRole` → `getByLabelText` → `getByText` → `getByTestId`
- `getBy` vs `queryBy` vs `findBy`
- `userEvent` for realistic clicks and typing
- Testing async states (pending, success, error) with Promises you control
- Mocking: modules (`vi.mock`), `fetch`, Next.js navigation, timers
- Testing custom hooks with `renderHook`
- What **not** to test, and how mutation testing measures test quality

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Component test** | Render one component (with its children) and use it like a user | Tes komponen |
| **Vitest** | A fast test runner (like Jest) that works well with Vite | Alat menjalankan tes |
| **jsdom** | A fake browser page that runs inside Node.js | DOM simulasi |
| **Testing Library** | Helpers to find elements the way users see them (by role, label, text) | Pustaka pencari elemen |
| **Query** | A function that finds an element: `getByRole`, `findByText`… | Pencarian elemen |
| **Mock** | A fake version of something (network, router, a module) | Tiruan |
| **Implementation detail** | How the code works inside (state names, CSS classes) — users never see it | Detail internal |
| **Coverage** | Which lines of code ran during tests | Cakupan kode |

## 🧠 The big idea

Testing Library's main rule: **the more your tests look like the way your software is used, the more you can trust them.** A user doesn't know your component has a `useState` called `deletingId` — they see a button that says "Deleting…" and can't be clicked twice. Test **that**.

Component tests are a **flight simulator**: realistic enough to practice every emergency (errors, slow networks, empty lists) in milliseconds, without the cost of flying the real plane (E2E).

## ❓ Why it matters

E2E tests are slow and need a running app, API and database. Unit tests of pure functions miss how the UI is wired. Component tests render a real React tree in jsdom, click and type like a user, and run hundreds of cases per second — perfect for tables, forms, dialogs, conditional rendering and accessibility.

Testing the wrong way looks like this:

```tsx
// ❌ implementation-detail tests
expect(wrapper.state("deletingId")).toBe(13);                 // breaks on refactor to useReducer
expect(container.querySelector(".btn-danger")).toBeTruthy();  // breaks on a CSS change, misses a11y
expect(asFragment()).toMatchSnapshot();                       // 400-line snapshot nobody reads; "update snapshot" on every change
```

These tests fail when you refactor correctly, and pass when behavior breaks — the worst of both. Like a driving test that checks the engine's color instead of whether you can brake.

## 📖 Step by step

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

Vitest can't render async **Server Components** yet. Test their data functions as unit tests, their client children as components, and whole pages with E2E.

### 2. Queries

| Query | No match | Many matches | Async? | Use for |
|---|---|---|---|---|
| `getBy…` | throws | throws | no | elements that must be there |
| `queryBy…` | `null` | throws | no | checking something is **not** there |
| `findBy…` | rejects after timeout | rejects | **yes** | elements that appear later |
| `getAllBy…` / `queryAllBy…` / `findAllBy…` | — | array | — | lists |

Easy way to remember: `get` = "it's here now", `query` = "maybe it's not here", `find` = "wait for it".

Priority: `getByRole("button", { name: "Delete Backend Engineer" })` → `getByLabelText("Search")` → `getByText("No applications match your filters")` → `getByTestId` as a last resort. Use `within(row)` to search inside one part of the UI, and `screen.debug()` / `screen.logTestingPlaygroundURL()` when stuck.

### 3. Interactions with `userEvent`

```tsx
const user = userEvent.setup();
render(<ApplicationsTable applications={rows} onDelete={onDelete} />);

await user.type(screen.getByLabelText("Search"), "  FRONTEND ");
await user.selectOptions(screen.getByLabelText("Status"), "offer");
await user.click(screen.getByRole("button", { name: "Applied on" }));
await user.keyboard("{Escape}");
```

`userEvent` fires the whole chain of events a real browser would (focus, keydown, input, keyup, click). `fireEvent` fires just one event — like teleporting a finger onto the button. Use `fireEvent` only when you need that control (for example with fake timers).

### 4. Async states with a Promise you control

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

You hold the **remote control of the network**: the request stays "loading" until you press `finish()`. That lets you check the in-between state every time — no sleeps, no luck.

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

Mock at the **edges** of your app (network, router, time, browser APIs) — like a film set with a painted city in the background, while the actors (your components) are real.

- Don't mock your own child components.
- For components that call many APIs, **MSW (Mock Service Worker)** fakes requests at the network level and can be shared by tests, Storybook and local development.
- Wrap components that need providers (TanStack Query, context) in a `renderWithProviders` helper; create a **new QueryClient per test** with `retry: false`.

### 6. Hooks

```tsx
const { result, rerender } = renderHook(({ value }) => useDebouncedValue(value, 300), { initialProps: { value: "d" } });
```

Prefer testing a hook through a component that uses it; use `renderHook` for reusable hooks with many cases.

### 7. What not to test

- Internal state, private functions, CSS class names.
- How a third-party library works (Radix already tests its focus trap — test **your** use of it: title, confirm action, pending state).
- Large snapshots. Small inline snapshots of stable, meaningful output are fine.

### 8. Are the tests any good? Mutants again

The exercise gives you a finished component and 9 mutants (versions with one bug each). A test suite with 100% coverage can still let most of them survive:

```tsx
test("renders", () => {
  render(<ApplicationsTable applications={rows} onDelete={vi.fn()} />);
  expect(screen.getByRole("table")).toBeInTheDocument();       // covers most lines, kills almost nothing
});
```

Coverage says the simulator was **turned on**; it doesn't say any emergency was practiced. In real projects, **Stryker** runs mutation testing on Vitest suites — use it on critical code (permissions, pricing, validation).

### When to use component tests

- ✅ Forms, tables, filters, dialogs, conditional rendering, loading/error/empty states, accessible names.
- ✅ Tests for UI bugs found in production.
- 🚫 Visual layout → visual regression or E2E screenshots (jsdom has no real CSS layout).
- 🚫 Async Server Components and full routing → E2E.

## ⚠️ Common mistakes

- `getBy` to check something is absent (it throws) → use `queryBy` + `not.toBeInTheDocument()`.
- Forgetting `await` on `user.click` → checks run before the UI updates.
- Expecting instant updates after async work → use `findBy`.
- Ignoring "not wrapped in act(...)" warnings — usually an update happened after the test ended; await the final state.
- Test data that accidentally matches several rows (searching "data" matches both a role and a company).

## 🏆 Best practices

- [ ] Query by role/label/text; `within` to narrow down; `getByTestId` last.
- [ ] `userEvent.setup()` per test; `await` every interaction.
- [ ] `findBy` / `vi.waitFor` for async; Promises you control for pending states; never `setTimeout` sleeps.
- [ ] Test all states of async UI: pending, success, error — plus empty.
- [ ] Mock the edges (network, router, timers), not children; reset mocks between tests (`restoreMocks`).
- [ ] New providers/clients per test; no shared changing state.
- [ ] One behavior per test, named like a sentence from the spec.
- [ ] Run tests in CI on every PR; check test quality with mutations on critical code.

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
| company load error | MSW returns 500 | render | alert "Couldn't load companies" + Retry button fetches again |
| required fields | companies loaded | click Save | messages for role/company, `aria-invalid`, `onSubmit` not called |
| skills rows | — | Add skill ×2, type, remove first | the remaining row keeps its typed value; Add disabled at max |
| salary rule | — | min 20, max 10, blur | "Maximum must be at least the minimum" on max |
| pending | `onSubmit` returns a Promise you control | fill valid + Save | button disabled "Saving…"; resolve → enabled |
| server field error | `onSubmit` resolves `{ fieldErrors: { role: "Already applied" } }` | submit | message under Role, focus moves to Role |
| success | `onSubmit` resolves `undefined` | submit | status "Application saved", form reset (not dirty) |

Mocks: network via MSW (or a `fetch` stub), the `next/navigation` router if the form redirects. Not mocked: RHF, Zod, child inputs.
:::

### 📝 Self-review checklist

- [ ] Pending, success, error and empty states covered
- [ ] Only the edges are mocked
- [ ] Every assertion is something a user can see

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w6/06-component-tests" ai="no-ai" title="Tests that kill 9 mutants"}
Write Vitest + Testing Library tests for a finished applications table (sorting, search, status filter, empty state, delete pending and error). The grader runs your tests against the real component and 9 mutants.
:::

:::hints
- Read each rule in the README and ask: "what would a user see if this were broken?"
- Choose test data where a search matches **only** the role or **only** the company.
- A pending-state check needs a Promise you resolve yourself.
:::

## ✅ Quick check

:::quiz
When do you use `queryByText` instead of `getByText`?

When checking that something is **not** there: `expect(screen.queryByText("Error")).not.toBeInTheDocument()`. `getBy` would throw before the check runs.
:::

:::quiz
Why create a new TanStack `QueryClient` for every test?

Otherwise the cache leaks data from one test to the next, so results depend on the order tests run in.
:::

## 📚 Keep learning

- Next.js docs (bundled): Testing → Vitest
- [Testing Library: Guiding principles](https://testing-library.com/docs/guiding-principles) · [Which query should I use?](https://testing-library.com/docs/queries/about#priority)
- [Kent C. Dodds: Common mistakes with React Testing Library](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
- [MSW docs](https://mswjs.io/docs)
