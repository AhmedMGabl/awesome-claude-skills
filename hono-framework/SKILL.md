---
name: hono-framework
description: Hono web framework development covering routing, middleware (CORS, logger, JWT, bearer auth), Zod OpenAPI integration with @hono/zod-openapi, request validation, context helpers, file handling and streaming, error handling with HTTPException, multi-runtime support (Cloudflare Workers, Bun, Node.js, Deno), RPC client with hono/client, and testing with app.request.
---

# Hono Framework Development

This skill should be used when building web applications and APIs with the Hono framework. It covers routing patterns, built-in and custom middleware, type-safe validation with Zod OpenAPI, context helpers, streaming responses, error handling, multi-runtime deployment, end-to-end type-safe RPC clients, and testing strategies.

## When to Use This Skill

- Build lightweight, high-performance APIs with Hono
- Deploy to Cloudflare Workers, Bun, Node.js, or Deno
- Integrate Zod OpenAPI for type-safe request/response validation and auto-generated docs
- Add middleware for CORS, logging, JWT authentication, and bearer auth
- Create end-to-end type-safe clients with hono/client RPC
- Handle file uploads, streaming responses, and Server-Sent Events
- Test routes using the built-in app.request method

## Project Setup

```bash
# Create a new Hono project (interactive runtime selection)
npm create hono@latest my-app

# Or specify the runtime template directly
npm create hono@latest my-app -- --template cloudflare-workers
npm create hono@latest my-app -- --template bun
npm create hono@latest my-app -- --template nodejs
npm create hono@latest my-app -- --template deno

# Install core dependencies
npm install hono
npm install -D typescript @types/node wrangler  # for Cloudflare Workers

# Install optional packages
npm install @hono/zod-openapi   # Zod OpenAPI integration
npm install @hono/swagger-ui    # Swagger UI middleware
npm install zod                 # Schema validation

# Project structure
src/
├── index.ts              # App entry point and runtime adapter
├── app.ts                # Hono app factory
├── routes/
│   ├── index.ts          # Route aggregation
│   ├── users.ts          # User routes
│   └── auth.ts           # Auth routes
├── middleware/
│   ├── auth.ts           # Custom auth middleware
│   └── timing.ts         # Request timing middleware
├── schemas/
│   └── user.ts           # Zod schemas and OpenAPI route definitions
├── services/
│   └── user.service.ts   # Business logic
└── types/
    └── index.ts          # Shared types and env bindings
```

## Basic Routing

### HTTP Methods and Route Patterns

```typescript
import { Hono } from "hono";

const app = new Hono();

// Basic HTTP methods
app.get("/", (c) => c.text("Hello Hono!"));
app.post("/posts", (c) => c.json({ message: "Created" }, 201));
app.put("/posts/:id", (c) => c.json({ message: "Updated" }));
app.delete("/posts/:id", (c) => c.json({ message: "Deleted" }));
app.patch("/posts/:id", (c) => c.json({ message: "Patched" }));

// Route parameters
app.get("/users/:id", (c) => {
  const id = c.req.param("id");
  return c.json({ id });
});

// Multiple parameters
app.get("/posts/:postId/comments/:commentId", (c) => {
  const { postId, commentId } = c.req.param();
  return c.json({ postId, commentId });
});

// Optional parameters via regex
app.get("/api/:version?/users", (c) => {
  const version = c.req.param("version") ?? "v1";
  return c.json({ version });
});

// Wildcard routes
app.get("/files/*", (c) => {
  const path = c.req.path;
  return c.text(`Serving: ${path}`);
});

// Handle all methods
app.all("/api/*", (c) => {
  return c.json({ method: c.req.method, path: c.req.path });
});
```

### Route Grouping

```typescript
import { Hono } from "hono";

const app = new Hono();

// Group with .route()
const api = new Hono();

const users = new Hono();
users.get("/", (c) => c.json({ users: [] }));
users.get("/:id", (c) => c.json({ id: c.req.param("id") }));
users.post("/", async (c) => {
  const body = await c.req.json();
  return c.json(body, 201);
});

const posts = new Hono();
posts.get("/", (c) => c.json({ posts: [] }));
posts.post("/", async (c) => {
  const body = await c.req.json();
  return c.json(body, 201);
});

api.route("/users", users);
api.route("/posts", posts);
app.route("/api/v1", api);

// Basepath with .basePath()
const v2 = new Hono().basePath("/api/v2");
v2.get("/health", (c) => c.json({ status: "ok" }));

export default app;
```

### Reading Request Data

```typescript
app.post("/submit", async (c) => {
  // JSON body
  const body = await c.req.json<{ name: string; email: string }>();

  // Form data
  const formData = await c.req.formData();
  const name = formData.get("name");

  // Query parameters
  const page = c.req.query("page") ?? "1";
  const filters = c.req.queries("filter"); // string[] for repeated params

  // Headers
  const userAgent = c.req.header("User-Agent");

  // URL and path info
  const url = c.req.url;       // full URL
  const path = c.req.path;     // path only
  const method = c.req.method;  // HTTP method

  return c.json({ body, page, userAgent });
});
```

## Middleware

### Built-in Middleware

```typescript
import { Hono } from "hono";
import { cors } from "hono/cors";
import { logger } from "hono/logger";
import { prettyJSON } from "hono/pretty-json";
import { secureHeaders } from "hono/secure-headers";
import { timing, startTime, endTime } from "hono/timing";
import { compress } from "hono/compress";
import { etag } from "hono/etag";
import { cache } from "hono/cache";

const app = new Hono();

// Logger - logs request and response
app.use("*", logger());

// CORS
app.use("/api/*", cors({
  origin: ["http://localhost:3000", "https://myapp.com"],
  allowMethods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
  allowHeaders: ["Content-Type", "Authorization"],
  exposeHeaders: ["X-Total-Count"],
  maxAge: 3600,
  credentials: true,
}));

// Secure headers (X-Content-Type-Options, X-Frame-Options, etc.)
app.use("*", secureHeaders());

// Pretty JSON in development (adds ?pretty query param support)
app.use("*", prettyJSON());

// Server timing headers
app.use("*", timing());

// Compression (gzip)
app.use("*", compress());

// ETag for caching
app.use("/assets/*", etag());

// Cache (Cloudflare Workers only)
app.use("/api/public/*", cache({
  cacheName: "my-app",
  cacheControl: "max-age=3600",
}));

// Server timing example
app.get("/data", async (c) => {
  startTime(c, "db", "Database query");
  const data = await fetchFromDB();
  endTime(c, "db");
  return c.json(data);
});
```

### JWT Authentication

```typescript
import { Hono } from "hono";
import { jwt, sign, verify } from "hono/jwt";

type Env = {
  Variables: {
    jwtPayload: { sub: string; role: string; exp: number };
  };
  Bindings: {
    JWT_SECRET: string;
  };
};

const app = new Hono<Env>();

// Generate a token
app.post("/auth/login", async (c) => {
  const { email, password } = await c.req.json();

  // Validate credentials (example)
  const user = await authenticateUser(email, password);
  if (!user) {
    return c.json({ error: "Invalid credentials" }, 401);
  }

  const now = Math.floor(Date.now() / 1000);
  const payload = {
    sub: user.id,
    role: user.role,
    exp: now + 60 * 60, // 1 hour
    iat: now,
  };

  const token = await sign(payload, c.env.JWT_SECRET);
  return c.json({ token });
});

// Protect routes with JWT middleware
app.use("/api/*", jwt({ secret: c => c.env.JWT_SECRET }));

// Access the decoded payload
app.get("/api/me", (c) => {
  const payload = c.get("jwtPayload");
  return c.json({ userId: payload.sub, role: payload.role });
});
```

### Bearer Auth

```typescript
import { Hono } from "hono";
import { bearerAuth } from "hono/bearer-auth";

const app = new Hono();

// Simple static token
app.use("/api/*", bearerAuth({ token: "my-secret-token" }));

// Multiple valid tokens
app.use("/api/*", bearerAuth({
  token: ["token-1", "token-2", "token-3"],
}));

// Custom verification function
app.use("/api/*", bearerAuth({
  verifyToken: async (token, c) => {
    const apiKey = await lookupApiKey(token);
    if (!apiKey || apiKey.revoked) return false;
    c.set("apiKey", apiKey);
    return true;
  },
}));
```

### Custom Middleware

```typescript
import { Hono } from "hono";
import { createMiddleware } from "hono/factory";

const app = new Hono();

// Inline middleware
app.use("*", async (c, next) => {
  const start = Date.now();
  await next();
  const ms = Date.now() - start;
  c.header("X-Response-Time", `${ms}ms`);
});

// Reusable middleware with createMiddleware
type Env = {
  Variables: {
    user: { id: string; role: string };
  };
};

const requireRole = (role: string) =>
  createMiddleware<Env>(async (c, next) => {
    const user = c.get("user");
    if (!user) {
      return c.json({ error: "Authentication required" }, 401);
    }
    if (user.role !== role) {
      return c.json({ error: "Insufficient permissions" }, 403);
    }
    await next();
  });

app.get("/admin/dashboard", requireRole("admin"), (c) => {
  return c.json({ message: "Welcome, admin" });
});

// Middleware that modifies the response
const addPoweredBy = createMiddleware(async (c, next) => {
  await next();
  c.header("X-Powered-By", "Hono");
});

app.use("*", addPoweredBy);
```

## Zod OpenAPI Integration

### Setup and Configuration

```typescript
import { OpenAPIHono, createRoute, z } from "@hono/zod-openapi";
import { swaggerUI } from "@hono/swagger-ui";

const app = new OpenAPIHono();

// Serve Swagger UI
app.get("/docs", swaggerUI({ url: "/openapi.json" }));

// Serve the OpenAPI spec
app.doc("/openapi.json", {
  openapi: "3.1.0",
  info: {
    title: "My API",
    version: "1.0.0",
    description: "API built with Hono and Zod OpenAPI",
  },
  servers: [
    { url: "http://localhost:8787", description: "Development" },
    { url: "https://api.myapp.com", description: "Production" },
  ],
});
```

### Defining Schemas and Routes

```typescript
import { OpenAPIHono, createRoute, z } from "@hono/zod-openapi";

// Define reusable schemas
const UserSchema = z.object({
  id: z.string().uuid().openapi({ example: "123e4567-e89b-12d3-a456-426614174000" }),
  name: z.string().min(1).max(100).openapi({ example: "Alice" }),
  email: z.string().email().openapi({ example: "alice@example.com" }),
  role: z.enum(["admin", "user"]).default("user"),
  createdAt: z.string().datetime(),
}).openapi("User");

const CreateUserSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
  password: z.string().min(8),
  role: z.enum(["admin", "user"]).default("user"),
}).openapi("CreateUser");

const ErrorSchema = z.object({
  error: z.string(),
  details: z.record(z.unknown()).optional(),
}).openapi("Error");

const PaginationQuery = z.object({
  page: z.string().pipe(z.coerce.number().int().min(1)).default("1"),
  limit: z.string().pipe(z.coerce.number().int().min(1).max(100)).default("20"),
});

// Define a route with full request/response validation
const listUsersRoute = createRoute({
  method: "get",
  path: "/users",
  tags: ["Users"],
  summary: "List all users",
  request: {
    query: PaginationQuery,
  },
  responses: {
    200: {
      content: {
        "application/json": {
          schema: z.object({
            users: z.array(UserSchema),
            total: z.number(),
          }),
        },
      },
      description: "List of users",
    },
  },
});

const createUserRoute = createRoute({
  method: "post",
  path: "/users",
  tags: ["Users"],
  summary: "Create a new user",
  request: {
    body: {
      content: {
        "application/json": { schema: CreateUserSchema },
      },
      required: true,
    },
  },
  responses: {
    201: {
      content: {
        "application/json": { schema: UserSchema },
      },
      description: "User created successfully",
    },
    400: {
      content: {
        "application/json": { schema: ErrorSchema },
      },
      description: "Validation error",
    },
    409: {
      content: {
        "application/json": { schema: ErrorSchema },
      },
      description: "Email already exists",
    },
  },
});

const getUserRoute = createRoute({
  method: "get",
  path: "/users/:id",
  tags: ["Users"],
  summary: "Get a user by ID",
  request: {
    params: z.object({
      id: z.string().uuid(),
    }),
  },
  responses: {
    200: {
      content: {
        "application/json": { schema: UserSchema },
      },
      description: "User found",
    },
    404: {
      content: {
        "application/json": { schema: ErrorSchema },
      },
      description: "User not found",
    },
  },
});

// Register routes with handlers
const app = new OpenAPIHono();

app.openapi(listUsersRoute, async (c) => {
  const { page, limit } = c.req.valid("query");
  const users = await userService.findAll({ page, limit });
  return c.json({ users, total: users.length }, 200);
});

app.openapi(createUserRoute, async (c) => {
  const data = c.req.valid("json");
  const user = await userService.create(data);
  return c.json(user, 201);
});

app.openapi(getUserRoute, async (c) => {
  const { id } = c.req.valid("param");
  const user = await userService.findById(id);
  if (!user) {
    return c.json({ error: "User not found" }, 404);
  }
  return c.json(user, 200);
});
```

### OpenAPI Security Schemes

```typescript
import { OpenAPIHono, createRoute, z } from "@hono/zod-openapi";

const app = new OpenAPIHono();

// Register security scheme in the OpenAPI doc
app.doc("/openapi.json", {
  openapi: "3.1.0",
  info: { title: "Secure API", version: "1.0.0" },
  security: [{ Bearer: [] }],
  components: {
    securitySchemes: {
      Bearer: {
        type: "http",
        scheme: "bearer",
        bearerFormat: "JWT",
      },
    },
  },
});

// Apply security to individual routes
const protectedRoute = createRoute({
  method: "get",
  path: "/api/protected",
  tags: ["Protected"],
  security: [{ Bearer: [] }],
  responses: {
    200: {
      content: {
        "application/json": {
          schema: z.object({ message: z.string() }),
        },
      },
      description: "Success",
    },
  },
});
```

## Request Validation

### Validator Middleware

```typescript
import { Hono } from "hono";
import { zValidator } from "@hono/zod-validator";
import { z } from "zod";

const app = new Hono();

// Validate JSON body
const CreatePostSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().min(10),
  tags: z.array(z.string()).max(5).default([]),
  published: z.boolean().default(false),
});

app.post("/posts", zValidator("json", CreatePostSchema), async (c) => {
  const data = c.req.valid("json"); // fully typed
  return c.json(data, 201);
});

// Validate query parameters
const ListQuerySchema = z.object({
  page: z.string().pipe(z.coerce.number().int().positive()).default("1"),
  limit: z.string().pipe(z.coerce.number().int().min(1).max(100)).default("20"),
  search: z.string().optional(),
  sort: z.enum(["asc", "desc"]).default("desc"),
});

app.get("/posts", zValidator("query", ListQuerySchema), (c) => {
  const { page, limit, search, sort } = c.req.valid("query");
  return c.json({ page, limit, search, sort });
});

// Validate route parameters
const ParamSchema = z.object({
  id: z.string().uuid(),
});

app.get("/posts/:id", zValidator("param", ParamSchema), (c) => {
  const { id } = c.req.valid("param");
  return c.json({ id });
});

// Validate headers
const HeaderSchema = z.object({
  "x-api-key": z.string().min(1),
  "x-request-id": z.string().uuid().optional(),
});

app.post(
  "/webhook",
  zValidator("header", HeaderSchema),
  async (c) => {
    const headers = c.req.valid("header");
    return c.json({ apiKey: headers["x-api-key"] });
  }
);

// Validate form data
const UploadSchema = z.object({
  name: z.string().min(1),
  description: z.string().optional(),
});

app.post("/upload", zValidator("form", UploadSchema), async (c) => {
  const data = c.req.valid("form");
  return c.json(data);
});

// Custom error handling for validation
app.post(
  "/strict",
  zValidator("json", CreatePostSchema, (result, c) => {
    if (!result.success) {
      return c.json(
        {
          error: "Validation failed",
          details: result.error.flatten(),
        },
        400
      );
    }
  }),
  (c) => {
    const data = c.req.valid("json");
    return c.json(data, 201);
  }
);

// Multiple validators on a single route
app.put(
  "/posts/:id",
  zValidator("param", ParamSchema),
  zValidator("json", CreatePostSchema.partial()),
  async (c) => {
    const { id } = c.req.valid("param");
    const body = c.req.valid("json");
    return c.json({ id, ...body });
  }
);
```

## Context Helpers

### Response Helpers

```typescript
import { Hono } from "hono";

const app = new Hono();

// JSON response
app.get("/json", (c) => {
  return c.json({ message: "Hello", timestamp: Date.now() });
});

// JSON with status code
app.post("/create", (c) => {
  return c.json({ id: "123", created: true }, 201);
});

// JSON with custom headers
app.get("/custom", (c) => {
  return c.json(
    { data: "value" },
    200,
    { "X-Custom-Header": "custom-value" }
  );
});

// Plain text
app.get("/text", (c) => {
  return c.text("Hello, plain text!");
});

// HTML
app.get("/page", (c) => {
  return c.html("<html><body><h1>Hello Hono</h1></body></html>");
});

// HTML with JSX (requires JSX configuration)
app.get("/jsx", (c) => {
  return c.html(
    <html>
      <body>
        <h1>Hello from JSX</h1>
      </body>
    </html>
  );
});

// Redirect
app.get("/old-page", (c) => {
  return c.redirect("/new-page");        // 302 by default
});
app.get("/moved", (c) => {
  return c.redirect("/new-location", 301); // permanent redirect
});

// Set status and return body
app.get("/no-content", (c) => {
  return c.body(null, 204);
});

// Set headers
app.get("/headers", (c) => {
  c.header("X-Request-Id", crypto.randomUUID());
  c.header("Cache-Control", "no-cache");
  return c.json({ ok: true });
});

// Set and get cookies
import { setCookie, getCookie, deleteCookie } from "hono/cookie";

app.get("/cookie", (c) => {
  const session = getCookie(c, "session");
  return c.json({ session });
});

app.post("/login", (c) => {
  setCookie(c, "session", "abc123", {
    path: "/",
    httpOnly: true,
    secure: true,
    sameSite: "Strict",
    maxAge: 60 * 60 * 24, // 1 day
  });
  return c.json({ message: "Logged in" });
});

app.post("/logout", (c) => {
  deleteCookie(c, "session");
  return c.json({ message: "Logged out" });
});
```

### Environment Bindings and Variables

```typescript
// Define typed environment bindings
type Env = {
  Bindings: {
    // Cloudflare Workers bindings
    DATABASE: D1Database;
    KV_STORE: KVNamespace;
    R2_BUCKET: R2Bucket;
    JWT_SECRET: string;
  };
  Variables: {
    // Custom variables set by middleware
    user: { id: string; role: string };
    requestId: string;
  };
};

const app = new Hono<Env>();

// Access bindings
app.get("/data", async (c) => {
  const db = c.env.DATABASE;
  const result = await db.prepare("SELECT * FROM users").all();
  return c.json(result);
});

// Set and get variables
app.use("*", async (c, next) => {
  c.set("requestId", crypto.randomUUID());
  await next();
});

app.get("/info", (c) => {
  const requestId = c.get("requestId");
  return c.json({ requestId });
});
```

## File Handling and Streaming

### File Uploads

```typescript
import { Hono } from "hono";

const app = new Hono();

// Single file upload
app.post("/upload", async (c) => {
  const body = await c.req.parseBody();
  const file = body["file"] as File;

  if (!file || !(file instanceof File)) {
    return c.json({ error: "No file provided" }, 400);
  }

  // Validate file type
  const allowedTypes = ["image/jpeg", "image/png", "image/webp"];
  if (!allowedTypes.includes(file.type)) {
    return c.json({ error: "Invalid file type" }, 400);
  }

  // Validate file size (5MB max)
  if (file.size > 5 * 1024 * 1024) {
    return c.json({ error: "File too large" }, 413);
  }

  const arrayBuffer = await file.arrayBuffer();
  // Store the file (example with Cloudflare R2)
  // await c.env.R2_BUCKET.put(`uploads/${file.name}`, arrayBuffer);

  return c.json({
    filename: file.name,
    size: file.size,
    type: file.type,
  }, 201);
});

// Multiple file upload
app.post("/upload-multiple", async (c) => {
  const body = await c.req.parseBody({ all: true });
  const files = body["files"] as File[];

  const results = await Promise.all(
    files.map(async (file) => ({
      name: file.name,
      size: file.size,
      type: file.type,
    }))
  );

  return c.json({ uploaded: results }, 201);
});
```

### Streaming Responses

```typescript
import { Hono } from "hono";
import { stream, streamSSE, streamText } from "hono/streaming";

const app = new Hono();

// Basic streaming
app.get("/stream", (c) => {
  return stream(c, async (stream) => {
    for (let i = 0; i < 10; i++) {
      await stream.write(`Chunk ${i}\n`);
      await stream.sleep(100);
    }
  });
});

// Server-Sent Events (SSE)
app.get("/sse", (c) => {
  return streamSSE(c, async (stream) => {
    let id = 0;
    while (true) {
      const data = JSON.stringify({ time: new Date().toISOString(), id });
      await stream.writeSSE({
        data,
        event: "time-update",
        id: String(id++),
      });
      await stream.sleep(1000);
    }
  });
});

// Stream text (e.g., for LLM-style token streaming)
app.get("/ai/stream", (c) => {
  return streamText(c, async (stream) => {
    const words = ["Hello", " ", "from", " ", "Hono", "!"];
    for (const word of words) {
      await stream.write(word);
      await stream.sleep(200);
    }
  });
});

// Stream a large file
app.get("/download/:filename", async (c) => {
  const filename = c.req.param("filename");

  // Example with Cloudflare R2
  // const object = await c.env.R2_BUCKET.get(`files/${filename}`);
  // if (!object) return c.notFound();
  // c.header("Content-Type", object.httpMetadata?.contentType ?? "application/octet-stream");
  // c.header("Content-Disposition", `attachment; filename="${filename}"`);
  // return c.body(object.body);

  // Example with a ReadableStream
  return stream(c, async (stream) => {
    const response = await fetch(`https://storage.example.com/${filename}`);
    if (!response.body) return;

    const reader = response.body.getReader();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      await stream.write(value);
    }
  });
});
```

## Error Handling

### HTTPException

```typescript
import { Hono } from "hono";
import { HTTPException } from "hono/http-exception";

const app = new Hono();

// Throw HTTPException in route handlers
app.get("/users/:id", async (c) => {
  const id = c.req.param("id");
  const user = await userService.findById(id);

  if (!user) {
    throw new HTTPException(404, { message: "User not found" });
  }

  return c.json(user);
});

// HTTPException with custom response
app.post("/upload", async (c) => {
  const body = await c.req.parseBody();
  const file = body["file"] as File;

  if (!file) {
    throw new HTTPException(400, {
      message: "File is required",
      cause: new Error("Missing file in request body"),
    });
  }

  if (file.size > 10 * 1024 * 1024) {
    const errorResponse = new Response(
      JSON.stringify({
        error: "File too large",
        maxSize: "10MB",
        actualSize: `${(file.size / 1024 / 1024).toFixed(2)}MB`,
      }),
      {
        status: 413,
        headers: { "Content-Type": "application/json" },
      }
    );
    throw new HTTPException(413, { res: errorResponse });
  }

  return c.json({ uploaded: true });
});

// Global error handler
app.onError((err, c) => {
  console.error(`Error: ${err.message}`, err.stack);

  if (err instanceof HTTPException) {
    return err.getResponse();
  }

  // Zod validation errors
  if (err.name === "ZodError") {
    return c.json(
      { error: "Validation failed", details: JSON.parse(err.message) },
      400
    );
  }

  // Unexpected errors
  return c.json(
    {
      error:
        process.env.NODE_ENV === "production"
          ? "Internal server error"
          : err.message,
    },
    500
  );
});

// Custom 404 handler
app.notFound((c) => {
  return c.json(
    {
      error: "Not found",
      path: c.req.path,
      method: c.req.method,
    },
    404
  );
});
```

### Error Handling Patterns

```typescript
import { Hono } from "hono";
import { HTTPException } from "hono/http-exception";

// Application-specific error classes
class NotFoundError extends HTTPException {
  constructor(resource: string, id: string) {
    super(404, { message: `${resource} with id '${id}' not found` });
  }
}

class ConflictError extends HTTPException {
  constructor(message: string) {
    super(409, { message });
  }
}

class UnauthorizedError extends HTTPException {
  constructor(message = "Authentication required") {
    super(401, { message });
  }
}

// Usage in routes
app.get("/users/:id", async (c) => {
  const user = await userService.findById(c.req.param("id"));
  if (!user) throw new NotFoundError("User", c.req.param("id"));
  return c.json(user);
});

app.post("/users", async (c) => {
  const data = await c.req.json();
  const existing = await userService.findByEmail(data.email);
  if (existing) throw new ConflictError("Email already registered");
  const user = await userService.create(data);
  return c.json(user, 201);
});
```

## Multi-Runtime Support

### Cloudflare Workers

```typescript
// src/index.ts - Cloudflare Workers entry point
import { Hono } from "hono";

type Bindings = {
  DATABASE: D1Database;
  KV: KVNamespace;
  R2: R2Bucket;
  AI: Ai;
  JWT_SECRET: string;
};

const app = new Hono<{ Bindings: Bindings }>();

app.get("/", (c) => c.json({ runtime: "Cloudflare Workers" }));

// Access D1 database
app.get("/users", async (c) => {
  const { results } = await c.env.DATABASE
    .prepare("SELECT id, name, email FROM users LIMIT ?")
    .bind(50)
    .all();
  return c.json(results);
});

// Access KV store
app.get("/cache/:key", async (c) => {
  const key = c.req.param("key");
  const value = await c.env.KV.get(key);
  if (!value) return c.json({ error: "Key not found" }, 404);
  return c.json(JSON.parse(value));
});

// Access R2 storage
app.get("/files/:key", async (c) => {
  const object = await c.env.R2.get(c.req.param("key"));
  if (!object) return c.notFound();

  c.header("Content-Type", object.httpMetadata?.contentType ?? "application/octet-stream");
  return c.body(object.body);
});

export default app;

// wrangler.toml
// name = "my-hono-app"
// main = "src/index.ts"
// compatibility_date = "2024-12-01"
// [[d1_databases]]
// binding = "DATABASE"
// database_name = "my-db"
// database_id = "xxxx"
```

### Bun

```typescript
// src/index.ts - Bun entry point
import { Hono } from "hono";
import { serveStatic } from "hono/bun";

const app = new Hono();

// Serve static files
app.use("/static/*", serveStatic({ root: "./" }));

app.get("/", (c) => c.json({ runtime: "Bun" }));

// File system operations with Bun APIs
app.post("/files", async (c) => {
  const body = await c.req.parseBody();
  const file = body["file"] as File;
  await Bun.write(`./uploads/${file.name}`, file);
  return c.json({ saved: file.name }, 201);
});

export default {
  port: 3000,
  fetch: app.fetch,
};
```

### Node.js

```typescript
// src/index.ts - Node.js entry point
import { serve } from "@hono/node-server";
import { serveStatic } from "@hono/node-server/serve-static";
import { Hono } from "hono";

const app = new Hono();

// Serve static files
app.use("/static/*", serveStatic({ root: "./" }));

app.get("/", (c) => c.json({ runtime: "Node.js" }));

serve({
  fetch: app.fetch,
  port: 3000,
}, (info) => {
  console.log(`Server running at http://localhost:${info.port}`);
});
```

### Deno

```typescript
// main.ts - Deno entry point
import { Hono } from "hono";
import { serveStatic } from "hono/deno";

const app = new Hono();

// Serve static files
app.use("/static/*", serveStatic({ root: "./" }));

app.get("/", (c) => c.json({ runtime: "Deno" }));

Deno.serve({ port: 3000 }, app.fetch);
```

### Portable App Pattern

```typescript
// src/app.ts - Runtime-agnostic application
import { Hono } from "hono";
import { cors } from "hono/cors";
import { logger } from "hono/logger";
import { userRoutes } from "./routes/users";
import { authRoutes } from "./routes/auth";

export function createApp() {
  const app = new Hono();

  app.use("*", logger());
  app.use("*", cors());

  app.get("/health", (c) => c.json({ status: "ok" }));

  app.route("/api/users", userRoutes);
  app.route("/api/auth", authRoutes);

  return app;
}

export type AppType = ReturnType<typeof createApp>;

// src/entry-cloudflare.ts
import { createApp } from "./app";
export default createApp();

// src/entry-node.ts
import { serve } from "@hono/node-server";
import { createApp } from "./app";
serve({ fetch: createApp().fetch, port: 3000 });

// src/entry-bun.ts
import { createApp } from "./app";
export default { port: 3000, fetch: createApp().fetch };

// src/entry-deno.ts
import { createApp } from "./app";
Deno.serve({ port: 3000 }, createApp().fetch);
```

## RPC Client with hono/client

### Server-Side Route Definitions

```typescript
// src/routes/users.ts
import { Hono } from "hono";
import { zValidator } from "@hono/zod-validator";
import { z } from "zod";

const CreateUserSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
});

const app = new Hono()
  .get("/", (c) => {
    return c.json({ users: [{ id: "1", name: "Alice" }] });
  })
  .get("/:id", (c) => {
    const id = c.req.param("id");
    return c.json({ id, name: "Alice" });
  })
  .post("/", zValidator("json", CreateUserSchema), async (c) => {
    const data = c.req.valid("json");
    return c.json({ id: "new-id", ...data }, 201);
  })
  .delete("/:id", (c) => {
    return c.json({ deleted: true });
  });

// Export the type for the client
export type UserRoutes = typeof app;
export { app as userRoutes };

// src/app.ts
import { Hono } from "hono";
import { userRoutes } from "./routes/users";

const app = new Hono()
  .route("/api/users", userRoutes);

export type AppType = typeof app;
export default app;
```

### Client-Side Usage

```typescript
// client.ts
import { hc } from "hono/client";
import type { AppType } from "./app";

// Create a typed client
const client = hc<AppType>("http://localhost:3000");

// All requests are fully typed (URL, params, body, response)
async function main() {
  // GET /api/users
  const listRes = await client.api.users.$get();
  const { users } = await listRes.json();
  // users is typed as { id: string; name: string }[]

  // GET /api/users/:id
  const getRes = await client.api.users[":id"].$get({
    param: { id: "1" },
  });
  const user = await getRes.json();
  // user is typed as { id: string; name: string }

  // POST /api/users
  const createRes = await client.api.users.$post({
    json: { name: "Bob", email: "bob@example.com" },
  });
  const created = await createRes.json();
  // created is typed as { id: string; name: string; email: string }

  // DELETE /api/users/:id
  const deleteRes = await client.api.users[":id"].$delete({
    param: { id: "1" },
  });
  const deleteResult = await deleteRes.json();
  // deleteResult is typed as { deleted: boolean }
}

// Using with query parameters
const searchRes = await client.api.users.$get({
  query: { page: "1", limit: "10", search: "alice" },
});

// Using with custom headers
const authRes = await client.api.users.$get(
  {},
  {
    headers: {
      Authorization: "Bearer my-token",
    },
  }
);

// Custom fetch for interceptors (e.g., attach auth automatically)
const authenticatedClient = hc<AppType>("http://localhost:3000", {
  headers: {
    Authorization: `Bearer ${getToken()}`,
  },
});

// Custom fetch function for advanced scenarios
const clientWithRetry = hc<AppType>("http://localhost:3000", {
  fetch: async (input, init) => {
    let response = await fetch(input, init);
    if (response.status === 401) {
      await refreshToken();
      response = await fetch(input, {
        ...init,
        headers: {
          ...init?.headers,
          Authorization: `Bearer ${getToken()}`,
        },
      });
    }
    return response;
  },
});
```

## Testing with app.request

### Basic Testing

```typescript
import { describe, it, expect } from "vitest"; // or bun:test, jest
import app from "../src/app";

describe("GET /", () => {
  it("returns hello message", async () => {
    const res = await app.request("/");

    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body).toEqual({ message: "Hello Hono!" });
  });
});

describe("GET /users/:id", () => {
  it("returns user by ID", async () => {
    const res = await app.request("/api/users/123");

    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body.id).toBe("123");
  });

  it("returns 404 for unknown user", async () => {
    const res = await app.request("/api/users/unknown");

    expect(res.status).toBe(404);
    const body = await res.json();
    expect(body.error).toBe("User not found");
  });
});
```

### Testing with Request Options

```typescript
import { describe, it, expect } from "vitest";
import app from "../src/app";

describe("POST /api/users", () => {
  it("creates a user with valid data", async () => {
    const res = await app.request("/api/users", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "Alice",
        email: "alice@example.com",
        password: "secure123",
      }),
    });

    expect(res.status).toBe(201);
    const body = await res.json();
    expect(body).toMatchObject({ name: "Alice", email: "alice@example.com" });
    expect(body.id).toBeDefined();
  });

  it("rejects invalid input", async () => {
    const res = await app.request("/api/users", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: "" }),
    });

    expect(res.status).toBe(400);
    const body = await res.json();
    expect(body.error).toContain("Validation");
  });
});

describe("Protected routes", () => {
  it("rejects unauthenticated requests", async () => {
    const res = await app.request("/api/protected");

    expect(res.status).toBe(401);
  });

  it("allows authenticated requests", async () => {
    const token = await generateTestToken({ sub: "user-1", role: "admin" });

    const res = await app.request("/api/protected", {
      headers: { Authorization: `Bearer ${token}` },
    });

    expect(res.status).toBe(200);
  });
});
```

### Testing with Cloudflare Workers Bindings

```typescript
import { describe, it, expect } from "vitest";
import app from "../src/index";

describe("Cloudflare Workers app", () => {
  // Mock environment bindings
  const mockEnv = {
    DATABASE: {
      prepare: (sql: string) => ({
        bind: () => ({
          all: async () => ({
            results: [{ id: "1", name: "Alice" }],
          }),
        }),
      }),
    },
    JWT_SECRET: "test-secret",
    KV: {
      get: async (key: string) => JSON.stringify({ value: "cached" }),
      put: async (key: string, value: string) => {},
    },
  };

  it("fetches users from D1", async () => {
    const res = await app.request("/users", {}, mockEnv);

    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body).toEqual([{ id: "1", name: "Alice" }]);
  });

  it("reads from KV cache", async () => {
    const res = await app.request("/cache/my-key", {}, mockEnv);

    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body).toEqual({ value: "cached" });
  });
});
```

### Testing Streaming and SSE

```typescript
import { describe, it, expect } from "vitest";
import app from "../src/app";

describe("Streaming endpoints", () => {
  it("streams SSE events", async () => {
    const res = await app.request("/sse");

    expect(res.status).toBe(200);
    expect(res.headers.get("content-type")).toContain("text/event-stream");

    // Read the stream
    const reader = res.body!.getReader();
    const decoder = new TextDecoder();
    const { value } = await reader.read();
    const text = decoder.decode(value);

    expect(text).toContain("event: time-update");
    expect(text).toContain("data:");

    reader.cancel();
  });
});
```

### Helper Utilities for Testing

```typescript
// test/helpers.ts
import { sign } from "hono/jwt";

export async function generateTestToken(
  payload: Record<string, unknown>,
  secret = "test-secret"
) {
  return sign(
    {
      ...payload,
      exp: Math.floor(Date.now() / 1000) + 3600,
      iat: Math.floor(Date.now() / 1000),
    },
    secret
  );
}

export function jsonRequest(
  path: string,
  body: unknown,
  options: RequestInit = {}
) {
  return new Request(`http://localhost${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    body: JSON.stringify(body),
    ...options,
  });
}

// Usage in tests
import app from "../src/app";
import { generateTestToken, jsonRequest } from "./helpers";

const res = await app.request(
  jsonRequest("/api/users", { name: "Alice", email: "alice@test.com" })
);
```

## Additional Resources

- Hono documentation: https://hono.dev/
- Hono GitHub repository: https://github.com/honojs/hono
- @hono/zod-openapi: https://github.com/honojs/middleware/tree/main/packages/zod-openapi
- Hono examples: https://github.com/honojs/examples
- Cloudflare Workers: https://developers.cloudflare.com/workers/
- Bun: https://bun.sh/
