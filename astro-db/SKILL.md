---
name: astro-db
description: Astro DB patterns covering table definitions, column types, seed data, queries with the drizzle-based API, relationships, indexes, server-side data loading, and integration with Astro pages and API endpoints.
---

# Astro DB

This skill should be used when working with Astro DB, the built-in database for Astro projects. It covers table definitions, seeding, queries, relationships, and integration with Astro pages.

## When to Use This Skill

Use this skill when you need to:

- Define database tables in an Astro project
- Seed data for development and production
- Query data using the drizzle-based API
- Define relationships between tables
- Load data in Astro pages and API endpoints

## Table Definitions

```typescript
// db/config.ts
import { column, defineDb, defineTable } from "astro:db";

const Post = defineTable({
  columns: {
    id: column.number({ primaryKey: true, autoIncrement: true }),
    title: column.text(),
    slug: column.text({ unique: true }),
    body: column.text(),
    published: column.boolean({ default: false }),
    authorId: column.number({ references: () => Author.columns.id }),
    createdAt: column.date({ default: new Date() }),
    updatedAt: column.date({ optional: true }),
  },
  indexes: [{ on: ["slug"], unique: true }, { on: ["authorId"] }],
});

const Author = defineTable({
  columns: {
    id: column.number({ primaryKey: true, autoIncrement: true }),
    name: column.text(),
    email: column.text({ unique: true }),
    bio: column.text({ optional: true }),
  },
});

const Tag = defineTable({
  columns: {
    id: column.number({ primaryKey: true, autoIncrement: true }),
    name: column.text({ unique: true }),
  },
});

const PostTag = defineTable({
  columns: {
    postId: column.number({ references: () => Post.columns.id }),
    tagId: column.number({ references: () => Tag.columns.id }),
  },
});

export default defineDb({
  tables: { Post, Author, Tag, PostTag },
});
```

## Seed Data

```typescript
// db/seed.ts
import { db, Post, Author, Tag, PostTag } from "astro:db";

export default async function seed() {
  const [alice] = await db
    .insert(Author)
    .values([
      { name: "Alice", email: "alice@example.com", bio: "Writer and developer" },
      { name: "Bob", email: "bob@example.com" },
    ])
    .returning();

  const [post1] = await db
    .insert(Post)
    .values([
      {
        title: "Getting Started with Astro DB",
        slug: "getting-started-astro-db",
        body: "Astro DB is a built-in database...",
        published: true,
        authorId: alice.id,
      },
    ])
    .returning();

  const [tag1] = await db
    .insert(Tag)
    .values([{ name: "astro" }, { name: "database" }, { name: "tutorial" }])
    .returning();

  await db.insert(PostTag).values([
    { postId: post1.id, tagId: tag1.id },
  ]);
}
```

## Queries

```typescript
// src/pages/posts/index.astro
---
import { db, Post, Author, eq, desc, like, and } from "astro:db";

// Select all published posts
const posts = await db
  .select()
  .from(Post)
  .where(eq(Post.published, true))
  .orderBy(desc(Post.createdAt));

// Join with author
const postsWithAuthors = await db
  .select({
    id: Post.id,
    title: Post.title,
    slug: Post.slug,
    authorName: Author.name,
    createdAt: Post.createdAt,
  })
  .from(Post)
  .innerJoin(Author, eq(Post.authorId, Author.id))
  .where(eq(Post.published, true))
  .orderBy(desc(Post.createdAt));

// Search
const searchResults = await db
  .select()
  .from(Post)
  .where(
    and(
      like(Post.title, `%${Astro.url.searchParams.get("q") ?? ""}%`),
      eq(Post.published, true),
    ),
  );
---

<ul>
  {postsWithAuthors.map((post) => (
    <li>
      <a href={`/posts/${post.slug}`}>{post.title}</a>
      <span>by {post.authorName}</span>
    </li>
  ))}
</ul>
```

## API Endpoints

```typescript
// src/pages/api/posts.ts
import type { APIRoute } from "astro";
import { db, Post, eq } from "astro:db";

export const GET: APIRoute = async ({ url }) => {
  const page = Number(url.searchParams.get("page") ?? "1");
  const limit = 10;
  const offset = (page - 1) * limit;

  const posts = await db
    .select()
    .from(Post)
    .where(eq(Post.published, true))
    .limit(limit)
    .offset(offset);

  return new Response(JSON.stringify(posts), {
    headers: { "Content-Type": "application/json" },
  });
};

export const POST: APIRoute = async ({ request }) => {
  const data = await request.json();
  const [post] = await db.insert(Post).values(data).returning();
  return new Response(JSON.stringify(post), { status: 201 });
};
```

## Update and Delete

```typescript
import { db, Post, eq } from "astro:db";

// Update
await db
  .update(Post)
  .set({ title: "Updated Title", updatedAt: new Date() })
  .where(eq(Post.id, 1));

// Delete
await db.delete(Post).where(eq(Post.id, 1));

// Upsert (insert or update on conflict)
await db
  .insert(Post)
  .values({ title: "New Post", slug: "new-post", body: "...", authorId: 1 })
  .onConflictDoUpdate({
    target: Post.slug,
    set: { title: "Updated Post" },
  });
```

## Additional Resources

- Astro DB docs: https://docs.astro.build/en/guides/astro-db/
- Drizzle ORM (used internally): https://orm.drizzle.team/
