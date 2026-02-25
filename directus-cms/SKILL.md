---
name: directus-cms
description: Directus CMS patterns covering headless content management, REST/GraphQL APIs, custom flows, role-based access, file storage, Directus SDK, and self-hosted or cloud deployment.
---

# Directus CMS

This skill should be used when building content-driven applications with Directus as a headless CMS. It covers data modeling, APIs, flows, permissions, and SDK integration.

## When to Use This Skill

Use this skill when you need to:

- Set up a headless CMS with visual data modeling
- Query content via REST or GraphQL APIs
- Create custom automation flows
- Manage role-based access and permissions
- Integrate Directus with frontend frameworks

## Setup

```bash
npx create-directus-project my-project
# or Docker
docker run -d -p 8055:8055 directus/directus

# JavaScript SDK
npm install @directus/sdk
```

## SDK Client

```ts
import { createDirectus, rest, authentication, realtime } from "@directus/sdk";

interface Schema {
  posts: Post[];
  categories: Category[];
}

interface Post {
  id: string;
  title: string;
  content: string;
  status: "draft" | "published";
  category: string | Category;
  date_created: string;
}

const client = createDirectus<Schema>("http://localhost:8055")
  .with(authentication())
  .with(rest())
  .with(realtime());

// Authenticate
await client.login("admin@example.com", "password");
```

## CRUD Operations

```ts
import { readItems, readItem, createItem, updateItem, deleteItem } from "@directus/sdk";

// List with filters
const posts = await client.request(
  readItems("posts", {
    filter: { status: { _eq: "published" } },
    sort: ["-date_created"],
    limit: 20,
    offset: 0,
    fields: ["id", "title", "content", { category: ["id", "name"] }],
  })
);

// Get single item
const post = await client.request(
  readItem("posts", "item-id", {
    fields: ["*", { category: ["*"] }],
  })
);

// Create
const newPost = await client.request(
  createItem("posts", {
    title: "New Post",
    content: "<p>Hello World</p>",
    status: "draft",
    category: "category-id",
  })
);

// Update
await client.request(
  updateItem("posts", "item-id", { status: "published" })
);

// Delete
await client.request(deleteItem("posts", "item-id"));
```

## Real-Time Subscriptions

```ts
const { subscription } = await client.subscribe("posts", {
  query: {
    filter: { status: { _eq: "published" } },
    fields: ["id", "title", "content"],
  },
});

for await (const event of subscription) {
  console.log(event.event); // "create", "update", "delete"
  console.log(event.data);
}
```

## File Uploads

```ts
import { uploadFiles } from "@directus/sdk";

const formData = new FormData();
formData.append("file", fileInput.files[0]);
formData.append("title", "My Image");

const file = await client.request(uploadFiles(formData));

// Get file URL
const imageUrl = `${DIRECTUS_URL}/assets/${file.id}?width=800&height=600&fit=cover`;
```

## Custom Flows (Automation)

```json
{
  "name": "Notify on Publish",
  "trigger": "event",
  "options": {
    "type": "action",
    "scope": ["items.update"],
    "collections": ["posts"]
  },
  "operations": [
    {
      "name": "Check Status",
      "type": "condition",
      "options": {
        "filter": { "$trigger.payload.status": { "_eq": "published" } }
      }
    },
    {
      "name": "Send Webhook",
      "type": "request",
      "options": {
        "url": "https://api.example.com/notify",
        "method": "POST",
        "body": { "title": "{{$trigger.payload.title}}" }
      }
    }
  ]
}
```

## Additional Resources

- Directus: https://directus.io/
- SDK Reference: https://docs.directus.io/reference/sdk.html
- Flows: https://docs.directus.io/app/flows.html
