// Adds matchers like expect(element).toBeInTheDocument() and cleans the DOM after each test.
import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

afterEach(() => {
  cleanup();
  document.body.innerHTML = "";
});
