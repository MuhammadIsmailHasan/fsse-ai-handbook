---
title: "Interfaces, Type Aliases & Union Types"
summary: Describe real data precisely — object types, optional and readonly fields, unions where each state has only its own data, type guards, switches that cover every case, and building new types from existing ones.
type: lesson
source: core
sourceRef: "M3 · W2 · L2"
roles: { be: recommended, fe: core, fs: core, ai: core, ops: optional }
durationMinutes: 150
tags: [typescript, interfaces, unions, discriminated-unions, utility-types]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Describing objects with `interface` and `type`
- Optional (`?`) and `readonly` fields
- **Discriminated unions**: a separate shape for each state
- Checking every case in a `switch`
- Type guards: teaching TypeScript your own checks
- Building new types from existing ones (`Pick`, `Omit`, `Partial`…)

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Interface** | A named description of an object's shape | Bentuk objek |
| **Type alias** | A name for any type: `type Status = "saved" \| "applied"` | Nama tipe |
| **Optional field (`?`)** | A field that may be missing | Field opsional |
| **Discriminated union** | Several shapes, told apart by one field like `status` | Union dengan penanda |
| **Type guard** | A function that tells TypeScript "if this returns true, the value is type X" | Penjaga tipe |
| **`never`** | A type with no possible value — used to catch forgotten cases | Tidak mungkin terjadi |
| **Utility type** | Built-in helpers that create a type from another type (`Partial`, `Pick`…) | Tipe bantuan |

## 🧠 The big idea

Good types are like a **form with the right fields for each situation**. A marriage certificate form has fields for two spouses; a birth certificate has fields for parents. One giant form with every field "optional" would let people fill in nonsense.

Same for code: an application with status **offer** always has an amount; a **saved** application never has an interview date. If the types say this, impossible combinations can't even be written.

## ❓ Why it matters

Many frontend bugs are **impossible states**: a spinner and an error shown at the same time, an "offer" with no amount, reading `interviewAt` on a rejected application.

A type where everything is optional allows all of those:

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

Every place that uses it must guess: "Is `offerAmount` there? Which statuses exist? Can `isLoading` and `error` both be true?" TypeScript can't help, because the type allows everything.

## 📖 Step by step

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

- `website?` = the field may be missing.
- `readonly` = the value can't be changed after it's created.

### 2. `interface` or `type`?

Both describe objects. The differences are small:

| | `interface` | `type` |
|---|---|---|
| Object shapes | ✅ | ✅ |
| Unions, tuples, simple types | ❌ | ✅ |
| Extend another | ✅ `interface B extends A` | with `&` |

A common team habit: `interface` for object shapes (props, API data), `type` for unions. What matters most is being consistent.

### 3. Discriminated unions: one shape per state

```ts
interface ApplicationBase { id: number; job: JobPosting; updatedAt: string }

type Application =
  | (ApplicationBase & { status: "saved" })
  | (ApplicationBase & { status: "applied"; appliedOn: string })
  | (ApplicationBase & { status: "interview"; appliedOn: string; interviewAt: string })
  | (ApplicationBase & { status: "offer"; appliedOn: string; offerAmount: number })
  | (ApplicationBase & { status: "rejected"; reason?: string });
```

- `|` means "one of these shapes".
- `&` means "combine": the shared base fields **plus** the fields for that state.
- `status` is the **label** that tells the shapes apart — like the color of a ticket at a parking lot that tells the guard which rate applies.

When you check the label, TypeScript knows the exact shape:

```ts
if (app.status === "offer") {
  app.offerAmount;     // ✅ number
}
app.interviewAt;       // ❌ doesn't exist on all members
```

The same idea works for loading data:

```ts
type Remote<T> =
  | { state: "idle" }
  | { state: "loading" }
  | { state: "error"; error: string }
  | { state: "success"; data: T };
```

Now "loading **and** error at the same time" is impossible to write.

### 4. A `switch` that covers every case

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

`never` means "this can't happen". If all cases are handled, nothing is left for `default`. When someone adds a new status like `"withdrawn"`, TypeScript shows an error **at every switch that forgot it** — like a checklist that won't let you submit until every box is ticked.

### 5. Type guards

```ts
function isRemote(job: JobPosting): job is JobPosting & { location: { kind: "remote" } } {
  return job.location.kind === "remote";
}

const remoteJobs = jobs.filter(isRemote);   // typed as remote jobs
```

The return type `job is …` is a promise to TypeScript: "if I return `true`, this job is remote". After `filter(isRemote)`, TypeScript knows every item is remote. Be careful: if your check is wrong, TypeScript will believe the wrong thing.

### 6. Building types from other types

Instead of copying fields (and forgetting to update the copy), build new types from the main one — like making different forms from one master template.

```ts
type Status = Application["status"];                     // indexed access
type ApplicationUpdate = Partial<Pick<JobPosting, "title" | "salaryMax">>;
type NewCompany = Omit<Company, "id">;                   // for create forms
type ById = Record<number, Company>;
type Loader = ReturnType<typeof createLoader>;
```

| Helper | What it does |
|---|---|
| `Partial<T>` | makes every field optional (good for PATCH updates) |
| `Required<T>` | makes every field required |
| `Pick<T, K>` / `Omit<T, K>` | keep only some fields / remove some fields |
| `Record<K, V>` | an object with keys of type K and values of type V |
| `Readonly<T>` | makes every field readonly |
| `NonNullable<T>` | removes `null` and `undefined` |

When `JobPosting` changes, every type built from it updates too.

## ⚠️ Common mistakes

- `status: string` instead of a union of the real values.
- Optional fields for data that is always there in some states.
- A `default:` that quietly returns something instead of `assertNever`.
- Using `as` to force a shape instead of checking the label.
- Copying fields into a second type instead of using `Pick` / `Omit`.

## 🏆 Best practices

- [ ] Use discriminated unions so impossible states can't be written.
- [ ] End switches with `assertNever`, so new cases cause compile errors.
- [ ] Build related types with `Pick`, `Omit`, `Partial` and `Type["field"]`.
- [ ] Use `readonly` for data that shouldn't change (props, API data).
- [ ] Keep type guards small and tested.
- [ ] Check outside data at the boundary, then convert it into your precise types.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a teammate what "make impossible states impossible to write" means, using the example of a loading spinner and an error message shown together.

## 📐 Design it

Design the types for CareerPilot's **CV match feature**. A request can be: idle, uploading a CV, analyzing, done (score 0–100, matched skills, missing skills, advice), or failed (file too large, unsupported file type, or AI unavailable — retry is allowed only for the last one). Write the union types and a function that returns a message for each state.

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

- `result` only exists in the `done` state, so the page can't show a score while uploading.
- The failure reasons are their own union, each with its own extra data.
- The retry rule lives in one place: `canRetry`.
:::

### 📝 Self-review checklist

- [ ] Each state carries only its own data
- [ ] Failure reasons are a union too
- [ ] Every switch covers every case

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w2/02-interfaces-unions" ai="no-ai" title="Model applications so impossible states can't compile"}
Write interfaces, a location union, an application union labeled by `status`, a `Status` type built from it, a `Partial<Pick<…>>` update type, a type guard and switch functions that cover every case. Type tests check that wrong objects (an offer without an amount, a remote job with a city) fail to compile.
:::

:::hints
- Put the shared fields in a base interface and combine it (`&`) with each status shape.
- `type Status = Application["status"]` — built automatically.
- `function assertNever(value: never): never` in the `default` branch.
:::

## ✅ Quick check

:::quiz
What makes a union "discriminated"?

Every shape has the same field (like `status`) with a different fixed value, so checking that field tells TypeScript which shape it is.
:::

:::quiz
Why call `assertNever` in the `default` branch?

If someone adds a new case and forgets to handle it, the value is no longer `never`, so the code fails to compile right there.
:::

## 📚 Keep learning

- [TypeScript Handbook: Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html)
- [TypeScript Handbook: Utility Types](https://www.typescriptlang.org/docs/handbook/utility-types.html)
