---
name: kysely-orm
description: Kysely type-safe SQL query builder covering select/insert/update/delete queries, joins, subqueries, transactions, migrations, raw SQL, and dialect support for PostgreSQL, MySQL, and SQLite.
---

# Kysely ORM

This skill should be used when building type-safe SQL queries with Kysely. It covers query building, migrations, transactions, and multi-dialect support.

## When to Use This Skill

Use this skill when you need to:

- Write type-safe SQL queries in TypeScript
- Build complex queries with joins and subqueries
- Manage database migrations programmatically
- Use raw SQL when needed without losing type safety
- Support PostgreSQL, MySQL, or SQLite

## Setup

```typescript
import { Kysely, PostgresDialect } from "kysely";
import { Pool } from "pg";

interface Database {
  users: {
    id: Generated<number>;
    name: string;
    email: string;
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
  comments: {
    id: Generated<number>;
    post_id: number;
    user_id: number;
    body: string;
    created_at: Generated<Date>;
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
// Select with filtering
const users = await db
  .selectFrom("users")
  .select(["id", "name", "email"])
  .where("email", "like", "%@example.com")
  .orderBy("created_at", "desc")
  .limit(20)
  .execute();

// Insert
const newUser = await db
  .insertInto("users")
  .values({ name: "Alice", email: "alice@example.com" })
  .returningAll()
  .executeTakeFirstOrThrow();

// Update
const updated = await db
  .updateTable("posts")
  .set({ published: true })
  .where("author_id", "=", userId)
  .where("published", "=", false)
  .returningAll()
  .execute();

// Delete
await db
  .deleteFrom("comments")
  .where("post_id", "=", postId)
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
    db.fn.count("posts.id").as("post_count"),
  ])
  .groupBy(["users.id", "users.name"])
  .execute();
```

## Subqueries

```typescript
// Subquery in WHERE
const activeAuthors = await db
  .selectFrom("users")
  .selectAll()
  .where("id", "in",
    db.selectFrom("posts")
      .select("author_id")
      .where("published", "=", true)
  )
  .execute();
```

## Transactions

```typescript
async function createPostWithTags(post: NewPost, tagIds: number[]) {
  return await db.transaction().execute(async (trx) => {
    const newPost = await trx
      .insertInto("posts")
      .values(post)
      .returningAll()
      .executeTakeFirstOrThrow();

    if (tagIds.length > 0) {
      await trx
        .insertInto("post_tags")
        .values(tagIds.map((tagId) => ({ post_id: newPost.id, tag_id: tagId })))
        .execute();
    }

    return newPost;
  });
}
```

## Migrations

```typescript
import { Kysely, sql } from "kysely";

export async function up(db: Kysely<any>): Promise<void> {
  await db.schema
    .createTable("users")
    .addColumn("id", "serial", (col) => col.primaryKey())
    .addColumn("name", "varchar(255)", (col) => col.notNull())
    .addColumn("email", "varchar(255)", (col) => col.notNull().unique())
    .addColumn("created_at", "timestamp", (col) =>
      col.defaultTo(sql`now()`).notNull()
    )
    .execute();

  await db.schema
    .createIndex("idx_users_email")
    .on("users")
    .column("email")
    .execute();
}

export async function down(db: Kysely<any>): Promise<void> {
  await db.schema.dropTable("users").execute();
}
```

## Additional Resources

- Kysely docs: https://kysely.dev/docs/intro
- API reference: https://kysely-org.github.io/kysely-apidoc/
- Dialect plugins: https://kysely.dev/docs/dialects
