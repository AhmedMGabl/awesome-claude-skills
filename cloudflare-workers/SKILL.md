---
name: cloudflare-workers
description: Cloudflare Workers and edge computing covering Workers runtime, Hono framework, D1 database, R2 storage, KV store, Durable Objects, Queues, Cron Triggers, middleware patterns, authentication at the edge, and deployment with Wrangler.
---

# Cloudflare Workers & Edge Computing

This skill should be used when building applications that run at the edge with Cloudflare Workers. It covers the Workers runtime, storage options, and edge-first architecture patterns.

## When to Use This Skill

Use this skill when you need to:

- Build edge functions with Cloudflare Workers
- Use D1 (SQLite at the edge), R2 (object storage), or KV
- Implement Durable Objects for stateful edge computing
- Create API backends with Hono on Workers
- Deploy globally distributed applications
- Build middleware, auth, and caching at the edge

## Project Setup

```toml
# wrangler.toml
name = "my-api"
main = "src/index.ts"
compatibility_date = "2024-12-01"

[vars]
ENVIRONMENT = "production"

[[d1_databases]]
binding = "DB"
database_name = "my-db"
database_id = "xxx-xxx-xxx"

[[r2_buckets]]
binding = "STORAGE"
bucket_name = "my-bucket"

[[kv_namespaces]]
binding = "CACHE"
id = "xxx-xxx-xxx"

[durable_objects]
bindings = [{ name = "COUNTER", class_name = "Counter" }]

[[migrations]]
tag = "v1"
new_classes = ["Counter"]
```

## Hono API on Workers

```typescript
// src/index.ts
import { Hono } from "hono";
import { cors } from "hono/cors";
import { jwt } from "hono/jwt";
import { logger } from "hono/logger";
import { zValidator } from "@hono/zod-validator";
import { z } from "zod";

type Bindings = {
  DB: D1Database;
  STORAGE: R2Bucket;
  CACHE: KVNamespace;
  JWT_SECRET: string;
};

const app = new Hono<{ Bindings: Bindings }>();

// Middleware
app.use("*", logger());
app.use("/api/*", cors({ origin: ["https://example.com"], credentials: true }));
app.use("/api/protected/*", jwt({ secret: (c) => c.env.JWT_SECRET }));

// Health check
app.get("/health", (c) => c.json({ status: "ok", region: c.req.raw.cf?.colo }));

// CRUD with D1
const createPostSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().min(1),
});

app.get("/api/posts", async (c) => {
  const { results } = await c.env.DB.prepare(
    "SELECT id, title, created_at FROM posts ORDER BY created_at DESC LIMIT 50"
  ).all();
  return c.json(results);
});

app.post("/api/posts", zValidator("json", createPostSchema), async (c) => {
  const { title, content } = c.req.valid("json");
  const id = crypto.randomUUID();
  await c.env.DB.prepare("INSERT INTO posts (id, title, content) VALUES (?, ?, ?)")
    .bind(id, title, content)
    .run();
  return c.json({ id, title }, 201);
});

app.get("/api/posts/:id", async (c) => {
  const id = c.req.param("id");
  // Check cache first
  const cached = await c.env.CACHE.get(`post:${id}`);
  if (cached) return c.json(JSON.parse(cached));

  const post = await c.env.DB.prepare("SELECT * FROM posts WHERE id = ?").bind(id).first();
  if (!post) return c.notFound();

  // Cache for 5 minutes
  await c.env.CACHE.put(`post:${id}`, JSON.stringify(post), { expirationTtl: 300 });
  return c.json(post);
});

export default app;
```

## D1 Database (SQLite at Edge)

```typescript
// Database migrations
// migrations/0001_create_tables.sql
CREATE TABLE IF NOT EXISTS posts (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  author_id TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_posts_author ON posts(author_id);
CREATE INDEX idx_posts_created ON posts(created_at DESC);

// Batch operations
async function batchInsert(db: D1Database, posts: Post[]) {
  const stmt = db.prepare("INSERT INTO posts (id, title, content) VALUES (?, ?, ?)");
  const batch = posts.map((p) => stmt.bind(p.id, p.title, p.content));
  return db.batch(batch); // Executes all in single round-trip
}

// Apply migrations: npx wrangler d1 migrations apply my-db
```

## R2 Object Storage

```typescript
// File upload
app.post("/api/upload", async (c) => {
  const formData = await c.req.formData();
  const file = formData.get("file") as File;
  if (!file) return c.json({ error: "No file" }, 400);

  const key = `uploads/${Date.now()}-${file.name}`;
  await c.env.STORAGE.put(key, file.stream(), {
    httpMetadata: { contentType: file.type },
    customMetadata: { originalName: file.name },
  });

  return c.json({ key, url: `/api/files/${key}` }, 201);
});

// File download with range support
app.get("/api/files/*", async (c) => {
  const key = c.req.path.replace("/api/files/", "");
  const object = await c.env.STORAGE.get(key, {
    range: c.req.raw.headers,
    onlyIf: c.req.raw.headers,
  });
  if (!object) return c.notFound();

  const headers = new Headers();
  object.writeHttpMetadata(headers);
  headers.set("etag", object.httpEtag);
  headers.set("cache-control", "public, max-age=31536000, immutable");

  return new Response(object.body, { headers });
});
```

## Durable Objects (Stateful Edge)

```typescript
// Real-time counter / rate limiter
export class Counter implements DurableObject {
  private count = 0;
  private storage: DurableObjectStorage;

  constructor(state: DurableObjectState) {
    this.storage = state.storage;
    state.blockConcurrencyWhile(async () => {
      this.count = (await this.storage.get<number>("count")) ?? 0;
    });
  }

  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/increment") {
      this.count++;
      await this.storage.put("count", this.count);
      return Response.json({ count: this.count });
    }

    if (url.pathname === "/get") {
      return Response.json({ count: this.count });
    }

    return new Response("Not found", { status: 404 });
  }
}

// Usage from Worker
app.post("/api/counter/:name/increment", async (c) => {
  const id = c.env.COUNTER.idFromName(c.req.param("name"));
  const stub = c.env.COUNTER.get(id);
  const res = await stub.fetch(new Request("https://dummy/increment"));
  return c.json(await res.json());
});
```

## KV Cache Patterns

```typescript
// Cache-aside pattern with stale-while-revalidate
async function cachedQuery<T>(
  kv: KVNamespace,
  key: string,
  fetcher: () => Promise<T>,
  ttl = 300,
): Promise<T> {
  const { value, metadata } = await kv.getWithMetadata<T>(key, "json");

  if (value) {
    // Check if stale (past soft TTL) — revalidate in background
    const meta = metadata as { softExpiry?: number } | null;
    if (meta?.softExpiry && Date.now() > meta.softExpiry) {
      // Stale — return cached but refresh in background (non-blocking)
      void fetcher().then((fresh) =>
        kv.put(key, JSON.stringify(fresh), {
          expirationTtl: ttl * 2,
          metadata: { softExpiry: Date.now() + ttl * 1000 },
        }),
      );
    }
    return value;
  }

  const fresh = await fetcher();
  await kv.put(key, JSON.stringify(fresh), {
    expirationTtl: ttl * 2,
    metadata: { softExpiry: Date.now() + ttl * 1000 },
  });
  return fresh;
}
```

## Cron Triggers

```typescript
// Scheduled tasks
export default {
  async scheduled(event: ScheduledEvent, env: Bindings, ctx: ExecutionContext) {
    switch (event.cron) {
      case "0 * * * *": // Hourly
        ctx.waitUntil(cleanupExpiredSessions(env));
        break;
      case "0 0 * * *": // Daily
        ctx.waitUntil(generateDailyReport(env));
        break;
    }
  },

  async fetch(request: Request, env: Bindings, ctx: ExecutionContext) {
    return app.fetch(request, env, ctx);
  },
};
```

```toml
# wrangler.toml — add triggers
[triggers]
crons = ["0 * * * *", "0 0 * * *"]
```

## Deployment

```bash
# Development
npx wrangler dev

# Deploy to production
npx wrangler deploy

# Create D1 database
npx wrangler d1 create my-db

# Run D1 migrations
npx wrangler d1 migrations apply my-db --remote

# Create KV namespace
npx wrangler kv namespace create CACHE

# Create R2 bucket
npx wrangler r2 bucket create my-bucket
```

## Additional Resources

- Cloudflare Workers Docs: https://developers.cloudflare.com/workers/
- D1 Documentation: https://developers.cloudflare.com/d1/
- Hono Framework: https://hono.dev/
- Wrangler CLI: https://developers.cloudflare.com/workers/wrangler/
