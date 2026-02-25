---
name: deno-development
description: Deno runtime development covering permissions, deno.json configuration, HTTP servers with Deno.serve and Oak/Hono frameworks, file system operations, testing with Deno.test, built-in TypeScript support, npm compatibility, Fresh framework patterns, Deno Deploy, and Deno KV store.
---

# Deno Development

This skill should be used when building applications with the Deno runtime. It covers project configuration, HTTP servers, file system operations, testing, npm interoperability, the Fresh framework, deployment to Deno Deploy, and the Deno KV key-value store.

## When to Use This Skill

Use this skill when you need to:

- Set up Deno projects with deno.json configuration and import maps
- Build HTTP servers with Deno.serve, Oak, or Hono
- Perform file system operations with Deno's built-in APIs
- Write and run tests with Deno.test and BDD-style assertions
- Use npm packages and Node.js built-in modules from Deno
- Build full-stack applications with the Fresh framework
- Deploy applications to Deno Deploy
- Use Deno KV for persistent key-value storage

## Project Setup

### deno.json Configuration

```json
{
  "tasks": {
    "dev": "deno run --watch --allow-net --allow-read --allow-env main.ts",
    "start": "deno run --allow-net --allow-read --allow-env main.ts",
    "test": "deno test --allow-net --allow-read --allow-env",
    "lint": "deno lint",
    "fmt": "deno fmt",
    "check": "deno check main.ts"
  },
  "imports": {
    "@std/http": "jsr:@std/http@^1.0.0",
    "@std/assert": "jsr:@std/assert@^1.0.0",
    "@std/path": "jsr:@std/path@^1.0.0",
    "@std/fs": "jsr:@std/fs@^1.0.0",
    "@std/dotenv": "jsr:@std/dotenv@^0.225.0",
    "hono": "jsr:@hono/hono@^4.0.0",
    "oak": "jsr:@oak/oak@^17.0.0",
    "zod": "npm:zod@^3.23.0"
  },
  "compilerOptions": {
    "strict": true,
    "jsx": "react-jsx",
    "jsxImportSource": "preact"
  },
  "fmt": {
    "lineWidth": 100,
    "indentWidth": 2,
    "semiColons": true,
    "singleQuote": false
  },
  "lint": {
    "rules": {
      "exclude": ["no-explicit-any"]
    }
  }
}
```

### Project Structure

```
my-project/
├── deno.json           # Configuration, tasks, import map
├── main.ts             # Entry point
├── deps.ts             # (optional) Centralized dependency re-exports
├── src/
│   ├── routes/         # Route handlers
│   ├── middleware/      # Middleware functions
│   ├── services/       # Business logic
│   ├── models/         # Data models and types
│   └── utils/          # Shared utilities
├── static/             # Static files
└── tests/              # Test files
```

## Permissions

Deno runs with no permissions by default. Grant only what is needed.

```bash
# Individual permissions
deno run --allow-net main.ts                    # All network access
deno run --allow-net=api.example.com main.ts    # Specific host only
deno run --allow-read=. main.ts                 # Read current directory
deno run --allow-write=./data main.ts           # Write to ./data only
deno run --allow-env main.ts                    # Environment variables
deno run --allow-env=DATABASE_URL main.ts       # Specific env var
deno run --allow-run=git main.ts                # Run git subprocess
deno run --allow-ffi main.ts                    # Foreign function interface
deno run --allow-sys main.ts                    # System info

# Allow all (development only - never use in production)
deno run -A main.ts

# Deny specific permissions (overrides allow)
deno run --allow-net --deny-net=evil.com main.ts
```

## HTTP Server with Deno.serve

### Basic Server

```typescript
// main.ts
Deno.serve({ port: 8000 }, async (req: Request): Promise<Response> => {
  const url = new URL(req.url);

  if (url.pathname === "/health") {
    return Response.json({ status: "ok", timestamp: new Date().toISOString() });
  }

  if (url.pathname === "/api/greet" && req.method === "POST") {
    const body = await req.json();
    return Response.json({ message: `Hello, ${body.name}!` });
  }

  return new Response("Not Found", { status: 404 });
});
```

### Router Pattern with Deno.serve

```typescript
// router.ts
type Handler = (req: Request, params: Record<string, string>) => Promise<Response> | Response;

interface Route {
  method: string;
  pattern: URLPattern;
  handler: Handler;
}

class Router {
  private routes: Route[] = [];

  add(method: string, pathname: string, handler: Handler): void {
    this.routes.push({
      method,
      pattern: new URLPattern({ pathname }),
      handler,
    });
  }

  get(pathname: string, handler: Handler): void {
    this.add("GET", pathname, handler);
  }

  post(pathname: string, handler: Handler): void {
    this.add("POST", pathname, handler);
  }

  put(pathname: string, handler: Handler): void {
    this.add("PUT", pathname, handler);
  }

  delete(pathname: string, handler: Handler): void {
    this.add("DELETE", pathname, handler);
  }

  handle(req: Request): Promise<Response> | Response {
    for (const route of this.routes) {
      if (req.method !== route.method) continue;
      const match = route.pattern.exec(req.url);
      if (match) {
        const params = match.pathname.groups as Record<string, string>;
        return route.handler(req, params);
      }
    }
    return new Response("Not Found", { status: 404 });
  }
}

// Usage
const router = new Router();

router.get("/api/users", async () => {
  const users = await getUsers();
  return Response.json(users);
});

router.get("/api/users/:id", async (_req, params) => {
  const user = await getUserById(params.id);
  if (!user) return Response.json({ error: "Not found" }, { status: 404 });
  return Response.json(user);
});

router.post("/api/users", async (req) => {
  const body = await req.json();
  const user = await createUser(body);
  return Response.json(user, { status: 201 });
});

Deno.serve({ port: 8000 }, (req) => router.handle(req));
```

## Hono Framework

```typescript
// main.ts
import { Hono } from "hono";
import { cors } from "hono/cors";
import { logger } from "hono/logger";
import { jwt } from "hono/jwt";
import { z } from "zod";

const app = new Hono();

// Middleware
app.use("*", logger());
app.use("/api/*", cors({ origin: ["https://example.com"], credentials: true }));

// JWT-protected routes
const secret = Deno.env.get("JWT_SECRET") ?? "dev-secret";
app.use("/api/protected/*", jwt({ secret }));

// Health check
app.get("/health", (c) => c.json({ status: "ok" }));

// Validation with Zod
const CreateUserSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
});

app.post("/api/users", async (c) => {
  const body = await c.req.json();
  const result = CreateUserSchema.safeParse(body);
  if (!result.success) {
    return c.json({ error: "Validation failed", details: result.error.flatten() }, 400);
  }

  const user = { id: crypto.randomUUID(), ...result.data };
  return c.json(user, 201);
});

// Access JWT payload in protected routes
app.get("/api/protected/profile", (c) => {
  const payload = c.get("jwtPayload");
  return c.json({ userId: payload.sub, email: payload.email });
});

// Grouped routes
const posts = new Hono();
posts.get("/", (c) => c.json({ posts: [] }));
posts.get("/:id", (c) => c.json({ id: c.req.param("id") }));
posts.post("/", async (c) => {
  const body = await c.req.json();
  return c.json(body, 201);
});
app.route("/api/posts", posts);

Deno.serve({ port: 8000 }, app.fetch);
```

## Oak Framework

```typescript
// main.ts
import { Application, Router } from "oak";

const router = new Router();

router.get("/api/users", async (ctx) => {
  const users = await getUsers();
  ctx.response.body = users;
});

router.get("/api/users/:id", async (ctx) => {
  const user = await getUserById(ctx.params.id!);
  if (!user) {
    ctx.response.status = 404;
    ctx.response.body = { error: "User not found" };
    return;
  }
  ctx.response.body = user;
});

router.post("/api/users", async (ctx) => {
  const body = await ctx.request.body.json();
  const user = await createUser(body);
  ctx.response.status = 201;
  ctx.response.body = user;
});

const app = new Application();

// Logger middleware
app.use(async (ctx, next) => {
  const start = Date.now();
  await next();
  const ms = Date.now() - start;
  console.log(`${ctx.request.method} ${ctx.request.url.pathname} - ${ctx.response.status} ${ms}ms`);
});

// Error handling middleware
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    console.error(err);
    ctx.response.status = 500;
    ctx.response.body = { error: "Internal server error" };
  }
});

app.use(router.routes());
app.use(router.allowedMethods());

app.listen({ port: 8000 });
```

## File System Operations

```typescript
// Reading files
const text = await Deno.readTextFile("./config.json");
const config = JSON.parse(text);

const binary = await Deno.readFile("./image.png");

// Writing files
await Deno.writeTextFile("./output.json", JSON.stringify(data, null, 2));
await Deno.writeFile("./output.bin", new Uint8Array([0, 1, 2, 3]));

// Append to file
await Deno.writeTextFile("./log.txt", "new entry\n", { append: true });

// File info
const stat = await Deno.stat("./file.txt");
console.log(stat.size, stat.isFile, stat.isDirectory, stat.mtime);

// Check if file exists
async function fileExists(path: string): Promise<boolean> {
  try {
    await Deno.stat(path);
    return true;
  } catch (e) {
    if (e instanceof Deno.errors.NotFound) return false;
    throw e;
  }
}

// Directory operations
await Deno.mkdir("./data/nested", { recursive: true });
await Deno.remove("./temp", { recursive: true });
await Deno.rename("./old.txt", "./new.txt");
await Deno.copyFile("./source.txt", "./dest.txt");

// Read directory contents
for await (const entry of Deno.readDir("./src")) {
  console.log(entry.name, entry.isFile, entry.isDirectory, entry.isSymlink);
}

// Walk directory tree (recursive)
import { walk } from "@std/fs";

for await (const entry of walk("./src", { exts: [".ts"], skip: [/node_modules/] })) {
  console.log(entry.path);
}

// Streaming file I/O
using file = await Deno.open("./large-file.csv", { read: true });
const reader = file.readable.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  processChunk(value);
}

// Watch for file changes
const watcher = Deno.watchFs("./src");
for await (const event of watcher) {
  console.log(event.kind, event.paths);
}
```

## Testing

### Basic Tests with Deno.test

```typescript
// user_test.ts
import { assertEquals, assertRejects, assertThrows } from "@std/assert";

Deno.test("addition works", () => {
  assertEquals(1 + 1, 2);
});

Deno.test("async operation", async () => {
  const result = await fetchData();
  assertEquals(result.status, "ok");
});

// Test with setup/teardown
Deno.test({
  name: "database operation",
  async fn() {
    const db = await connectToTestDb();
    try {
      await db.insert({ name: "Alice" });
      const user = await db.findByName("Alice");
      assertEquals(user?.name, "Alice");
    } finally {
      await db.close();
    }
  },
  // Sanitizers control resource leak detection
  sanitizeResources: false,
  sanitizeOps: false,
});

// Nested test steps
Deno.test("user service", async (t) => {
  const service = new UserService();

  await t.step("creates a user", async () => {
    const user = await service.create({ name: "Alice", email: "alice@test.com" });
    assertEquals(user.name, "Alice");
  });

  await t.step("rejects duplicate email", async () => {
    await assertRejects(
      () => service.create({ name: "Bob", email: "alice@test.com" }),
      Error,
      "Email already exists",
    );
  });

  await t.step("lists users", async () => {
    const users = await service.findAll();
    assertEquals(users.length, 1);
  });
});
```

### BDD-Style Testing

```typescript
// user_bdd_test.ts
import { describe, it, beforeEach, afterEach, beforeAll, afterAll } from "@std/testing/bdd";
import { assertEquals, assertExists, assertStringIncludes } from "@std/assert";
import { stub, assertSpyCalls } from "@std/testing/mock";

describe("UserService", () => {
  let service: UserService;

  beforeEach(() => {
    service = new UserService();
  });

  afterEach(async () => {
    await service.cleanup();
  });

  describe("create()", () => {
    it("should create a user with valid data", async () => {
      const user = await service.create({ name: "Alice", email: "alice@test.com" });
      assertExists(user.id);
      assertEquals(user.name, "Alice");
    });

    it("should reject invalid email", async () => {
      try {
        await service.create({ name: "Alice", email: "not-an-email" });
        throw new Error("Expected error");
      } catch (err) {
        assertStringIncludes((err as Error).message, "Invalid email");
      }
    });
  });

  describe("findById()", () => {
    it("should return null for nonexistent user", async () => {
      const user = await service.findById("nonexistent-id");
      assertEquals(user, null);
    });
  });
});

// Mocking with stubs
describe("API client", () => {
  it("should retry on failure", async () => {
    const fetchStub = stub(globalThis, "fetch", () => {
      return Promise.resolve(new Response("OK", { status: 200 }));
    });

    try {
      const result = await apiClient.get("/data");
      assertEquals(result, "OK");
      assertSpyCalls(fetchStub, 1);
    } finally {
      fetchStub.restore();
    }
  });
});
```

### Testing HTTP Handlers

```typescript
// server_test.ts
import { assertEquals } from "@std/assert";

// Test Deno.serve handlers directly
Deno.test("GET /health returns ok", async () => {
  const req = new Request("http://localhost/health");
  const res = await handler(req);
  assertEquals(res.status, 200);
  const body = await res.json();
  assertEquals(body.status, "ok");
});

Deno.test("POST /api/users creates user", async () => {
  const req = new Request("http://localhost/api/users", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: "Alice", email: "alice@test.com" }),
  });
  const res = await handler(req);
  assertEquals(res.status, 201);
});

// Run tests
// deno test --allow-net --allow-read --allow-env
```

### Running Tests

```bash
# Run all tests
deno test

# Run with permissions
deno test --allow-net --allow-read --allow-env

# Run specific file
deno test tests/user_test.ts

# Run matching filter
deno test --filter "UserService"

# Watch mode
deno test --watch

# Coverage report
deno test --coverage=coverage/
deno coverage coverage/ --lcov > coverage.lcov

# Parallel execution (default)
deno test --parallel
```

## TypeScript Support

Deno supports TypeScript natively with no configuration required. No `tsconfig.json`, no build step, no `tsc`.

```typescript
// Works out of the box - no setup needed
interface User {
  id: string;
  name: string;
  email: string;
  createdAt: Date;
}

function greet(user: User): string {
  return `Hello, ${user.name}!`;
}

// Type checking without running
// deno check main.ts
// deno check --all  (includes remote modules)

// Compiler options in deno.json (optional, for JSX or strict settings)
// See deno.json example in Project Setup above
```

## npm Compatibility and Node.js Imports

### Using npm Packages

```typescript
// Import npm packages with npm: specifier
import { z } from "npm:zod@^3.23.0";
import express from "npm:express@^4.18.0";
import pg from "npm:pg@^8.12.0";

// Or map in deno.json imports
// "zod": "npm:zod@^3.23.0"
import { z } from "zod";

// Using npm packages works with full TypeScript support
const schema = z.object({
  name: z.string(),
  age: z.number().min(0),
});

type Person = z.infer<typeof schema>;
```

### Node.js Built-in Modules

```typescript
// Import Node.js built-ins with node: prefix
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { EventEmitter } from "node:events";
import { Buffer } from "node:buffer";
import process from "node:process";
import { createHash } from "node:crypto";

// Example: hashing with Node.js crypto
function hashPassword(password: string): string {
  return createHash("sha256").update(password).digest("hex");
}

// Example: using EventEmitter
class AppEvents extends EventEmitter {}
const events = new AppEvents();
events.on("user:created", (user) => {
  console.log("New user:", user.name);
});
```

## Fresh Framework

Fresh is a full-stack web framework for Deno with islands architecture, server-side rendering, and zero client-side JavaScript by default.

### Project Setup

```bash
# Create a new Fresh project
deno run -A -r https://fresh.deno.dev my-app
cd my-app
deno task dev
```

### Project Structure

```
my-app/
├── deno.json
├── dev.ts              # Development entry point
├── main.ts             # Production entry point
├── fresh.gen.ts        # Auto-generated manifest
├── routes/
│   ├── _app.tsx        # App wrapper (layout)
│   ├── _layout.tsx     # Shared layout
│   ├── _middleware.ts  # Route middleware
│   ├── index.tsx       # Home page (/)
│   ├── about.tsx       # Static page (/about)
│   ├── api/
│   │   └── users.ts    # API route (/api/users)
│   └── users/
│       ├── index.tsx   # /users
│       └── [id].tsx    # /users/:id
├── islands/            # Interactive client-side components
│   ├── Counter.tsx
│   └── SearchBar.tsx
├── components/         # Server-side components (no JS shipped)
│   ├── Header.tsx
│   └── Footer.tsx
└── static/             # Static assets
    ├── favicon.ico
    └── styles.css
```

### Routes

```typescript
// routes/index.tsx - Server-rendered page
import { Handlers, PageProps } from "$fresh/server.ts";
import { Counter } from "../islands/Counter.tsx";

interface Data {
  posts: Array<{ id: string; title: string }>;
}

export const handler: Handlers<Data> = {
  async GET(_req, ctx) {
    const posts = await fetchPosts();
    return ctx.render({ posts });
  },
};

export default function HomePage({ data }: PageProps<Data>) {
  return (
    <div>
      <h1>Latest Posts</h1>
      <ul>
        {data.posts.map((post) => (
          <li key={post.id}>
            <a href={`/posts/${post.id}`}>{post.title}</a>
          </li>
        ))}
      </ul>
      {/* Island: only this component ships JS to the browser */}
      <Counter start={0} />
    </div>
  );
}

// routes/users/[id].tsx - Dynamic route
export const handler: Handlers = {
  async GET(_req, ctx) {
    const user = await getUserById(ctx.params.id);
    if (!user) return ctx.renderNotFound();
    return ctx.render({ user });
  },

  async PUT(req, ctx) {
    const body = await req.json();
    const user = await updateUser(ctx.params.id, body);
    return new Response(JSON.stringify(user), {
      headers: { "Content-Type": "application/json" },
    });
  },
};

export default function UserPage({ data }: PageProps<{ user: User }>) {
  return (
    <div>
      <h1>{data.user.name}</h1>
      <p>{data.user.email}</p>
    </div>
  );
}
```

### API Routes

```typescript
// routes/api/users.ts
import { Handlers } from "$fresh/server.ts";

export const handler: Handlers = {
  async GET(req) {
    const url = new URL(req.url);
    const page = Number(url.searchParams.get("page") ?? "1");
    const limit = Number(url.searchParams.get("limit") ?? "10");

    const users = await getUsers({ page, limit });
    return Response.json(users);
  },

  async POST(req) {
    const body = await req.json();
    const user = await createUser(body);
    return Response.json(user, { status: 201 });
  },
};
```

### Islands (Interactive Components)

```typescript
// islands/Counter.tsx - Ships JavaScript to the browser
import { useSignal } from "@preact/signals";

interface Props {
  start: number;
}

export default function Counter({ start }: Props) {
  const count = useSignal(start);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => count.value--}>-</button>
      <button onClick={() => count.value++}>+</button>
    </div>
  );
}

// islands/SearchBar.tsx - Client-side search with debounce
import { useSignal } from "@preact/signals";
import { useEffect, useRef } from "preact/hooks";

export default function SearchBar() {
  const query = useSignal("");
  const results = useSignal<string[]>([]);
  const timer = useRef<number | null>(null);

  useEffect(() => {
    if (timer.current) clearTimeout(timer.current);
    if (!query.value) {
      results.value = [];
      return;
    }

    timer.current = setTimeout(async () => {
      const res = await fetch(`/api/search?q=${encodeURIComponent(query.value)}`);
      results.value = await res.json();
    }, 300);
  }, [query.value]);

  return (
    <div>
      <input
        type="text"
        value={query}
        onInput={(e) => (query.value = (e.target as HTMLInputElement).value)}
        placeholder="Search..."
      />
      <ul>
        {results.value.map((item) => <li key={item}>{item}</li>)}
      </ul>
    </div>
  );
}
```

### Middleware

```typescript
// routes/_middleware.ts
import { FreshContext } from "$fresh/server.ts";

export async function handler(req: Request, ctx: FreshContext) {
  // Logging
  const start = Date.now();
  const res = await ctx.next();
  const ms = Date.now() - start;
  console.log(`${req.method} ${new URL(req.url).pathname} ${res.status} ${ms}ms`);

  // Add security headers
  res.headers.set("X-Content-Type-Options", "nosniff");
  res.headers.set("X-Frame-Options", "DENY");

  return res;
}

// routes/api/_middleware.ts - Auth middleware for API routes
export async function handler(req: Request, ctx: FreshContext) {
  const token = req.headers.get("Authorization")?.replace("Bearer ", "");
  if (!token) {
    return Response.json({ error: "Unauthorized" }, { status: 401 });
  }

  try {
    const payload = await verifyToken(token);
    ctx.state.user = payload;
    return ctx.next();
  } catch {
    return Response.json({ error: "Invalid token" }, { status: 401 });
  }
}
```

## Deno Deploy

Deno Deploy is a globally distributed platform for serverless Deno applications.

### Deployment

```bash
# Install deployctl
deno install -Arf jsr:@deno/deployctl

# Deploy from local
deployctl deploy --project=my-project main.ts

# Deploy with environment variables
deployctl deploy --project=my-project --env-file=.env main.ts

# Deploy from GitHub (recommended for production)
# Link your repository at https://dash.deno.com and set the entry point
```

### Deploy-Compatible Server

```typescript
// main.ts - Works both locally and on Deno Deploy
import "@std/dotenv/load";

const kv = await Deno.openKv(); // Uses Deploy's managed KV in production

Deno.serve(async (req: Request): Promise<Response> => {
  const url = new URL(req.url);

  if (url.pathname === "/api/visits") {
    const key = ["visits", "total"];
    const entry = await kv.get<number>(key);
    const count = (entry.value ?? 0) + 1;
    await kv.set(key, count);
    return Response.json({ visits: count });
  }

  if (url.pathname === "/") {
    return new Response("<h1>Hello from Deno Deploy</h1>", {
      headers: { "content-type": "text/html" },
    });
  }

  return new Response("Not Found", { status: 404 });
});
```

### Environment Variables on Deploy

```typescript
// Access environment variables (set in Deno Deploy dashboard)
const databaseUrl = Deno.env.get("DATABASE_URL");
const apiKey = Deno.env.get("API_KEY");

// Environment-aware configuration
const isDenoDeploy = Deno.env.get("DENO_DEPLOYMENT_ID") !== undefined;
const port = isDenoDeploy ? 8000 : Number(Deno.env.get("PORT") ?? "8000");
```

## Deno KV

Deno KV is a built-in key-value database that works locally (backed by SQLite) and on Deno Deploy (globally replicated).

### Basic Operations

```typescript
const kv = await Deno.openKv();

// Set a value
await kv.set(["users", "user-123"], {
  name: "Alice",
  email: "alice@example.com",
  createdAt: new Date(),
});

// Get a value
const entry = await kv.get<User>(["users", "user-123"]);
if (entry.value) {
  console.log(entry.value.name); // "Alice"
  console.log(entry.versionstamp); // Optimistic concurrency token
}

// Delete a value
await kv.delete(["users", "user-123"]);

// List by prefix
const iter = kv.list<User>({ prefix: ["users"] });
const users: User[] = [];
for await (const entry of iter) {
  users.push(entry.value);
}

// List with limit and cursor (pagination)
const page = kv.list<User>({ prefix: ["users"] }, { limit: 10 });
const firstPage: User[] = [];
let cursor: string | undefined;
for await (const entry of page) {
  firstPage.push(entry.value);
  cursor = page.cursor;
}
// Use cursor for next page
const nextPage = kv.list<User>({ prefix: ["users"] }, { limit: 10, cursor });
```

### Atomic Operations

```typescript
const kv = await Deno.openKv();

// Atomic transaction with optimistic concurrency
const userKey = ["users", "user-123"];
const entry = await kv.get<User>(userKey);

const result = await kv.atomic()
  .check(entry) // Fails if value changed since read
  .set(userKey, { ...entry.value!, name: "Alice Updated" })
  .commit();

if (!result.ok) {
  console.log("Conflict detected, retry the operation");
}

// Atomic counter increment
async function incrementCounter(key: Deno.KvKey): Promise<number> {
  while (true) {
    const entry = await kv.get<number>(key);
    const newValue = (entry.value ?? 0) + 1;
    const result = await kv.atomic()
      .check(entry)
      .set(key, newValue)
      .commit();
    if (result.ok) return newValue;
    // Retry on conflict
  }
}

// Multi-key atomic operations (secondary indexes)
async function createUser(user: User): Promise<void> {
  const byId = ["users", user.id];
  const byEmail = ["users_by_email", user.email];

  const result = await kv.atomic()
    .check({ key: byId, versionstamp: null })    // Ensure ID doesn't exist
    .check({ key: byEmail, versionstamp: null })  // Ensure email doesn't exist
    .set(byId, user)
    .set(byEmail, user)
    .commit();

  if (!result.ok) {
    throw new Error("User already exists");
  }
}
```

### KV Watch (Real-time Updates)

```typescript
const kv = await Deno.openKv();

// Watch for changes to specific keys
const stream = kv.watch<[User, number]>([
  ["users", "user-123"],
  ["stats", "total-users"],
]);

for await (const entries of stream) {
  const [userEntry, statsEntry] = entries;
  console.log("User:", userEntry.value);
  console.log("Total users:", statsEntry.value);
}
```

### KV Queues

```typescript
const kv = await Deno.openKv();

// Enqueue a message
await kv.enqueue(
  { type: "email", to: "alice@example.com", subject: "Welcome!" },
  { delay: 5000 }, // Optional delay in milliseconds
);

// Listen for messages
kv.listenQueue(async (msg: unknown) => {
  const message = msg as { type: string; to: string; subject: string };
  if (message.type === "email") {
    await sendEmail(message.to, message.subject);
  }
});
```

### CRUD Service with KV

```typescript
// services/user_service.ts
interface User {
  id: string;
  name: string;
  email: string;
  createdAt: string;
}

export class UserService {
  constructor(private kv: Deno.Kv) {}

  async create(input: { name: string; email: string }): Promise<User> {
    const user: User = {
      id: crypto.randomUUID(),
      name: input.name,
      email: input.email,
      createdAt: new Date().toISOString(),
    };

    const result = await this.kv.atomic()
      .check({ key: ["users_by_email", user.email], versionstamp: null })
      .set(["users", user.id], user)
      .set(["users_by_email", user.email], user)
      .commit();

    if (!result.ok) throw new Error("Email already exists");
    return user;
  }

  async findById(id: string): Promise<User | null> {
    const entry = await this.kv.get<User>(["users", id]);
    return entry.value;
  }

  async findByEmail(email: string): Promise<User | null> {
    const entry = await this.kv.get<User>(["users_by_email", email]);
    return entry.value;
  }

  async findAll(options?: { limit?: number; cursor?: string }): Promise<{
    users: User[];
    cursor?: string;
  }> {
    const iter = this.kv.list<User>(
      { prefix: ["users"] },
      { limit: options?.limit ?? 20, cursor: options?.cursor },
    );

    const users: User[] = [];
    for await (const entry of iter) {
      users.push(entry.value);
    }

    return { users, cursor: iter.cursor || undefined };
  }

  async update(id: string, input: Partial<Pick<User, "name" | "email">>): Promise<User> {
    const entry = await this.kv.get<User>(["users", id]);
    if (!entry.value) throw new Error("User not found");

    const updated = { ...entry.value, ...input };
    const atomic = this.kv.atomic().check(entry).set(["users", id], updated);

    // Update email index if email changed
    if (input.email && input.email !== entry.value.email) {
      atomic
        .delete(["users_by_email", entry.value.email])
        .set(["users_by_email", input.email], updated);
    }

    const result = await atomic.commit();
    if (!result.ok) throw new Error("Conflict, retry");
    return updated;
  }

  async delete(id: string): Promise<void> {
    const entry = await this.kv.get<User>(["users", id]);
    if (!entry.value) return;

    await this.kv.atomic()
      .check(entry)
      .delete(["users", id])
      .delete(["users_by_email", entry.value.email])
      .commit();
  }
}
```

## Useful CLI Commands

```bash
# Run a script
deno run main.ts

# Run with watch mode (restarts on file changes)
deno run --watch main.ts

# Type check without running
deno check main.ts

# Format code
deno fmt
deno fmt --check          # Check only, no write

# Lint code
deno lint

# Compile to single executable
deno compile --allow-net --allow-read main.ts --output my-app

# Show dependency tree
deno info main.ts

# Cache dependencies
deno cache main.ts

# REPL
deno repl

# Benchmark
deno bench bench.ts

# Generate documentation
deno doc main.ts
```

## Additional Resources

- Deno Manual: https://docs.deno.com/
- Deno Standard Library: https://jsr.io/@std
- Fresh Framework: https://fresh.deno.dev/
- Deno Deploy: https://deno.com/deploy
- Deno KV: https://docs.deno.com/deploy/kv/manual/
- JSR (JavaScript Registry): https://jsr.io/
- Oak Framework: https://jsr.io/@oak/oak
- Hono Framework: https://hono.dev/
