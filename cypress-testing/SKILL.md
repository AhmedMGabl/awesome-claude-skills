---
name: cypress-testing
description: Cypress end-to-end testing covering component testing, custom commands, fixtures, intercepts for API mocking, visual regression with Percy, authentication flows, CI configuration, retry strategies, and best practices for reliable test suites.
---

# Cypress Testing

This skill should be used when writing end-to-end or component tests with Cypress. It covers test structure, custom commands, API interception, authentication, and CI integration.

## When to Use This Skill

Use this skill when you need to:

- Write E2E tests for web applications
- Test user flows and interactions
- Mock API responses in tests
- Set up authentication in test suites
- Run Cypress in CI/CD pipelines

## Basic Test Structure

```typescript
// cypress/e2e/auth.cy.ts
describe("Authentication", () => {
  beforeEach(() => {
    cy.visit("/login");
  });

  it("logs in successfully", () => {
    cy.get("[data-testid=email]").type("user@example.com");
    cy.get("[data-testid=password]").type("password123");
    cy.get("[data-testid=submit]").click();

    cy.url().should("include", "/dashboard");
    cy.get("[data-testid=welcome]").should("contain", "Welcome");
  });

  it("shows validation errors", () => {
    cy.get("[data-testid=submit]").click();

    cy.get("[data-testid=email-error]").should("be.visible");
    cy.get("[data-testid=password-error]").should("be.visible");
  });

  it("handles incorrect credentials", () => {
    cy.get("[data-testid=email]").type("user@example.com");
    cy.get("[data-testid=password]").type("wrongpassword");
    cy.get("[data-testid=submit]").click();

    cy.get("[data-testid=error-message]")
      .should("be.visible")
      .and("contain", "Invalid credentials");
  });
});
```

## API Interception

```typescript
describe("Dashboard", () => {
  beforeEach(() => {
    // Intercept API calls
    cy.intercept("GET", "/api/users", { fixture: "users.json" }).as("getUsers");
    cy.intercept("GET", "/api/stats", {
      statusCode: 200,
      body: { revenue: 50000, users: 1200, orders: 340 },
    }).as("getStats");

    cy.loginByAPI("admin@example.com", "password");
    cy.visit("/dashboard");
  });

  it("loads and displays data", () => {
    cy.wait(["@getUsers", "@getStats"]);

    cy.get("[data-testid=revenue]").should("contain", "$50,000");
    cy.get("[data-testid=user-count]").should("contain", "1,200");
  });

  it("handles API errors gracefully", () => {
    cy.intercept("GET", "/api/stats", { statusCode: 500, body: { error: "Server error" } }).as("statsError");
    cy.visit("/dashboard");

    cy.wait("@statsError");
    cy.get("[data-testid=error-banner]").should("be.visible");
    cy.get("[data-testid=retry-button]").should("be.visible");
  });

  it("paginates through users", () => {
    cy.intercept("GET", "/api/users?page=2", { fixture: "users-page2.json" }).as("getPage2");

    cy.get("[data-testid=next-page]").click();
    cy.wait("@getPage2");
    cy.get("[data-testid=user-row]").should("have.length", 20);
  });
});
```

## Custom Commands

```typescript
// cypress/support/commands.ts
declare global {
  namespace Cypress {
    interface Chainable {
      loginByAPI(email: string, password: string): Chainable;
      loginByUI(email: string, password: string): Chainable;
    }
  }
}

// Fast login via API (use for most tests)
Cypress.Commands.add("loginByAPI", (email: string, password: string) => {
  cy.request("POST", "/api/auth/login", { email, password }).then((res) => {
    window.localStorage.setItem("token", res.body.token);
  });
});

// UI login (use only for testing login flow itself)
Cypress.Commands.add("loginByUI", (email: string, password: string) => {
  cy.visit("/login");
  cy.get("[data-testid=email]").type(email);
  cy.get("[data-testid=password]").type(password);
  cy.get("[data-testid=submit]").click();
  cy.url().should("include", "/dashboard");
});
```

## Cypress Config

```typescript
// cypress.config.ts
import { defineConfig } from "cypress";

export default defineConfig({
  e2e: {
    baseUrl: "http://localhost:3000",
    viewportWidth: 1280,
    viewportHeight: 720,
    video: false,
    screenshotOnRunFailure: true,
    retries: { runMode: 2, openMode: 0 },
    defaultCommandTimeout: 10000,
    setupNodeEvents(on, config) {
      // Plugins
    },
  },
  component: {
    devServer: { framework: "react", bundler: "vite" },
  },
});
```

## CI Configuration

```yaml
# .github/workflows/cypress.yml
name: Cypress Tests
on: [push, pull_request]
jobs:
  cypress:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: cypress-io/github-action@v6
        with:
          build: npm run build
          start: npm start
          wait-on: "http://localhost:3000"
          wait-on-timeout: 120
          browser: chrome
```

## Additional Resources

- Cypress docs: https://docs.cypress.io/
- Best Practices: https://docs.cypress.io/guides/references/best-practices
- Cypress Real World App: https://github.com/cypress-io/cypress-realworld-app
