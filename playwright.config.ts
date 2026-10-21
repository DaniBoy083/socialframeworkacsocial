import { defineConfig, devices } from "@playwright/test";
export default defineConfig({
  testDir: "./tests",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  use: {
    baseURL: "http://localhost:3000",
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
  },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"] } },
    {
      name: "mobile",
      use: { ...devices["iPhone 13"], defaultBrowserType: "chromium" },
    },
  ],
  webServer: [
    {
      command: "node tests/fixtures/api-server.mjs",
      url: "http://127.0.0.1:18001/health",
      reuseExistingServer: false,
    },
    {
      command: "npm run dev",
      url: "http://localhost:3000/login",
      reuseExistingServer: false,
      timeout: 120000,
      env: {
        SOCIAL_API_URL: "http://127.0.0.1:18001",
        APP_ORIGIN: "http://localhost:3000",
      },
    },
  ],
});
