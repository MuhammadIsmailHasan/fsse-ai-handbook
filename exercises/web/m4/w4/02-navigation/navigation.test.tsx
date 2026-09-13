import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";

const nav = vi.hoisted(() => ({
  pathname: "/",
  search: "",
  router: { push: vi.fn(), replace: vi.fn(), back: vi.fn(), refresh: vi.fn(), prefetch: vi.fn(), forward: vi.fn() },
}));

vi.mock("next/navigation", () => ({
  usePathname: () => nav.pathname,
  useSearchParams: () => new URLSearchParams(nav.search),
  useRouter: () => nav.router,
}));

import { Breadcrumbs, NavLinks, SaveAndOpen, StatusFilter } from "./navigation";

beforeEach(() => {
  nav.pathname = "/";
  nav.search = "";
  Object.values(nav.router).forEach((fn) => fn.mockReset());
});

const LINKS = [
  { href: "/", label: "Home" },
  { href: "/jobs", label: "Jobs" },
  { href: "/applications", label: "Applications" },
];

describe("NavLinks", () => {
  const active = () => screen.getAllByRole("link").filter((a) => a.getAttribute("aria-current") === "page").map((a) => a.textContent);

  test.each([
    ["/", ["Home"]],
    ["/jobs", ["Jobs"]],
    ["/jobs/12", ["Jobs"]],
    ["/jobsearch", []],
    ["/applications/3/notes", ["Applications"]],
  ])("on %s", (pathname, expected) => {
    nav.pathname = pathname;
    render(<NavLinks links={LINKS} />);
    expect(screen.getByRole("navigation", { name: "Main" })).toBeInTheDocument();
    expect(active()).toEqual(expected);
    for (const link of screen.getAllByRole("link")) {
      expect(link.classList.contains("font-semibold")).toBe(link.getAttribute("aria-current") === "page");
    }
  });
});

describe("Breadcrumbs", () => {
  test("builds links from the path and marks the current page", () => {
    nav.pathname = "/dashboard/applications/12";
    render(<Breadcrumbs />);
    const items = within(screen.getByRole("navigation", { name: "Breadcrumb" })).getAllByRole("listitem");
    expect(items.map((li) => li.textContent)).toEqual(["Home", "Dashboard", "Applications", "12"]);
    expect(screen.getAllByRole("link").map((a) => a.getAttribute("href"))).toEqual(["/", "/dashboard", "/dashboard/applications"]);
    expect(screen.getByText("12")).toHaveAttribute("aria-current", "page");
    expect(screen.getByText("12").closest("a")).toBeNull();
  });

  test("labels and humanized segments", () => {
    nav.pathname = "/saved-jobs/ai-engineer";
    render(<Breadcrumbs labels={{ "ai-engineer": "AI Engineer" }} />);
    expect(screen.getAllByRole("listitem").map((li) => li.textContent)).toEqual(["Home", "Saved jobs", "AI Engineer"]);
  });

  test("renders nothing on the home page", () => {
    nav.pathname = "/";
    const { container } = render(<Breadcrumbs />);
    expect(container).toBeEmptyDOMElement();
  });
});

describe("StatusFilter", () => {
  test("reads the current value from the URL", () => {
    nav.search = "status=interview&q=python";
    render(<StatusFilter />);
    expect(screen.getByLabelText("Status")).toHaveValue("interview");
    expect(screen.getAllByRole("option").map((o) => o.textContent)).toEqual(["All", "Saved", "Applied", "Interview", "Offer", "Rejected"]);
  });

  test("sets status, keeps other params, resets page", async () => {
    nav.pathname = "/applications";
    nav.search = "q=python&page=3";
    render(<StatusFilter />);
    await userEvent.setup().selectOptions(screen.getByLabelText("Status"), "Offer");
    expect(nav.router.replace).toHaveBeenCalledWith("/applications?q=python&status=offer", { scroll: false });
    expect(nav.router.push).not.toHaveBeenCalled();
  });

  test("choosing All removes the param (and the ? when nothing is left)", async () => {
    nav.pathname = "/applications";
    nav.search = "status=saved&page=2";
    render(<StatusFilter />);
    await userEvent.setup().selectOptions(screen.getByLabelText("Status"), "All");
    expect(nav.router.replace).toHaveBeenCalledWith("/applications", { scroll: false });
  });
});

describe("SaveAndOpen", () => {
  test("navigates after a successful save", async () => {
    let resolve!: (value: { id: number }) => void;
    const onSave = vi.fn(() => new Promise<{ id: number }>((r) => (resolve = r)));
    const user = userEvent.setup();
    render(<SaveAndOpen onSave={onSave} />);
    await user.click(screen.getByRole("button", { name: "Save and open" }));
    expect(screen.getByRole("button", { name: "Save and open" })).toBeDisabled();
    expect(nav.router.push).not.toHaveBeenCalled();
    resolve({ id: 42 });
    await vi.waitFor(() => expect(nav.router.push).toHaveBeenCalledWith("/applications/42"));
  });

  test("stays and shows an error when saving fails", async () => {
    const user = userEvent.setup();
    render(<SaveAndOpen onSave={() => Promise.reject(new Error("500"))} />);
    await user.click(screen.getByRole("button", { name: "Save and open" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Couldn't save. Try again.");
    expect(screen.getByRole("button", { name: "Save and open" })).toBeEnabled();
    expect(nav.router.push).not.toHaveBeenCalled();
  });

  test("back button", async () => {
    render(<SaveAndOpen onSave={async () => ({ id: 1 })} />);
    await userEvent.setup().click(screen.getByRole("button", { name: "Back" }));
    expect(nav.router.back).toHaveBeenCalledTimes(1);
  });
});

test("client component and types", async () => {
  const { readFileSync } = await import("node:fs");
  expect(readFileSync(`${import.meta.dirname}/navigation.tsx`, "utf8").trimStart()).toMatch(/^["']use client["']/);
  expect(typecheckFolder(import.meta.dirname).output).toBe("");
});
