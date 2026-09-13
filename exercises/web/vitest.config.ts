// One test setup for every JavaScript / TypeScript / React exercise.
//   cd exercises/web
//   npm install
//   npx vitest run m4/w1/04-js-basics      ← run one exercise
import { fileURLToPath } from "node:url";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  resolve: {
    // Shared test helpers: import { parseCss } from "@support/css"
    alias: { "@support": fileURLToPath(new URL("./_support", import.meta.url)) },
  },
  test: {
    environment: "jsdom", // a simulated browser: document, window, events
    setupFiles: ["./vitest.setup.ts"],
    include: ["**/*.test.{js,ts,tsx}"],
    exclude: ["**/node_modules/**", "**/solution/**"],
    restoreMocks: true,
  },
});
