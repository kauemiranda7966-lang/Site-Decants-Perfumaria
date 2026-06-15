const { defineConfig, devices } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./tests/e2e",
  globalSetup: require.resolve("./tests/e2e/global-setup"),
  fullyParallel: false,
  retries: 1,
  reporter: "list",
  use: {
    baseURL: "http://127.0.0.1:8765",
    trace: "retain-on-failure"
  },
  projects: [
    {
      name: "desktop-chromium",
      use: { ...devices["Desktop Chrome"] }
    },
    {
      name: "mobile-chromium",
      use: { ...devices["Pixel 7"] }
    }
  ]
});
