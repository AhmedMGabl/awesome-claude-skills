---
name: val-town
description: Val Town serverless functions covering vals, HTTP handlers, cron jobs, email handlers, blob storage, SQLite database, environment variables, and TypeScript-first development patterns.
---

# Val Town

This skill should be used when building serverless functions on Val Town. It covers HTTP endpoints, scheduled tasks, email handling, storage, and database access.

## When to Use This Skill

Use this skill when you need to:

- Create quick serverless HTTP endpoints
- Schedule recurring tasks (cron)
- Process incoming emails programmatically
- Store data with built-in SQLite
- Build and share TypeScript utilities

## HTTP Handler

```typescript
// HTTP endpoint val
export default async function handler(req: Request): Promise<Response> {
  const url = new URL(req.url);

  if (req.method === "GET") {
    const name = url.searchParams.get("name") ?? "World";
    return Response.json({ message: `Hello, ${name}!` });
  }

  if (req.method === "POST") {
    const body = await req.json();
    const result = await processData(body);
    return Response.json(result, { status: 201 });
  }

  return new Response("Method Not Allowed", { status: 405 });
}
```

## Cron Job

```typescript
// Scheduled val - runs on a cron schedule
export default async function dailyReport() {
  const stats = await fetchDailyStats();
  await sendSlackNotification(stats);
  console.log("Daily report sent:", stats);
}
```

## SQLite Database

```typescript
import { sqlite } from "https://esm.town/v/std/sqlite";

// Create table
await sqlite.execute(`
  CREATE TABLE IF NOT EXISTS bookmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    title TEXT,
    tags TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )
`);

// Insert
await sqlite.execute(
  "INSERT INTO bookmarks (url, title, tags) VALUES (?, ?, ?)",
  ["https://example.com", "Example", "reference,web"],
);

// Query
const bookmarks = await sqlite.execute("SELECT * FROM bookmarks ORDER BY created_at DESC LIMIT 20");
```

## Blob Storage

```typescript
import { blob } from "https://esm.town/v/std/blob";

// Store data
await blob.setJSON("config", { theme: "dark", lang: "en" });
await blob.set("avatar.png", imageBuffer);

// Retrieve data
const config = await blob.getJSON("config");
const avatar = await blob.get("avatar.png");

// List keys
const keys = await blob.list("config");
```

## Email Handler

```typescript
// Email handler val - triggered by emails sent to your val address
export default async function emailHandler(email: {
  from: string;
  to: string[];
  subject: string;
  text: string;
  html: string;
}) {
  console.log(`Email from ${email.from}: ${email.subject}`);

  // Process and store
  await sqlite.execute(
    "INSERT INTO inbox (sender, subject, body) VALUES (?, ?, ?)",
    [email.from, email.subject, email.text],
  );
}
```

## Additional Resources

- Val Town docs: https://docs.val.town/
- Standard library: https://docs.val.town/std/
- Examples: https://val.town/examples
