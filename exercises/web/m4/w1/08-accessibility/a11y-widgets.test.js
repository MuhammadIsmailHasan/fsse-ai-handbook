import { screen } from "@testing-library/dom";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, test } from "vitest";
import { createTabs, validateSignup } from "./a11y-widgets.js";

const TABS = [
  { id: "all", label: "All jobs", content: "12 jobs" },
  { id: "saved", label: "Saved", content: "3 saved jobs" },
  { id: "applied", label: "Applied", content: "5 applications" },
];

describe("tabs", () => {
  beforeEach(() => {
    const root = document.createElement("div");
    document.body.append(root);
    createTabs(root, TABS);
  });

  const selected = () => screen.getAllByRole("tab").filter((t) => t.getAttribute("aria-selected") === "true").map((t) => t.textContent);

  test("structure and initial state", () => {
    expect(screen.getByRole("tablist")).toBeInTheDocument();
    const tabs = screen.getAllByRole("tab");
    expect(tabs.map((t) => t.textContent)).toEqual(["All jobs", "Saved", "Applied"]);
    expect(tabs.map((t) => t.getAttribute("tabindex"))).toEqual(["0", "-1", "-1"]);
    expect(tabs[1]).toHaveAttribute("aria-controls", "panel-saved");
    const panel = screen.getByRole("tabpanel", { name: "All jobs" });
    expect(panel).toHaveTextContent("12 jobs");
    expect(document.getElementById("panel-saved")).toHaveAttribute("hidden");
    expect(screen.queryByRole("tabpanel", { name: "Saved" })).toBeNull();
  });

  test("click selects", async () => {
    await userEvent.setup().click(screen.getByRole("tab", { name: "Applied" }));
    expect(selected()).toEqual(["Applied"]);
    expect(screen.getByRole("tabpanel", { name: "Applied" })).toHaveTextContent("5 applications");
    expect(screen.getByRole("tab", { name: "Applied" })).toHaveAttribute("tabindex", "0");
  });

  test("keyboard: Tab into the list, arrows, wrap, Home and End", async () => {
    const user = userEvent.setup();
    await user.tab();
    expect(screen.getByRole("tab", { name: "All jobs" })).toHaveFocus();
    await user.keyboard("{ArrowRight}");
    expect(selected()).toEqual(["Saved"]);
    expect(screen.getByRole("tab", { name: "Saved" })).toHaveFocus();
    await user.keyboard("{ArrowRight}{ArrowRight}");
    expect(selected()).toEqual(["All jobs"]);
    await user.keyboard("{ArrowLeft}");
    expect(selected()).toEqual(["Applied"]);
    await user.keyboard("{Home}");
    expect(screen.getByRole("tab", { name: "All jobs" })).toHaveFocus();
    await user.keyboard("{End}");
    expect(selected()).toEqual(["Applied"]);
    await user.tab();
    expect(screen.getByRole("tab", { name: "Applied" })).not.toHaveFocus();
  });
});

describe("form validation", () => {
  let form;
  beforeEach(() => {
    document.body.innerHTML = `
      <form>
        <label for="email">Email</label><input id="email" type="email"><p id="email-error"></p>
        <label for="password">Password</label><input id="password" type="password"><p id="password-error"></p>
        <button type="submit">Sign up</button>
      </form>`;
    form = document.querySelector("form");
  });

  test("marks invalid fields, describes errors and focuses the first", async () => {
    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Email"), "not-an-email");
    await user.type(screen.getByLabelText("Password"), "short");
    expect(validateSignup(form)).toBe(false);
    const email = screen.getByLabelText("Email");
    expect(email).toHaveAttribute("aria-invalid", "true");
    expect(email).toHaveAccessibleDescription("Enter a valid email address");
    expect(screen.getByLabelText("Password")).toHaveAccessibleDescription("Password must be at least 8 characters");
    expect(email).toHaveFocus();
  });

  test("fixing fields clears errors", async () => {
    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Password"), "short");
    validateSignup(form);
    expect(screen.getByLabelText("Email")).toHaveFocus();
    await user.type(screen.getByLabelText("Email"), "siti@example.com");
    expect(validateSignup(form)).toBe(false);
    expect(screen.getByLabelText("Email")).not.toHaveAttribute("aria-invalid");
    expect(document.getElementById("email-error")).toHaveTextContent("");
    expect(screen.getByLabelText("Password")).toHaveFocus();
    await user.type(screen.getByLabelText("Password"), "-long-enough");
    expect(validateSignup(form)).toBe(true);
    expect(screen.getByLabelText("Password")).not.toHaveAttribute("aria-describedby");
  });
});
