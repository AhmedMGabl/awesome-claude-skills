---
name: playwright-component
description: Playwright Component Testing patterns covering mounting React, Vue, and Svelte components, prop and slot testing, event handling, visual regression, accessibility checks, and integration with Vite for isolated component testing.
---

# Playwright Component Testing

This skill should be used when testing UI components in isolation with Playwright Component Testing. It covers mounting, interaction, visual regression, and accessibility testing.

## When to Use This Skill

Use this skill when you need to:

- Test React, Vue, or Svelte components in a real browser
- Mount components with props, slots, and context
- Verify visual appearance with screenshot comparisons
- Test component interactions (click, type, drag)
- Run accessibility checks on individual components

## Setup

```typescript
// playwright-ct.config.ts
import { defineConfig, devices } from "@playwright/experimental-ct-react";

export default defineConfig({
  testDir: "./src",
  testMatch: "**/*.spec.tsx",
  use: {
    ctPort: 3100,
    ctViteConfig: {
      resolve: {
        alias: { "@": "./src" },
      },
    },
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
    { name: "webkit", use: { ...devices["Desktop Safari"] } },
  ],
});
```

## React Component Testing

```tsx
// src/components/Button.spec.tsx
import { test, expect } from "@playwright/experimental-ct-react";
import { Button } from "./Button";

test.describe("Button", () => {
  test("renders with text", async ({ mount }) => {
    const component = await mount(<Button>Click me</Button>);
    await expect(component).toContainText("Click me");
  });

  test("applies variant styles", async ({ mount }) => {
    const component = await mount(<Button variant="primary">Primary</Button>);
    await expect(component).toHaveCSS("background-color", "rgb(59, 130, 246)");
  });

  test("handles click events", async ({ mount }) => {
    let clicked = false;
    const component = await mount(
      <Button onClick={() => (clicked = true)}>Click</Button>,
    );
    await component.click();
    expect(clicked).toBe(true);
  });

  test("is disabled when loading", async ({ mount }) => {
    const component = await mount(<Button loading>Submit</Button>);
    await expect(component).toBeDisabled();
    await expect(component).toContainText("Loading...");
  });

  test("matches screenshot", async ({ mount }) => {
    const component = await mount(<Button variant="primary">Submit</Button>);
    await expect(component).toHaveScreenshot("button-primary.png");
  });
});
```

## Testing with Context and Providers

```tsx
// src/components/ThemeToggle.spec.tsx
import { test, expect } from "@playwright/experimental-ct-react";
import { ThemeToggle } from "./ThemeToggle";
import { ThemeProvider } from "../context/ThemeContext";

test("toggles theme", async ({ mount }) => {
  const component = await mount(
    <ThemeProvider>
      <ThemeToggle />
    </ThemeProvider>,
  );

  // Initially light mode
  await expect(component.getByRole("button")).toContainText("Dark mode");

  // Toggle to dark
  await component.getByRole("button").click();
  await expect(component.getByRole("button")).toContainText("Light mode");
});
```

## Form Component Testing

```tsx
// src/components/LoginForm.spec.tsx
import { test, expect } from "@playwright/experimental-ct-react";
import { LoginForm } from "./LoginForm";

test.describe("LoginForm", () => {
  test("submits with valid data", async ({ mount }) => {
    let submitted: { email: string; password: string } | null = null;

    const component = await mount(
      <LoginForm onSubmit={(data) => (submitted = data)} />,
    );

    await component.getByLabel("Email").fill("user@example.com");
    await component.getByLabel("Password").fill("password123");
    await component.getByRole("button", { name: "Log in" }).click();

    expect(submitted).toEqual({
      email: "user@example.com",
      password: "password123",
    });
  });

  test("shows validation errors", async ({ mount }) => {
    const component = await mount(<LoginForm onSubmit={() => {}} />);

    await component.getByRole("button", { name: "Log in" }).click();

    await expect(component.getByText("Email is required")).toBeVisible();
    await expect(component.getByText("Password is required")).toBeVisible();
  });

  test("disables submit while loading", async ({ mount }) => {
    const component = await mount(<LoginForm loading onSubmit={() => {}} />);
    await expect(component.getByRole("button", { name: /log/i })).toBeDisabled();
  });
});
```

## Visual Regression Testing

```tsx
// src/components/Card.spec.tsx
import { test, expect } from "@playwright/experimental-ct-react";
import { Card } from "./Card";

test.describe("Card visual regression", () => {
  test("default state", async ({ mount }) => {
    const component = await mount(
      <Card title="Hello" description="World" />,
    );
    await expect(component).toHaveScreenshot("card-default.png");
  });

  test("hover state", async ({ mount }) => {
    const component = await mount(
      <Card title="Hello" description="World" hoverable />,
    );
    await component.hover();
    await expect(component).toHaveScreenshot("card-hover.png");
  });

  test("dark mode", async ({ mount, page }) => {
    await page.emulateMedia({ colorScheme: "dark" });
    const component = await mount(
      <Card title="Hello" description="World" />,
    );
    await expect(component).toHaveScreenshot("card-dark.png");
  });
});
```

## Accessibility Testing

```tsx
// src/components/Dialog.spec.tsx
import { test, expect } from "@playwright/experimental-ct-react";
import { Dialog } from "./Dialog";

test("meets accessibility requirements", async ({ mount }) => {
  const component = await mount(
    <Dialog open title="Confirm Action">
      <p>Are you sure?</p>
    </Dialog>,
  );

  // Check ARIA attributes
  await expect(component.getByRole("dialog")).toBeVisible();
  await expect(component.getByRole("dialog")).toHaveAttribute(
    "aria-labelledby",
  );

  // Check focus management
  await expect(component.getByRole("button", { name: "Close" })).toBeFocused();

  // Check keyboard navigation
  await component.press("Escape");
  // Dialog should close
});
```

## Additional Resources

- Playwright CT docs: https://playwright.dev/docs/test-components
- React testing: https://playwright.dev/docs/test-components#react
- Visual comparisons: https://playwright.dev/docs/test-snapshots
