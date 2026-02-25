---
name: xata-database
description: Xata database patterns covering serverless Postgres, full-text search, vector embeddings, file attachments, branching, transactions, TypeScript SDK, and edge-compatible queries.
---

# Xata Database

This skill should be used when building applications with Xata serverless database. It covers queries, search, vector embeddings, file attachments, and branching.

## When to Use This Skill

Use this skill when you need to:

- Use serverless Postgres with built-in search
- Add full-text and vector search capabilities
- Handle file attachments in database records
- Use database branching for development workflows
- Query from edge functions with TypeScript SDK

## Setup

```bash
npm install @xata.io/client
npx xata init
```

## Schema Definition

```ts
// xata.ts (auto-generated, customizable)
import { buildClient } from "@xata.io/client";

const tables = [
  {
    name: "posts",
    columns: [
      { name: "title", type: "string" },
      { name: "content", type: "text" },
      { name: "slug", type: "string", unique: true },
      { name: "status", type: "string", defaultValue: "draft" },
      { name: "author", type: "link", link: { table: "users" } },
      { name: "tags", type: "multiple" },
      { name: "cover", type: "file" },
      { name: "embedding", type: "vector", vector: { dimension: 1536 } },
      { name: "publishedAt", type: "datetime" },
    ],
  },
] as const;

const DatabaseClient = buildClient();
export const xata = new DatabaseClient({ databaseURL: process.env.XATA_DATABASE_URL!, apiKey: process.env.XATA_API_KEY! });
```

## CRUD Operations

```ts
// Create
const post = await xata.db.posts.create({
  title: "Hello World",
  content: "My first post",
  slug: "hello-world",
  status: "draft",
  author: "rec_user123",
  tags: ["intro", "hello"],
});

// Read
const post = await xata.db.posts.read("rec_abc123");

// Read with columns
const post = await xata.db.posts.read("rec_abc123", ["title", "content", "author.*"]);

// Update
await xata.db.posts.update("rec_abc123", { status: "published", publishedAt: new Date() });

// Delete
await xata.db.posts.delete("rec_abc123");

// Upsert
await xata.db.posts.createOrUpdate("rec_abc123", { title: "Updated Title" });
```

## Queries and Filtering

```ts
// List with filters
const posts = await xata.db.posts
  .filter({ status: "published" })
  .sort("publishedAt", "desc")
  .select(["title", "slug", "publishedAt", "author.name"])
  .getPaginated({ pagination: { size: 20 } });

// Complex filters
const results = await xata.db.posts
  .filter({
    $all: [
      { status: "published" },
      { $any: [{ "tags": { $includes: "react" } }, { "tags": { $includes: "vue" } }] },
      { publishedAt: { $ge: new Date("2024-01-01") } },
    ],
  })
  .getMany();

// Aggregations
const stats = await xata.db.posts.aggregate({
  totalPosts: { count: "*" },
  byStatus: { topValues: { column: "status" } },
  avgLength: { average: { column: "content" } },
});
```

## Full-Text Search

```ts
const results = await xata.db.posts.search("react server components", {
  target: [
    { column: "title", weight: 3 },
    { column: "content", weight: 1 },
  ],
  filter: { status: "published" },
  fuzziness: 1,
  page: { size: 10 },
});
```

## Vector Search

```ts
// Store embedding
await xata.db.posts.update("rec_abc123", {
  embedding: await generateEmbedding(post.content),
});

// Vector similarity search
const similar = await xata.db.posts.vectorSearch("embedding", queryVector, {
  size: 5,
  filter: { status: "published" },
});
```

## Additional Resources

- Xata: https://xata.io/docs
- TypeScript SDK: https://xata.io/docs/sdk/typescript/overview
- Search: https://xata.io/docs/sdk/search
