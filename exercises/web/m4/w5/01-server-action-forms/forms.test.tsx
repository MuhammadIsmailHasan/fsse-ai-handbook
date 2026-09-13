import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { readFileSync } from "node:fs";
import { beforeEach, describe, expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";

const mocks = vi.hoisted(() => ({
  createApplication: vi.fn(),
  updateTag: vi.fn(),
  redirect: vi.fn((url: string) => {
    throw Object.assign(new Error("NEXT_REDIRECT"), { url });
  }),
}));
vi.mock("next/cache", () => ({ updateTag: mocks.updateTag }));
vi.mock("next/navigation", () => ({ redirect: mocks.redirect }));
vi.mock("./lib/api", async (importOriginal) => ({ ...(await importOriginal<typeof import("./lib/api")>()), createApplication: mocks.createApplication }));

import { ApiError } from "./lib/api";
import { createApplicationAction, type FormState } from "./app/applications/new/actions";
import { ApplicationForm } from "./app/applications/new/application-form";
import { applicationSchema } from "./app/applications/new/schema";

const EMPTY: FormState = { message: null, fieldErrors: {} };
const form = (values: Record<string, string>) => {
  const data = new FormData();
  Object.entries(values).forEach(([k, v]) => data.append(k, v));
  return data;
};

beforeEach(() => Object.values(mocks).forEach((m) => m.mockClear()));

describe("schema", () => {
  test("coerces and trims", () => {
    expect(applicationSchema.parse({ company_id: "3", role: "  Backend Engineer ", salary_min: "", salary_max: "14000000" })).toEqual({
      company_id: 3,
      role: "Backend Engineer",
      salary_max: 14_000_000,
    });
  });

  test("errors", () => {
    const result = applicationSchema.safeParse({ company_id: "", role: "   ", salary_min: "20", salary_max: "10" });
    expect(result.success).toBe(false);
    const issues = Object.fromEntries(result.error!.issues.map((i) => [i.path.join("."), i.message]));
    expect(issues.company_id).toBe("Choose a company");
    expect(issues.role).toBe("Role is required");
    const refined = applicationSchema.safeParse({ company_id: "1", role: "Dev", salary_min: "20", salary_max: "10" });
    expect(refined.error!.issues).toEqual([expect.objectContaining({ path: ["salary_max"], message: "Maximum must be at least the minimum" })]);
    expect(applicationSchema.safeParse({ company_id: "1", role: "Dev", salary_min: "-5" }).success).toBe(false);
  });
});

describe("server action", () => {
  test("is a use server module", () => {
    expect(readFileSync(`${import.meta.dirname}/app/applications/new/actions.ts`, "utf8").trimStart()).toMatch(/^["']use server["']/);
  });

  test("returns field errors without calling the API", async () => {
    const state = await createApplicationAction(EMPTY, form({ company_id: "", role: "" }));
    expect(state.message).toBe("Please fix the errors below");
    expect(state.fieldErrors.company_id).toEqual(["Choose a company"]);
    expect(state.fieldErrors.role).toEqual(["Role is required"]);
    expect(mocks.createApplication).not.toHaveBeenCalled();
  });

  test("maps API 422 fields and 409 conflicts", async () => {
    mocks.createApplication.mockRejectedValueOnce(new ApiError(422, "validation_failed", { company_id: ["Company not found."] }));
    await expect(createApplicationAction(EMPTY, form({ company_id: "99", role: "Dev" }))).resolves.toEqual({
      message: "Please fix the errors below",
      fieldErrors: { company_id: ["Company not found."] },
    });
    mocks.createApplication.mockRejectedValueOnce(new ApiError(409, "duplicate"));
    await expect(createApplicationAction(EMPTY, form({ company_id: "3", role: "Dev" }))).resolves.toEqual({
      message: "You already have an application for this role",
      fieldErrors: {},
    });
    mocks.createApplication.mockRejectedValueOnce(new ApiError(500, "internal_error"));
    await expect(createApplicationAction(EMPTY, form({ company_id: "3", role: "Dev" }))).rejects.toMatchObject({ status: 500 });
    expect(mocks.updateTag).not.toHaveBeenCalled();
  });

  test("on success: sends typed data, expires the tag, redirects", async () => {
    mocks.createApplication.mockResolvedValueOnce({ id: 42 });
    await expect(createApplicationAction(EMPTY, form({ company_id: "3", role: " AI Engineer ", salary_min: "9000000", salary_max: "" }))).rejects.toMatchObject({
      url: "/applications/42",
    });
    expect(mocks.createApplication).toHaveBeenCalledWith({ company_id: 3, role: "AI Engineer", salary_min: 9_000_000 });
    expect(mocks.updateTag).toHaveBeenCalledWith("applications");
  });
});

describe("form component", () => {
  test("shows server errors accessibly after submitting", async () => {
    const user = userEvent.setup();
    render(<ApplicationForm companies={[{ id: 3, name: "Kopi Data" }]} />);
    expect(screen.getAllByRole("option").map((o) => o.textContent)).toEqual(["Choose a company", "Kopi Data"]);
    await user.type(screen.getByLabelText("Minimum salary"), "20");
    await user.type(screen.getByLabelText("Maximum salary"), "10");
    await user.click(screen.getByRole("button", { name: "Save application" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Please fix the errors below");
    expect(screen.getByLabelText("Company")).toHaveAccessibleDescription("Choose a company");
    expect(screen.getByLabelText("Role")).toHaveAttribute("aria-invalid", "true");
    expect(screen.getByLabelText("Maximum salary")).toHaveAccessibleDescription("Maximum must be at least the minimum");
    expect(screen.getByLabelText("Minimum salary")).not.toHaveAttribute("aria-invalid");
  });

  test("submit button shows pending state", async () => {
    let finish!: () => void;
    mocks.createApplication.mockImplementationOnce(() => new Promise((_, reject) => (finish = () => reject(new ApiError(409, "duplicate")))));
    const user = userEvent.setup();
    render(<ApplicationForm companies={[{ id: 3, name: "Kopi Data" }]} />);
    await user.selectOptions(screen.getByLabelText("Company"), "Kopi Data");
    await user.type(screen.getByLabelText("Role"), "Dev");
    await user.click(screen.getByRole("button", { name: "Save application" }));
    expect(await screen.findByRole("button", { name: "Saving…" })).toBeDisabled();
    finish();
    expect(await screen.findByRole("alert")).toHaveTextContent("You already have an application for this role");
    expect(screen.getByRole("button", { name: "Save application" })).toBeEnabled();
  });
});

test("types", () => {
  expect(typecheckFolder(import.meta.dirname, { recursive: true }).output).toBe("");
});
