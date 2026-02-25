---
name: convex-schema
description: Convex schema patterns covering table definitions, validators, indexes, relationships, query and mutation functions, real-time subscriptions, file storage, and React hooks integration.
---

# Convex Schema

This skill should be used when defining and working with Convex database schemas. It covers table definitions, validators, indexes, queries, mutations, and real-time subscriptions.

## When to Use This Skill

Use this skill when you need to:

- Define type-safe database schemas in Convex
- Create queries and mutation functions
- Set up indexes for efficient querying
- Handle real-time data subscriptions
- Manage file storage with Convex

## Setup

```bash
npm install convex
npx convex dev
```

## Schema Definition

```ts
// convex/schema.ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  users: defineTable({
    name: v.string(),
    email: v.string(),
    avatarUrl: v.optional(v.string()),
    role: v.union(v.literal("admin"), v.literal("user"), v.literal("editor")),
    createdAt: v.number(),
  })
    .index("by_email", ["email"])
    .index("by_role", ["role"]),

  posts: defineTable({
    title: v.string(),
    slug: v.string(),
    content: v.string(),
    status: v.union(v.literal("draft"), v.literal("published")),
    authorId: v.id("users"),
    tags: v.array(v.string()),
    publishedAt: v.optional(v.number()),
  })
    .index("by_slug", ["slug"])
    .index("by_author", ["authorId"])
    .index("by_status_date", ["status", "publishedAt"])
    .searchIndex("search_posts", { searchField: "content", filterFields: ["status"] }),

  comments: defineTable({
    postId: v.id("posts"),
    authorId: v.id("users"),
    content: v.string(),
    createdAt: v.number(),
  }).index("by_post", ["postId"]),
});
```

## Query Functions

```ts
// convex/posts.ts
import { query } from "./_generated/server";
import { v } from "convex/values";

export const list = query({
  args: {
    status: v.optional(v.string()),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    let q = ctx.db.query("posts");

    if (args.status) {
      q = q.withIndex("by_status_date", (q) => q.eq("status", args.status!));
    }

    const posts = await q.order("desc").take(args.limit ?? 20);

    return Promise.all(
      posts.map(async (post) => ({
        ...post,
        author: await ctx.db.get(post.authorId),
      }))
    );
  },
});

export const getBySlug = query({
  args: { slug: v.string() },
  handler: async (ctx, args) => {
    const post = await ctx.db
      .query("posts")
      .withIndex("by_slug", (q) => q.eq("slug", args.slug))
      .unique();

    if (!post) return null;

    const author = await ctx.db.get(post.authorId);
    const comments = await ctx.db
      .query("comments")
      .withIndex("by_post", (q) => q.eq("postId", post._id))
      .collect();

    return { ...post, author, comments };
  },
});

export const search = query({
  args: { query: v.string() },
  handler: async (ctx, args) => {
    return ctx.db
      .query("posts")
      .withSearchIndex("search_posts", (q) =>
        q.search("content", args.query).eq("status", "published")
      )
      .take(10);
  },
});
```

## Mutation Functions

```ts
// convex/posts.ts
import { mutation } from "./_generated/server";
import { v } from "convex/values";

export const create = mutation({
  args: {
    title: v.string(),
    slug: v.string(),
    content: v.string(),
    tags: v.array(v.string()),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");

    const user = await ctx.db
      .query("users")
      .withIndex("by_email", (q) => q.eq("email", identity.email!))
      .unique();

    return ctx.db.insert("posts", {
      ...args,
      status: "draft",
      authorId: user!._id,
    });
  },
});

export const publish = mutation({
  args: { id: v.id("posts") },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      status: "published",
      publishedAt: Date.now(),
    });
  },
});

export const remove = mutation({
  args: { id: v.id("posts") },
  handler: async (ctx, args) => {
    // Delete associated comments first
    const comments = await ctx.db
      .query("comments")
      .withIndex("by_post", (q) => q.eq("postId", args.id))
      .collect();
    for (const comment of comments) {
      await ctx.db.delete(comment._id);
    }
    await ctx.db.delete(args.id);
  },
});
```

## React Integration

```tsx
import { useQuery, useMutation } from "convex/react";
import { api } from "../convex/_generated/api";

function PostList() {
  const posts = useQuery(api.posts.list, { status: "published", limit: 10 });
  const publish = useMutation(api.posts.publish);

  if (!posts) return <div>Loading...</div>;

  return (
    <ul>
      {posts.map((post) => (
        <li key={post._id}>
          <h2>{post.title}</h2>
          <p>By {post.author?.name}</p>
          {post.status === "draft" && (
            <button onClick={() => publish({ id: post._id })}>Publish</button>
          )}
        </li>
      ))}
    </ul>
  );
}
```

## Additional Resources

- Convex: https://docs.convex.dev/
- Schema: https://docs.convex.dev/database/schemas
- Indexes: https://docs.convex.dev/database/indexes
