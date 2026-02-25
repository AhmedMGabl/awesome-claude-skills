---
name: convex-queries
description: Convex advanced query patterns covering paginated queries, search indexes, aggregate functions, joins, optimistic updates, file storage, and real-time subscription patterns.
---

# Convex Queries

This skill should be used when building advanced query patterns with Convex. It covers pagination, search, aggregation, joins, optimistic updates, and file storage.

## When to Use This Skill

Use this skill when you need to:

- Build paginated data views with Convex
- Implement full-text search
- Aggregate and join data across tables
- Handle optimistic updates for instant UI feedback
- Upload and serve files with Convex storage

## Paginated Queries

```typescript
// convex/messages.ts
import { v } from "convex/values";
import { query } from "./_generated/server";
import { paginationOptsValidator } from "convex/server";

export const list = query({
  args: {
    channelId: v.id("channels"),
    paginationOpts: paginationOptsValidator,
  },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("messages")
      .withIndex("by_channel", (q) => q.eq("channelId", args.channelId))
      .order("desc")
      .paginate(args.paginationOpts);
  },
});

// React component
import { usePaginatedQuery } from "convex/react";
import { api } from "../convex/_generated/api";

function MessageList({ channelId }: { channelId: string }) {
  const { results, status, loadMore } = usePaginatedQuery(
    api.messages.list,
    { channelId },
    { initialNumItems: 25 },
  );

  return (
    <div>
      {results.map((msg) => (
        <div key={msg._id}>{msg.text}</div>
      ))}
      {status === "CanLoadMore" && (
        <button onClick={() => loadMore(25)}>Load more</button>
      )}
    </div>
  );
}
```

## Search

```typescript
// convex/schema.ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  articles: defineTable({
    title: v.string(),
    body: v.string(),
    author: v.string(),
    published: v.boolean(),
  })
    .index("by_author", ["author"])
    .searchIndex("search_articles", {
      searchField: "body",
      filterFields: ["author", "published"],
    }),
});

// convex/articles.ts
export const search = query({
  args: {
    query: v.string(),
    author: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    let searchQuery = ctx.db
      .query("articles")
      .withSearchIndex("search_articles", (q) => {
        let search = q.search("body", args.query);
        if (args.author) search = search.eq("author", args.author);
        return search.eq("published", true);
      });

    return await searchQuery.take(20);
  },
});
```

## Joins and Relationships

```typescript
// convex/posts.ts
export const getWithAuthor = query({
  args: { postId: v.id("posts") },
  handler: async (ctx, args) => {
    const post = await ctx.db.get(args.postId);
    if (!post) return null;

    const author = await ctx.db.get(post.authorId);
    const comments = await ctx.db
      .query("comments")
      .withIndex("by_post", (q) => q.eq("postId", args.postId))
      .collect();

    // Fetch comment authors in parallel
    const commentAuthors = await Promise.all(
      comments.map((c) => ctx.db.get(c.authorId)),
    );

    return {
      ...post,
      author,
      comments: comments.map((c, i) => ({
        ...c,
        author: commentAuthors[i],
      })),
    };
  },
});
```

## Optimistic Updates

```tsx
import { useMutation } from "convex/react";
import { api } from "../convex/_generated/api";

function TodoItem({ todo }: { todo: Todo }) {
  const toggleTodo = useMutation(api.todos.toggle).withOptimisticUpdate(
    (localStore, args) => {
      const currentValue = localStore.getQuery(api.todos.list, {});
      if (currentValue) {
        localStore.setQuery(
          api.todos.list,
          {},
          currentValue.map((t) =>
            t._id === args.id ? { ...t, done: !t.done } : t,
          ),
        );
      }
    },
  );

  return (
    <div>
      <input
        type="checkbox"
        checked={todo.done}
        onChange={() => toggleTodo({ id: todo._id })}
      />
      <span>{todo.text}</span>
    </div>
  );
}
```

## File Storage

```typescript
// convex/files.ts
import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const generateUploadUrl = mutation({
  handler: async (ctx) => {
    return await ctx.storage.generateUploadUrl();
  },
});

export const saveFile = mutation({
  args: { storageId: v.id("_storage"), name: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db.insert("files", {
      storageId: args.storageId,
      name: args.name,
      uploadedAt: Date.now(),
    });
  },
});

export const getFileUrl = query({
  args: { storageId: v.id("_storage") },
  handler: async (ctx, args) => {
    return await ctx.storage.getUrl(args.storageId);
  },
});

// React upload component
function FileUpload() {
  const generateUrl = useMutation(api.files.generateUploadUrl);
  const saveFile = useMutation(api.files.saveFile);

  const handleUpload = async (file: File) => {
    const url = await generateUrl();
    const result = await fetch(url, { method: "POST", body: file });
    const { storageId } = await result.json();
    await saveFile({ storageId, name: file.name });
  };

  return <input type="file" onChange={(e) => handleUpload(e.target.files![0])} />;
}
```

## Additional Resources

- Convex docs: https://docs.convex.dev/
- Pagination: https://docs.convex.dev/database/pagination
- Search: https://docs.convex.dev/text-search
