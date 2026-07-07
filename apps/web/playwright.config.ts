import { defineConfig, devices } from "@playwright/test";

const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:8080";

export default defineConfig({
  testDir: "./tests/e2e",
  timeout: 30_000,
  expect: {
    timeout: 5_000,
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: "list",
  use: {
    baseURL,
    trace: "retain-on-failure",
  },
  projects: [
    {
      name: "mobile-390",
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 390, height: 844 },
      },
    },
    {
      name: "mobile-393",
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 393, height: 852 },
      },
    },
    {
      name: "mobile-414",
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 414, height: 896 },
      },
    },
    {
      name: "mobile-430",
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 430, height: 932 },
      },
    },
  ],
});
