---
name: vitest-patterns
description: Vitest testing patterns covering test organization, mocking with vi.fn/vi.mock, snapshot testing, concurrent tests, coverage, workspace projects, browser mode, and integration with React Testing Library.
---

# Vitest Patterns

This skill should be used when writing tests with Vitest. It covers test organization, mocking, snapshots, concurrent testing, coverage, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Write fast unit and integration tests
- Mock modules, functions, and timers
- Test React/Vue/Svelte components with Vitest
- Configure workspaces for monorepo testing
- Generate code coverage reports

## Basic Tests

```typescript
import { describe, it, expect, beforeEach, afterEach } from "vitest";

describe("Calculator", () => {
  let calc: Calculator;

  beforeEach(() => {
    calc = new Calculator();
  });

  it("adds two numbers", () => {
    expect(calc.add(2, 3)).toBe(5);
  });

  it("throws on division by zero", () => {
    expect(() => calc.divide(10, 0)).toThrowError("Division by zero");
  });

  it("handles floating point", () => {
    expect(calc.add(0.1, 0.2)).toBeCloseTo(0.3);
  });
});

// Concurrent tests
describe("API calls", () => {
  it.concurrent("fetches users", async () => {
    const users = await fetchUsers();
    expect(users).toHaveLength(10);
  });

  it.concurrent("fetches posts", async () => {
    const posts = await fetchPosts();
    expect(posts.length).toBeGreaterThan(0);
  });
});
```

## Mocking

```typescript
import { vi, describe, it, expect, beforeEach } from "vitest";

// Mock functions
const mockFn = vi.fn();
mockFn.mockReturnValue(42);
mockFn.mockResolvedValue({ data: "test" });
mockFn.mockImplementation((x: number) => x * 2);

// Mock modules
vi.mock("./api", () => ({
  fetchUser: vi.fn().mockResolvedValue({ id: 1, name: "Alice" }),
  fetchPosts: vi.fn().mockResolvedValue([]),
}));

// Partial mock (keep original, override specific exports)
vi.mock("./utils", async (importOriginal) => {
  const actual = await importOriginal<typeof import("./utils")>();
  return {
    ...actual,
    formatDate: vi.fn().mockReturnValue("2024-01-01"),
  };
});

// Mock timers
describe("debounce", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("debounces function calls", () => {
    const fn = vi.fn();
    const debounced = debounce(fn, 300);

    debounced();
    debounced();
    debounced();

    expect(fn).not.toHaveBeenCalled();

    vi.advanceTimersByTime(300);
    expect(fn).toHaveBeenCalledOnce();
  });
});

// Spy on methods
const spy = vi.spyOn(console, "log");
doSomething();
expect(spy).toHaveBeenCalledWith("expected message");
spy.mockRestore();
```

## React Testing Library Integration

```typescript
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";

describe("LoginForm", () => {
  it("submits with valid credentials", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();

    render(<LoginForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText("Email"), "test@test.com");
    await user.type(screen.getByLabelText("Password"), "password123");
    await user.click(screen.getByRole("button", { name: "Log In" }));

    expect(onSubmit).toHaveBeenCalledWith({
      email: "test@test.com",
      password: "password123",
    });
  });

  it("shows validation errors", async () => {
    const user = userEvent.setup();
    render(<LoginForm onSubmit={vi.fn()} />);

    await user.click(screen.getByRole("button", { name: "Log In" }));

    expect(screen.getByText("Email is required")).toBeInTheDocument();
  });
});
```

## Snapshot Testing

```typescript
import { expect, it } from "vitest";

it("serializes user object", () => {
  const user = createUser({ name: "Alice", role: "admin" });
  expect(user).toMatchSnapshot();
});

it("renders component correctly", () => {
  const { container } = render(<Badge variant="success">Active</Badge>);
  expect(container).toMatchSnapshot();
});

// Inline snapshots
it("formats date", () => {
  expect(formatDate(new Date("2024-01-15"))).toMatchInlineSnapshot(
    '"January 15, 2024"'
  );
});
```

## Configuration

```typescript
// vitest.config.ts
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    include: ["src/**/*.{test,spec}.{ts,tsx}"],
    coverage: {
      provider: "v8",
      reporter: ["text", "html", "lcov"],
      exclude: ["node_modules/", "src/test/"],
      thresholds: {
        branches: 80,
        functions: 80,
        lines: 80,
        statements: 80,
      },
    },
  },
});

// src/test/setup.ts
import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

afterEach(() => {
  cleanup();
});
```

## Workspace Configuration

```typescript
// vitest.workspace.ts
import { defineWorkspace } from "vitest/config";

export default defineWorkspace([
  {
    extends: "./vitest.config.ts",
    test: {
      name: "unit",
      include: ["src/**/*.unit.test.ts"],
    },
  },
  {
    extends: "./vitest.config.ts",
    test: {
      name: "integration",
      include: ["src/**/*.integration.test.ts"],
      environment: "node",
    },
  },
]);
```

## Additional Resources

- Vitest: https://vitest.dev/
- Vitest API: https://vitest.dev/api/
- Testing Library: https://testing-library.com/
