---
name: nock-mocking
description: Nock HTTP mocking patterns covering request interception, response fixtures, scope management, query/body matching, recording, and testing with Jest/Vitest.
---

# Nock Mocking

This skill should be used when mocking HTTP requests in Node.js tests with Nock. It covers interception, fixtures, scope management, matching, and test integration.

## When to Use This Skill

Use this skill when you need to:

- Mock external HTTP APIs in Node.js tests
- Define request/response fixtures
- Match requests by URL, headers, query, and body
- Record real HTTP interactions for replay
- Integrate with Jest or Vitest test runners

## Setup

```bash
npm install --save-dev nock
```

## Basic Mocking

```ts
import nock from "nock";
import { describe, it, expect, afterEach } from "vitest";

afterEach(() => {
  nock.cleanAll();
});

describe("API client", () => {
  it("should fetch users", async () => {
    const scope = nock("https://api.example.com")
      .get("/users")
      .reply(200, [
        { id: 1, name: "Alice" },
        { id: 2, name: "Bob" },
      ]);

    const response = await fetch("https://api.example.com/users");
    const users = await response.json();

    expect(users).toHaveLength(2);
    expect(users[0].name).toBe("Alice");
    expect(scope.isDone()).toBe(true);
  });

  it("should handle POST requests", async () => {
    const scope = nock("https://api.example.com")
      .post("/users", { name: "Charlie", email: "charlie@test.com" })
      .reply(201, { id: 3, name: "Charlie", email: "charlie@test.com" });

    const response = await fetch("https://api.example.com/users", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: "Charlie", email: "charlie@test.com" }),
    });

    expect(response.status).toBe(201);
    expect(scope.isDone()).toBe(true);
  });
});
```

## Query and Header Matching

```ts
// Match query parameters
nock("https://api.example.com")
  .get("/search")
  .query({ q: "test", page: "1", limit: "10" })
  .reply(200, { results: [] });

// Match specific headers
nock("https://api.example.com", {
  reqheaders: {
    Authorization: "Bearer token123",
    "Content-Type": "application/json",
  },
})
  .get("/protected")
  .reply(200, { data: "secret" });

// Match with regex
nock("https://api.example.com")
  .get(/\/users\/\d+/)
  .reply(200, { id: 1, name: "User" });
```

## Error Simulation

```ts
// HTTP error
nock("https://api.example.com")
  .get("/users")
  .reply(500, { error: "Internal Server Error" });

// Network error
nock("https://api.example.com")
  .get("/users")
  .replyWithError("Connection refused");

// Timeout simulation
nock("https://api.example.com")
  .get("/slow")
  .delay(5000)
  .reply(200, { data: "delayed" });

// Repeated responses
nock("https://api.example.com")
  .get("/users")
  .times(3)
  .reply(200, { users: [] });
```

## Recording and Playback

```ts
import nock from "nock";

// Record real HTTP calls
nock.recorder.rec({
  output_objects: true,
  dont_print: true,
});

// Make real requests...
await fetch("https://api.example.com/users");

// Get recorded calls
const recordings = nock.recorder.play();
nock.recorder.clear();

// Replay recorded calls
const scope = nock.define(recordings as any);
```

## Additional Resources

- Nock: https://github.com/nock/nock
- API: https://github.com/nock/nock#usage
- Best Practices: https://github.com/nock/nock#best-practices
