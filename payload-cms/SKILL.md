---
name: payload-cms
description: Payload CMS headless content management covering collection and global configs, access control, hooks, custom endpoints, rich text with Lexical editor, file uploads, localization, draft and version history, GraphQL and REST APIs, and Next.js integration.
---

# Payload CMS

This skill should be used when building applications with Payload CMS. It covers collections, access control, hooks, rich text, localization, and Next.js integration.

## When to Use This Skill

Use this skill when you need to:

- Build a self-hosted headless CMS with TypeScript
- Define collections with complex access control
- Implement hooks for business logic
- Handle rich text content and media
- Integrate CMS with a Next.js frontend

## Collection Configuration

```typescript
// collections/Posts.ts
import { CollectionConfig } from "payload";

export const Posts: CollectionConfig = {
  slug: "posts",
  admin: {
    useAsTitle: "title",
    defaultColumns: ["title", "author", "status", "publishedAt"],
  },
  access: {
    read: () => true,
    create: ({ req }) => !!req.user,
    update: ({ req }) => req.user?.role === "admin" || req.user?.role === "editor",
    delete: ({ req }) => req.user?.role === "admin",
  },
  versions: { drafts: true },
  fields: [
    { name: "title", type: "text", required: true },
    {
      name: "slug",
      type: "text",
      unique: true,
      admin: { position: "sidebar" },
      hooks: {
        beforeValidate: [({ value, data }) => {
          if (!value && data?.title) {
            return data.title.toLowerCase().replace(/\s+/g, "-").replace(/[^a-z0-9-]/g, "");
          }
          return value;
        }],
      },
    },
    {
      name: "author",
      type: "relationship",
      relationTo: "users",
      required: true,
    },
    {
      name: "content",
      type: "richText", // Lexical editor
    },
    {
      name: "featuredImage",
      type: "upload",
      relationTo: "media",
    },
    {
      name: "categories",
      type: "relationship",
      relationTo: "categories",
      hasMany: true,
    },
    {
      name: "status",
      type: "select",
      options: [
        { label: "Draft", value: "draft" },
        { label: "Published", value: "published" },
      ],
      defaultValue: "draft",
      admin: { position: "sidebar" },
    },
    {
      name: "publishedAt",
      type: "date",
      admin: { position: "sidebar" },
    },
  ],
};
```

## Payload Config

```typescript
// payload.config.ts
import { buildConfig } from "payload";
import { postgresAdapter } from "@payloadcms/db-postgres";
import { lexicalEditor } from "@payloadcms/richtext-lexical";
import { s3Storage } from "@payloadcms/storage-s3";
import { Posts } from "./collections/Posts";
import { Users } from "./collections/Users";
import { Media } from "./collections/Media";

export default buildConfig({
  admin: { user: Users.slug },
  collections: [Users, Posts, Media],
  db: postgresAdapter({ pool: { connectionString: process.env.DATABASE_URL! } }),
  editor: lexicalEditor(),
  plugins: [
    s3Storage({
      collections: { media: true },
      bucket: process.env.S3_BUCKET!,
      config: {
        region: process.env.S3_REGION!,
        credentials: {
          accessKeyId: process.env.S3_ACCESS_KEY!,
          secretAccessKey: process.env.S3_SECRET_KEY!,
        },
      },
    }),
  ],
  typescript: { outputFile: "payload-types.ts" },
});
```

## Hooks

```typescript
// collections/Posts.ts — hooks
hooks: {
  beforeChange: [
    ({ data, req, operation }) => {
      if (operation === "create") {
        data.author = req.user?.id;
      }
      if (data.status === "published" && !data.publishedAt) {
        data.publishedAt = new Date().toISOString();
      }
      return data;
    },
  ],
  afterChange: [
    async ({ doc, operation }) => {
      if (operation === "create" || doc.status === "published") {
        // Revalidate Next.js page
        await fetch(`${process.env.NEXT_URL}/api/revalidate?path=/blog/${doc.slug}`);
      }
    },
  ],
},
```

## Querying from Next.js

```typescript
import { getPayload } from "payload";
import config from "@payload-config";

async function getPosts() {
  const payload = await getPayload({ config });

  const { docs } = await payload.find({
    collection: "posts",
    where: { status: { equals: "published" } },
    sort: "-publishedAt",
    limit: 10,
    depth: 2, // populate relationships
  });

  return docs;
}

async function getPost(slug: string) {
  const payload = await getPayload({ config });

  const { docs } = await payload.find({
    collection: "posts",
    where: { slug: { equals: slug } },
    limit: 1,
    depth: 2,
  });

  return docs[0] ?? null;
}
```

## Access Control Patterns

```typescript
// Fine-grained field-level access
{
  name: "internalNotes",
  type: "textarea",
  access: {
    read: ({ req }) => req.user?.role === "admin",
    update: ({ req }) => req.user?.role === "admin",
  },
}

// Row-level access — users can only edit their own posts
access: {
  update: ({ req }) => {
    if (req.user?.role === "admin") return true;
    return { author: { equals: req.user?.id } };
  },
}
```

## CLI Commands

```bash
npx create-payload-app@latest    # Create new project
pnpm dev                         # Start dev server
pnpm payload generate:types      # Generate TypeScript types
pnpm payload migrate             # Run migrations
```

## Additional Resources

- Payload docs: https://payloadcms.com/docs
- Payload + Next.js: https://payloadcms.com/docs/getting-started/installation
- Payload examples: https://github.com/payloadcms/payload/tree/main/examples
