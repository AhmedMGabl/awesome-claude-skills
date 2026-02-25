---
name: hono-api
description: Hono web framework patterns covering route definitions, middleware, context helpers, validation with Zod, JWT authentication, CORS, streaming, RPC client, and multi-runtime deployment to Cloudflare Workers, Deno, Bun, and Node.js.
---

# Hono API

This skill should be used when building APIs with the Hono web framework. It covers routing, middleware, validation, authentication, and multi-runtime deployment.

## When to Use This Skill

Use this skill when you need to:

- Build lightweight, fast APIs with Hono
- Deploy to Cloudflare Workers, Deno, Bun, or Node.js
- Add typed validation with Zod middleware
- Implement JWT authentication and CORS
- Use Hono's RPC client for end-to-end type safety

## Basic Routing

```typescript
import { Hono } from "hono";

const app = new Hono();

// Basic routes
app.get("/", (c) => c.text("Hello Hono!"));
app.post("/users", async (c) => {
  const body = await c.req.json();
  return c.json({ id: "1", ...body }, 201);
});

// Route parameters
app.get("/users/:id", (c) => {
  const id = c.req.param("id");
  return c.json({ id, name: "Alice" });
});

// Query parameters
app.get("/search", (c) => {
  const q = c.req.query("q");
  const page = c.req.query("page") ?? "1";
  return c.json({ query: q, page: Number(page) });
});

// Grouped routes
const api = new Hono().basePath("/api");
const v1 = new Hono();

v1.get("/users", (c) => c.json([]));
v1.get("/posts", (c) => c.json([]));

api.route("/v1", v1);

export default app;
```

## Middleware

```typescript
import { Hono } from "hono";
import { cors } from "hono/cors";
import { logger } from "hono/logger";
import { prettyJSON } from "hono/pretty-json";
import { secureHeaders } from "hono/secure-headers";
import { timing } from "hono/timing";

const app = new Hono();

// Built-in middleware
app.use("*", logger());
app.use("*", secureHeaders());
app.use("*", timing());
app.use("*", prettyJSON());
app.use(
  "/api/*",
  cors({
    origin: ["https://example.com"],
    allowMethods: ["GET", "POST", "PUT", "DELETE"],
    allowHeaders: ["Content-Type", "Authorization"],
    maxAge: 86400,
  }),
);

// Custom middleware
app.use("/api/*", async (c, next) => {
  const start = Date.now();
  await next();
  const ms = Date.now() - start;
  c.header("X-Response-Time", `${ms}ms`);
});

// Error handling middleware
app.onError((err, c) => {
  console.error(`${err}`);
  return c.json({ error: "Internal Server Error" }, 500);
});

app.notFound((c) => {
  return c.json({ error: "Not Found" }, 404);
});
```

## Zod Validation

```typescript
import { Hono } from "hono";
import { zValidator } from "@hono/zod-validator";
import { z } from "zod";

const app = new Hono();

const createUserSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
  role: z.enum(["admin", "user"]).default("user"),
});

const querySchema = z.object({
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
});

app.post("/users", zValidator("json", createUserSchema), async (c) => {
  const data = c.req.valid("json"); // Fully typed
  return c.json({ id: "1", ...data }, 201);
});

app.get("/users", zValidator("query", querySchema), async (c) => {
  const { page, limit } = c.req.valid("query");
  return c.json({ page, limit, data: [] });
});
```

## JWT Authentication

```typescript
import { Hono } from "hono";
import { jwt, sign, verify } from "hono/jwt";

type Env = {
  Variables: {
    jwtPayload: { sub: string; role: string };
  };
  Bindings: {
    JWT_SECRET: string;
  };
};

const app = new Hono<Env>();

app.post("/auth/login", async (c) => {
  const { email, password } = await c.req.json();
  // Validate credentials...
  const token = await sign(
    { sub: "user-123", role: "admin", exp: Math.floor(Date.now() / 1000) + 3600 },
    c.env.JWT_SECRET,
  );
  return c.json({ token });
});

// Protected routes
app.use("/api/*", jwt({ secret: "your-secret" }));

app.get("/api/me", (c) => {
  const payload = c.get("jwtPayload");
  return c.json({ userId: payload.sub, role: payload.role });
});
```

## RPC Client (End-to-End Type Safety)

```typescript
// server.ts
import { Hono } from "hono";
import { zValidator } from "@hono/zod-validator";
import { z } from "zod";

const app = new Hono()
  .get("/api/users", async (c) => {
    return c.json({ users: [{ id: "1", name: "Alice" }] });
  })
  .post(
    "/api/users",
    zValidator("json", z.object({ name: z.string(), email: z.string().email() })),
    async (c) => {
      const data = c.req.valid("json");
      return c.json({ id: "2", ...data }, 201);
    },
  );

export type AppType = typeof app;
export default app;

// client.ts
import { hc } from "hono/client";
import type { AppType } from "./server";

const client = hc<AppType>("http://localhost:8787");

// Fully typed - IDE autocomplete for routes and responses
const res = await client.api.users.$get();
const data = await res.json(); // { users: { id: string; name: string }[] }

const created = await client.api.users.$post({
  json: { name: "Bob", email: "bob@example.com" },
});
```

## Streaming

```typescript
import { Hono } from "hono";
import { streamText, streamSSE } from "hono/streaming";

const app = new Hono();

app.get("/stream", (c) => {
  return streamText(c, async (stream) => {
    for (let i = 0; i < 5; i++) {
      await stream.writeln(`chunk ${i}`);
      await stream.sleep(1000);
    }
  });
});

app.get("/sse", (c) => {
  return streamSSE(c, async (stream) => {
    let id = 0;
    while (true) {
      await stream.writeSSE({
        data: JSON.stringify({ time: new Date().toISOString() }),
        event: "tick",
        id: String(id++),
      });
      await stream.sleep(1000);
    }
  });
});
```

## Multi-Runtime Deployment

```typescript
// Cloudflare Workers
// wrangler.toml: main = "src/index.ts"
export default app;

// Bun
// bun run src/index.ts
export default { port: 3000, fetch: app.fetch };

// Deno
// deno run --allow-net src/index.ts
import { serve } from "@std/http/server";
serve(app.fetch, { port: 3000 });

// Node.js
import { serve } from "@hono/node-server";
serve({ fetch: app.fetch, port: 3000 });
```

## Additional Resources

- Hono docs: https://hono.dev/
- Middleware: https://hono.dev/docs/middleware/builtin/cors
- RPC: https://hono.dev/docs/guides/rpc
