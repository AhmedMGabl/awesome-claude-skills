---
name: deno-patterns
description: Deno runtime patterns covering permissions, HTTP servers with Deno.serve, KV database, Fresh framework, testing, npm compatibility, TypeScript-first development, and deployment to Deno Deploy.
---

# Deno Patterns

This skill should be used when building applications with Deno runtime. It covers permissions, HTTP servers, KV database, Fresh framework, testing, and deployment.

## When to Use This Skill

Use this skill when you need to:

- Build secure TypeScript-first applications
- Create HTTP servers with Deno.serve
- Use Deno KV for key-value storage
- Build web apps with Fresh framework
- Deploy to Deno Deploy edge network

## HTTP Server

```typescript
// Simple HTTP server
Deno.serve({ port: 8000 }, (req: Request): Response => {
  const url = new URL(req.url);

  if (url.pathname === "/api/hello") {
    return Response.json({ message: "Hello from Deno!" });
  }

  if (url.pathname === "/api/data" && req.method === "POST") {
    const body = await req.json();
    return Response.json({ received: body }, { status: 201 });
  }

  return new Response("Not Found", { status: 404 });
});

// With middleware pattern
function cors(handler: (req: Request) => Response | Promise<Response>) {
  return (req: Request) => {
    if (req.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE",
          "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
      });
    }
    const response = handler(req);
    if (response instanceof Response) {
      response.headers.set("Access-Control-Allow-Origin", "*");
    }
    return response;
  };
}

Deno.serve(cors(handler));
```

## Deno KV

```typescript
// Open KV database
const kv = await Deno.openKv();

// Set values
await kv.set(["users", "user-1"], {
  name: "Alice",
  email: "alice@example.com",
  createdAt: new Date().toISOString(),
});

// Get value
const result = await kv.get<User>(["users", "user-1"]);
if (result.value) {
  console.log(result.value.name); // "Alice"
}

// List with prefix
const users = kv.list<User>({ prefix: ["users"] });
for await (const entry of users) {
  console.log(entry.key, entry.value);
}

// Atomic operations
const res = await kv.atomic()
  .check({ key: ["users", "user-1"], versionstamp: result.versionstamp })
  .set(["users", "user-1"], { ...result.value, name: "Alice Updated" })
  .set(["users_by_email", "alice@example.com"], "user-1")
  .commit();

if (!res.ok) {
  console.error("Conflict: data was modified by another request");
}

// Enqueue background work
await kv.enqueue({ type: "send_email", to: "alice@example.com" });

kv.listenQueue(async (msg: { type: string; to: string }) => {
  if (msg.type === "send_email") {
    await sendEmail(msg.to);
  }
});
```

## Fresh Framework

```typescript
// routes/index.tsx
import { Handlers, PageProps } from "$fresh/server.ts";

interface Data {
  items: Item[];
}

export const handler: Handlers<Data> = {
  async GET(_req, ctx) {
    const items = await fetchItems();
    return ctx.render({ items });
  },
};

export default function Home({ data }: PageProps<Data>) {
  return (
    <div>
      <h1>Items</h1>
      {data.items.map((item) => (
        <div key={item.id}>{item.name}</div>
      ))}
    </div>
  );
}

// routes/api/items.ts - API route
export const handler: Handlers = {
  async GET() {
    const items = await fetchItems();
    return Response.json(items);
  },
  async POST(req) {
    const body = await req.json();
    const item = await createItem(body);
    return Response.json(item, { status: 201 });
  },
};

// islands/Counter.tsx - Interactive island
import { useSignal } from "@preact/signals";

export default function Counter() {
  const count = useSignal(0);
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => count.value++}>+</button>
    </div>
  );
}
```

## Permissions

```bash
# Run with specific permissions
deno run --allow-net=example.com --allow-read=./data server.ts

# Permission flags
# --allow-net          Network access
# --allow-read         File system read
# --allow-write        File system write
# --allow-env          Environment variables
# --allow-run          Subprocess execution
# --allow-ffi          Foreign function interface
# --allow-sys          System info access
# --deny-net=evil.com  Deny specific access
```

```typescript
// Request permissions at runtime
const status = await Deno.permissions.request({ name: "read", path: "./data" });
if (status.state === "granted") {
  const data = await Deno.readTextFile("./data/config.json");
}
```

## Testing

```typescript
// math_test.ts
import { assertEquals, assertThrows } from "https://deno.land/std/assert/mod.ts";

Deno.test("addition", () => {
  assertEquals(1 + 1, 2);
});

Deno.test("async operation", async () => {
  const result = await fetchData();
  assertEquals(result.status, "ok");
});

Deno.test({
  name: "with permissions",
  permissions: { read: true },
  fn() {
    const content = Deno.readTextFileSync("./test-data.txt");
    assertEquals(content, "hello");
  },
});

// Test steps
Deno.test("user workflow", async (t) => {
  await t.step("create user", async () => {
    const user = await createUser({ name: "Alice" });
    assertEquals(user.name, "Alice");
  });

  await t.step("update user", async () => {
    await updateUser("1", { name: "Bob" });
  });
});
```

```bash
# Run tests
deno test
deno test --filter "addition"
deno test --coverage
```

## npm Compatibility

```typescript
// Import npm packages with npm: specifier
import express from "npm:express@4";
import { z } from "npm:zod";
import chalk from "npm:chalk@5";

// Use in deno.json
{
  "imports": {
    "express": "npm:express@4",
    "zod": "npm:zod@3",
    "@hono/hono": "npm:hono@4"
  }
}
```

## Additional Resources

- Deno: https://deno.land/
- Deno KV: https://deno.com/kv
- Fresh framework: https://fresh.deno.dev/
