---
name: accessibility-testing
description: Accessibility testing and automation covering axe-core integration, Playwright accessibility audits, screen reader testing patterns, ARIA attribute validation, color contrast checking, keyboard navigation testing, focus management, and automated a11y CI pipeline setup.
---

# Accessibility Testing

This skill should be used when testing web applications for accessibility compliance. It covers automated testing with axe-core, screen reader patterns, keyboard navigation, and CI integration.

## When to Use This Skill

Use this skill when you need to:

- Run automated accessibility audits
- Test keyboard navigation
- Validate ARIA attributes and roles
- Check color contrast compliance
- Set up a11y testing in CI pipelines
- Test with screen reader patterns

## axe-core with Playwright

```typescript
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test.describe("Accessibility", () => {
  test("homepage has no a11y violations", async ({ page }) => {
    await page.goto("/");

    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
      .exclude(".third-party-widget")
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test("login form is accessible", async ({ page }) => {
    await page.goto("/login");

    const results = await new AxeBuilder({ page })
      .include("#login-form")
      .analyze();

    // Report violations with details
    if (results.violations.length > 0) {
      const report = results.violations.map((v) => ({
        id: v.id,
        impact: v.impact,
        description: v.description,
        nodes: v.nodes.map((n) => n.html),
      }));
      console.error("A11y violations:", JSON.stringify(report, null, 2));
    }

    expect(results.violations).toEqual([]);
  });

  test("each page passes audit", async ({ page }) => {
    const pages = ["/", "/about", "/dashboard", "/settings"];

    for (const url of pages) {
      await page.goto(url);
      const results = await new AxeBuilder({ page }).analyze();
      expect(results.violations, `Violations on ${url}`).toEqual([]);
    }
  });
});
```

## Keyboard Navigation Testing

```typescript
test("modal has proper focus trap", async ({ page }) => {
  await page.goto("/dashboard");
  await page.getByRole("button", { name: "Open Settings" }).click();

  // Modal should be visible
  const modal = page.getByRole("dialog");
  await expect(modal).toBeVisible();

  // First focusable element should have focus
  const firstInput = modal.getByRole("textbox").first();
  await expect(firstInput).toBeFocused();

  // Tab through all focusable elements
  await page.keyboard.press("Tab");
  await page.keyboard.press("Tab");
  await page.keyboard.press("Tab");

  // Should not escape modal (focus trap)
  const focusedElement = page.locator(":focus");
  await expect(focusedElement).toBeAttached();
  const isInModal = await focusedElement.evaluate((el) =>
    el.closest("[role='dialog']") !== null,
  );
  expect(isInModal).toBe(true);

  // Escape should close modal
  await page.keyboard.press("Escape");
  await expect(modal).not.toBeVisible();

  // Focus should return to trigger button
  await expect(page.getByRole("button", { name: "Open Settings" })).toBeFocused();
});

test("skip link works", async ({ page }) => {
  await page.goto("/");
  await page.keyboard.press("Tab");

  const skipLink = page.getByText("Skip to main content");
  await expect(skipLink).toBeFocused();

  await page.keyboard.press("Enter");
  const main = page.getByRole("main");
  await expect(main).toBeFocused();
});
```

## React Testing Library A11y

```typescript
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe, toHaveNoViolations } from "jest-axe";

expect.extend(toHaveNoViolations);

test("form is accessible", async () => {
  const { container } = render(<SignupForm />);

  // axe-core audit
  const results = await axe(container);
  expect(results).toHaveNoViolations();

  // Labels are associated with inputs
  expect(screen.getByLabelText("Email")).toBeInTheDocument();
  expect(screen.getByLabelText("Password")).toBeInTheDocument();

  // Error messages are announced
  await userEvent.click(screen.getByRole("button", { name: "Sign Up" }));
  const errors = screen.getAllByRole("alert");
  expect(errors.length).toBeGreaterThan(0);
});

test("uses correct ARIA roles", () => {
  render(<Navigation />);
  expect(screen.getByRole("navigation")).toBeInTheDocument();
  expect(screen.getByRole("menubar")).toBeInTheDocument();
});
```

## A11y Checklist for Developers

```
AUTOMATED (axe-core catches these):
  [ ] All images have alt text
  [ ] Form inputs have associated labels
  [ ] Color contrast meets WCAG AA (4.5:1 text, 3:1 large)
  [ ] Page has exactly one <h1>
  [ ] Heading levels don't skip (h1 → h3)
  [ ] ARIA attributes are valid
  [ ] No duplicate IDs

MANUAL TESTING REQUIRED:
  [ ] Tab order is logical and visible
  [ ] Focus indicators are visible
  [ ] Modals trap focus
  [ ] Skip links work
  [ ] Content makes sense without visual context
  [ ] Animations respect prefers-reduced-motion
  [ ] Touch targets are at least 44x44px
  [ ] Error messages are descriptive and helpful
```

## Additional Resources

- axe-core: https://github.com/dequelabs/axe-core
- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- WAI-ARIA patterns: https://www.w3.org/WAI/ARIA/apg/patterns/
- jest-axe: https://github.com/nickcolley/jest-axe
