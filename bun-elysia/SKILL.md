---
name: bun-elysia
description: Elysia.js patterns for Bun covering type-safe routing, validation with TypeBox, plugins, WebSocket, authentication guards, and Eden Treaty client.
---

# Bun Elysia

This skill should be used when building APIs with Elysia.js on Bun runtime. It covers type-safe routing, validation, plugins, WebSocket, auth guards, and Eden Treaty.

## When to Use This Skill

Use this skill when you need to:

- Build type-safe REST APIs on Bun
- Use schema validation with TypeBox
- Create reusable plugins and guards
- Implement WebSocket handlers
- Generate end-to-end type-safe clients

## Basic Server

```typescript
import { Elysia, t } from "elysia";

const app = new Elysia()
  .get("/", () => "Hello from Elysia!")
  .get("/users/:id", ({ params: { id } }) => getUser(id))
  .post("/users", ({ body }) => createUser(body), {
    body: t.Object({
      name: t.String({ minLength: 1 }),
      email: t.String({ format: "email" }),
    }),
  })
  .listen(3000);

console.log(`Running at http://localhost:${app.server?.port}`);
```

## Validation and Response Types

```typescript
const app = new Elysia()
  .post("/users", ({ body }) => createUser(body), {
    body: t.Object({
      name: t.String({ minLength: 2, maxLength: 100 }),
      email: t.String({ format: "email" }),
      role: t.Optional(t.Union([t.Literal("user"), t.Literal("admin")])),
    }),
    response: {
      200: t.Object({
        id: t.String(),
        name: t.String(),
        email: t.String(),
      }),
      400: t.Object({ error: t.String() }),
    },
  })
  .get("/users", ({ query }) => listUsers(query), {
    query: t.Object({
      page: t.Optional(t.Numeric({ default: 1 })),
      limit: t.Optional(t.Numeric({ default: 20 })),
      search: t.Optional(t.String()),
    }),
  });
```

## Plugins

```typescript
const authPlugin = new Elysia({ name: "auth" })
  .derive(async ({ headers }) => {
    const token = headers.authorization?.replace("Bearer ", "");
    if (!token) throw new Error("Unauthorized");
    const user = await verifyToken(token);
    return { user };
  });

const loggingPlugin = new Elysia({ name: "logging" })
  .onBeforeHandle(({ request }) => {
    console.log(`${request.method} ${new URL(request.url).pathname}`);
  });

const app = new Elysia()
  .use(loggingPlugin)
  .group("/api", (app) =>
    app.use(authPlugin)
      .get("/me", ({ user }) => user)
      .get("/posts", ({ user }) => getUserPosts(user.id))
  );
```

## Guards

```typescript
const app = new Elysia()
  .guard({ beforeHandle: [isAuthenticated] }, (app) =>
    app
      .get("/profile", ({ user }) => user)
      .guard({ beforeHandle: [isAdmin] }, (app) =>
        app
          .get("/admin/users", () => getAllUsers())
          .delete("/admin/users/:id", ({ params }) => deleteUser(params.id))
      )
  );
```

## WebSocket

```typescript
const app = new Elysia()
  .ws("/chat", {
    body: t.Object({ message: t.String() }),
    open(ws) {
      ws.subscribe("chat-room");
      ws.publish("chat-room", { type: "join", user: ws.data.user });
    },
    message(ws, { message }) {
      ws.publish("chat-room", {
        type: "message",
        user: ws.data.user,
        message,
        timestamp: Date.now(),
      });
    },
    close(ws) {
      ws.publish("chat-room", { type: "leave", user: ws.data.user });
    },
  });
```

## Eden Treaty (Type-Safe Client)

```typescript
import { treaty } from "@elysiajs/eden";
import type { App } from "./server";

const client = treaty<App>("http://localhost:3000");

// Fully typed!
const { data, error } = await client.users.post({
  name: "Alice",
  email: "alice@example.com",
});

const { data: users } = await client.users.get({ query: { page: 1 } });
```

## Error Handling

```typescript
const app = new Elysia()
  .error({ NOT_FOUND: Error, VALIDATION: Error })
  .onError(({ code, error, set }) => {
    switch (code) {
      case "NOT_FOUND":
        set.status = 404;
        return { error: error.message };
      case "VALIDATION":
        set.status = 400;
        return { error: "Validation failed", details: error.message };
      default:
        set.status = 500;
        return { error: "Internal server error" };
    }
  });
```

## Additional Resources

- Elysia: https://elysiajs.com/
- Eden Treaty: https://elysiajs.com/eden/overview
- Bun: https://bun.sh/docs
