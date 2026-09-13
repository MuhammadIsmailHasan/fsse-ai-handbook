import { readFileSync } from "node:fs";
import { expect, test } from "vitest";
import { typecheckFolder } from "@support/typecheck";
import { isRemote, locationLabel, statusSummary, type Application, type JobPosting } from "./model";

const job = (location: JobPosting["location"]): JobPosting => ({
  id: 1,
  title: "Backend Engineer",
  company: { id: 3, name: "Kopi Data" },
  location,
  salaryMax: 14_000_000,
  skills: ["python"],
});

test("locationLabel", () => {
  expect(locationLabel({ kind: "onsite", city: "Jakarta" })).toBe("Jakarta");
  expect(locationLabel({ kind: "remote", timezone: "UTC+7" })).toBe("Remote (UTC+7)");
  expect(locationLabel({ kind: "hybrid", city: "Bandung", officeDays: 3 })).toBe("Bandung · 3 days in office");
});

test("isRemote", () => {
  expect(isRemote(job({ kind: "remote", timezone: "UTC+7" }))).toBe(true);
  expect(isRemote(job({ kind: "hybrid", city: "Bandung", officeDays: 2 }))).toBe(false);
});

test("statusSummary", () => {
  const base = { id: 1, job: job({ kind: "onsite", city: "Jakarta" }), updatedAt: "2026-09-12" };
  const apps: [Application, string][] = [
    [{ ...base, status: "saved" }, "Saved"],
    [{ ...base, status: "applied", appliedOn: "2026-09-02" }, "Applied on 2026-09-02"],
    [{ ...base, status: "interview", appliedOn: "2026-09-02", interviewAt: "2026-09-10T09:00" }, "Interview at 2026-09-10T09:00"],
    [{ ...base, status: "offer", appliedOn: "2026-09-02", offerAmount: 18_000_000 }, "Offer: Rp 18000000"],
    [{ ...base, status: "rejected" }, "Rejected"],
    [{ ...base, status: "rejected", reason: "Position filled" }, "Rejected: Position filled"],
  ];
  for (const [app, expected] of apps) expect(statusSummary(app)).toBe(expected);
});

test("switches are exhaustive with a never check", () => {
  const source = readFileSync(`${import.meta.dirname}/model.ts`, "utf8");
  expect(source).toMatch(/:\s*never/);
  expect(source).not.toMatch(/\bany\b/);
});

test("types are correct (tsc strict)", () => {
  const result = typecheckFolder(import.meta.dirname);
  expect(result.output).toBe("");
});
