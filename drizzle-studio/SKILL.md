---
name: drizzle-studio
description: Drizzle ORM advanced patterns covering relational queries, prepared statements, custom SQL, migration strategies, database push vs migrate, Drizzle Studio GUI, multi-database support for PostgreSQL, MySQL, and SQLite, and integration with Next.js and Hono.
---

# Drizzle ORM Advanced

This skill should be used when implementing advanced Drizzle ORM patterns. It covers relational queries, migrations, prepared statements, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Write complex relational queries with Drizzle
- Manage database migrations and schema push
- Use prepared statements for performance
- Set up Drizzle with Next.js or Hono
- Handle multi-database configurations

## Schema with Relations

```typescript
// db/schema.ts
import { pgTable, text, timestamp, uuid, integer, boolean } from "drizzle-orm/pg-core";
import { relations } from "drizzle-orm";

export const users = pgTable("users", {
  id: uuid("id").primaryKey().defaultRandom(),
  email: text("email").notNull().unique(),
  name: text("name").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const posts = pgTable("posts", {
  id: uuid("id").primaryKey().defaultRandom(),
  title: text("title").notNull(),
  content: text("content"),
  published: boolean("published").default(false).notNull(),
  authorId: uuid("author_id").notNull().references(() => users.id),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const comments = pgTable("comments", {
  id: uuid("id").primaryKey().defaultRandom(),
  body: text("body").notNull(),
  postId: uuid("post_id").notNull().references(() => posts.id, { onDelete: "cascade" }),
  authorId: uuid("author_id").notNull().references(() => users.id),
});

// Relations
export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts),
  comments: many(comments),
}));

export const postsRelations = relations(posts, ({ one, many }) => ({
  author: one(users, { fields: [posts.authorId], references: [users.id] }),
  comments: many(comments),
}));

export const commentsRelations = relations(comments, ({ one }) => ({
  post: one(posts, { fields: [comments.postId], references: [posts.id] }),
  author: one(users, { fields: [comments.authorId], references: [users.id] }),
}));
```

## Relational Queries

```typescript
import { db } from "./db";
import { eq, desc, and, like, sql, count } from "drizzle-orm";

// Nested relational query
const postsWithComments = await db.query.posts.findMany({
  where: eq(posts.published, true),
  orderBy: desc(posts.createdAt),
  limit: 10,
  with: {
    author: { columns: { name: true, email: true } },
    comments: {
      with: { author: { columns: { name: true } } },
      orderBy: desc(comments.createdAt),
      limit: 5,
    },
  },
});

// Single record with relations
const post = await db.query.posts.findFirst({
  where: eq(posts.id, postId),
  with: { author: true, comments: { with: { author: true } } },
});
```

## Select Builder Queries

```typescript
// Join with aggregation
const authorStats = await db
  .select({
    authorId: users.id,
    authorName: users.name,
    postCount: count(posts.id),
  })
  .from(users)
  .leftJoin(posts, eq(users.id, posts.authorId))
  .groupBy(users.id, users.name)
  .orderBy(desc(count(posts.id)));

// Subquery
const popularAuthors = db
  .select({ authorId: posts.authorId })
  .from(posts)
  .groupBy(posts.authorId)
  .having(sql`count(*) > 5`)
  .as("popular");

const result = await db
  .select()
  .from(users)
  .innerJoin(popularAuthors, eq(users.id, popularAuthors.authorId));
```

## Transactions

```typescript
const result = await db.transaction(async (tx) => {
  const [user] = await tx.insert(users).values({ email, name }).returning();
  const [post] = await tx.insert(posts).values({
    title,
    content,
    authorId: user.id,
  }).returning();
  return { user, post };
});
```

## Prepared Statements

```typescript
const getUser = db.query.users.findFirst({
  where: eq(users.id, sql.placeholder("id")),
}).prepare("get_user");

// Reuse prepared statement
const user1 = await getUser.execute({ id: "uuid-1" });
const user2 = await getUser.execute({ id: "uuid-2" });
```

## Drizzle Config and Migrations

```typescript
// drizzle.config.ts
import { defineConfig } from "drizzle-kit";

export default defineConfig({
  schema: "./db/schema.ts",
  out: "./drizzle",
  dialect: "postgresql",
  dbCredentials: { url: process.env.DATABASE_URL! },
});
```

```bash
npx drizzle-kit generate    # Generate migration SQL
npx drizzle-kit migrate     # Run migrations
npx drizzle-kit push        # Push schema directly (dev)
npx drizzle-kit studio      # Open Drizzle Studio GUI
npx drizzle-kit introspect  # Introspect existing DB
```

## Additional Resources

- Drizzle ORM docs: https://orm.drizzle.team/docs/overview
- Drizzle Kit: https://orm.drizzle.team/docs/kit-overview
- Drizzle Studio: https://orm.drizzle.team/drizzle-studio/overview
