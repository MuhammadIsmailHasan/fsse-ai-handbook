# M4 · W2 · 02 — Modeling Applications with Interfaces and Unions

> 🚫🤖 **No-AI** · ⏱️ ~60 min · edit **`model.ts`**

Model CareerPilot's data so that **impossible states can't be represented**.

| Export | Requirement |
|---|---|
| `interface Company` | `id: number`, `name: string`, `website?: string` |
| `interface JobPosting` | `id`, `title`, `company: Company`, `location: Location`, `salaryMax: number \| null`, `readonly skills: readonly string[]` |
| `type Location` | a **discriminated union** on `kind`: `{ kind: "onsite"; city: string }` \| `{ kind: "remote"; timezone: string }` \| `{ kind: "hybrid"; city: string; officeDays: number }` |
| `type Application` | a discriminated union on `status` sharing `{ id: number; job: JobPosting; updatedAt: string }`: `"saved"`, `"applied"` (+ `appliedOn: string`), `"interview"` (+ `appliedOn`, `interviewAt: string`), `"offer"` (+ `appliedOn`, `offerAmount: number`), `"rejected"` (+ `reason?: string`) |
| `type Status` | `Application["status"]` (derived, not re-typed) |
| `type ApplicationUpdate` | `Partial<Pick<JobPosting, "title" \| "salaryMax">>` |
| `isRemote(job)` | **type guard** `job is JobPosting & { location: { kind: "remote" } }` |
| `locationLabel(location)` | `"Jakarta"`, `"Remote (UTC+7)"`, `"Bandung · 3 days in office"` — use a `switch` on `kind` with an exhaustive `never` check |
| `statusSummary(app)` | `"Saved"`, `"Applied on 2026-09-02"`, `"Interview at 2026-09-10T09:00"`, `"Offer: Rp 18000000"`, `"Rejected"` / `"Rejected: {reason}"` — exhaustive `switch` on `status` |

`model.types.ts` checks the types (including things that must NOT compile).

```bash
cd exercises/web
npx vitest run m4/w2/02-interfaces-unions
```
