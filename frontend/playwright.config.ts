import { defineConfig, devices } from '@playwright/test';

/**
 * E2E Testing Configuration for MeStore Marketplace
 *
 * @author e2e-testing-ai
 * @date 2025-10-01
 *
 * Purpose: Complete checkout flow testing from marketplace to Wompi payment
 */

export default defineConfig({
  testDir: './tests/e2e',

  /* Maximum time one test can run for */
  timeout: 60 * 1000,

  /* Run tests in files in parallel */
  fullyParallel: false, // Sequential for checkout flow

  /* Fail the build on CI if you accidentally left test.only in the source code */
  forbidOnly: !!process.env.CI,

  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,

  /* Opt out of parallel tests on CI */
  workers: process.env.CI ? 1 : 1, // Single worker for checkout state management

  /* Reporter to use */
  reporter: [
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['list']
  ],

  /* Shared settings for all the projects below */
  use: {
    /* Base URL to use in actions like `await page.goto('/')` */
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://192.168.1.137:5173',

    /* Collect trace when retrying the failed test */
    trace: 'retain-on-failure',

    /* Screenshot on failure */
    screenshot: 'only-on-failure',

    /* Video on failure */
    video: 'retain-on-failure',

    /* Maximum time each action can take */
    actionTimeout: 15 * 1000,

    /* Navigation timeout */
    navigationTimeout: 30 * 1000,
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 }
      },
    },

    /* Test against mobile viewports */
    {
      name: 'mobile-chrome',
      use: {
        ...devices['Pixel 5']
      },
    },
  ],

  /* Run your local dev server before starting the tests */
  webServer: {
    command: 'npm run dev',
    url: 'http://192.168.1.137:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
