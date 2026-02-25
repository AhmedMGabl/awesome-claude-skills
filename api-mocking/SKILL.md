---
name: api-mocking
description: API mocking and testing patterns covering MSW (Mock Service Worker) for browser and Node.js, Nock for HTTP interception, JSON Server for rapid prototyping, Mirage.js, factory patterns for test data generation, and contract testing with Pact.
---

# API Mocking

This skill should be used when mocking APIs for development, testing, or prototyping. It covers MSW, Nock, JSON Server, test data factories, and contract testing.

## When to Use This Skill

Use this skill when you need to:

- Mock API responses during development
- Test components that depend on APIs
- Prototype UIs before backend is ready
- Generate realistic test data
- Implement contract testing between services

## MSW (Mock Service Worker)

```typescript
// mocks/handlers.ts
import { http, HttpResponse, delay } from "msw";

export const handlers = [
  // GET /api/users
  http.get("/api/users", async ({ request }) => {
    const url = new URL(request.url);
    const page = Number(url.searchParams.get("page") ?? "1");
    const size = Number(url.searchParams.get("size") ?? "20");

    await delay(100); // Simulate network latency

    return HttpResponse.json({
      users: generateUsers(size, (page - 1) * size),
      total: 100,
      page,
    });
  }),

  // POST /api/users
  http.post("/api/users", async ({ request }) => {
    const body = await request.json() as { name: string; email: string };

    // Simulate validation error
    if (!body.email?.includes("@")) {
      return HttpResponse.json(
        { error: "Invalid email" },
        { status: 400 },
      );
    }

    return HttpResponse.json(
      { id: crypto.randomUUID(), ...body, createdAt: new Date().toISOString() },
      { status: 201 },
    );
  }),

  // Simulate server error
  http.get("/api/unstable", () => {
    if (Math.random() > 0.5) {
      return HttpResponse.json({ error: "Internal error" }, { status: 500 });
    }
    return HttpResponse.json({ data: "success" });
  }),

  // Network error
  http.get("/api/offline", () => {
    return HttpResponse.error();
  }),
];
```

```typescript
// mocks/browser.ts — For development
import { setupWorker } from "msw/browser";
import { handlers } from "./handlers";
export const worker = setupWorker(...handlers);

// Start in dev mode
if (process.env.NODE_ENV === "development") {
  const { worker } = await import("./mocks/browser");
  await worker.start({ onUnhandledRequest: "bypass" });
}
```

```typescript
// mocks/server.ts — For testing (Vitest/Jest)
import { setupServer } from "msw/node";
import { handlers } from "./handlers";
export const server = setupServer(...handlers);

// vitest.setup.ts
import { server } from "./mocks/server";
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

## Testing with MSW

```typescript
import { http, HttpResponse } from "msw";
import { server } from "../mocks/server";
import { render, screen, waitFor } from "@testing-library/react";

test("displays user list", async () => {
  render(<UserList />);
  await waitFor(() => {
    expect(screen.getByText("John Doe")).toBeInTheDocument();
  });
});

test("shows error state on API failure", async () => {
  // Override handler for this test
  server.use(
    http.get("/api/users", () => {
      return HttpResponse.json({ error: "Server error" }, { status: 500 });
    }),
  );

  render(<UserList />);
  await waitFor(() => {
    expect(screen.getByText(/error/i)).toBeInTheDocument();
  });
});

test("shows loading state", async () => {
  server.use(
    http.get("/api/users", async () => {
      await delay("infinite"); // Never resolves
      return HttpResponse.json({});
    }),
  );

  render(<UserList />);
  expect(screen.getByText(/loading/i)).toBeInTheDocument();
});
```

## Test Data Factories

```typescript
import { faker } from "@faker-js/faker";

// Factory pattern for consistent test data
function createUser(overrides?: Partial<User>): User {
  return {
    id: faker.string.uuid(),
    name: faker.person.fullName(),
    email: faker.internet.email(),
    avatar: faker.image.avatar(),
    role: faker.helpers.arrayElement(["admin", "user", "editor"]),
    createdAt: faker.date.past().toISOString(),
    ...overrides,
  };
}

function createOrder(overrides?: Partial<Order>): Order {
  const items = Array.from({ length: faker.number.int({ min: 1, max: 5 }) }, () => ({
    id: faker.string.uuid(),
    name: faker.commerce.productName(),
    price: parseFloat(faker.commerce.price()),
    quantity: faker.number.int({ min: 1, max: 3 }),
  }));

  return {
    id: faker.string.uuid(),
    userId: faker.string.uuid(),
    items,
    total: items.reduce((sum, i) => sum + i.price * i.quantity, 0),
    status: faker.helpers.arrayElement(["pending", "confirmed", "shipped", "delivered"]),
    createdAt: faker.date.recent().toISOString(),
    ...overrides,
  };
}

// Generate bulk test data
const users = Array.from({ length: 50 }, () => createUser());
const orders = users.flatMap((u) =>
  Array.from({ length: faker.number.int({ min: 0, max: 5 }) }, () => createOrder({ userId: u.id })),
);
```

## JSON Server (Rapid Prototyping)

```bash
# Quick REST API from a JSON file
npx json-server db.json --port 3001
```

```json
{
  "users": [
    { "id": "1", "name": "Alice", "email": "alice@example.com" },
    { "id": "2", "name": "Bob", "email": "bob@example.com" }
  ],
  "posts": [
    { "id": "1", "title": "Hello World", "userId": "1" }
  ]
}
```

## Additional Resources

- MSW: https://mswjs.io/
- Faker.js: https://fakerjs.dev/
- JSON Server: https://github.com/typicode/json-server
- Nock (Node.js): https://github.com/nock/nock
- Pact (contract testing): https://docs.pact.io/
