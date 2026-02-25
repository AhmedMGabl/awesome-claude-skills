---
name: drizzle-migrations
description: Drizzle ORM migration patterns covering schema changes, migration generation, push vs migrate, seed scripts, custom migration SQL, rollback strategies, CI/CD integration, and multi-database support for PostgreSQL, MySQL, and SQLite.
---

# Drizzle Migrations

This skill should be used when managing database migrations with Drizzle ORM. It covers schema changes, migration generation, seeding, rollbacks, and CI/CD integration.

## When to Use This Skill

Use this skill when you need to:

- Generate migrations from Drizzle schema changes
- Choose between push and migrate strategies
- Write seed scripts for development data
- Handle custom migration SQL and rollbacks
- Integrate migrations into CI/CD pipelines

## Configuration

```typescript
// drizzle.config.ts
import { defineConfig } from "drizzle-kit";

export default defineConfig({
  schema: "./src/db/schema.ts",
  out: "./drizzle",
  dialect: "postgresql",
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
  verbose: true,
  strict: true,
});
```

## Schema Definition

```typescript
// src/db/schema.ts
import { pgTable, serial, text, timestamp, integer, boolean, index, uniqueIndex } from "drizzle-orm/pg-core";
import { relations } from "drizzle-orm";

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  email: text("email").notNull(),
  role: text("role", { enum: ["admin", "user", "editor"] }).default("user"),
  createdAt: timestamp("created_at").defaultNow(),
}, (table) => [
  uniqueIndex("users_email_idx").on(table.email),
]);

export const posts = pgTable("posts", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  content: text("content"),
  published: boolean("published").default(false),
  authorId: integer("author_id").references(() => users.id, { onDelete: "cascade" }),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
}, (table) => [
  index("posts_author_idx").on(table.authorId),
]);

export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts),
}));

export const postsRelations = relations(posts, ({ one }) => ({
  author: one(users, { fields: [posts.authorId], references: [users.id] }),
}));
```

## Migration Commands

```bash
# Generate migration from schema diff
npx drizzle-kit generate

# Apply migrations to database
npx drizzle-kit migrate

# Push schema directly (development only, no migration files)
npx drizzle-kit push

# Open Drizzle Studio (database browser)
npx drizzle-kit studio

# Drop all tables (dangerous!)
npx drizzle-kit drop

# Check migration status
npx drizzle-kit check
```

## Running Migrations Programmatically

```typescript
// src/db/migrate.ts
import { drizzle } from "drizzle-orm/node-postgres";
import { migrate } from "drizzle-orm/node-postgres/migrator";
import { Pool } from "pg";

async function runMigrations() {
  const pool = new Pool({ connectionString: process.env.DATABASE_URL });
  const db = drizzle(pool);

  console.log("Running migrations...");
  await migrate(db, { migrationsFolder: "./drizzle" });
  console.log("Migrations complete!");

  await pool.end();
}

runMigrations().catch(console.error);
```

## Seed Script

```typescript
// src/db/seed.ts
import { drizzle } from "drizzle-orm/node-postgres";
import { Pool } from "pg";
import { users, posts } from "./schema";

async function seed() {
  const pool = new Pool({ connectionString: process.env.DATABASE_URL });
  const db = drizzle(pool);

  // Clear existing data
  await db.delete(posts);
  await db.delete(users);

  // Insert seed data
  const [alice, bob] = await db.insert(users).values([
    { name: "Alice", email: "alice@example.com", role: "admin" },
    { name: "Bob", email: "bob@example.com", role: "user" },
  ]).returning();

  await db.insert(posts).values([
    { title: "First Post", content: "Hello world!", published: true, authorId: alice.id },
    { title: "Draft Post", content: "Work in progress...", authorId: bob.id },
  ]);

  console.log("Seeding complete!");
  await pool.end();
}

seed().catch(console.error);
```

## Custom SQL Migrations

```sql
-- drizzle/0001_custom_migration.sql
-- Custom migration for complex operations

-- Add full-text search index
CREATE INDEX IF NOT EXISTS posts_search_idx
ON posts USING gin(to_tsvector('english', title || ' ' || coalesce(content, '')));

-- Create a materialized view
CREATE MATERIALIZED VIEW IF NOT EXISTS user_stats AS
SELECT
  u.id,
  u.name,
  COUNT(p.id) as post_count,
  COUNT(p.id) FILTER (WHERE p.published) as published_count
FROM users u
LEFT JOIN posts p ON p.author_id = u.id
GROUP BY u.id, u.name;
```

## CI/CD Integration

```yaml
# .github/workflows/migrate.yml
name: Database Migration
on:
  push:
    branches: [main]
    paths: ["drizzle/**"]

jobs:
  migrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npx drizzle-kit migrate
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

## Additional Resources

- Drizzle Kit docs: https://orm.drizzle.team/kit-docs/overview
- Migrations: https://orm.drizzle.team/docs/migrations
- Schema declaration: https://orm.drizzle.team/docs/sql-schema-declaration
