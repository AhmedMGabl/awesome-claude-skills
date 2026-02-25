---
name: testing-strategies
description: Comprehensive testing strategies covering the testing pyramid, integration testing patterns, contract testing with Pact, mutation testing, snapshot testing, API testing with supertest, database testing with test containers, performance testing, and CI test optimization.
---

# Testing Strategies

This skill should be used when designing test suites and testing architectures. It covers the testing pyramid, integration patterns, contract testing, and CI optimization.

## When to Use This Skill

Use this skill when you need to:

- Design a comprehensive test strategy
- Write integration tests for APIs and databases
- Implement contract testing between services
- Optimize test execution in CI
- Choose between testing approaches

## Testing Pyramid

```
            /   \
           / E2E \          Few — Critical paths only
          /-------\
         /  Integ  \        Some — API & DB integration
        /-----------\
       /    Unit     \      Many — Business logic
      /_______________\
```

## API Integration Testing

```typescript
import { describe, it, expect, beforeAll, afterAll } from "vitest";
import supertest from "supertest";
import { createApp } from "../src/app";
import { setupTestDb, teardownTestDb } from "./helpers/db";

let app: Express;
let request: supertest.SuperTest<supertest.Test>;

beforeAll(async () => {
  await setupTestDb();
  app = createApp();
  request = supertest(app);
});

afterAll(async () => {
  await teardownTestDb();
});

describe("POST /api/users", () => {
  it("should create a user with valid data", async () => {
    const res = await request
      .post("/api/users")
      .send({ email: "test@example.com", name: "Test User" })
      .expect(201);

    expect(res.body).toMatchObject({
      id: expect.any(String),
      email: "test@example.com",
      name: "Test User",
    });
  });

  it("should return 400 for invalid email", async () => {
    const res = await request
      .post("/api/users")
      .send({ email: "invalid", name: "Test" })
      .expect(400);

    expect(res.body.error).toContain("email");
  });

  it("should return 409 for duplicate email", async () => {
    await request.post("/api/users").send({ email: "dup@test.com", name: "First" });
    const res = await request
      .post("/api/users")
      .send({ email: "dup@test.com", name: "Second" })
      .expect(409);

    expect(res.body.error).toContain("already exists");
  });
});
```

## Database Testing with Testcontainers

```typescript
import { PostgreSqlContainer, StartedPostgreSqlContainer } from "@testcontainers/postgresql";
import { drizzle } from "drizzle-orm/node-postgres";
import { migrate } from "drizzle-orm/node-postgres/migrator";
import { Pool } from "pg";

let container: StartedPostgreSqlContainer;
let db: ReturnType<typeof drizzle>;

beforeAll(async () => {
  container = await new PostgreSqlContainer("postgres:16").start();
  const pool = new Pool({ connectionString: container.getConnectionUri() });
  db = drizzle(pool);
  await migrate(db, { migrationsFolder: "./drizzle" });
}, 60_000);

afterAll(async () => {
  await container.stop();
});
```

## Contract Testing (Pact)

```typescript
import { PactV3, MatchersV3 } from "@pact-foundation/pact";
const { like, eachLike } = MatchersV3;

const provider = new PactV3({
  consumer: "frontend",
  provider: "user-api",
});

describe("User API contract", () => {
  it("should return a user by ID", async () => {
    await provider
      .given("user 123 exists")
      .uponReceiving("a request for user 123")
      .withRequest({ method: "GET", path: "/api/users/123" })
      .willRespondWith({
        status: 200,
        body: like({
          id: "123",
          name: "Alice",
          email: "alice@test.com",
        }),
      });

    await provider.executeTest(async (mockServer) => {
      const response = await fetch(`${mockServer.url}/api/users/123`);
      const user = await response.json();
      expect(user.id).toBe("123");
    });
  });
});
```

## Test Data Factories

```typescript
import { faker } from "@faker-js/faker";

function createUser(overrides: Partial<User> = {}): User {
  return {
    id: faker.string.uuid(),
    email: faker.internet.email(),
    name: faker.person.fullName(),
    role: "user",
    createdAt: new Date(),
    ...overrides,
  };
}

function createOrder(overrides: Partial<Order> = {}): Order {
  return {
    id: faker.string.uuid(),
    userId: faker.string.uuid(),
    total: faker.number.float({ min: 10, max: 1000, fractionDigits: 2 }),
    status: "pending",
    ...overrides,
  };
}
```

## CI Test Optimization

```yaml
# .github/workflows/test.yml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: "pnpm" }
      - run: pnpm install --frozen-lockfile
      - run: pnpm vitest --shard=${{ matrix.shard }}/${{ strategy.job-total }}
      - uses: actions/upload-artifact@v4
        with:
          name: coverage-${{ matrix.shard }}
          path: coverage/
```

## When to Use Each Approach

```
APPROACH           WHEN                           TOOLS
──────────────────────────────────────────────────────────────
Unit tests         Pure logic, utils, transforms  Vitest, Jest
Integration        API endpoints, DB queries      Supertest, Testcontainers
Contract           Service-to-service APIs        Pact
E2E                Critical user journeys         Playwright, Cypress
Snapshot           UI components                  Vitest, Storybook
Mutation           Verify test quality            Stryker
```

## Additional Resources

- Vitest: https://vitest.dev/
- Testcontainers: https://testcontainers.com/
- Pact: https://docs.pact.io/
- Stryker: https://stryker-mutator.io/
