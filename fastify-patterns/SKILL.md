---
name: fastify-patterns
description: Fastify patterns covering route registration, schema validation with JSON Schema, plugins, hooks, decorators, serialization, TypeBox integration, WebSocket support, and production-ready Node.js API development.
---

# Fastify Patterns

This skill should be used when building high-performance Node.js APIs with Fastify. It covers routes, validation, plugins, hooks, TypeBox, WebSockets, and production patterns.

## When to Use This Skill

Use this skill when you need to:

- Build high-performance Node.js APIs
- Validate requests with JSON Schema
- Create reusable plugins and decorators
- Use hooks for request lifecycle
- Integrate TypeBox for type-safe schemas

## Basic Server

```typescript
import Fastify from "fastify";

const app = Fastify({
  logger: true,
});

app.get("/", async () => {
  return { message: "Hello Fastify!" };
});

app.listen({ port: 3000, host: "0.0.0.0" }, (err) => {
  if (err) {
    app.log.error(err);
    process.exit(1);
  }
});
```

## Routes with Schema Validation

```typescript
import { Type, Static } from "@sinclair/typebox";

const CreateUserSchema = Type.Object({
  name: Type.String({ minLength: 1 }),
  email: Type.String({ format: "email" }),
  age: Type.Optional(Type.Integer({ minimum: 0 })),
});

type CreateUserBody = Static<typeof CreateUserSchema>;

const UserResponseSchema = Type.Object({
  id: Type.String(),
  name: Type.String(),
  email: Type.String(),
  createdAt: Type.String(),
});

app.post<{ Body: CreateUserBody }>("/api/users", {
  schema: {
    body: CreateUserSchema,
    response: {
      201: UserResponseSchema,
    },
  },
  handler: async (request, reply) => {
    const { name, email, age } = request.body;
    const user = await createUser({ name, email, age });
    reply.status(201).send(user);
  },
});

// Route with params and query
const GetUsersSchema = {
  querystring: Type.Object({
    page: Type.Integer({ minimum: 1, default: 1 }),
    limit: Type.Integer({ minimum: 1, maximum: 100, default: 20 }),
    search: Type.Optional(Type.String()),
  }),
  params: Type.Object({
    orgId: Type.String(),
  }),
};

app.get<{
  Querystring: Static<typeof GetUsersSchema.querystring>;
  Params: Static<typeof GetUsersSchema.params>;
}>("/api/orgs/:orgId/users", {
  schema: GetUsersSchema,
  handler: async (request) => {
    const { page, limit, search } = request.query;
    const { orgId } = request.params;
    return userService.list(orgId, { page, limit, search });
  },
});
```

## Plugins

```typescript
import fp from "fastify-plugin";

// Database plugin
const dbPlugin = fp(async (fastify) => {
  const pool = new Pool({ connectionString: process.env.DATABASE_URL });
  fastify.decorate("db", pool);

  fastify.addHook("onClose", async () => {
    await pool.end();
  });
});

// Auth plugin
const authPlugin = fp(async (fastify) => {
  fastify.decorate("authenticate", async (request: FastifyRequest, reply: FastifyReply) => {
    const token = request.headers.authorization?.replace("Bearer ", "");
    if (!token) {
      reply.status(401).send({ error: "Unauthorized" });
      return;
    }
    try {
      request.user = await verifyToken(token);
    } catch {
      reply.status(401).send({ error: "Invalid token" });
    }
  });
});

// Register plugins
app.register(dbPlugin);
app.register(authPlugin);

// Use in routes
app.get("/api/profile", {
  onRequest: [app.authenticate],
  handler: async (request) => {
    return request.user;
  },
});
```

## Hooks

```typescript
// Request lifecycle hooks
app.addHook("onRequest", async (request, reply) => {
  request.startTime = Date.now();
});

app.addHook("preHandler", async (request, reply) => {
  // Run before handler
  if (request.headers["x-api-key"] !== process.env.API_KEY) {
    reply.status(403).send({ error: "Forbidden" });
  }
});

app.addHook("onSend", async (request, reply, payload) => {
  // Modify response before sending
  reply.header("X-Response-Time", `${Date.now() - request.startTime}ms`);
  return payload;
});

app.addHook("onError", async (request, reply, error) => {
  request.log.error({ err: error }, "Request error");
});

// Route-level hooks
app.get("/api/admin", {
  onRequest: [app.authenticate, requireRole("admin")],
  handler: async () => ({ admin: true }),
});
```

## Error Handling

```typescript
// Custom error handler
app.setErrorHandler((error, request, reply) => {
  request.log.error({ err: error });

  if (error.validation) {
    reply.status(400).send({
      error: "Validation Error",
      details: error.validation,
    });
    return;
  }

  reply.status(error.statusCode || 500).send({
    error: error.message || "Internal Server Error",
  });
});

// Not found handler
app.setNotFoundHandler((request, reply) => {
  reply.status(404).send({
    error: "Not Found",
    path: request.url,
  });
});
```

## Encapsulated Routes

```typescript
// routes/users.ts
async function userRoutes(app: FastifyInstance) {
  app.get("/", async () => {
    return userService.findAll();
  });

  app.get("/:id", async (request) => {
    const { id } = request.params as { id: string };
    return userService.findById(id);
  });

  app.post("/", {
    schema: { body: CreateUserSchema },
    handler: async (request, reply) => {
      const user = await userService.create(request.body);
      reply.status(201).send(user);
    },
  });
}

// Register with prefix
app.register(userRoutes, { prefix: "/api/users" });
```

## Additional Resources

- Fastify: https://fastify.dev/
- Fastify plugins: https://fastify.dev/ecosystem/
- TypeBox: https://github.com/sinclairzx81/typebox
