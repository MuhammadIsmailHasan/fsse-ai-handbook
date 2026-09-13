// Interfaces, type aliases and unions. See README.md.

export interface Company {}
export interface JobPosting {}
export type Location = unknown;
export type Application = unknown;
export type Status = unknown;
export type ApplicationUpdate = unknown;

export function isRemote(job: JobPosting): boolean {
  throw new Error("TODO");
}

export function locationLabel(location: Location): string {
  throw new Error("TODO");
}

export function statusSummary(app: Application): string {
  throw new Error("TODO");
}
