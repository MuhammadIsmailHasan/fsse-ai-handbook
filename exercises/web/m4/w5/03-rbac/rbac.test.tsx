import { render, screen } from "@testing-library/react";
import { readFileSync } from "node:fs";
import { beforeEach, describe, expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";

const mocks = vi.hoisted(() => ({ verifySession: vi.fn(), deleteCompany: vi.fn() }));
vi.mock("./lib/dal", () => ({ verifySession: mocks.verifySession }));
vi.mock("./lib/companies-api", () => ({ deleteCompany: mocks.deleteCompany }));

import { deleteCompanyAction } from "./app/admin/companies/actions";
import { Can } from "./components/can";
import { can, canEditApplication, canViewApplication, navFor, ROLE_PERMISSIONS, type Role } from "./lib/permissions";

const member = { id: 1, role: "member" as const };
const mentor = { id: 2, role: "mentor" as const, menteeIds: [1, 5] };
const admin = { id: 3, role: "admin" as const };

beforeEach(() => {
  mocks.verifySession.mockReset();
  mocks.deleteCompany.mockReset();
});

describe("policy", () => {
  test("role permission table", () => {
    expect([...ROLE_PERMISSIONS.member].sort()).toEqual(["applications:read:own", "applications:write:own"]);
    expect([...ROLE_PERMISSIONS.mentor].sort()).toEqual(["applications:read:mentees", "applications:read:own", "applications:write:own", "notes:comment"]);
    expect(ROLE_PERMISSIONS.admin).toHaveLength(6);
  });

  test("can", () => {
    expect(can(member, "applications:write:own")).toBe(true);
    expect(can(member, "notes:comment")).toBe(false);
    expect(can(mentor, "notes:comment")).toBe(true);
    expect(can(mentor, "companies:manage")).toBe(false);
    expect(can(admin, "users:manage")).toBe(true);
    expect(can(null, "applications:read:own")).toBe(false);
    expect(can({ role: "superuser" as Role }, "users:manage")).toBe(false);
    expect(can({ role: "toString" as Role }, "users:manage")).toBe(false);
  });

  test("viewing applications", () => {
    expect(canViewApplication(member, { ownerId: 1 })).toBe(true);
    expect(canViewApplication(member, { ownerId: 5 })).toBe(false);
    expect(canViewApplication(mentor, { ownerId: 5 })).toBe(true);
    expect(canViewApplication(mentor, { ownerId: 2 })).toBe(true);
    expect(canViewApplication(mentor, { ownerId: 9 })).toBe(false);
    expect(canViewApplication({ id: 4, role: "mentor" }, { ownerId: 1 })).toBe(false);
    expect(canViewApplication(admin, { ownerId: 9 })).toBe(true);
  });

  test("editing applications", () => {
    expect(canEditApplication(member, { ownerId: 1 })).toBe(true);
    expect(canEditApplication(mentor, { ownerId: 5 })).toBe(false);
    expect(canEditApplication(member, { ownerId: 2 })).toBe(false);
    expect(canEditApplication(admin, { ownerId: 1 })).toBe(true);
  });

  test("navigation", () => {
    expect(navFor(null).map((i) => i.label)).toEqual(["Dashboard"]);
    expect(navFor(member).map((i) => i.label)).toEqual(["Dashboard", "My applications"]);
    expect(navFor(mentor).map((i) => i.label)).toEqual(["Dashboard", "My applications", "Mentees"]);
    expect(navFor(admin)).toHaveLength(5);
  });
});

test("<Can>", () => {
  const { rerender } = render(
    <Can user={member} permission="companies:manage" fallback={<p>Ask an admin</p>}>
      <button>Delete company</button>
    </Can>,
  );
  expect(screen.queryByRole("button")).not.toBeInTheDocument();
  expect(screen.getByText("Ask an admin")).toBeInTheDocument();
  rerender(
    <Can user={admin} permission="companies:manage">
      <button>Delete company</button>
    </Can>,
  );
  expect(screen.getByRole("button", { name: "Delete company" })).toBeInTheDocument();
  rerender(
    <Can user={null} permission="companies:manage">
      <button>Delete company</button>
    </Can>,
  );
  expect(document.body.textContent).toBe("");
});

describe("server action enforces permissions", () => {
  test("use server", () => {
    expect(readFileSync(`${import.meta.dirname}/app/admin/companies/actions.ts`, "utf8").trimStart()).toMatch(/^["']use server["']/);
  });

  test("forbidden for members and mentors", async () => {
    for (const session of [{ userId: 1, role: "member" }, { userId: 2, role: "mentor" }]) {
      mocks.verifySession.mockResolvedValueOnce(session);
      await expect(deleteCompanyAction(4)).resolves.toEqual({ ok: false, message: "You don't have permission to do that" });
    }
    expect(mocks.deleteCompany).not.toHaveBeenCalled();
  });

  test("admins can delete; unauthenticated calls never reach the API", async () => {
    mocks.verifySession.mockResolvedValueOnce({ userId: 3, role: "admin" });
    await expect(deleteCompanyAction(4)).resolves.toEqual({ ok: true });
    expect(mocks.deleteCompany).toHaveBeenCalledWith(4);
    mocks.deleteCompany.mockClear();
    mocks.verifySession.mockRejectedValueOnce(new Error("NEXT_REDIRECT"));
    await expect(deleteCompanyAction(4)).rejects.toThrow("NEXT_REDIRECT");
    expect(mocks.deleteCompany).not.toHaveBeenCalled();
  });
});

test("types", () => {
  expect(typecheckFolder(import.meta.dirname, { recursive: true }).output).toBe("");
});
