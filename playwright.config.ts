import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./tests",
  testMatch: "**/*.spec.ts",
  timeout: 60000,
  use: { baseURL: "http://localhost:5173", headless: true },
  workers: 1,
  reporter: "list",
});
