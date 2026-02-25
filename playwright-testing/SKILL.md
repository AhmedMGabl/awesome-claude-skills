---
name: playwright-testing
description: Playwright end-to-end testing covering browser automation, page object models, network interception, visual regression testing, component testing, authentication state reuse, parallel execution, trace viewer debugging, and CI/CD integration with GitHub Actions.
---

# Playwright Testing

This skill should be used when writing end-to-end tests with Playwright. It covers browser automation, page objects, network mocking, visual testing, and CI integration.

## When to Use This Skill

Use this skill when you need to:

- Write cross-browser E2E tests
- Implement page object models for maintainable tests
- Mock API responses in tests
- Set up visual regression testing
- Run Playwright tests in CI pipelines

## Basic Test

```typescript
// tests/login.spec.ts
import { test, expect } from "@playwright/test";

test.describe("Login", () => {
  test("should login with valid credentials", async ({ page }) => {
    await page.goto("/login");

    await page.getByLabel("Email").fill("user@example.com");
    await page.getByLabel("Password").fill("password123");
    await page.getByRole("button", { name: "Sign in" }).click();

    await expect(page).toHaveURL("/dashboard");
    await expect(page.getByRole("heading", { name: "Welcome" })).toBeVisible();
  });

  test("should show error for invalid credentials", async ({ page }) => {
    await page.goto("/login");

    await page.getByLabel("Email").fill("wrong@example.com");
    await page.getByLabel("Password").fill("wrong");
    await page.getByRole("button", { name: "Sign in" }).click();

    await expect(page.getByText("Invalid credentials")).toBeVisible();
  });
});
```

## Page Object Model

```typescript
// pages/login-page.ts
import { Page, Locator, expect } from "@playwright/test";

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel("Email");
    this.passwordInput = page.getByLabel("Password");
    this.submitButton = page.getByRole("button", { name: "Sign in" });
    this.errorMessage = page.getByTestId("error-message");
  }

  async goto() {
    await this.page.goto("/login");
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async expectError(message: string) {
    await expect(this.errorMessage).toContainText(message);
  }
}

// Usage in test
test("login flow", async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login("user@example.com", "password123");
  await expect(page).toHaveURL("/dashboard");
});
```

## Network Interception

```typescript
test("should display products from API", async ({ page }) => {
  await page.route("**/api/products", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        { id: 1, name: "Widget", price: 9.99 },
        { id: 2, name: "Gadget", price: 24.99 },
      ]),
    });
  });

  await page.goto("/products");
  await expect(page.getByText("Widget")).toBeVisible();
  await expect(page.getByText("$9.99")).toBeVisible();
});

// Wait for specific API call
test("should submit form", async ({ page }) => {
  await page.goto("/contact");

  const responsePromise = page.waitForResponse("**/api/contact");
  await page.getByLabel("Message").fill("Hello");
  await page.getByRole("button", { name: "Send" }).click();

  const response = await responsePromise;
  expect(response.status()).toBe(200);
});
```

## Authentication State Reuse

```typescript
// auth.setup.ts
import { test as setup, expect } from "@playwright/test";

const authFile = "playwright/.auth/user.json";

setup("authenticate", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Email").fill("user@example.com");
  await page.getByLabel("Password").fill("password123");
  await page.getByRole("button", { name: "Sign in" }).click();
  await page.waitForURL("/dashboard");
  await page.context().storageState({ path: authFile });
});

// playwright.config.ts
export default defineConfig({
  projects: [
    { name: "setup", testMatch: /.*\.setup\.ts/ },
    {
      name: "chromium",
      dependencies: ["setup"],
      use: { storageState: authFile },
    },
  ],
});
```

## Visual Regression

```typescript
test("homepage visual regression", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveScreenshot("homepage.png", {
    maxDiffPixelRatio: 0.01,
  });
});
```

## Configuration

```typescript
// playwright.config.ts
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: [["html"], ["junit", { outputFile: "results.xml" }]],
  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
    { name: "mobile", use: { ...devices["iPhone 14"] } },
  ],
  webServer: {
    command: "npm run dev",
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
  },
});
```

## CI Integration

```yaml
# .github/workflows/e2e.yml
name: E2E Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npx playwright test
      - uses: actions/upload-artifact@v4
        if: ${{ !cancelled() }}
        with:
          name: playwright-report
          path: playwright-report/
```

## Additional Resources

- Playwright docs: https://playwright.dev/docs/intro
- Best practices: https://playwright.dev/docs/best-practices
- Trace viewer: https://playwright.dev/docs/trace-viewer
