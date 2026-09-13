// One test setup for every JavaScript / TypeScript / React exercise.
//   cd exercises/web
//   npm install
//   npx vitest run m4/w1/04-js-basics      ← run one exercise
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom", // a simulated browser: document, window, events
    setupFiles: ["./vitest.setup.ts"],
    include: ["**/*.test.{ts,tsx}"],
    exclude: ["**/node_modules/**", "**/solution/**"],
    restoreMocks: true,
  },
});
