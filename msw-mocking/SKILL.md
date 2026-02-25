---
name: msw-mocking
description: Mock Service Worker (MSW) covering request handlers, REST and GraphQL mocking, browser service worker setup, Node.js server integration, response resolvers, and testing patterns with Vitest and Playwright.
---

# Mock Service Worker (MSW)

This skill should be used when mocking API requests with MSW. It covers request handlers, REST/GraphQL mocking, browser and Node.js setup, and testing integration.

## When to Use This Skill

Use this skill when you need to:

- Mock REST or GraphQL APIs during development
- Write integration tests with consistent API responses
- Intercept network requests in the browser or Node.js
- Simulate error states and edge cases
- Share mock definitions between dev and test environments

## Setup

```typescript
// src/mocks/handlers.ts
import { http, HttpResponse, graphql } from "msw";

export const handlers = [
  // GET request
  http.get("/api/users", () => {
    return HttpResponse.json([
      { id: 1, name: "Alice", email: "alice@example.com" },
      { id: 2, name: "Bob", email: "bob@example.com" },
    ]);
  }),

  // GET with params
  http.get("/api/users/:id", ({ params }) => {
    const { id } = params;
    return HttpResponse.json({ id: Number(id), name: "Alice", email: "alice@example.com" });
  }),

  // POST
  http.post("/api/users", async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json(
      { id: 3, ...body },
      { status: 201 },
    );
  }),

  // DELETE
  http.delete("/api/users/:id", () => {
    return new HttpResponse(null, { status: 204 });
  }),
];
```

## Browser Setup

```typescript
// src/mocks/browser.ts
import { setupWorker } from "msw/browser";
import { handlers } from "./handlers";

export const worker = setupWorker(...handlers);

// src/main.tsx (development only)
async function enableMocking() {
  if (process.env.NODE_ENV !== "development") return;
  const { worker } = await import("./mocks/browser");
  return worker.start({ onUnhandledRequest: "bypass" });
}

enableMocking().then(() => {
  createRoot(document.getElementById("root")!).render(<App />);
});
```

## Node.js Setup (Testing)

```typescript
// src/mocks/server.ts
import { setupServer } from "msw/node";
import { handlers } from "./handlers";

export const server = setupServer(...handlers);

// vitest.setup.ts
import { beforeAll, afterEach, afterAll } from "vitest";
import { server } from "./src/mocks/server";

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

## Response Patterns

```typescript
import { http, HttpResponse, delay } from "msw";

// Error responses
http.get("/api/data", () => {
  return HttpResponse.json(
    { message: "Internal Server Error" },
    { status: 500 },
  );
}),

// Delayed response (simulate slow network)
http.get("/api/slow", async () => {
  await delay(2000);
  return HttpResponse.json({ data: "finally" });
}),

// Network error
http.get("/api/offline", () => {
  return HttpResponse.error();
}),

// One-time override (for specific tests)
http.get("/api/users", () => {
  return HttpResponse.json([]);
}, { once: true }),

// Conditional response
http.get("/api/search", ({ request }) => {
  const url = new URL(request.url);
  const query = url.searchParams.get("q");
  if (!query) {
    return HttpResponse.json({ results: [] });
  }
  return HttpResponse.json({
    results: [{ id: 1, title: `Result for ${query}` }],
  });
}),
```

## GraphQL Mocking

```typescript
import { graphql, HttpResponse } from "msw";

export const graphqlHandlers = [
  graphql.query("GetUser", ({ variables }) => {
    return HttpResponse.json({
      data: {
        user: { id: variables.id, name: "Alice", email: "alice@example.com" },
      },
    });
  }),

  graphql.mutation("CreatePost", ({ variables }) => {
    return HttpResponse.json({
      data: {
        createPost: { id: "1", title: variables.title, published: false },
      },
    });
  }),
];
```

## Test Example

```typescript
import { describe, it, expect } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { server } from "../mocks/server";
import { UserList } from "./UserList";

describe("UserList", () => {
  it("renders users", async () => {
    render(<UserList />);
    await waitFor(() => {
      expect(screen.getByText("Alice")).toBeInTheDocument();
      expect(screen.getByText("Bob")).toBeInTheDocument();
    });
  });

  it("handles error state", async () => {
    server.use(
      http.get("/api/users", () => {
        return HttpResponse.json({ message: "Error" }, { status: 500 });
      }),
    );

    render(<UserList />);
    await waitFor(() => {
      expect(screen.getByText("Failed to load users")).toBeInTheDocument();
    });
  });
});
```

## Additional Resources

- MSW docs: https://mswjs.io/docs
- Getting started: https://mswjs.io/docs/getting-started
- Recipes: https://mswjs.io/docs/recipes
