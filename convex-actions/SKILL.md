---
name: convex-actions
description: Convex actions patterns covering server-side actions, internal functions, HTTP endpoints, scheduled jobs, file storage, vector search, aggregation, and integration with external APIs and third-party services.
---

# Convex Actions

This skill should be used when building server-side actions and integrations with Convex. It covers actions, HTTP endpoints, scheduled jobs, file storage, and external API integration.

## When to Use This Skill

Use this skill when you need to:

- Call external APIs from Convex functions
- Build HTTP endpoints for webhooks
- Schedule background jobs and cron tasks
- Handle file uploads and storage
- Implement vector search and aggregation

## Actions (External API Calls)

```typescript
// convex/actions.ts
import { action } from "./_generated/server";
import { v } from "convex/values";

export const sendEmail = action({
  args: {
    to: v.string(),
    subject: v.string(),
    body: v.string(),
  },
  handler: async (ctx, args) => {
    // Actions can call external APIs
    const response = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${process.env.RESEND_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: "noreply@example.com",
        to: args.to,
        subject: args.subject,
        html: args.body,
      }),
    });

    if (!response.ok) {
      throw new Error(`Email failed: ${response.statusText}`);
    }

    // Actions can also call mutations
    await ctx.runMutation(internal.emails.logSent, {
      to: args.to,
      subject: args.subject,
    });

    return { success: true };
  },
});

// Generate with AI
export const generateSummary = action({
  args: { documentId: v.id("documents") },
  handler: async (ctx, args) => {
    // Read from database via query
    const doc = await ctx.runQuery(internal.documents.getById, {
      id: args.documentId,
    });

    if (!doc) throw new Error("Document not found");

    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "x-api-key": process.env.ANTHROPIC_API_KEY!,
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: "claude-sonnet-4-20250514",
        max_tokens: 500,
        messages: [{ role: "user", content: `Summarize: ${doc.content}` }],
      }),
    });

    const result = await response.json();
    const summary = result.content[0].text;

    // Save result back to database
    await ctx.runMutation(internal.documents.updateSummary, {
      id: args.documentId,
      summary,
    });

    return { summary };
  },
});
```

## HTTP Endpoints

```typescript
// convex/http.ts
import { httpRouter } from "convex/server";
import { httpAction } from "./_generated/server";
import { internal } from "./_generated/api";

const http = httpRouter();

// Webhook handler
http.route({
  path: "/webhooks/stripe",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    const signature = request.headers.get("stripe-signature");
    const body = await request.text();

    // Verify webhook
    const event = verifyStripeWebhook(body, signature!);

    // Process event
    await ctx.runMutation(internal.payments.handleWebhook, {
      type: event.type,
      data: event.data,
    });

    return new Response("OK", { status: 200 });
  }),
});

// REST-style endpoint
http.route({
  path: "/api/public/products",
  method: "GET",
  handler: httpAction(async (ctx) => {
    const products = await ctx.runQuery(internal.products.listPublic);
    return new Response(JSON.stringify(products), {
      headers: { "Content-Type": "application/json" },
    });
  }),
});

export default http;
```

## Scheduled Jobs

```typescript
// convex/crons.ts
import { cronJobs } from "convex/server";
import { internal } from "./_generated/api";

const crons = cronJobs();

// Run every hour
crons.interval("cleanup-expired", { hours: 1 }, internal.cleanup.removeExpired);

// Cron expression
crons.cron("daily-digest", "0 9 * * *", internal.notifications.sendDailyDigest);

// Monthly billing
crons.cron("monthly-billing", "0 0 1 * *", internal.billing.processMonthly);

export default crons;

// Schedule from mutations
export const scheduleReminder = mutation({
  args: { userId: v.id("users"), message: v.string(), delayMs: v.number() },
  handler: async (ctx, args) => {
    await ctx.scheduler.runAfter(args.delayMs, internal.notifications.sendReminder, {
      userId: args.userId,
      message: args.message,
    });
  },
});
```

## File Storage

```typescript
// Generate upload URL
export const generateUploadUrl = mutation(async (ctx) => {
  return await ctx.storage.generateUploadUrl();
});

// Save file reference
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

// Get file URL
export const getFileUrl = query({
  args: { storageId: v.id("_storage") },
  handler: async (ctx, args) => {
    return await ctx.storage.getUrl(args.storageId);
  },
});
```

## Vector Search

```typescript
// Schema with vector index
export default defineSchema({
  documents: defineTable({
    content: v.string(),
    embedding: v.array(v.float64()),
  }).vectorIndex("by_embedding", {
    vectorField: "embedding",
    dimensions: 1536,
  }),
});

// Search by vector similarity
export const searchSimilar = query({
  args: { embedding: v.array(v.float64()) },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("documents")
      .withIndex("by_embedding", (q) =>
        q.vector(args.embedding, 10)
      )
      .collect();
  },
});
```

## Additional Resources

- Convex actions: https://docs.convex.dev/functions/actions
- HTTP endpoints: https://docs.convex.dev/functions/http-actions
- Scheduled functions: https://docs.convex.dev/scheduling/scheduled-functions
