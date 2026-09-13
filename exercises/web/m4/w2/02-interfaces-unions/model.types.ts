// Type-level checks. Don't edit. Lines after @ts-expect-error MUST be type errors.
import { expectTypeOf } from "vitest";
import { isRemote, type Application, type ApplicationUpdate, type JobPosting, type Location, type Status } from "./model";

expectTypeOf<Status>().toEqualTypeOf<"saved" | "applied" | "interview" | "offer" | "rejected">();
expectTypeOf<ApplicationUpdate>().toEqualTypeOf<{ title?: string; salaryMax?: number | null }>();
expectTypeOf<Location["kind"]>().toEqualTypeOf<"onsite" | "remote" | "hybrid">();

const job: JobPosting = {
  id: 1,
  title: "Backend Engineer",
  company: { id: 3, name: "Kopi Data" },
  location: { kind: "remote", timezone: "UTC+7" },
  salaryMax: null,
  skills: ["python"],
};

// @ts-expect-error — a remote location has no city
const badLocation: Location = { kind: "remote", city: "Jakarta" };

// @ts-expect-error — an offer must include offerAmount
const badOffer: Application = { id: 1, job, updatedAt: "2026-09-01", status: "offer", appliedOn: "2026-09-01" };

// @ts-expect-error — a saved application has no interviewAt
const badSaved: Application = { id: 1, job, updatedAt: "2026-09-01", status: "saved", interviewAt: "2026-09-10" };

// @ts-expect-error — skills are readonly
job.skills.push("go");

// @ts-expect-error — website is optional but must be a string
const badCompany: JobPosting["company"] = { id: 1, name: "X", website: 42 };

declare const someJob: JobPosting;
if (isRemote(someJob)) {
  expectTypeOf(someJob.location.timezone).toEqualTypeOf<string>(); // only compiles if the guard narrowed to remote
}

declare const app: Application;
if (app.status === "interview") {
  expectTypeOf(app.interviewAt).toEqualTypeOf<string>();
}

export { badLocation, badOffer, badSaved, badCompany };
