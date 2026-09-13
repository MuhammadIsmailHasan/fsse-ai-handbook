---
title: "Interfaces, Type Aliases & Union Types"
summary: Model real data precisely — object types with interfaces and aliases, optional and readonly fields, discriminated unions that make impossible states unrepresentable, type guards, exhaustive switches and utility types.
type: lesson
source: core
sourceRef: "M3 · W2 · L2"
roles: { be: recommended, fe: core, fs: core, ai: core, ops: optional }
durationMinutes: 150
tags: [typescript, interfaces, unions, discriminated-unions, utility-types]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- `interface` vs `type` — and when it matters
- Optional (`?`), `readonly`, and nested object types
- **Discriminated unions**: one type per state
- **Type guards** and exhaustive `switch` with `never`
- Intersections (`&`) and extending interfaces
- Utility types: `Partial`, `Required`, `Pick`, `Omit`, `Record`, `ReturnType`
- Deriving types from other types instead of repeating them

## 🧠 The big idea

Good types are a **map of what's possible**. A sloppy map says "an application has a status, maybe an interview date, maybe an offer amount" — so the code must check everything everywhere. A precise map says "an **offer** always has an amount, a **saved** application never has an interview date" — so impossible combinations can't even be written.

## ❓ Why does this exist?

Front-end bugs often come from **impossible states**: a spinner and an error message shown together, an "offer" with no amount, `interviewAt` read on a rejected application. Modeling states explicitly moves those bugs from runtime to compile time — the same "domain rules" thinking as the State pattern in Architecture Stage D.

## 💥 What happens if we DON'T?

```ts
interface Application {
  status: string;
  appliedOn?: string;
  interviewAt?: string;
  offerAmount?: number;
  isLoading?: boolean;
  error?: string;
}
```

Every consumer asks: "is `offerAmount` defined? which statuses exist? can `isLoading` and `error` both be true?" TypeScript can't help because the type allows everything.

## 📖 How it works, step by step

### 1. Object types

```ts
interface Company {
  id: number;
  name: string;
  website?: string;                 // optional: string | undefined
}

type JobPosting = {
  readonly id: number;              // can't be reassigned
  title: string;
  company: Company;
  readonly skills: readonly string[];
};
```

### 2. `interface` or `type`?

| | `interface` | `type` |
|---|---|---|
| Object shapes | ✅ | ✅ |
| Unions, tuples, primitives, mapped types | ❌ | ✅ |
| `extends` | ✅ `interface B extends A` | via `&` |
| Declaration merging (reopening) | ✅ (useful for libraries) | ❌ |

Team convention is what matters. A common one: `interface` for object shapes (props, API models), `type` for unions and computed types.

### 3. Discriminated unions

```ts
interface ApplicationBase { id: number; job: JobPosting; updatedAt: string }

type Application =
  | (ApplicationBase & { status: "saved" })
  | (ApplicationBase & { status: "applied"; appliedOn: string })
  | (ApplicationBase & { status: "interview"; appliedOn: string; interviewAt: string })
  | (ApplicationBase & { status: "offer"; appliedOn: string; offerAmount: number })
  | (ApplicationBase & { status: "rejected"; reason?: string });
```

The **discriminant** (`status`) is a literal property present in every member. Checking it narrows:

```ts
if (app.status === "offer") {
  app.offerAmount;     // ✅ number
}
app.interviewAt;       // ❌ doesn't exist on all members
```

The same trick for UI state:

```ts
type Remote<T> =
  | { state: "idle" }
  | { state: "loading" }
  | { state: "error"; error: string }
  | { state: "success"; data: T };
```

No more `isLoading && error` contradictions.

### 4. Exhaustive switches

```ts
function assertNever(value: never): never {
  throw new Error(`Unhandled: ${JSON.stringify(value)}`);
}

function statusSummary(app: Application): string {
  switch (app.status) {
    case "saved": return "Saved";
    case "applied": return `Applied on ${app.appliedOn}`;
    case "interview": return `Interview at ${app.interviewAt}`;
    case "offer": return `Offer: Rp ${app.offerAmount}`;
    case "rejected": return app.reason ? `Rejected: ${app.reason}` : "Rejected";
    default: return assertNever(app);   // add "withdrawn" to the union → compile error here
  }
}
```

When the backend adds a status, TypeScript lists every place that must handle it.

### 5. Type guards

```ts
function isRemote(job: JobPosting): job is JobPosting & { location: { kind: "remote" } } {
  return job.location.kind === "remote";
}

const remoteJobs = jobs.filter(isRemote);   // typed as remote jobs
```

A function returning `value is Type` teaches TypeScript your custom check.

### 6. Deriving types

```ts
type Status = Application["status"];                     // indexed access
type ApplicationUpdate = Partial<Pick<JobPosting, "title" | "salaryMax">>;
type NewCompany = Omit<Company, "id">;                   // for create forms
type ById = Record<number, Company>;
type Loader = ReturnType<typeof createLoader>;
```

**Single source of truth**: when `JobPosting` changes, derived types follow.

| Utility | Result |
|---|---|
| `Partial<T>` | all fields optional (PATCH payloads) |
| `Required<T>` | all fields required |
| `Pick<T, K>` / `Omit<T, K>` | select / remove fields |
| `Record<K, V>` | object with keys K and values V |
| `Readonly<T>` | all fields readonly |
| `NonNullable<T>` | remove `null`/`undefined` |

## ⚖️ Trade-offs

| Choice | ✅ | ❌ |
|---|---|---|
| Discriminated unions | impossible states unrepresentable, exhaustive checks | more types; API responses must be narrowed/validated |
| One big optional-fields interface | quick | every consumer re-checks; bugs slip through |
| Derived types | single source of truth | long type expressions can be hard to read — name them |
| Type guards | reusable narrowing | a wrong guard lies to the compiler |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ Anything with states: statuses, async requests, form steps, payment results.
- ✅ Derive update/create payload types from the main model.
- 🚫 Don't model every possible nuance of external data you don't control — validate and convert at the boundary into your precise types.

## 🏆 Best practices

- [ ] Make impossible states unrepresentable with discriminated unions.
- [ ] Add `assertNever` defaults so new cases fail to compile.
- [ ] Derive related types with `Pick`/`Omit`/`Partial`/indexed access instead of copying fields.
- [ ] Use `readonly` for data you shouldn't mutate (props, API data).
- [ ] Keep guards simple and tested; prefer built-in narrowing when possible.
- [ ] Keep API DTO types separate from UI view models when they differ.

## 🏭 How it's used in industry

- Redux Toolkit and TanStack Query expose request state as discriminated unions (`status: "pending" | "error" | "success"`).
- Payment SDKs model results as unions (`succeeded | requires_action | failed`) so integrations handle every case.
- Code generators (OpenAPI → TypeScript) turn `oneOf` schemas into unions.

## ⚠️ Common mistakes

- `status: string` instead of a literal union.
- Optional fields for data that's required in some states.
- A `default:` branch that silently returns something instead of `assertNever`.
- Using `as` to force a union member instead of narrowing.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a teammate what "make impossible states unrepresentable" means, using a loading spinner + error message example.

## 📐 Design it

Design the types for CareerPilot's **CV match feature** (Phase 3 AI service): a request can be idle, uploading a CV, analyzing, done (score 0–100, matched skills, missing skills, advice), or failed (reason: file too large, unsupported type, AI unavailable — with a retry allowed only for the last). Write the union types and a function signature that renders a message.

:::quiz
Show a possible design

```ts
type MatchFailure =
  | { reason: "file_too_large"; maxMb: number }
  | { reason: "unsupported_type"; allowed: readonly string[] }
  | { reason: "ai_unavailable"; retryAfterSeconds: number };

interface MatchResult {
  score: number;                         // 0–100 (validated at the API boundary)
  matchedSkills: readonly string[];
  missingSkills: readonly string[];
  advice: string;
}

type CvMatchState =
  | { phase: "idle" }
  | { phase: "uploading"; fileName: string; progress: number }
  | { phase: "analyzing"; fileName: string }
  | { phase: "done"; fileName: string; result: MatchResult }
  | { phase: "failed"; fileName: string; failure: MatchFailure };

function canRetry(state: CvMatchState): boolean {
  return state.phase === "failed" && state.failure.reason === "ai_unavailable";
}

function statusMessage(state: CvMatchState): string {
  switch (state.phase) {
    case "idle": return "Upload your CV to see how well you match.";
    case "uploading": return `Uploading ${state.fileName}… ${state.progress}%`;
    case "analyzing": return "Analyzing your CV…";
    case "done": return `Match score: ${state.result.score}/100`;
    case "failed":
      switch (state.failure.reason) {
        case "file_too_large": return `File is larger than ${state.failure.maxMb} MB.`;
        case "unsupported_type": return `Please upload ${state.failure.allowed.join(", ")}.`;
        case "ai_unavailable": return `The AI is busy. Try again in ${state.failure.retryAfterSeconds}s.`;
        default: return assertNever(state.failure);
      }
    default: return assertNever(state);
  }
}
```

Retry being allowed only for `ai_unavailable` is encoded once (`canRetry`); the UI can't show a result during upload because `result` only exists in `done`.
:::

### 📝 Self-review checklist

- [ ] Each phase carries only its own data
- [ ] Nested unions for failure reasons
- [ ] Exhaustive switches

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w2/02-interfaces-unions" ai="no-ai" title="Model applications so impossible states can't compile"}
Write interfaces, a location union and an application union keyed by status, a derived `Status` type, a `Partial<Pick<…>>` update type, a type guard, and exhaustive switch functions. Type-level tests check that invalid objects (an offer without an amount, a remote job with a city) fail to compile.
:::

:::hints
- Put shared fields in a base interface and intersect it with each status member.
- `type Status = Application["status"]` — derived automatically.
- `function assertNever(value: never): never` in the `default` branch.
:::

## ✅ Quick check

:::quiz
What makes a union "discriminated"?

Every member has a common property with a distinct literal type (e.g. `status: "offer"`), so checking it narrows to one member.
:::

:::quiz
Why call `assertNever` in a switch's default branch?

If a new member is added to the union and not handled, the value isn't `never` anymore, so the code fails to compile at that spot.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Interface | Antarmuka (bentuk objek) |
| Type alias | Nama alias tipe |
| Discriminated union | Union bertanda (dibedakan oleh satu properti) |
| Type guard | Penjaga tipe |
| Exhaustive check | Pemeriksaan menyeluruh semua kasus |
| Utility type | Tipe utilitas (Partial, Pick, Omit…) |

## 📚 Keep learning

- [TypeScript Handbook: Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html)
- [TypeScript Handbook: Utility Types](https://www.typescriptlang.org/docs/handbook/utility-types.html)
