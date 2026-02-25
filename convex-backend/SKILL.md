---
name: convex-backend
description: Convex backend-as-a-service covering reactive queries, mutations, actions, file storage, scheduled functions, authentication with Clerk, real-time subscriptions, full-text search, database schema validation, and deployment patterns.
---

# Convex Backend

This skill should be used when building applications with Convex as a backend. It covers reactive queries, mutations, actions, real-time data, and authentication.

## When to Use This Skill

Use this skill when you need to:

- Build real-time applications with automatic reactivity
- Define type-safe database schemas and queries
- Handle file storage and scheduled functions
- Integrate authentication with Clerk or Auth0
- Deploy serverless backend logic

## Schema Definition

```typescript
// convex/schema.ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  users: defineTable({
    name: v.string(),
    email: v.string(),
    avatarUrl: v.optional(v.string()),
    tokenIdentifier: v.string(),
  }).index("by_token", ["tokenIdentifier"]),

  messages: defineTable({
    body: v.string(),
    userId: v.id("users"),
    channelId: v.id("channels"),
  }).index("by_channel", ["channelId"]),

  channels: defineTable({
    name: v.string(),
    description: v.optional(v.string()),
  }),
});
```

## Queries (Reactive)

```typescript
// convex/messages.ts
import { query } from "./_generated/server";
import { v } from "convex/values";

export const list = query({
  args: { channelId: v.id("channels"), limit: v.optional(v.number()) },
  handler: async (ctx, args) => {
    const messages = await ctx.db
      .query("messages")
      .withIndex("by_channel", (q) => q.eq("channelId", args.channelId))
      .order("desc")
      .take(args.limit ?? 50);

    return Promise.all(
      messages.map(async (msg) => {
        const user = await ctx.db.get(msg.userId);
        return { ...msg, author: user?.name ?? "Unknown" };
      }),
    );
  },
});
```

## Mutations

```typescript
// convex/messages.ts
import { mutation } from "./_generated/server";
import { v } from "convex/values";

export const send = mutation({
  args: { body: v.string(), channelId: v.id("channels") },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");

    const user = await ctx.db
      .query("users")
      .withIndex("by_token", (q) => q.eq("tokenIdentifier", identity.tokenIdentifier))
      .unique();

    if (!user) throw new Error("User not found");

    return ctx.db.insert("messages", {
      body: args.body,
      userId: user._id,
      channelId: args.channelId,
    });
  },
});
```

## React Integration

```tsx
import { useQuery, useMutation } from "convex/react";
import { api } from "../convex/_generated/api";

function Chat({ channelId }: { channelId: Id<"channels"> }) {
  const messages = useQuery(api.messages.list, { channelId });
  const sendMessage = useMutation(api.messages.send);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    const body = new FormData(form).get("body") as string;
    await sendMessage({ body, channelId });
    form.reset();
  }

  return (
    <div>
      {messages?.map((msg) => (
        <div key={msg._id}>
          <strong>{msg.author}</strong>: {msg.body}
        </div>
      ))}
      <form onSubmit={handleSubmit}>
        <input name="body" placeholder="Type a message..." />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}
```

## Actions (External API Calls)

```typescript
// convex/actions.ts
import { action } from "./_generated/server";
import { v } from "convex/values";
import { api } from "./_generated/api";

export const generateSummary = action({
  args: { channelId: v.id("channels") },
  handler: async (ctx, args) => {
    const messages = await ctx.runQuery(api.messages.list, {
      channelId: args.channelId,
      limit: 20,
    });

    const response = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
      },
      body: JSON.stringify({
        model: "gpt-4o-mini",
        messages: [
          { role: "system", content: "Summarize this conversation." },
          { role: "user", content: messages.map((m) => `${m.author}: ${m.body}`).join("\n") },
        ],
      }),
    });

    const data = await response.json();
    return data.choices[0].message.content;
  },
});
```

## Scheduled Functions

```typescript
import { cronJobs } from "convex/server";
import { internal } from "./_generated/api";

const crons = cronJobs();

crons.interval("clean old messages", { hours: 24 }, internal.cleanup.removeOldMessages);
crons.cron("daily digest", "0 9 * * *", internal.notifications.sendDailyDigest);

export default crons;
```

## CLI Commands

```bash
npx convex dev           # Start dev mode
npx convex deploy        # Deploy to production
npx convex run messages:list '{"channelId": "..."}' # Run function
npx convex import --table users data.jsonl # Import data
```

## Additional Resources

- Convex docs: https://docs.convex.dev/
- Convex + React: https://docs.convex.dev/client/react
- Convex dashboard: https://dashboard.convex.dev/
