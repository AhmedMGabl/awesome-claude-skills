---
name: database-migrations
description: Database migration strategies and patterns covering schema versioning, zero-downtime migrations, data migrations, rollback strategies, migration testing, ORM-specific patterns (Prisma, Drizzle, Knex, Alembic, Django), PostgreSQL ALTER operations, and production deployment safety practices.
---

# Database Migrations

This skill should be used when managing database schema changes, writing migrations, or planning zero-downtime schema deployments. It covers migration strategies, rollback patterns, and ORM-specific workflows.

## When to Use This Skill

Use this skill when you need to:

- Write database migrations for schema changes
- Plan zero-downtime migration strategies
- Handle data migrations alongside schema changes
- Set up migration tooling and workflows
- Roll back failed migrations safely
- Test migrations before production deployment

## Migration Principles

```
SAFE MIGRATION RULES:
1. Never drop columns/tables in the same deploy that removes code using them
2. Always make migrations reversible when possible
3. Add new columns as nullable or with defaults first
4. Use multi-step deployments for breaking changes
5. Test migrations against production-sized data
6. Always back up before running migrations in production
```

## Zero-Downtime Migration Pattern

```
BREAKING CHANGE: Rename column "name" to "full_name"

Step 1 (Deploy 1): Add new column
  ALTER TABLE users ADD COLUMN full_name TEXT;
  -- Backfill: UPDATE users SET full_name = name;
  -- Add trigger to keep both in sync

Step 2 (Deploy 2): Update application
  -- Code reads from full_name, writes to both
  -- Verify full_name is populated

Step 3 (Deploy 3): Drop old column
  -- Code only uses full_name
  ALTER TABLE users DROP COLUMN name;
  -- Drop sync trigger
```

## Drizzle ORM Migrations

```typescript
// drizzle.config.ts
import { defineConfig } from "drizzle-kit";

export default defineConfig({
  schema: "./src/db/schema.ts",
  out: "./drizzle",
  dialect: "postgresql",
  dbCredentials: { url: process.env.DATABASE_URL! },
});

// src/db/schema.ts
import { pgTable, text, timestamp, uuid, integer, boolean, index } from "drizzle-orm/pg-core";

export const users = pgTable("users", {
  id: uuid("id").primaryKey().defaultRandom(),
  email: text("email").notNull().unique(),
  name: text("name").notNull(),
  role: text("role", { enum: ["admin", "user"] }).default("user"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
}, (table) => [
  index("users_email_idx").on(table.email),
]);

export const posts = pgTable("posts", {
  id: uuid("id").primaryKey().defaultRandom(),
  title: text("title").notNull(),
  content: text("content"),
  published: boolean("published").default(false),
  authorId: uuid("author_id").references(() => users.id, { onDelete: "cascade" }),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

// Generate migration: npx drizzle-kit generate
// Apply migration: npx drizzle-kit migrate
// Push (dev only): npx drizzle-kit push
```

## Prisma Migrations

```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        String   @id @default(uuid())
  email     String   @unique
  name      String
  posts     Post[]
  createdAt DateTime @default(now()) @map("created_at")

  @@map("users")
  @@index([email])
}

model Post {
  id        String   @id @default(uuid())
  title     String
  content   String?
  published Boolean  @default(false)
  author    User     @relation(fields: [authorId], references: [id], onDelete: Cascade)
  authorId  String   @map("author_id")
  createdAt DateTime @default(now()) @map("created_at")

  @@map("posts")
}
```

```bash
# Create migration: npx prisma migrate dev --name add_posts_table
# Apply in production: npx prisma migrate deploy
# Reset (dev only): npx prisma migrate reset
# Check status: npx prisma migrate status
```

## Knex.js Migrations

```typescript
// knexfile.ts
import type { Knex } from "knex";

const config: Record<string, Knex.Config> = {
  development: {
    client: "postgresql",
    connection: process.env.DATABASE_URL,
    migrations: { directory: "./migrations", extension: "ts" },
    seeds: { directory: "./seeds" },
  },
};
export default config;

// migrations/20240101000000_create_users.ts
import type { Knex } from "knex";

export async function up(knex: Knex): Promise<void> {
  await knex.schema.createTable("users", (table) => {
    table.uuid("id").primary().defaultTo(knex.fn.uuid());
    table.string("email").notNull().unique();
    table.string("name").notNull();
    table.enum("role", ["admin", "user"]).defaultTo("user");
    table.timestamps(true, true);
    table.index(["email"]);
  });
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.dropTable("users");
}

// Run: npx knex migrate:latest
// Rollback: npx knex migrate:rollback
```

## Alembic (Python/SQLAlchemy)

```python
# alembic/versions/001_create_users.py
"""create users table"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None

def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])

def downgrade() -> None:
    op.drop_index("ix_users_email")
    op.drop_table("users")
```

```bash
# Generate: alembic revision --autogenerate -m "add posts table"
# Apply: alembic upgrade head
# Rollback: alembic downgrade -1
# Status: alembic current
```

## Safe PostgreSQL Operations

```sql
-- Add column (safe, non-blocking)
ALTER TABLE users ADD COLUMN bio TEXT;

-- Add column with default (PG 11+ is safe, no table rewrite)
ALTER TABLE users ADD COLUMN active BOOLEAN DEFAULT true;

-- Create index concurrently (non-blocking)
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- Add NOT NULL with default (safe in PG 11+)
ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user';

-- Rename column (safe but requires code change coordination)
ALTER TABLE users RENAME COLUMN name TO full_name;

-- DANGEROUS: Adding NOT NULL to existing column (requires table scan)
-- Safe approach: add default first, backfill, then add constraint
ALTER TABLE users ALTER COLUMN bio SET DEFAULT '';
UPDATE users SET bio = '' WHERE bio IS NULL;  -- batch if large table
ALTER TABLE users ALTER COLUMN bio SET NOT NULL;

-- DANGEROUS: Changing column type (rewrites table, locks)
-- Safe approach: add new column, backfill, swap
ALTER TABLE users ADD COLUMN age_int INTEGER;
UPDATE users SET age_int = age::integer;
ALTER TABLE users DROP COLUMN age;
ALTER TABLE users RENAME COLUMN age_int TO age;
```

## Data Migration Pattern

```typescript
// migrations/20240201_backfill_full_names.ts
import type { Knex } from "knex";

export async function up(knex: Knex): Promise<void> {
  // Batch update to avoid locking entire table
  const batchSize = 1000;
  let updated = 0;

  do {
    const result = await knex.raw(`
      UPDATE users
      SET full_name = first_name || ' ' || last_name
      WHERE full_name IS NULL
      AND id IN (
        SELECT id FROM users WHERE full_name IS NULL LIMIT ?
      )
    `, [batchSize]);
    updated = result.rowCount ?? 0;
  } while (updated === batchSize);
}

export async function down(knex: Knex): Promise<void> {
  await knex.raw("UPDATE users SET full_name = NULL");
}
```

## Migration Testing

```bash
# Test migrate up and down cleanly
npx knex migrate:latest --env test
npx knex migrate:rollback --all --env test
npx knex migrate:latest --env test  # proves idempotency

# Test against production-like data volume
npx knex seed:run --env test
time npx knex migrate:latest --env test  # should be < 30s
```

## Production Deployment Checklist

```
PRE-DEPLOYMENT:
  [ ] Migration tested against copy of production data
  [ ] Rollback migration written and tested
  [ ] Estimated migration time documented
  [ ] Database backup taken
  [ ] Team notified of migration window

DEPLOYMENT:
  [ ] Run migration in transaction if supported
  [ ] Monitor database locks during migration
  [ ] Verify application works after migration
  [ ] Check for slow queries caused by schema change

POST-DEPLOYMENT:
  [ ] Verify all data integrity constraints
  [ ] Update database documentation
  [ ] Clean up old columns/tables (after code fully migrated)
```

## Additional Resources

- Prisma Migrations: https://www.prisma.io/docs/orm/prisma-migrate
- Drizzle Migrations: https://orm.drizzle.team/docs/migrations
- PostgreSQL ALTER: https://www.postgresql.org/docs/current/sql-altertable.html
- Zero-Downtime Migrations: https://postgres.ai/blog/20210923-zero-downtime-postgres-schema-migrations-lock-timeout-and-retries
