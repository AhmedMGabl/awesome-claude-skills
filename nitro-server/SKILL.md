---
name: nitro-server
description: Nitro server engine patterns covering event handlers, route rules, middleware, storage drivers, caching, scheduled tasks, WebSocket support, and deployment presets for Cloudflare, Vercel, Deno, and Node.js.
---

# Nitro Server

This skill should be used when building server applications with Nitro, the server engine behind Nuxt 3. It covers event handlers, storage, caching, tasks, and multi-platform deployment.

## When to Use This Skill

Use this skill when you need to:

- Build a standalone server with file-based routing
- Use cross-platform storage with KV, filesystem, or cloud drivers
- Cache responses and data with built-in caching layer
- Deploy to Cloudflare Workers, Vercel, Deno, or Node.js
- Schedule background tasks and cron jobs

## Event Handlers

```typescript
// routes/index.ts
export default defineEventHandler(() => {
  return { message: "Hello from Nitro!" };
});

// routes/users/index.get.ts
export default defineEventHandler(async (event) => {
  const query = getQuery(event);
  return { users: [], page: query.page ?? 1 };
});

// routes/users/index.post.ts
export default defineEventHandler(async (event) => {
  const body = await readBody(event);
  if (!body.name) {
    throw createError({ statusCode: 400, statusMessage: "Name is required" });
  }
  setResponseStatus(event, 201);
  return { id: "1", ...body };
});

// routes/users/[id].get.ts
export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, "id");
  return { id, name: "Alice" };
});

// routes/users/[...slug].get.ts  (catch-all)
export default defineEventHandler((event) => {
  const slug = getRouterParam(event, "slug");
  return { slug };
});
```

## Middleware

```typescript
// middleware/auth.ts
export default defineEventHandler(async (event) => {
  // Runs on every request
  const url = getRequestURL(event);
  if (!url.pathname.startsWith("/api")) return;

  const token = getHeader(event, "authorization")?.split(" ")[1];
  if (!token) {
    throw createError({ statusCode: 401, statusMessage: "Unauthorized" });
  }

  event.context.user = await verifyJWT(token);
});

// middleware/cors.ts
export default defineEventHandler((event) => {
  setResponseHeaders(event, {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
  });

  if (event.method === "OPTIONS") {
    setResponseStatus(event, 204);
    return "";
  }
});
```

## Storage

```typescript
// nitro.config.ts
export default defineNitroConfig({
  storage: {
    cache: { driver: "memory" },
    data: { driver: "fs", base: "./data" },
    redis: { driver: "redis", url: "redis://localhost:6379" },
  },
  devStorage: {
    cache: { driver: "memory" },
    data: { driver: "fs", base: "./.data" },
  },
});

// routes/api/kv.ts
export default defineEventHandler(async (event) => {
  const storage = useStorage("data");

  // Set value
  await storage.setItem("users:1", { name: "Alice", email: "alice@example.com" });

  // Get value
  const user = await storage.getItem("users:1");

  // List keys
  const keys = await storage.getKeys("users:");

  // Check existence
  const exists = await storage.hasItem("users:1");

  // Remove
  await storage.removeItem("users:1");

  return { user, keys, exists };
});
```

## Caching

```typescript
// routes/api/stats.get.ts
export default defineCachedEventHandler(
  async () => {
    // Expensive computation
    const stats = await computeStats();
    return stats;
  },
  {
    maxAge: 3600, // 1 hour
    staleMaxAge: 7200, // Serve stale for 2 hours while revalidating
    name: "stats",
    getKey: () => "global",
  },
);

// Cached utility function
// utils/cached.ts
export const getPopularItems = defineCachedFunction(
  async (category: string) => {
    return await db.query(`SELECT * FROM items WHERE category = ? ORDER BY views DESC LIMIT 10`, [category]);
  },
  {
    maxAge: 600, // 10 minutes
    name: "popular-items",
    getKey: (category) => category,
  },
);
```

## Scheduled Tasks

```typescript
// nitro.config.ts
export default defineNitroConfig({
  experimental: {
    tasks: true,
  },
  scheduledTasks: {
    "0 * * * *": ["cleanup:expired"],     // Every hour
    "*/5 * * * *": ["sync:data"],          // Every 5 minutes
    "0 0 * * *": ["reports:daily"],        // Daily at midnight
  },
});

// tasks/cleanup/expired.ts
export default defineTask({
  meta: {
    name: "cleanup:expired",
    description: "Remove expired sessions and tokens",
  },
  async run() {
    const storage = useStorage("data");
    const keys = await storage.getKeys("sessions:");

    let cleaned = 0;
    for (const key of keys) {
      const session = await storage.getItem(key);
      if (session && session.expiresAt < Date.now()) {
        await storage.removeItem(key);
        cleaned++;
      }
    }

    return { result: `Cleaned ${cleaned} expired sessions` };
  },
});
```

## WebSockets

```typescript
// routes/_ws.ts
export default defineWebSocketHandler({
  open(peer) {
    console.log(`Connected: ${peer.id}`);
    peer.subscribe("chat");
    peer.publish("chat", JSON.stringify({ type: "join", peerId: peer.id }));
  },
  message(peer, message) {
    const data = JSON.parse(message.text());
    peer.publish("chat", JSON.stringify({ ...data, from: peer.id }));
  },
  close(peer) {
    peer.publish("chat", JSON.stringify({ type: "leave", peerId: peer.id }));
  },
});
```

## Deployment Presets

```typescript
// nitro.config.ts
export default defineNitroConfig({
  // Cloudflare Workers
  preset: "cloudflare-worker",

  // Vercel
  // preset: "vercel-edge",

  // Deno Deploy
  // preset: "deno-deploy",

  // Node.js (default)
  // preset: "node-server",

  // Static (pre-rendered)
  // preset: "static",
});

// Build and run
// npx nitropack build
// node .output/server/index.mjs
```

## Additional Resources

- Nitro docs: https://nitro.build/
- Storage drivers: https://nitro.build/guide/storage
- Deployment: https://nitro.build/deploy
