---
name: vitest-testing
description: Vitest testing framework covering configuration, test organization, mocking with vi.fn/vi.mock, snapshot testing, coverage with v8/istanbul, workspace mode for monorepos, browser mode, concurrent tests, and migration from Jest.
---

# Vitest Testing

This skill should be used when testing with Vitest. It covers configuration, mocking, coverage, workspace mode, and migration from Jest.

## When to Use This Skill

Use this skill when you need to:

- Configure Vitest for a project
- Write tests with Vitest-specific APIs
- Mock modules and functions
- Set up code coverage
- Use workspace mode for monorepos

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
    setupFiles: ["./tests/setup.ts"],
    include: ["src/**/*.{test,spec}.{ts,tsx}"],
    coverage: {
      provider: "v8",
      reporter: ["text", "lcov", "html"],
      include: ["src/**/*.{ts,tsx}"],
      exclude: ["src/**/*.test.*", "src/**/*.d.ts"],
      thresholds: { lines: 80, branches: 80, functions: 80 },
    },
    css: true,
  },
  resolve: {
    alias: { "~": "/src" },
  },
});
```

```typescript
// tests/setup.ts
import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

afterEach(() => cleanup());
```

## Mocking

```typescript
import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock a module
vi.mock("~/lib/api", () => ({
  fetchUsers: vi.fn(),
}));

import { fetchUsers } from "~/lib/api";

describe("UserList", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("displays users from API", async () => {
    vi.mocked(fetchUsers).mockResolvedValue([
      { id: "1", name: "Alice" },
      { id: "2", name: "Bob" },
    ]);

    // ... test component
  });
});

// Spy on a method
const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});
// ...
expect(consoleSpy).toHaveBeenCalledWith("something failed");
consoleSpy.mockRestore();

// Mock timers
vi.useFakeTimers();
const callback = vi.fn();
setTimeout(callback, 1000);
vi.advanceTimersByTime(1000);
expect(callback).toHaveBeenCalled();
vi.useRealTimers();
```

## Snapshot Testing

```typescript
it("renders correctly", () => {
  const { container } = render(<Button variant="primary">Click</Button>);
  expect(container).toMatchSnapshot();
});

// Inline snapshots (auto-updated in source)
it("formats output", () => {
  expect(formatDate(new Date("2025-01-15"))).toMatchInlineSnapshot(`"Jan 15, 2025"`);
});
```

## Workspace Mode (Monorepo)

```typescript
// vitest.workspace.ts
import { defineWorkspace } from "vitest/config";

export default defineWorkspace([
  "apps/*/vitest.config.ts",
  "packages/*/vitest.config.ts",
  {
    test: {
      name: "unit",
      include: ["packages/**/src/**/*.test.ts"],
      environment: "node",
    },
  },
  {
    test: {
      name: "components",
      include: ["packages/ui/**/*.test.tsx"],
      environment: "jsdom",
    },
  },
]);
```

## Concurrent Tests

```typescript
// Run tests in parallel within a describe
describe.concurrent("math utils", () => {
  it("adds numbers", async () => {
    expect(add(1, 2)).toBe(3);
  });

  it("multiplies numbers", async () => {
    expect(multiply(2, 3)).toBe(6);
  });
});
```

## Additional Resources

- Vitest docs: https://vitest.dev/
- Migration from Jest: https://vitest.dev/guide/migration
- Browser mode: https://vitest.dev/guide/browser/
