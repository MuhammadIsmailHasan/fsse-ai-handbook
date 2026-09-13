import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { readFileSync } from "node:fs";
import { describe, expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";
import { ProfileForm } from "./profile-form";
import { profileSchema, type ProfileValues } from "./profile-schema";

const defaults: ProfileValues = { name: "Sari", email: "sari@example.com", headline: "Backend developer", links: [{ label: "GitHub", url: "https://github.com/sari" }] };

describe("schema", () => {
  test("valid and trimmed", () => {
    expect(profileSchema.parse({ ...defaults, name: "  Sari W ", links: [] })).toMatchObject({ name: "Sari W", links: [] });
  });

  test("messages", () => {
    const result = profileSchema.safeParse({ name: "S", email: "nope", headline: "x".repeat(121), links: [{ label: "", url: "github.com" }] });
    const messages = Object.fromEntries(result.error!.issues.map((i) => [i.path.join("."), i.message]));
    expect(messages).toEqual({
      name: "Name must be at least 2 characters",
      email: "Enter a valid email",
      headline: "Keep your headline under 120 characters",
      "links.0.label": "Label is required",
      "links.0.url": "Enter a full URL, e.g. https://…",
    });
    expect(profileSchema.safeParse({ ...defaults, links: Array(6).fill(defaults.links[0]) }).success).toBe(false);
  });
});

describe("form", () => {
  test("uses RHF + zodResolver + useFieldArray", () => {
    const source = readFileSync(`${import.meta.dirname}/profile-form.tsx`, "utf8");
    expect(source).toMatch(/useForm/);
    expect(source).toMatch(/zodResolver\(profileSchema\)/);
    expect(source).toMatch(/useFieldArray/);
  });

  test("client validation blocks submit and is accessible", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(<ProfileForm defaultValues={defaults} onSubmit={onSubmit} />);
    await user.clear(screen.getByLabelText("Name"));
    await user.type(screen.getByLabelText("Name"), "S");
    await user.tab();
    expect(await screen.findByText("Name must be at least 2 characters")).toBeInTheDocument();
    expect(screen.getByLabelText("Name")).toHaveAttribute("aria-invalid", "true");
    expect(screen.getByLabelText("Name")).toHaveAccessibleDescription("Name must be at least 2 characters");
    await user.clear(screen.getByLabelText("Link 1 URL"));
    await user.type(screen.getByLabelText("Link 1 URL"), "github.com");
    await user.click(screen.getByRole("button", { name: "Save profile" }));
    expect(await screen.findByText("Enter a full URL, e.g. https://…")).toBeInTheDocument();
    expect(screen.getByLabelText("Link 1 URL")).toHaveAccessibleDescription("Enter a full URL, e.g. https://…");
    expect(onSubmit).not.toHaveBeenCalled();
  });

  test("dynamic links", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();
    render(<ProfileForm defaultValues={defaults} onSubmit={onSubmit} />);
    const add = screen.getByRole("button", { name: "Add link" });
    for (let i = 0; i < 4; i++) await user.click(add);
    expect(screen.getByLabelText("Link 5 label")).toBeInTheDocument();
    expect(add).toBeDisabled();
    await user.type(screen.getByLabelText("Link 2 label"), "Blog");
    await user.click(screen.getByRole("button", { name: "Remove link 1" }));
    expect(screen.getByLabelText("Link 1 label")).toHaveValue("Blog");
    for (let i = 0; i < 3; i++) await user.click(screen.getByRole("button", { name: "Remove link 2" }));
    expect(add).toBeEnabled();
    await user.type(screen.getByLabelText("Link 1 URL"), "https://sari.dev");
    await user.click(screen.getByRole("button", { name: "Save profile" }));
    await waitFor(() => expect(onSubmit).toHaveBeenCalledTimes(1));
    expect(onSubmit.mock.calls[0]![0]).toEqual({ ...defaults, links: [{ label: "Blog", url: "https://sari.dev" }] });
  });

  test("server errors, pending state, success", async () => {
    let resolveSubmit!: (value: unknown) => void;
    const onSubmit = vi
      .fn()
      .mockImplementationOnce(() => new Promise((resolve) => (resolveSubmit = resolve)))
      .mockResolvedValueOnce({ message: "Could not save right now" })
      .mockResolvedValueOnce(undefined);
    const user = userEvent.setup();
    render(<ProfileForm defaultValues={defaults} onSubmit={onSubmit} />);
    const save = screen.getByRole("button", { name: "Save profile" });

    await user.click(save);
    await waitFor(() => expect(save).toBeDisabled());
    resolveSubmit({ fieldErrors: { email: "Email already in use" } });
    expect(await screen.findByText("Email already in use")).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toHaveAccessibleDescription("Email already in use");
    expect(save).toBeEnabled();

    await user.click(save);
    expect(await screen.findByRole("alert")).toHaveTextContent("Could not save right now");

    await user.clear(screen.getByLabelText("Headline"));
    await user.type(screen.getByLabelText("Headline"), "Full-stack developer");
    await user.click(save);
    expect(await screen.findByRole("status")).toHaveTextContent("Profile saved");
    expect(onSubmit.mock.calls[2]![0].headline).toBe("Full-stack developer");
    expect(screen.getByLabelText("Headline")).toHaveValue("Full-stack developer");
  });
});

test("types", () => {
  expect(typecheckFolder(import.meta.dirname).output).toBe("");
});
