---
name: pactjs-contracts
description: Pact.js contract testing patterns covering consumer-driven contracts, provider verification, matchers, message pacts, Pact Broker integration, and CI/CD workflows.
---

# Pact.js Contract Testing

This skill should be used when implementing consumer-driven contract tests with Pact.js. It covers contracts, provider verification, matchers, and Pact Broker.

## When to Use This Skill

Use this skill when you need to:

- Write consumer-driven contract tests
- Verify provider implementations against contracts
- Use flexible matchers for API contracts
- Publish and share pacts via Pact Broker
- Integrate contract testing in CI/CD pipelines

## Setup

```bash
npm install --save-dev @pact-foundation/pact
```

## Consumer Test

```ts
import { PactV4, MatchersV3 } from "@pact-foundation/pact";
import path from "path";
import { describe, it, expect } from "vitest";

const { like, eachLike, string, integer, datetime } = MatchersV3;

const provider = new PactV4({
  consumer: "frontend-app",
  provider: "user-service",
  dir: path.resolve(process.cwd(), "pacts"),
});

describe("User API consumer", () => {
  it("should fetch a user by ID", async () => {
    await provider
      .addInteraction()
      .given("user with ID 1 exists")
      .uponReceiving("a request for user 1")
      .withRequest("GET", "/api/users/1", (builder) => {
        builder.headers({ Accept: "application/json" });
      })
      .willRespondWith(200, (builder) => {
        builder
          .headers({ "Content-Type": "application/json" })
          .jsonBody(
            like({
              id: integer(1),
              name: string("Alice"),
              email: string("alice@example.com"),
              createdAt: datetime("2024-01-01T00:00:00Z", "yyyy-MM-dd'T'HH:mm:ss'Z'"),
            })
          );
      })
      .executeTest(async (mockServer) => {
        const response = await fetch(`${mockServer.url}/api/users/1`, {
          headers: { Accept: "application/json" },
        });
        const user = await response.json();

        expect(response.status).toBe(200);
        expect(user).toHaveProperty("id");
        expect(user).toHaveProperty("name");
        expect(user).toHaveProperty("email");
      });
  });

  it("should fetch all users", async () => {
    await provider
      .addInteraction()
      .given("users exist")
      .uponReceiving("a request for all users")
      .withRequest("GET", "/api/users")
      .willRespondWith(200, (builder) => {
        builder.jsonBody(
          eachLike({
            id: integer(1),
            name: string("Alice"),
            email: string("alice@example.com"),
          })
        );
      })
      .executeTest(async (mockServer) => {
        const response = await fetch(`${mockServer.url}/api/users`);
        const users = await response.json();

        expect(users).toBeInstanceOf(Array);
        expect(users.length).toBeGreaterThan(0);
      });
  });
});
```

## Provider Verification

```ts
import { Verifier } from "@pact-foundation/pact";

describe("Provider verification", () => {
  it("should validate the contract against the provider", async () => {
    const verifier = new Verifier({
      providerBaseUrl: "http://localhost:3000",
      pactUrls: [
        path.resolve(process.cwd(), "pacts/frontend-app-user-service.json"),
      ],
      stateHandlers: {
        "user with ID 1 exists": async () => {
          // Set up test data
          await db.users.create({ id: 1, name: "Alice", email: "alice@example.com" });
        },
        "users exist": async () => {
          await db.users.createMany([
            { id: 1, name: "Alice", email: "alice@example.com" },
            { id: 2, name: "Bob", email: "bob@example.com" },
          ]);
        },
      },
    });

    await verifier.verifyProvider();
  });
});
```

## Matchers

```ts
import { MatchersV3 } from "@pact-foundation/pact";

const {
  like,          // Match by type (any value of same type)
  eachLike,      // Array with at least one element matching
  string,        // String matcher
  integer,       // Integer matcher
  decimal,       // Decimal matcher
  boolean,       // Boolean matcher
  datetime,      // DateTime with format
  regex,         // Regex pattern match
  uuid,          // UUID matcher
  ip4Address,    // IPv4 matcher
  email,         // Email matcher
} = MatchersV3;

// Complex body example
const orderBody = like({
  id: uuid(),
  customer: like({
    name: string("Alice"),
    email: email("alice@example.com"),
  }),
  items: eachLike({
    productId: uuid(),
    name: string("Widget"),
    quantity: integer(1),
    price: decimal(9.99),
  }),
  status: regex("pending|processing|shipped|delivered", "pending"),
  total: decimal(9.99),
  createdAt: datetime("2024-01-01T00:00:00Z"),
});
```

## Pact Broker Publishing

```ts
import { Publisher } from "@pact-foundation/pact";

const publisher = new Publisher({
  pactBroker: "https://pact-broker.example.com",
  pactBrokerToken: process.env.PACT_BROKER_TOKEN,
  pactFilesOrDirs: [path.resolve(process.cwd(), "pacts")],
  consumerVersion: process.env.GIT_COMMIT || "1.0.0",
  tags: [process.env.GIT_BRANCH || "main"],
});

await publisher.publishPacts();
```

## Additional Resources

- Pact.js: https://docs.pact.io/implementation_guides/javascript
- Matchers: https://docs.pact.io/implementation_guides/javascript/docs/matching
- Pact Broker: https://docs.pact.io/pact_broker
