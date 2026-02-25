---
name: nile-postgres
description: Nile Postgres patterns covering tenant-aware database, virtual tenant databases, tenant isolation, row-level security, user management, Drizzle ORM integration, and multi-tenant SaaS development.
---

# Nile Postgres

This skill should be used when building multi-tenant applications with Nile's tenant-aware Postgres. It covers tenant isolation, user management, Drizzle integration, and SaaS patterns.

## When to Use This Skill

Use this skill when you need to:

- Build multi-tenant SaaS applications
- Implement automatic tenant isolation
- Manage users per tenant
- Use Drizzle ORM with tenant-aware queries
- Handle tenant provisioning and onboarding

## Setup

```bash
npm install @niledatabase/server
# Optional: Drizzle integration
npm install drizzle-orm drizzle-kit
```

## Client Setup

```ts
import { Nile } from "@niledatabase/server";

const nile = new Nile({
  databaseId: process.env.NILE_DATABASE_ID!,
  databaseName: process.env.NILE_DATABASE_NAME!,
  user: process.env.NILE_USER!,
  password: process.env.NILE_PASSWORD!,
});
```

## Schema with Tenant Isolation

```sql
-- Tenants table (built-in)
-- CREATE TABLE tenants (
--   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--   name TEXT NOT NULL
-- );

-- Tenant-aware table
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id),
  title TEXT NOT NULL,
  content TEXT,
  status TEXT DEFAULT 'draft',
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Shared table (no tenant_id)
CREATE TABLE plans (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  price_monthly INTEGER NOT NULL,
  features JSONB
);
```

## Tenant-Scoped Queries

```ts
// Set tenant context - all queries automatically filtered
nile.tenantId = tenantId;

// These queries only return/affect the current tenant's data
const posts = await nile.db.query("SELECT * FROM posts WHERE status = $1 ORDER BY created_at DESC", ["published"]);

// Insert (tenant_id automatically set)
await nile.db.query(
  "INSERT INTO posts (tenant_id, title, content) VALUES ($1, $2, $3)",
  [nile.tenantId, "New Post", "Content here"]
);

// Update
await nile.db.query(
  "UPDATE posts SET status = $1 WHERE id = $2",
  ["published", postId]
);
```

## Tenant Management

```ts
// Create tenant
const tenant = await nile.db.query(
  "INSERT INTO tenants (name) VALUES ($1) RETURNING *",
  ["Acme Corp"]
);

// List tenants
const tenants = await nile.db.query("SELECT * FROM tenants");

// Create user for tenant
await nile.db.query(
  "INSERT INTO users.tenant_users (tenant_id, user_id, roles) VALUES ($1, $2, $3)",
  [tenantId, userId, ["admin"]]
);
```

## Drizzle Integration

```ts
// db/schema.ts
import { pgTable, uuid, text, timestamp, jsonb } from "drizzle-orm/pg-core";

export const tenants = pgTable("tenants", {
  id: uuid("id").primaryKey().defaultRandom(),
  name: text("name").notNull(),
});

export const posts = pgTable("posts", {
  id: uuid("id").primaryKey().defaultRandom(),
  tenantId: uuid("tenant_id").notNull().references(() => tenants.id),
  title: text("title").notNull(),
  content: text("content"),
  status: text("status").default("draft"),
  createdAt: timestamp("created_at").defaultNow(),
});

// db/index.ts
import { drizzle } from "drizzle-orm/nile";
import * as schema from "./schema";

export function getDb(tenantId?: string) {
  const db = drizzle(nile, { schema });
  if (tenantId) {
    nile.tenantId = tenantId;
  }
  return db;
}

// Usage
import { eq, desc } from "drizzle-orm";

const db = getDb(tenantId);
const publishedPosts = await db
  .select()
  .from(posts)
  .where(eq(posts.status, "published"))
  .orderBy(desc(posts.createdAt));
```

## Next.js API Route

```ts
// app/api/posts/route.ts
import { nile } from "@/lib/nile";
import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  const tenantId = request.headers.get("x-tenant-id");
  if (!tenantId) return NextResponse.json({ error: "Tenant required" }, { status: 400 });

  nile.tenantId = tenantId;
  const result = await nile.db.query(
    "SELECT * FROM posts WHERE status = 'published' ORDER BY created_at DESC LIMIT 20"
  );

  return NextResponse.json(result.rows);
}
```

## Additional Resources

- Nile: https://www.thenile.dev/docs
- Multi-tenant: https://www.thenile.dev/docs/tenant-virtualization
- Quickstart: https://www.thenile.dev/docs/getting-started
