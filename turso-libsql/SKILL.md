---
name: turso-libsql
description: Turso/libSQL patterns covering edge-distributed SQLite, embedded replicas, multi-tenancy with per-tenant databases, migrations, TypeScript SDK, Drizzle ORM integration, and offline-first sync.
---

# Turso / libSQL

This skill should be used when building applications with Turso edge database or libSQL. It covers connections, embedded replicas, multi-tenancy, Drizzle integration, and migrations.

## When to Use This Skill

Use this skill when you need to:

- Use edge-distributed SQLite databases
- Set up embedded replicas for local reads
- Implement multi-tenant databases
- Integrate with Drizzle ORM
- Handle migrations for libSQL

## Setup

```bash
npm install @libsql/client
# Optional: Drizzle integration
npm install drizzle-orm drizzle-kit
```

## Client Connection

```ts
import { createClient } from "@libsql/client";

// Remote database
const client = createClient({
  url: process.env.TURSO_DATABASE_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN!,
});

// Embedded replica (local reads, remote writes)
const client = createClient({
  url: "file:local.db",
  syncUrl: process.env.TURSO_DATABASE_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN!,
  syncInterval: 60, // seconds
});

// Local only (development)
const client = createClient({ url: "file:dev.db" });
```

## Queries

```ts
// Simple query
const result = await client.execute("SELECT * FROM users WHERE role = ?", ["admin"]);
console.log(result.rows); // Array of row objects

// Named parameters
const result = await client.execute({
  sql: "SELECT * FROM posts WHERE status = :status AND author_id = :authorId",
  args: { status: "published", authorId: 1 },
});

// Insert
const result = await client.execute({
  sql: "INSERT INTO users (email, name, role) VALUES (?, ?, ?)",
  args: ["alice@test.com", "Alice", "user"],
});
console.log(result.lastInsertRowid);

// Batch execute (atomic)
const results = await client.batch([
  { sql: "INSERT INTO users (email, name) VALUES (?, ?)", args: ["a@test.com", "A"] },
  { sql: "INSERT INTO users (email, name) VALUES (?, ?)", args: ["b@test.com", "B"] },
], "write");

// Transaction
const tx = await client.transaction("write");
try {
  await tx.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", [100, fromId]);
  await tx.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", [100, toId]);
  await tx.commit();
} catch (e) {
  await tx.rollback();
  throw e;
}
```

## Drizzle ORM Integration

```ts
// db/schema.ts
import { sqliteTable, text, integer } from "drizzle-orm/sqlite-core";

export const users = sqliteTable("users", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  email: text("email").notNull().unique(),
  name: text("name").notNull(),
  role: text("role", { enum: ["admin", "user", "editor"] }).default("user"),
  createdAt: text("created_at").default("(datetime('now'))"),
});

export const posts = sqliteTable("posts", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  title: text("title").notNull(),
  slug: text("slug").notNull().unique(),
  content: text("content"),
  status: text("status", { enum: ["draft", "published"] }).default("draft"),
  authorId: integer("author_id").references(() => users.id),
  publishedAt: text("published_at"),
});

// db/index.ts
import { drizzle } from "drizzle-orm/libsql";
import { createClient } from "@libsql/client";
import * as schema from "./schema";

const client = createClient({
  url: process.env.TURSO_DATABASE_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN!,
});

export const db = drizzle(client, { schema });

// Queries
import { eq, desc } from "drizzle-orm";

const publishedPosts = await db.query.posts.findMany({
  where: eq(posts.status, "published"),
  orderBy: desc(posts.publishedAt),
  with: { author: true },
  limit: 20,
});

const post = await db.query.posts.findFirst({
  where: eq(posts.slug, "my-post"),
  with: { author: true },
});

// Insert
await db.insert(users).values({ email: "alice@test.com", name: "Alice" });

// Update
await db.update(posts).set({ status: "published" }).where(eq(posts.id, 1));
```

## Multi-Tenant Databases

```ts
import { createClient } from "@libsql/client";

// Per-tenant database
function getTenantClient(tenantId: string) {
  return createClient({
    url: `libsql://${tenantId}-${process.env.TURSO_ORG}.turso.io`,
    authToken: process.env.TURSO_GROUP_AUTH_TOKEN!,
  });
}

// Usage
const client = getTenantClient("acme-corp");
const users = await client.execute("SELECT * FROM users");
```

## Embedded Replicas Sync

```ts
const client = createClient({
  url: "file:local-replica.db",
  syncUrl: process.env.TURSO_DATABASE_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN!,
});

// Manual sync
await client.sync();

// Reads are local (fast)
const result = await client.execute("SELECT * FROM posts WHERE status = 'published'");

// Writes go to remote and sync back
await client.execute("INSERT INTO posts (title, content) VALUES (?, ?)", ["New Post", "Content"]);
await client.sync();
```

## Additional Resources

- Turso: https://docs.turso.tech/
- libSQL Client: https://docs.turso.tech/sdk/ts
- Drizzle + Turso: https://orm.drizzle.team/docs/get-started/turso-new
