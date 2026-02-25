---
name: playwright-testing
description: End-to-end testing with Playwright covering browser automation, page object model, visual regression testing, API testing, component testing, authentication flows, network interception, accessibility testing, CI integration, and cross-browser testing strategies.
---

# Playwright E2E Testing

This skill should be used when building end-to-end tests, browser automation, or visual regression testing with Playwright. It covers test architecture, page objects, fixtures, and CI integration.

## When to Use This Skill

Use this skill when you need to:

- Write end-to-end tests for web applications
- Set up Playwright test infrastructure
- Create page object models
- Test authentication flows
- Intercept network requests in tests
- Run visual regression tests
- Integrate E2E tests into CI/CD

## Project Setup

```typescript
// playwright.config.ts
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ["html", { open: "never" }],
    ["junit", { outputFile: "test-results/junit.xml" }],
  ],
  use: {
    baseURL: process.env.BASE_URL ?? "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "on-first-retry",
  },
  projects: [
    { name: "setup", testMatch: /.*\.setup\.ts/ },
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
      dependencies: ["setup"],
    },
    {
      name: "firefox",
      use: { ...devices["Desktop Firefox"] },
      dependencies: ["setup"],
    },
    {
      name: "mobile-chrome",
      use: { ...devices["Pixel 5"] },
      dependencies: ["setup"],
    },
  ],
  webServer: {
    command: "npm run dev",
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
  },
});
```

## Page Object Model

```typescript
// e2e/pages/login.page.ts
import { type Locator, type Page, expect } from "@playwright/test";

export class LoginPage {
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(private page: Page) {
    this.emailInput = page.getByLabel("Email");
    this.passwordInput = page.getByLabel("Password");
    this.submitButton = page.getByRole("button", { name: "Sign in" });
    this.errorMessage = page.getByRole("alert");
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

// e2e/pages/dashboard.page.ts
export class DashboardPage {
  constructor(private page: Page) {}

  async expectLoggedIn(name: string) {
    await expect(this.page.getByText(`Welcome, ${name}`)).toBeVisible();
  }

  async navigateTo(section: string) {
    await this.page.getByRole("link", { name: section }).click();
  }
}
```

## Authentication Setup

```typescript
// e2e/auth.setup.ts
import { test as setup, expect } from "@playwright/test";
import path from "path";

const authFile = path.join(__dirname, ".auth/user.json");

setup("authenticate", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Email").fill("test@example.com");
  await page.getByLabel("Password").fill("password123");
  await page.getByRole("button", { name: "Sign in" }).click();
  await page.waitForURL("/dashboard");
  await expect(page.getByText("Welcome")).toBeVisible();
  // Save signed-in state
  await page.context().storageState({ path: authFile });
});

// Use in tests — automatically logged in
// e2e/dashboard.spec.ts
import { test, expect } from "@playwright/test";

test.use({ storageState: ".auth/user.json" });

test("dashboard loads with user data", async ({ page }) => {
  await page.goto("/dashboard");
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
});
```

## Custom Fixtures

```typescript
// e2e/fixtures.ts
import { test as base } from "@playwright/test";
import { LoginPage } from "./pages/login.page";
import { DashboardPage } from "./pages/dashboard.page";

type Fixtures = {
  loginPage: LoginPage;
  dashboardPage: DashboardPage;
  testUser: { email: string; password: string; name: string };
};

export const test = base.extend<Fixtures>({
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },
  dashboardPage: async ({ page }, use) => {
    await use(new DashboardPage(page));
  },
  testUser: async ({}, use) => {
    // Create user via API before test
    const user = { email: `test-${Date.now()}@example.com`, password: "pass123", name: "Test User" };
    await fetch("/api/test/users", { method: "POST", body: JSON.stringify(user) });
    await use(user);
    // Cleanup after test
    await fetch(`/api/test/users/${user.email}`, { method: "DELETE" });
  },
});

export { expect } from "@playwright/test";
```

## Network Interception

```typescript
import { test, expect } from "@playwright/test";

test("handles API errors gracefully", async ({ page }) => {
  // Mock API failure
  await page.route("**/api/products", (route) =>
    route.fulfill({ status: 500, body: JSON.stringify({ error: "Server error" }) }),
  );
  await page.goto("/products");
  await expect(page.getByText("Something went wrong")).toBeVisible();
  await expect(page.getByRole("button", { name: "Retry" })).toBeVisible();
});

test("loads products from API", async ({ page }) => {
  // Mock API success with specific data
  await page.route("**/api/products", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        { id: 1, name: "Widget", price: 9.99 },
        { id: 2, name: "Gadget", price: 19.99 },
      ]),
    }),
  );
  await page.goto("/products");
  await expect(page.getByText("Widget")).toBeVisible();
  await expect(page.getByText("$19.99")).toBeVisible();
});

test("waits for specific API response", async ({ page }) => {
  await page.goto("/dashboard");
  const response = await page.waitForResponse("**/api/analytics");
  expect(response.status()).toBe(200);
});
```

## Visual Regression Testing

```typescript
import { test, expect } from "@playwright/test";

test("homepage visual snapshot", async ({ page }) => {
  await page.goto("/");
  // Wait for animations/loading to complete
  await page.waitForLoadState("networkidle");
  await expect(page).toHaveScreenshot("homepage.png", {
    maxDiffPixelRatio: 0.01,
    fullPage: true,
  });
});

test("component visual snapshot", async ({ page }) => {
  await page.goto("/components");
  const card = page.getByTestId("product-card").first();
  await expect(card).toHaveScreenshot("product-card.png");
});

// Update snapshots: npx playwright test --update-snapshots
```

## API Testing

```typescript
import { test, expect } from "@playwright/test";

test.describe("API Tests", () => {
  test("CRUD operations", async ({ request }) => {
    // Create
    const createRes = await request.post("/api/items", {
      data: { name: "Test Item", price: 29.99 },
    });
    expect(createRes.ok()).toBeTruthy();
    const item = await createRes.json();
    expect(item.name).toBe("Test Item");

    // Read
    const getRes = await request.get(`/api/items/${item.id}`);
    expect(getRes.ok()).toBeTruthy();

    // Update
    const updateRes = await request.put(`/api/items/${item.id}`, {
      data: { name: "Updated Item" },
    });
    expect(updateRes.ok()).toBeTruthy();

    // Delete
    const deleteRes = await request.delete(`/api/items/${item.id}`);
    expect(deleteRes.ok()).toBeTruthy();
  });
});
```

## Accessibility Testing

```typescript
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("page has no accessibility violations", async ({ page }) => {
  await page.goto("/");
  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
    .analyze();
  expect(results.violations).toEqual([]);
});

test("form is keyboard navigable", async ({ page }) => {
  await page.goto("/contact");
  await page.keyboard.press("Tab");
  await expect(page.getByLabel("Name")).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.getByLabel("Email")).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.getByLabel("Message")).toBeFocused();
});
```

## Common Patterns

```typescript
// Wait for hydration (SSR apps)
test("SSR page hydrates correctly", async ({ page }) => {
  await page.goto("/");
  // Wait for React/Next.js hydration
  await page.waitForFunction(() => document.querySelector("[data-hydrated]"));
});

// File upload
test("upload file", async ({ page }) => {
  await page.goto("/upload");
  await page.getByLabel("Upload file").setInputFiles("./fixtures/test.pdf");
  await expect(page.getByText("test.pdf")).toBeVisible();
});

// Multi-tab / popup
test("OAuth popup flow", async ({ page, context }) => {
  const popupPromise = context.waitForEvent("page");
  await page.getByRole("button", { name: "Sign in with Google" }).click();
  const popup = await popupPromise;
  await popup.waitForLoadState();
  // Interact with popup...
});

// Drag and drop
test("reorder items", async ({ page }) => {
  await page.goto("/kanban");
  const source = page.getByText("Task 1");
  const target = page.getByText("Done column");
  await source.dragTo(target);
});
```

## CI Configuration (GitHub Actions)

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
          retention-days: 7
```

## Additional Resources

- Playwright Docs: https://playwright.dev/docs/intro
- Best Practices: https://playwright.dev/docs/best-practices
- Test Generator: `npx playwright codegen localhost:3000`
- UI Mode: `npx playwright test --ui`
- Debug: `npx playwright test --debug`
