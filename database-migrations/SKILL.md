---
name: database-migrations
description: Database migration management covering zero-downtime schema changes, Prisma and Drizzle migrations, Knex.js migration runner, Alembic for Python/SQLAlchemy, backward-compatible column additions, data migrations, rollback strategies, and CI/CD migration automation.
---

# Database Migrations

This skill should be used when managing database schema changes and data migrations. It covers migration tools, zero-downtime patterns, rollback strategies, and CI automation.

## When to Use This Skill

Use this skill when you need to:

- Manage schema changes with migration tools
- Perform zero-downtime database migrations
- Write data migrations for existing records
- Set up rollback strategies
- Automate migrations in CI/CD pipelines

## Zero-Downtime Pattern

```
STEP 1: Add new column (nullable)
STEP 2: Deploy code that writes to both old and new columns
STEP 3: Backfill data from old to new column
STEP 4: Deploy code that reads from new column only
STEP 5: Drop old column
```

## Knex.js Migrations

```typescript
import type { Knex } from "knex";

export async function up(knex: Knex): Promise<void> {
  await knex.schema.createTable("users", (table) => {
    table.uuid("id").primary().defaultTo(knex.fn.uuid());
    table.string("email").notNullable().unique();
    table.string("name").notNullable();
    table.enum("role", ["user", "admin"]).defaultTo("user");
    table.timestamps(true, true);
  });
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.dropTable("users");
}
```

## Data Migration (Batch Backfill)

```typescript
export async function up(knex: Knex): Promise<void> {
  await knex.schema.alterTable("users", (table) => {
    table.string("display_name").nullable();
  });

  // Backfill in batches to avoid locking
  const batchSize = 1000;
  let offset = 0;
  while (true) {
    const users = await knex("users")
      .whereNull("display_name")
      .limit(batchSize)
      .offset(offset);
    if (users.length === 0) break;
    for (const user of users) {
      await knex("users")
        .where("id", user.id)
        .update({ display_name: user.name });
    }
    offset += batchSize;
  }
}
```

## Alembic (Python/SQLAlchemy)

```python
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

def downgrade():
    op.drop_table("users")
```

```bash
alembic revision --autogenerate -m "add avatar column"
alembic upgrade head
alembic downgrade -1
```

## Prisma Migration Commands

```bash
npx prisma migrate dev --name add_avatar
npx prisma migrate deploy
npx prisma migrate reset
npx prisma db push
```

## CI/CD Automation

```yaml
jobs:
  migrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npx prisma migrate deploy
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
  deploy:
    needs: migrate
    runs-on: ubuntu-latest
    steps:
      - run: vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
```

## Safety Rules

```
RULE                                 WHY
──────────────────────────────────────────────────────
Add columns as nullable              No lock on large tables
Never rename in-place                Breaks running code
Backfill in batches                  Avoids table locks
Test down migrations                 Ensures safe rollback
Run migrations before deploy         New code expects new schema
```

## Additional Resources

- Knex.js migrations: https://knexjs.org/guide/migrations.html
- Alembic: https://alembic.sqlalchemy.org/
- Prisma Migrate: https://www.prisma.io/docs/orm/prisma-migrate
