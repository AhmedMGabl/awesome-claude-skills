---
name: neon-database
description: Neon serverless Postgres covering branching, connection pooling, autoscaling, Neon Auth, drizzle-orm integration, edge function access, database branching for preview deployments, and migration workflows.
---

# Neon Serverless Postgres

This skill should be used when working with Neon's serverless Postgres platform. It covers branching, connection pooling, edge access, and integration with ORMs.

## When to Use This Skill

Use this skill when you need to:

- Use serverless Postgres with auto-scaling
- Create database branches for previews and testing
- Connect from edge functions or serverless environments
- Integrate with Drizzle ORM or Prisma
- Set up migration workflows with branching

## Connection Setup

```typescript
// lib/db.ts
import { neon, neonConfig } from "@neondatabase/serverless";
import { drizzle } from "drizzle-orm/neon-http";
import * as schema from "./schema";

// HTTP mode — best for serverless/edge
neonConfig.fetchConnectionCache = true;
const sql = neon(process.env.DATABASE_URL!);
export const db = drizzle(sql, { schema });

// WebSocket mode — for long-running processes
import { Pool } from "@neondatabase/serverless";
import { drizzle as drizzleWs } from "drizzle-orm/neon-serverless";

const pool = new Pool({ connectionString: process.env.DATABASE_URL });
export const dbWs = drizzleWs(pool, { schema });
```

## Database Branching

```bash
# Create a branch from main
neonctl branches create --name preview-123 --parent main

# Get connection string for branch
neonctl connection-string preview-123

# Delete branch
neonctl branches delete preview-123

# List branches
neonctl branches list
```

## Preview Branch Automation

```yaml
# .github/workflows/preview.yml
name: Create Preview Branch
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  create-branch:
    runs-on: ubuntu-latest
    steps:
      - uses: neondatabase/create-branch-action@v5
        with:
          project_id: ${{ secrets.NEON_PROJECT_ID }}
          branch_name: preview/pr-${{ github.event.number }}
          api_key: ${{ secrets.NEON_API_KEY }}
          username: neondb_owner
        id: create-branch

      - name: Run migrations
        run: npx drizzle-kit push
        env:
          DATABASE_URL: ${{ steps.create-branch.outputs.db_url_with_pooler }}
```

## Schema with Drizzle

```typescript
// db/schema.ts
import { pgTable, text, timestamp, uuid, boolean, index } from "drizzle-orm/pg-core";

export const users = pgTable("users", {
  id: uuid("id").primaryKey().defaultRandom(),
  email: text("email").notNull().unique(),
  name: text("name").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
}, (table) => [
  index("users_email_idx").on(table.email),
]);

export const posts = pgTable("posts", {
  id: uuid("id").primaryKey().defaultRandom(),
  title: text("title").notNull(),
  content: text("content"),
  published: boolean("published").default(false).notNull(),
  authorId: uuid("author_id").notNull().references(() => users.id),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});
```

## Edge Function Usage (Next.js)

```typescript
// app/api/posts/route.ts
import { db } from "@/lib/db";
import { posts } from "@/db/schema";
import { eq, desc } from "drizzle-orm";

export const runtime = "edge";

export async function GET() {
  const results = await db.query.posts.findMany({
    where: eq(posts.published, true),
    orderBy: desc(posts.createdAt),
    limit: 20,
    with: { author: { columns: { name: true } } },
  });

  return Response.json(results);
}
```

## Prisma Integration

```prisma
// prisma/schema.prisma
datasource db {
  provider  = "postgresql"
  url       = env("DATABASE_URL")
  directUrl = env("DIRECT_URL")
}
```

```typescript
// For edge — use Neon adapter
import { Pool } from "@neondatabase/serverless";
import { PrismaNeon } from "@prisma/adapter-neon";
import { PrismaClient } from "@prisma/client";

const pool = new Pool({ connectionString: process.env.DATABASE_URL });
const adapter = new PrismaNeon(pool);
export const prisma = new PrismaClient({ adapter });
```

## CLI Commands

```bash
neonctl projects list                # List projects
neonctl branches list                # List branches
neonctl branches create --name dev   # Create branch
neonctl connection-string            # Get connection URL
neonctl databases list               # List databases
```

## Additional Resources

- Neon docs: https://neon.tech/docs
- Neon branching: https://neon.tech/docs/introduction/branching
- Neon + Drizzle: https://neon.tech/docs/guides/drizzle
