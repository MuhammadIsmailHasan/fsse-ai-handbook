// Adds matchers like expect(element).toBeInTheDocument() and cleans the DOM after each test.
import "@testing-library/jest-dom/vitest";
import { afterEach } from "vitest";

afterEach(async () => {
  if (typeof document === "undefined") return; // tests marked `// @vitest-environment node` have no DOM
  const { cleanup } = await import("@testing-library/react");
  cleanup();
  document.body.innerHTML = "";
});
