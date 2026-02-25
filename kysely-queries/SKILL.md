---
name: kysely-queries
description: Kysely type-safe SQL query builder patterns covering select, insert, update, delete, joins, subqueries, CTEs, transactions, migrations, and dialect support for PostgreSQL, MySQL, and SQLite.
---

# Kysely Queries

This skill should be used when building type-safe SQL queries with Kysely. It covers query building, joins, transactions, migrations, and dialect configuration.

## When to Use This Skill

Use this skill when you need to:

- Build type-safe SQL queries in TypeScript
- Write complex joins and subqueries
- Manage database migrations
- Use transactions with proper error handling
- Support multiple SQL dialects

## Setup

```typescript
import { Kysely, PostgresDialect } from "kysely";
import { Pool } from "pg";

interface Database {
  users: {
    id: Generated<number>;
    name: string;
    email: string;
    role: "admin" | "user";
    created_at: Generated<Date>;
  };
  posts: {
    id: Generated<number>;
    title: string;
    content: string;
    author_id: number;
    published: boolean;
    created_at: Generated<Date>;
  };
  tags: {
    id: Generated<number>;
    name: string;
  };
  post_tags: {
    post_id: number;
    tag_id: number;
  };
}

const db = new Kysely<Database>({
  dialect: new PostgresDialect({
    pool: new Pool({ connectionString: process.env.DATABASE_URL }),
  }),
});
```

## Queries

```typescript
// Select
const users = await db
  .selectFrom("users")
  .select(["id", "name", "email"])
  .where("role", "=", "admin")
  .orderBy("name", "asc")
  .limit(10)
  .execute();

// Select with conditions
const posts = await db
  .selectFrom("posts")
  .selectAll()
  .where("published", "=", true)
  .where("created_at", ">", new Date("2024-01-01"))
  .where((eb) =>
    eb.or([
      eb("title", "like", "%typescript%"),
      eb("content", "like", "%typescript%"),
    ])
  )
  .execute();

// Insert
const newUser = await db
  .insertInto("users")
  .values({
    name: "Alice",
    email: "alice@example.com",
    role: "user",
  })
  .returningAll()
  .executeTakeFirstOrThrow();

// Update
const updated = await db
  .updateTable("users")
  .set({ role: "admin" })
  .where("id", "=", userId)
  .returningAll()
  .executeTakeFirst();

// Delete
await db
  .deleteFrom("posts")
  .where("author_id", "=", userId)
  .where("published", "=", false)
  .execute();
```

## Joins

```typescript
// Inner join
const postsWithAuthors = await db
  .selectFrom("posts")
  .innerJoin("users", "users.id", "posts.author_id")
  .select([
    "posts.id",
    "posts.title",
    "users.name as author_name",
  ])
  .where("posts.published", "=", true)
  .execute();

// Left join with aggregation
const usersWithPostCount = await db
  .selectFrom("users")
  .leftJoin("posts", "posts.author_id", "users.id")
  .select([
    "users.id",
    "users.name",
    db.fn.count<number>("posts.id").as("post_count"),
  ])
  .groupBy(["users.id", "users.name"])
  .execute();

// Many-to-many through junction table
const postsWithTags = await db
  .selectFrom("posts")
  .innerJoin("post_tags", "post_tags.post_id", "posts.id")
  .innerJoin("tags", "tags.id", "post_tags.tag_id")
  .select(["posts.id", "posts.title", "tags.name as tag_name"])
  .execute();
```

## Transactions

```typescript
const result = await db.transaction().execute(async (trx) => {
  const user = await trx
    .insertInto("users")
    .values({ name: "Bob", email: "bob@example.com", role: "user" })
    .returningAll()
    .executeTakeFirstOrThrow();

  const post = await trx
    .insertInto("posts")
    .values({
      title: "First Post",
      content: "Hello World",
      author_id: user.id,
      published: true,
    })
    .returningAll()
    .executeTakeFirstOrThrow();

  return { user, post };
});
```

## Migrations

```typescript
import { Kysely, sql } from "kysely";

export async function up(db: Kysely<unknown>): Promise<void> {
  await db.schema
    .createTable("users")
    .addColumn("id", "serial", (col) => col.primaryKey())
    .addColumn("name", "varchar(255)", (col) => col.notNull())
    .addColumn("email", "varchar(255)", (col) => col.notNull().unique())
    .addColumn("role", "varchar(50)", (col) => col.notNull().defaultTo("user"))
    .addColumn("created_at", "timestamp", (col) =>
      col.notNull().defaultTo(sql`now()`)
    )
    .execute();

  await db.schema
    .createIndex("idx_users_email")
    .on("users")
    .column("email")
    .execute();
}

export async function down(db: Kysely<unknown>): Promise<void> {
  await db.schema.dropTable("users").execute();
}
```

## Additional Resources

- Kysely: https://kysely.dev/
- Kysely API: https://kysely-org.github.io/kysely-apidoc/
- Migrations: https://kysely.dev/docs/migrations
