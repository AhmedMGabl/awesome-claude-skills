---
name: cloudflare-workers
description: This skill should be used when building edge applications with Cloudflare Workers, covering Wrangler setup, request handling, KV namespace storage, D1 database, R2 object storage, Durable Objects, Hono framework integration, cron triggers, environment bindings, and deployment workflows.
---

# Cloudflare Workers Development

## When to Use This Skill

- Set up Worker projects with Wrangler and configure environment bindings
- Handle HTTP requests and build APIs with Hono on Workers
- Use KV, D1, R2, or Durable Objects for storage
- Configure cron triggers and deploy globally

## Project Setup

```bash
npm create cloudflare@latest my-worker -- --template hello-world --ts
cd my-worker && npm install hono @hono/zod-validator zod
```

```toml
# wrangler.toml
name = "my-worker"
main = "src/index.ts"
compatibility_date = "2024-12-01"
[vars]
ENVIRONMENT = "production"
[[kv_namespaces]]
binding = "CACHE"
id = "abc123"
[[d1_databases]]
binding = "DB"
database_name = "my-db"
database_id = "def456"
[[r2_buckets]]
binding = "STORAGE"
bucket_name = "my-bucket"
[durable_objects]
bindings = [{ name = "COUNTER", class_name = "Counter" }]
[[migrations]]
tag = "v1"
new_classes = ["Counter"]
[triggers]
crons = ["0 * * * *", "0 0 * * *"]
```

## Request Handling with Typed Bindings

```typescript
export interface Env {
  CACHE: KVNamespace; DB: D1Database; STORAGE: R2Bucket;
  COUNTER: DurableObjectNamespace; API_KEY: string; // set via `wrangler secret put`
}
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    if (url.pathname === "/health")
      return Response.json({ status: "ok", colo: (request as any).cf?.colo });
    if (url.pathname === "/api/data") {
      const cached = await env.CACHE.get("data-key");
      if (cached) return Response.json(JSON.parse(cached));
      const { results } = await env.DB.prepare("SELECT * FROM items LIMIT 50").all();
      ctx.waitUntil(env.CACHE.put("data-key", JSON.stringify(results), { expirationTtl: 300 }));
      return Response.json(results);
    }
    return new Response("Not Found", { status: 404 });
  },
};
```

## Hono Framework on Workers

```typescript
import { Hono } from "hono";
import { cors } from "hono/cors";
import { jwt } from "hono/jwt";
import { zValidator } from "@hono/zod-validator";
import { z } from "zod";
type Bindings = { DB: D1Database; CACHE: KVNamespace; STORAGE: R2Bucket; JWT_SECRET: string };
const app = new Hono<{ Bindings: Bindings }>();
app.use("/api/*", cors({ origin: ["https://example.com"], credentials: true }));
app.use("/api/protected/*", jwt({ secret: (c) => c.env.JWT_SECRET }));
const PostSchema = z.object({ title: z.string().min(1).max(200), content: z.string().min(1) });
app.get("/api/posts", async (c) => {
  const { results } = await c.env.DB.prepare(
    "SELECT id, title, created_at FROM posts ORDER BY created_at DESC LIMIT 50").all();
  return c.json(results);
});
app.post("/api/posts", zValidator("json", PostSchema), async (c) => {
  const { title, content } = c.req.valid("json");
  const id = crypto.randomUUID();
  await c.env.DB.prepare("INSERT INTO posts (id, title, content) VALUES (?, ?, ?)")
    .bind(id, title, content).run();
  return c.json({ id, title }, 201);
});
export default app;
```

## KV Namespace Storage

```typescript
await env.CACHE.put("key", JSON.stringify(data), { expirationTtl: 3600, metadata: { ts: Date.now() } });
const { value, metadata } = await env.CACHE.getWithMetadata("key", "json");
const list = await env.CACHE.list({ prefix: "session:", limit: 100 });
await env.CACHE.delete("key");
```

## D1 Database (SQLite at the Edge)

```typescript
// migrations/0001_init.sql: CREATE TABLE posts (id TEXT PRIMARY KEY, title TEXT NOT NULL, ...);
const stmt = env.DB.prepare("INSERT INTO posts (id, title, content) VALUES (?, ?, ?)");
await env.DB.batch([stmt.bind("a", "Title A", "Body"), stmt.bind("b", "Title B", "Body")]);
const post = await env.DB.prepare("SELECT * FROM posts WHERE id = ?").bind("a").first();
```

## R2 Object Storage

```typescript
app.post("/api/upload", async (c) => {
  const file = (await c.req.formData()).get("file") as File;
  if (!file) return c.json({ error: "No file" }, 400);
  const key = `uploads/${Date.now()}-${file.name}`;
  await c.env.STORAGE.put(key, file.stream(), {
    httpMetadata: { contentType: file.type }, customMetadata: { originalName: file.name },
  });
  return c.json({ key }, 201);
});
app.get("/api/files/*", async (c) => {
  const obj = await c.env.STORAGE.get(c.req.path.replace("/api/files/", ""));
  if (!obj) return c.notFound();
  const headers = new Headers();
  obj.writeHttpMetadata(headers);
  headers.set("etag", obj.httpEtag);
  return new Response(obj.body, { headers });
});
```

## Durable Objects

```typescript
export class Counter implements DurableObject {
  private count = 0;
  constructor(private state: DurableObjectState) {
    state.blockConcurrencyWhile(async () => {
      this.count = (await this.state.storage.get<number>("count")) ?? 0;
    });
  }
  async fetch(request: Request): Promise<Response> {
    if (new URL(request.url).pathname === "/increment") {
      this.count++;
      await this.state.storage.put("count", this.count);
    }
    return Response.json({ count: this.count });
  }
}
app.post("/api/counter/:name/increment", async (c) => {
  const id = c.env.COUNTER.idFromName(c.req.param("name"));
  return c.env.COUNTER.get(id).fetch(new Request("https://do/increment"));
});
```

## Cron Triggers

```typescript
export default {
  fetch: app.fetch,
  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext) {
    if (event.cron === "0 * * * *") ctx.waitUntil(refreshCache(env));
    if (event.cron === "0 0 * * *") ctx.waitUntil(cleanupExpired(env));
  },
};
async function refreshCache(env: Env) {
  const { results } = await env.DB.prepare("SELECT * FROM posts LIMIT 50").all();
  await env.CACHE.put("posts:latest", JSON.stringify(results), { expirationTtl: 600 });
}
async function cleanupExpired(env: Env) { await env.DB.prepare("DELETE FROM sessions WHERE expires_at < datetime('now')").run(); }
```

## Deployment

```bash
npx wrangler dev                                  # local development
npx wrangler d1 create my-db                      # create D1 database
npx wrangler d1 migrations apply my-db --remote   # apply migrations
npx wrangler kv namespace create CACHE            # create KV namespace
npx wrangler r2 bucket create my-bucket           # create R2 bucket
npx wrangler secret put API_KEY                   # set secrets
npx wrangler deploy                               # deploy to production
```

## Additional Resources

- [Workers Docs](https://developers.cloudflare.com/workers/) | [D1](https://developers.cloudflare.com/d1/) | [R2](https://developers.cloudflare.com/r2/) | [KV](https://developers.cloudflare.com/kv/)
- [Durable Objects](https://developers.cloudflare.com/durable-objects/) | [Hono](https://hono.dev/) | [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/)
