---
name: turso-database
description: Turso embedded SQLite database covering libSQL client, embedded replicas, local-first development, schema migrations, vector search, multi-tenant databases, and edge deployment patterns.
---

# Turso Database

This skill should be used when using Turso (libSQL) for edge-ready SQLite databases. It covers client setup, embedded replicas, migrations, and multi-tenant patterns.

## When to Use This Skill

Use this skill when you need to:

- Use SQLite at the edge with low latency
- Embed database replicas in applications
- Build multi-tenant databases per user/org
- Combine local-first development with cloud sync
- Use vector search with SQLite

## Client Setup

```typescript
import { createClient } from "@libsql/client";

// Remote database
const db = createClient({
  url: process.env.TURSO_DATABASE_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN!,
});

// Embedded replica (local + remote sync)
const db = createClient({
  url: "file:local.db",
  syncUrl: process.env.TURSO_DATABASE_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN!,
  syncInterval: 60, // sync every 60 seconds
});

// Sync manually
await db.sync();
```

## Queries

```typescript
// Create table
await db.execute(`
  CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    author_id INTEGER NOT NULL,
    published BOOLEAN DEFAULT FALSE,
    created_at TEXT DEFAULT (datetime('now'))
  )
`);

// Insert with parameters
const result = await db.execute({
  sql: "INSERT INTO posts (title, content, author_id) VALUES (?, ?, ?)",
  args: ["My Post", "Content here", 1],
});
console.log("Inserted ID:", result.lastInsertRowid);

// Select
const posts = await db.execute({
  sql: "SELECT * FROM posts WHERE published = ? ORDER BY created_at DESC LIMIT ?",
  args: [true, 20],
});
for (const row of posts.rows) {
  console.log(row.title, row.created_at);
}

// Batch operations (transaction)
await db.batch(
  [
    { sql: "INSERT INTO posts (title, content, author_id) VALUES (?, ?, ?)", args: ["Post 1", "Content", 1] },
    { sql: "INSERT INTO posts (title, content, author_id) VALUES (?, ?, ?)", args: ["Post 2", "Content", 1] },
    { sql: "UPDATE users SET post_count = post_count + 2 WHERE id = ?", args: [1] },
  ],
  "write"
);
```

## Drizzle ORM Integration

```typescript
import { drizzle } from "drizzle-orm/libsql";
import { createClient } from "@libsql/client";
import { sqliteTable, text, integer } from "drizzle-orm/sqlite-core";
import { eq } from "drizzle-orm";

const client = createClient({
  url: process.env.TURSO_DATABASE_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN!,
});

const db = drizzle(client);

const posts = sqliteTable("posts", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  title: text("title").notNull(),
  content: text("content").notNull(),
  authorId: integer("author_id").notNull(),
});

// Query
const allPosts = await db.select().from(posts).where(eq(posts.authorId, 1));

// Insert
await db.insert(posts).values({ title: "New", content: "Body", authorId: 1 });
```

## Multi-Tenant (Database per Tenant)

```typescript
import { createClient } from "@libsql/client";

function getTenantDb(tenantId: string) {
  return createClient({
    url: `libsql://${tenantId}-myorg.turso.io`,
    authToken: process.env.TURSO_AUTH_TOKEN!,
  });
}

// Each tenant gets isolated database
async function getTenantData(tenantId: string) {
  const db = getTenantDb(tenantId);
  return await db.execute("SELECT * FROM settings");
}
```

## Vector Search

```typescript
// Enable vector extension
await db.execute("SELECT load_extension('vector0')");

// Create table with vector column
await db.execute(`
  CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    content TEXT NOT NULL,
    embedding F32_BLOB(1536)
  )
`);

// Insert with embedding
await db.execute({
  sql: "INSERT INTO documents (content, embedding) VALUES (?, vector(?))",
  args: [text, JSON.stringify(embedding)],
});

// Vector similarity search
const results = await db.execute({
  sql: `
    SELECT content, vector_distance_cos(embedding, vector(?)) as distance
    FROM documents
    ORDER BY distance ASC
    LIMIT 10
  `,
  args: [JSON.stringify(queryEmbedding)],
});
```

## Additional Resources

- Turso docs: https://docs.turso.tech/
- libSQL client: https://docs.turso.tech/sdk/ts/quickstart
- Drizzle + Turso: https://orm.drizzle.team/docs/get-started/turso-new
