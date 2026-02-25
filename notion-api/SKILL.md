---
name: notion-api
description: Notion API integration covering database queries, page creation, block manipulation, property types, filters and sorts, pagination, OAuth authentication, and webhook-like polling patterns.
---

# Notion API

This skill should be used when integrating Notion into applications. It covers database queries, page and block operations, property types, pagination, and OAuth for third-party app authorization.

## When to Use This Skill

- Query or create Notion databases from an application
- Create, update, or archive Notion pages programmatically
- Manipulate page blocks (append, update, delete content)
- Implement OAuth so users can connect their own Notion workspaces
- Poll Notion for changes as a webhook substitute

## Client Setup

```bash
npm install @notionhq/client
```

```typescript
// lib/notion.ts
import { Client } from "@notionhq/client";
export const notion = new Client({ auth: process.env.NOTION_TOKEN });
```

## Database Queries with Filters and Sorts

```typescript
const response = await notion.databases.query({
  database_id: databaseId,
  filter: {
    and: [
      { property: "Status", select: { equals: "In Progress" } },
      { property: "Due Date", date: { on_or_before: new Date().toISOString() } },
    ],
  },
  sorts: [
    { property: "Priority", direction: "descending" },
    { property: "Due Date", direction: "ascending" },
  ],
  page_size: 50,
});
```

## Creating and Updating Pages

```typescript
// Create a page in a database
await notion.pages.create({
  parent: { database_id: databaseId },
  properties: {
    Name: { title: [{ text: { content: "New Task" } }] },
    Status: { select: { name: "Todo" } },
    Tags: { multi_select: [{ name: "feature" }] },
    "Due Date": { date: { start: "2026-03-01" } },
  },
});

// Update properties on an existing page
await notion.pages.update({
  page_id: pageId,
  properties: { Status: { select: { name: "Done" } } },
});

// Archive (soft-delete) a page
await notion.pages.update({ page_id: pageId, archived: true });
```

## Property Types Reference

```typescript
// title
Name: { title: [{ text: { content: "Title" } }] }

// rich_text
Notes: { rich_text: [{ text: { content: "Some text" } }] }

// select / multi_select
Status: { select: { name: "Active" } }
Tags:   { multi_select: [{ name: "tag1" }, { name: "tag2" }] }

// date (optional end for ranges)
Range: { date: { start: "2026-03-01", end: "2026-03-15" } }

// number / checkbox / url
Score:   { number: 42 }
Done:    { checkbox: true }
Website: { url: "https://example.com" }

// relation — link to pages in another database
Project: { relation: [{ id: "target-page-id" }] }

// formula and rollup are read-only
```

## Reading Property Values

```typescript
import { PageObjectResponse } from "@notionhq/client/build/src/api-endpoints";

function getTitle(page: PageObjectResponse): string {
  const prop = page.properties["Name"];
  return prop.type === "title"
    ? prop.title.map((t) => t.plain_text).join("")
    : "";
}

function getSelect(page: PageObjectResponse, key: string): string | null {
  const prop = page.properties[key];
  return prop.type === "select" ? (prop.select?.name ?? null) : null;
}
```

## Block Manipulation

```typescript
// Append blocks to a page
await notion.blocks.children.append({
  block_id: pageId,
  children: [
    { object: "block", type: "heading_2",
      heading_2: { rich_text: [{ text: { content: "Summary" } }] } },
    { object: "block", type: "paragraph",
      paragraph: { rich_text: [{ text: { content: "Details here." } }] } },
    { object: "block", type: "bulleted_list_item",
      bulleted_list_item: { rich_text: [{ text: { content: "Item one" } }] } },
  ],
});

await notion.blocks.update({ block_id: blockId,
  paragraph: { rich_text: [{ text: { content: "Updated." } }] } });

await notion.blocks.delete({ block_id: blockId });
```

## Pagination Handling

```typescript
async function getAllPages(databaseId: string) {
  const pages = [];
  let cursor: string | undefined;

  do {
    const res = await notion.databases.query({
      database_id: databaseId,
      start_cursor: cursor,
      page_size: 100,
    });
    pages.push(...res.results);
    cursor = res.has_more ? (res.next_cursor ?? undefined) : undefined;
  } while (cursor);

  return pages;
}
```

## OAuth Integration

```typescript
// Step 1: Build authorization URL
function getAuthUrl(state: string) {
  const params = new URLSearchParams({
    client_id: process.env.NOTION_CLIENT_ID!,
    response_type: "code",
    owner: "user",
    redirect_uri: process.env.NOTION_REDIRECT_URI!,
    state,
  });
  return `https://api.notion.com/v1/oauth/authorize?${params}`;
}

// Step 2: Exchange code for access token
async function exchangeCode(code: string) {
  const creds = Buffer.from(
    `${process.env.NOTION_CLIENT_ID}:${process.env.NOTION_CLIENT_SECRET}`
  ).toString("base64");

  const res = await fetch("https://api.notion.com/v1/oauth/token", {
    method: "POST",
    headers: { Authorization: `Basic ${creds}`, "Content-Type": "application/json" },
    body: JSON.stringify({ grant_type: "authorization_code", code,
      redirect_uri: process.env.NOTION_REDIRECT_URI }),
  });
  return res.json() as Promise<{ access_token: string; workspace_id: string }>;
}

// Step 3: Create a per-user client from the stored token
const userNotion = new Client({ auth: storedAccessToken });
```

## Webhook-Like Polling

Notion does not provide webhooks. Poll using `last_edited_time` on a timer.

```typescript
async function pollChanges(databaseId: string, since: Date) {
  const res = await notion.databases.query({
    database_id: databaseId,
    filter: { timestamp: "last_edited_time",
      last_edited_time: { on_or_after: since.toISOString() } },
  });
  return res.results;
}

setInterval(async () => {
  const changed = await pollChanges(DB_ID, new Date(Date.now() - 60_000));
  for (const page of changed) await processChange(page);
}, 60_000);
```

## TypeScript Types

```typescript
import type {
  PageObjectResponse,
  DatabaseObjectResponse,
  BlockObjectResponse,
  QueryDatabaseResponse,
} from "@notionhq/client/build/src/api-endpoints";

// Type guard for full page responses (partial pages lack properties)
function isFullPage(p: unknown): p is PageObjectResponse {
  return typeof p === "object" && p !== null && "properties" in p;
}
```

## Additional Resources

- Notion API Reference: https://developers.notion.com/reference
- Notion SDK (JS/TS): https://github.com/makenotion/notion-sdk-js
- OAuth Guide: https://developers.notion.com/docs/authorization
