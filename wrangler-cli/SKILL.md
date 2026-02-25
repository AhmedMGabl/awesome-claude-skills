---
name: wrangler-cli
description: Cloudflare Wrangler CLI covering Workers development, KV namespaces, R2 storage, D1 databases, Durable Objects, Pages deployment, secrets management, and local development with Miniflare.
---

# Wrangler CLI

This skill should be used when developing and deploying Cloudflare Workers with Wrangler. It covers Workers, KV, R2, D1, Durable Objects, and Pages.

## When to Use This Skill

Use this skill when you need to:

- Develop and deploy Cloudflare Workers
- Manage KV namespaces, R2 buckets, and D1 databases
- Configure Durable Objects for stateful edge computing
- Deploy sites with Cloudflare Pages
- Run local development with Miniflare

## Configuration

```toml
# wrangler.toml
name = "my-worker"
main = "src/index.ts"
compatibility_date = "2024-01-01"

[vars]
ENVIRONMENT = "production"

[[kv_namespaces]]
binding = "CACHE"
id = "abc123"

[[r2_buckets]]
binding = "STORAGE"
bucket_name = "my-bucket"

[[d1_databases]]
binding = "DB"
database_name = "my-database"
database_id = "xyz789"

[durable_objects]
bindings = [
  { name = "COUNTER", class_name = "Counter" }
]

[[migrations]]
tag = "v1"
new_classes = ["Counter"]
```

## Worker with Bindings

```typescript
// src/index.ts
export interface Env {
  CACHE: KVNamespace;
  STORAGE: R2Bucket;
  DB: D1Database;
  COUNTER: DurableObjectNamespace;
  API_KEY: string;
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/api/data") {
      // Check KV cache
      const cached = await env.CACHE.get("data", "json");
      if (cached) return Response.json(cached);

      // Query D1
      const { results } = await env.DB.prepare(
        "SELECT * FROM items ORDER BY created_at DESC LIMIT 20"
      ).all();

      // Cache for 5 minutes
      ctx.waitUntil(
        env.CACHE.put("data", JSON.stringify(results), { expirationTtl: 300 })
      );

      return Response.json(results);
    }

    return new Response("Not found", { status: 404 });
  },
};
```

## KV Operations

```typescript
// Write
await env.CACHE.put("key", "value");
await env.CACHE.put("json-key", JSON.stringify(data));
await env.CACHE.put("temp", "value", { expirationTtl: 3600 });

// Read
const value = await env.CACHE.get("key");
const data = await env.CACHE.get("json-key", "json");

// List keys
const list = await env.CACHE.list({ prefix: "user:" });

// Delete
await env.CACHE.delete("key");
```

## D1 Database

```typescript
// Create table
await env.DB.prepare(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
  )
`).run();

// Parameterized query
const user = await env.DB.prepare("SELECT * FROM users WHERE id = ?")
  .bind(userId)
  .first();

// Insert
const result = await env.DB.prepare("INSERT INTO users (email, name) VALUES (?, ?)")
  .bind(email, name)
  .run();

// Batch operations
await env.DB.batch([
  env.DB.prepare("INSERT INTO logs (action) VALUES (?)").bind("created"),
  env.DB.prepare("UPDATE counters SET value = value + 1 WHERE name = ?").bind("users"),
]);
```

## R2 Storage

```typescript
// Upload
await env.STORAGE.put("uploads/photo.jpg", request.body, {
  httpMetadata: { contentType: "image/jpeg" },
  customMetadata: { userId: "123" },
});

// Download
const object = await env.STORAGE.get("uploads/photo.jpg");
if (object) {
  return new Response(object.body, {
    headers: { "Content-Type": object.httpMetadata?.contentType ?? "" },
  });
}

// List objects
const listed = await env.STORAGE.list({ prefix: "uploads/", limit: 100 });

// Delete
await env.STORAGE.delete("uploads/photo.jpg");
```

## CLI Commands

```bash
# Development
wrangler dev                    # Start local dev server
wrangler dev --remote           # Dev with remote resources

# Deploy
wrangler deploy                 # Deploy to production
wrangler deploy --env staging   # Deploy to staging

# KV
wrangler kv namespace create CACHE
wrangler kv key put --binding CACHE "key" "value"

# D1
wrangler d1 create my-database
wrangler d1 execute my-database --file schema.sql
wrangler d1 execute my-database --command "SELECT * FROM users"

# Secrets
wrangler secret put API_KEY
wrangler secret list
```

## Additional Resources

- Wrangler docs: https://developers.cloudflare.com/workers/wrangler/
- Workers docs: https://developers.cloudflare.com/workers/
- D1 docs: https://developers.cloudflare.com/d1/
