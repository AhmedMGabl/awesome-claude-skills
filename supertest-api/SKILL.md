---
name: supertest-api
description: Supertest API testing patterns covering HTTP assertions, request chaining, authentication flows, file upload testing, middleware testing, and Express/Fastify integration.
---

# Supertest API Testing

This skill should be used when testing HTTP APIs with Supertest. It covers assertions, authentication, file uploads, middleware testing, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Test Express/Fastify/Koa HTTP endpoints
- Assert response status, headers, and body
- Test authenticated API routes
- Test file upload endpoints
- Build integration test suites for APIs

## Setup

```bash
npm install --save-dev supertest @types/supertest
```

## Basic Testing

```ts
import request from "supertest";
import { describe, it, expect } from "vitest";
import app from "../src/app";

describe("GET /api/users", () => {
  it("should return a list of users", async () => {
    const response = await request(app)
      .get("/api/users")
      .expect("Content-Type", /json/)
      .expect(200);

    expect(response.body).toBeInstanceOf(Array);
    expect(response.body.length).toBeGreaterThan(0);
    expect(response.body[0]).toHaveProperty("id");
    expect(response.body[0]).toHaveProperty("name");
  });

  it("should support pagination", async () => {
    const response = await request(app)
      .get("/api/users")
      .query({ page: 1, limit: 10 })
      .expect(200);

    expect(response.body).toHaveLength(10);
  });
});

describe("POST /api/users", () => {
  it("should create a new user", async () => {
    const newUser = { name: "Alice", email: "alice@test.com" };

    const response = await request(app)
      .post("/api/users")
      .send(newUser)
      .expect(201);

    expect(response.body).toMatchObject(newUser);
    expect(response.body).toHaveProperty("id");
  });

  it("should reject invalid data", async () => {
    const response = await request(app)
      .post("/api/users")
      .send({ name: "" })
      .expect(400);

    expect(response.body).toHaveProperty("errors");
  });
});
```

## Authentication Testing

```ts
describe("Authenticated routes", () => {
  let authToken: string;

  beforeAll(async () => {
    const loginResponse = await request(app)
      .post("/api/auth/login")
      .send({ email: "admin@test.com", password: "password123" });

    authToken = loginResponse.body.token;
  });

  it("should access protected route with token", async () => {
    const response = await request(app)
      .get("/api/profile")
      .set("Authorization", `Bearer ${authToken}`)
      .expect(200);

    expect(response.body).toHaveProperty("email", "admin@test.com");
  });

  it("should reject without token", async () => {
    await request(app)
      .get("/api/profile")
      .expect(401);
  });

  it("should reject with invalid token", async () => {
    await request(app)
      .get("/api/profile")
      .set("Authorization", "Bearer invalid-token")
      .expect(401);
  });
});
```

## File Upload Testing

```ts
import path from "path";

describe("POST /api/upload", () => {
  it("should upload a file", async () => {
    const response = await request(app)
      .post("/api/upload")
      .attach("file", path.join(__dirname, "fixtures/test-image.png"))
      .expect(200);

    expect(response.body).toHaveProperty("url");
    expect(response.body.url).toContain(".png");
  });

  it("should upload with form fields", async () => {
    const response = await request(app)
      .post("/api/upload")
      .field("description", "Test image")
      .field("category", "photos")
      .attach("file", path.join(__dirname, "fixtures/test-image.png"))
      .expect(200);

    expect(response.body).toHaveProperty("description", "Test image");
  });
});
```

## CRUD Test Pattern

```ts
describe("CRUD /api/posts", () => {
  let createdId: string;

  it("POST - should create", async () => {
    const res = await request(app)
      .post("/api/posts")
      .send({ title: "Test Post", content: "Hello" })
      .expect(201);

    createdId = res.body.id;
    expect(res.body.title).toBe("Test Post");
  });

  it("GET - should read", async () => {
    const res = await request(app)
      .get(`/api/posts/${createdId}`)
      .expect(200);

    expect(res.body.id).toBe(createdId);
  });

  it("PUT - should update", async () => {
    const res = await request(app)
      .put(`/api/posts/${createdId}`)
      .send({ title: "Updated Post" })
      .expect(200);

    expect(res.body.title).toBe("Updated Post");
  });

  it("DELETE - should delete", async () => {
    await request(app)
      .delete(`/api/posts/${createdId}`)
      .expect(204);

    await request(app)
      .get(`/api/posts/${createdId}`)
      .expect(404);
  });
});
```

## Additional Resources

- Supertest: https://github.com/ladjs/supertest
- API: https://github.com/ladjs/supertest#api
- Express Testing: https://expressjs.com/en/guide/testing.html
