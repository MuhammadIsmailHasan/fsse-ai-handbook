import { readFileSync } from "node:fs";
import { join } from "node:path";
import { expect, test } from "vitest";
import * as data from "./jobs-data.js";

const JOBS = Object.freeze([
  Object.freeze({ id: 3, title: "Backend Engineer", company: "Kopi Data", city: "Jakarta", remote: false, salaryMax: 14_000_000, skills: Object.freeze(["Python", "SQL"]) }),
  Object.freeze({ id: 1, title: "AI Engineer", company: "Lintas AI", city: "Remote", remote: true, salaryMax: 25_000_000, skills: Object.freeze(["python", "LLM"]) }),
  Object.freeze({ id: 2, title: "Data Analyst", company: "Awan", city: "Jakarta", remote: false, salaryMax: null, skills: Object.freeze(["sql", "Excel"]) }),
  Object.freeze({ id: 4, title: "Frontend Dev", company: "Batik", city: "Bandung", remote: true, salaryMax: 14_000_000, skills: Object.freeze(["React"]) }),
]);

test("remoteTitles", () => {
  expect(data.remoteTitles(JOBS)).toEqual(["AI Engineer", "Frontend Dev"]);
  expect(data.remoteTitles([])).toEqual([]);
});

test("averageSalary", () => {
  expect(data.averageSalary(JOBS)).toBe(17_666_666);
  expect(data.averageSalary([JOBS[2]])).toBe(0);
});

test("skillCounts", () => {
  expect(data.skillCounts(JOBS)).toEqual({ python: 2, sql: 2, llm: 1, excel: 1, react: 1 });
});

test("topPaying returns a new sorted array", () => {
  expect(data.topPaying(JOBS, 3).map((j) => j.id)).toEqual([1, 3, 4]);
  expect(data.topPaying(JOBS, 10).map((j) => j.id)).toEqual([1, 3, 4, 2]);
  expect(JOBS.map((j) => j.id)).toEqual([3, 1, 2, 4]);
});

test("jobsByCity", () => {
  expect(data.jobsByCity(JOBS)).toEqual({ Jakarta: ["Backend Engineer", "Data Analyst"], Remote: ["AI Engineer"], Bandung: ["Frontend Dev"] });
});

test("every / some / find", () => {
  expect(data.everyHasSalary(JOBS)).toBe(false);
  expect(data.everyHasSalary([JOBS[0], JOBS[1]])).toBe(true);
  expect(data.someInCity(JOBS, "BANDUNG")).toBe(true);
  expect(data.someInCity(JOBS, "Surabaya")).toBe(false);
  expect(data.findById(JOBS, 2)?.title).toBe("Data Analyst");
  expect(data.findById(JOBS, 99)).toBeUndefined();
});

test("uniqueSkills", () => {
  expect(data.uniqueSkills(JOBS)).toEqual(["excel", "llm", "python", "react", "sql"]);
});

test("no loops", () => {
  const source = readFileSync(join(import.meta.dirname, "jobs-data.js"), "utf8").replace(/\/\/.*$/gm, "");
  expect(source).not.toMatch(/\b(for|while)\s*\(/);
});
