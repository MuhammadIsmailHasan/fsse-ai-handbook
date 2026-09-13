import { screen, within } from "@testing-library/dom";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, test, vi } from "vitest";
import { mountJobBoard } from "./job-board.js";

const JOBS = [
  { id: 1, title: "Backend Engineer", company: "Kopi Data", city: "Jakarta" },
  { id: 2, title: "AI Engineer", company: "Lintas AI", city: "Remote" },
  { id: 3, title: "Data Analyst", company: "Awan Cloud", city: "Bandung" },
];

let root;
beforeEach(() => {
  root = document.createElement("div");
  document.body.append(root);
});

const titles = () => screen.queryAllByRole("heading", { level: 2 }).map((h) => h.textContent);
const status = () => document.querySelector('[aria-live="polite"]')?.textContent;

test("renders accessible search and job items", () => {
  mountJobBoard(root, JOBS);
  expect(screen.getByRole("search")).toBeInTheDocument();
  expect(screen.getByLabelText("Search jobs")).toHaveAttribute("type", "search");
  expect(titles()).toEqual(["Backend Engineer", "AI Engineer", "Data Analyst"]);
  const first = screen.getAllByRole("listitem")[0];
  expect(first).toHaveAttribute("data-id", "1");
  expect(within(first).getByText("Kopi Data · Jakarta")).toBeInTheDocument();
  expect(within(first).getByRole("button", { name: "Save" })).toHaveAttribute("aria-pressed", "false");
  expect(status()).toBe("3 jobs · 0 saved");
});

test("search filters by title or company, case-insensitive", async () => {
  const user = userEvent.setup();
  mountJobBoard(root, JOBS);
  await user.type(screen.getByLabelText("Search jobs"), "ENGINEER");
  expect(titles()).toEqual(["Backend Engineer", "AI Engineer"]);
  expect(status()).toBe("2 jobs · 0 saved");
  await user.clear(screen.getByLabelText("Search jobs"));
  await user.type(screen.getByLabelText("Search jobs"), "awan");
  expect(titles()).toEqual(["Data Analyst"]);
});

test("empty state appears and disappears", async () => {
  const user = userEvent.setup();
  mountJobBoard(root, JOBS);
  const search = screen.getByLabelText("Search jobs");
  await user.type(search, "golang");
  expect(screen.queryAllByRole("listitem")).toHaveLength(0);
  expect(document.querySelectorAll("p.empty")).toHaveLength(1);
  expect(document.querySelector("p.empty")).toHaveTextContent('No jobs match "golang"');
  expect(status()).toBe("0 jobs · 0 saved");
  await user.clear(search);
  expect(document.querySelector("p.empty")).toBeNull();
});

test("save toggles and survives searching", async () => {
  const user = userEvent.setup();
  mountJobBoard(root, JOBS);
  const aiItem = screen.getAllByRole("listitem")[1];
  await user.click(within(aiItem).getByRole("button", { name: "Save" }));
  expect(within(screen.getAllByRole("listitem")[1]).getByRole("button", { name: "Saved" })).toHaveAttribute("aria-pressed", "true");
  expect(status()).toBe("3 jobs · 1 saved");
  await user.type(screen.getByLabelText("Search jobs"), "ai");
  expect(screen.getByRole("button", { name: "Saved" })).toBeInTheDocument();
  expect(status()).toBe("1 jobs · 1 saved");
  await user.click(screen.getByRole("button", { name: "Saved" }));
  expect(status()).toBe("1 jobs · 0 saved");
});

test("pressing Enter doesn't submit the form", async () => {
  const user = userEvent.setup();
  mountJobBoard(root, JOBS);
  const submitted = vi.fn((event) => expect(event.defaultPrevented).toBe(true));
  screen.getByRole("search").addEventListener("submit", submitted);
  await user.type(screen.getByLabelText("Search jobs"), "data{Enter}");
  expect(submitted).toHaveBeenCalled();
});

test("job data is text, never HTML", () => {
  const evil = [{ id: 9, title: '<img src=x onerror="window.hacked=true">Pwned', company: "<b>Bad</b>", city: "X" }];
  mountJobBoard(root, evil);
  expect(root.querySelector("img")).toBeNull();
  expect(root.querySelector("b")).toBeNull();
  expect(titles()[0]).toContain("<img");
});

describe("event delegation and cleanup", () => {
  test("exactly one click listener, on the list", () => {
    const added = [];
    const original = EventTarget.prototype.addEventListener;
    vi.spyOn(EventTarget.prototype, "addEventListener").mockImplementation(function (type, listener, options) {
      added.push({ type, target: this });
      return original.call(this, type, listener, options);
    });
    mountJobBoard(root, JOBS);
    const clicks = added.filter((a) => a.type === "click");
    expect(clicks).toHaveLength(1);
    expect(clicks[0].target.tagName).toBe("UL");
  });

  test("cleanup removes the UI", () => {
    const cleanup = mountJobBoard(root, JOBS);
    expect(root.children.length).toBeGreaterThan(0);
    cleanup();
    expect(root.innerHTML).toBe("");
  });
});
