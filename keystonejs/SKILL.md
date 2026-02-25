---
name: keystonejs
description: KeystoneJS patterns covering schema-driven CMS, list definitions, field types, access control, hooks, GraphQL API, document fields, admin UI customization, and Next.js integration.
---

# KeystoneJS

This skill should be used when building content management systems with KeystoneJS. It covers schema definitions, access control, hooks, GraphQL API, and admin UI.

## When to Use This Skill

Use this skill when you need to:

- Build a schema-driven headless CMS
- Define lists with typed fields and validation
- Implement access control and authentication
- Use hooks for custom business logic
- Generate GraphQL APIs from schemas

## Setup

```bash
npm init keystone-app@latest
# or add to existing project
npm install @keystone-6/core @keystone-6/auth @keystone-6/fields-document
```

## Schema Definition

```ts
// keystone.ts
import { config, list } from "@keystone-6/core";
import { text, timestamp, select, relationship, image, integer } from "@keystone-6/core/fields";
import { document } from "@keystone-6/fields-document";
import { allowAll } from "@keystone-6/core/access";

const Post = list({
  access: allowAll,
  fields: {
    title: text({ validation: { isRequired: true } }),
    slug: text({ isIndexed: "unique", validation: { isRequired: true } }),
    status: select({
      options: [
        { label: "Draft", value: "draft" },
        { label: "Published", value: "published" },
        { label: "Archived", value: "archived" },
      ],
      defaultValue: "draft",
      ui: { displayMode: "segmented-control" },
    }),
    content: document({
      formatting: true,
      links: true,
      dividers: true,
      layouts: [
        [1, 1],
        [1, 1, 1],
      ],
    }),
    publishDate: timestamp(),
    author: relationship({ ref: "User.posts", many: false }),
    tags: relationship({ ref: "Tag.posts", many: true }),
    heroImage: image({ storage: "local_images" }),
  },
  hooks: {
    resolveInput: ({ resolvedData }) => {
      if (resolvedData.title && !resolvedData.slug) {
        resolvedData.slug = resolvedData.title.toLowerCase().replace(/\s+/g, "-");
      }
      return resolvedData;
    },
  },
});

const User = list({
  access: allowAll,
  fields: {
    name: text({ validation: { isRequired: true } }),
    email: text({ isIndexed: "unique", validation: { isRequired: true } }),
    password: password(),
    posts: relationship({ ref: "Post.author", many: true }),
    role: select({
      options: [
        { label: "Admin", value: "admin" },
        { label: "Editor", value: "editor" },
        { label: "Author", value: "author" },
      ],
      defaultValue: "author",
    }),
  },
});

const Tag = list({
  access: allowAll,
  fields: {
    name: text({ validation: { isRequired: true } }),
    posts: relationship({ ref: "Post.tags", many: true }),
  },
});

export default config({
  db: { provider: "postgresql", url: process.env.DATABASE_URL! },
  lists: { Post, User, Tag },
  storage: {
    local_images: {
      kind: "local",
      type: "image",
      generateUrl: (path) => `/images${path}`,
      serverRoute: { path: "/images" },
      storagePath: "public/images",
    },
  },
});
```

## Access Control

```ts
import { list } from "@keystone-6/core";

const Post = list({
  access: {
    operation: {
      query: () => true,
      create: ({ session }) => !!session,
      update: ({ session }) => !!session,
      delete: ({ session }) => session?.data.role === "admin",
    },
    filter: {
      query: ({ session }) => {
        if (session?.data.role === "admin") return {};
        return { status: { equals: "published" } };
      },
      update: ({ session }) => {
        if (session?.data.role === "admin") return {};
        return { author: { id: { equals: session?.itemId } } };
      },
    },
  },
  fields: { /* ... */ },
});
```

## GraphQL Queries

```graphql
# List posts
query {
  posts(where: { status: { equals: "published" } }, orderBy: { publishDate: desc }, take: 10) {
    id
    title
    slug
    status
    publishDate
    author { name }
    tags { name }
    content { document }
  }
}

# Single post
query {
  post(where: { slug: "my-post" }) {
    id
    title
    content { document }
    author { name email }
  }
}

# Create post
mutation {
  createPost(data: {
    title: "New Post"
    status: "draft"
    author: { connect: { id: "user-id" } }
    tags: { connect: [{ id: "tag-id" }] }
  }) {
    id
    title
  }
}
```

## Authentication

```ts
import { createAuth } from "@keystone-6/auth";
import { statelessSessions } from "@keystone-6/core/session";

const { withAuth } = createAuth({
  listKey: "User",
  identityField: "email",
  secretField: "password",
  sessionData: "name role",
  initFirstItem: {
    fields: ["name", "email", "password"],
    itemData: { role: "admin" },
  },
});

const session = statelessSessions({
  secret: process.env.SESSION_SECRET!,
  maxAge: 60 * 60 * 24 * 30, // 30 days
});

export default withAuth(config({ /* ... */, session }));
```

## Additional Resources

- KeystoneJS: https://keystonejs.com/
- Fields: https://keystonejs.com/docs/fields/overview
- Access Control: https://keystonejs.com/docs/config/access-control
