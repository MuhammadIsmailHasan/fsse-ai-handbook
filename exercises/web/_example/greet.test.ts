import { expect, test } from "vitest";
import { greet } from "./greet";

test("greets by name", () => {
  expect(greet(" Siti ")).toBe("Halo, Siti!");
  expect(greet("  ")).toBe("Halo, teman!");
});
