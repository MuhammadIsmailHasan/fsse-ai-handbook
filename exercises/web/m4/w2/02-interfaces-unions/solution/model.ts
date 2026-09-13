export interface Company {
  id: number;
  name: string;
  website?: string;
}

export type Location =
  | { kind: "onsite"; city: string }
  | { kind: "remote"; timezone: string }
  | { kind: "hybrid"; city: string; officeDays: number };

export interface JobPosting {
  id: number;
  title: string;
  company: Company;
  location: Location;
  salaryMax: number | null;
  readonly skills: readonly string[];
}

interface ApplicationBase {
  id: number;
  job: JobPosting;
  updatedAt: string;
}

// Each status carries exactly the data that exists in that state.
export type Application =
  | (ApplicationBase & { status: "saved" })
  | (ApplicationBase & { status: "applied"; appliedOn: string })
  | (ApplicationBase & { status: "interview"; appliedOn: string; interviewAt: string })
  | (ApplicationBase & { status: "offer"; appliedOn: string; offerAmount: number })
  | (ApplicationBase & { status: "rejected"; reason?: string });

export type Status = Application["status"];

export type ApplicationUpdate = Partial<Pick<JobPosting, "title" | "salaryMax">>;

export function isRemote(job: JobPosting): job is JobPosting & { location: { kind: "remote" } } {
  return job.location.kind === "remote";
}

function assertNever(value: never): never {
  throw new Error(`Unhandled case: ${JSON.stringify(value)}`);
}

export function locationLabel(location: Location): string {
  switch (location.kind) {
    case "onsite":
      return location.city;
    case "remote":
      return `Remote (${location.timezone})`;
    case "hybrid":
      return `${location.city} · ${location.officeDays} days in office`;
    default:
      return assertNever(location);
  }
}

export function statusSummary(app: Application): string {
  switch (app.status) {
    case "saved":
      return "Saved";
    case "applied":
      return `Applied on ${app.appliedOn}`;
    case "interview":
      return `Interview at ${app.interviewAt}`;
    case "offer":
      return `Offer: Rp ${app.offerAmount}`;
    case "rejected":
      return app.reason ? `Rejected: ${app.reason}` : "Rejected";
    default:
      return assertNever(app);
  }
}
