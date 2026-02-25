---
name: elysia-patterns
description: Elysia patterns covering route handlers, type-safe validation with TypeBox, derive and resolve middleware, Eden Treaty client, WebSocket support, groups, guards, and Bun-optimized API development.
---

# Elysia Patterns

This skill should be used when building APIs with Elysia on Bun runtime. It covers routes, validation, middleware, Eden Treaty, WebSockets, and Bun-optimized patterns.

## When to Use This Skill

Use this skill when you need to:

- Build high-performance APIs on Bun
- Use end-to-end type safety with Eden Treaty
- Validate requests with TypeBox schemas
- Create middleware with derive and resolve
- Handle WebSocket connections

## Basic Server

```typescript
import { Elysia } from "elysia";

const app = new Elysia()
  .get("/", () => "Hello Elysia!")
  .get("/api/health", () => ({ status: "ok", timestamp: Date.now() }))
  .listen(3000);

console.log(`Server running at http://localhost:${app.server?.port}`);
```

## Routes with Validation

```typescript
import { Elysia, t } from "elysia";

const app = new Elysia()
  .post("/api/users", ({ body }) => {
    return createUser(body);
  }, {
    body: t.Object({
      name: t.String({ minLength: 1 }),
      email: t.String({ format: "email" }),
      age: t.Optional(t.Number({ minimum: 0 })),
    }),
    response: t.Object({
      id: t.String(),
      name: t.String(),
      email: t.String(),
    }),
  })
  .get("/api/users/:id", ({ params: { id } }) => {
    return findUser(id);
  }, {
    params: t.Object({
      id: t.String(),
    }),
  })
  .get("/api/users", ({ query }) => {
    return listUsers(query);
  }, {
    query: t.Object({
      page: t.Optional(t.Numeric({ default: 1 })),
      limit: t.Optional(t.Numeric({ default: 20 })),
      search: t.Optional(t.String()),
    }),
  });
```

## Derive and Resolve (Middleware)

```typescript
const app = new Elysia()
  // derive: add properties to context
  .derive(({ headers }) => {
    const token = headers.authorization?.replace("Bearer ", "");
    return { token };
  })
  // resolve: async derive with validation
  .resolve(async ({ token }) => {
    if (!token) throw new Error("Unauthorized");
    const user = await verifyToken(token);
    return { user };
  })
  .get("/api/profile", ({ user }) => {
    // user is typed and available
    return { name: user.name, email: user.email };
  });
```

## Guards and Groups

```typescript
const app = new Elysia()
  // Public routes
  .group("/api/auth", (app) =>
    app
      .post("/login", ({ body }) => login(body), {
        body: t.Object({
          email: t.String(),
          password: t.String(),
        }),
      })
      .post("/register", ({ body }) => register(body), {
        body: t.Object({
          name: t.String(),
          email: t.String(),
          password: t.String(),
        }),
      })
  )
  // Protected routes with guard
  .guard(
    {
      beforeHandle: async ({ headers, set }) => {
        const token = headers.authorization?.replace("Bearer ", "");
        if (!token) {
          set.status = 401;
          return { error: "Unauthorized" };
        }
      },
    },
    (app) =>
      app
        .get("/api/profile", ({ user }) => user)
        .put("/api/profile", ({ user, body }) => updateProfile(user.id, body))
  );
```

## Plugins

```typescript
import { Elysia } from "elysia";
import { cors } from "@elysiajs/cors";
import { swagger } from "@elysiajs/swagger";
import { jwt } from "@elysiajs/jwt";

const app = new Elysia()
  .use(cors())
  .use(swagger())
  .use(
    jwt({
      name: "jwt",
      secret: process.env.JWT_SECRET!,
    })
  )
  .post("/api/login", async ({ jwt, body }) => {
    const user = await authenticate(body);
    const token = await jwt.sign({ sub: user.id, role: user.role });
    return { token };
  });
```

## Eden Treaty (Type-safe Client)

```typescript
// server.ts
const app = new Elysia()
  .get("/api/users", () => getUsers())
  .post("/api/users", ({ body }) => createUser(body), {
    body: t.Object({ name: t.String(), email: t.String() }),
  })
  .listen(3000);

export type App = typeof app;

// client.ts
import { treaty } from "@elysiajs/eden";
import type { App } from "./server";

const api = treaty<App>("localhost:3000");

// Fully typed API calls
const { data: users } = await api.api.users.get();
const { data: newUser } = await api.api.users.post({
  name: "Alice",
  email: "alice@example.com",
});
```

## WebSockets

```typescript
const app = new Elysia()
  .ws("/ws/chat", {
    body: t.Object({
      message: t.String(),
      room: t.String(),
    }),
    open(ws) {
      console.log("Connected:", ws.id);
    },
    message(ws, { message, room }) {
      ws.publish(room, { from: ws.id, message });
    },
    close(ws) {
      console.log("Disconnected:", ws.id);
    },
  });
```

## Error Handling

```typescript
const app = new Elysia()
  .onError(({ code, error, set }) => {
    switch (code) {
      case "VALIDATION":
        set.status = 400;
        return { error: "Validation failed", details: error.all };
      case "NOT_FOUND":
        set.status = 404;
        return { error: "Not found" };
      default:
        set.status = 500;
        return { error: "Internal server error" };
    }
  });
```

## Additional Resources

- Elysia: https://elysiajs.com/
- Eden Treaty: https://elysiajs.com/eden/treaty/overview
- Plugins: https://elysiajs.com/plugins/overview
