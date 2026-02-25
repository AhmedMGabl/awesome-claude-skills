---
name: upstash-serverless
description: Upstash serverless data services covering Redis REST API, QStash message queues, Vector for embeddings search, rate limiting, session management, caching, and integration with Next.js and Vercel Edge.
---

# Upstash Serverless

This skill should be used when using Upstash serverless data services. It covers Redis, QStash, Vector, rate limiting, and edge integration.

## When to Use This Skill

Use this skill when you need to:

- Use Redis from serverless/edge environments
- Implement rate limiting with @upstash/ratelimit
- Queue background jobs with QStash
- Store and search vector embeddings
- Add caching to serverless applications

## Upstash Redis

```typescript
import { Redis } from "@upstash/redis";

const redis = Redis.fromEnv(); // Uses UPSTASH_REDIS_REST_URL + TOKEN

// Basic operations
await redis.set("user:123", { name: "John", email: "john@example.com" });
await redis.set("session:abc", "user:123", { ex: 3600 }); // TTL 1 hour

const user = await redis.get<{ name: string; email: string }>("user:123");

// Pipeline
const results = await redis.pipeline()
  .incr("page:views")
  .expire("page:views", 86400)
  .get("page:views")
  .exec();

// Hash
await redis.hset("user:123:profile", { bio: "Developer", location: "NYC" });
const profile = await redis.hgetall("user:123:profile");
```

## Rate Limiting

```typescript
import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis";

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, "10 s"), // 10 requests per 10 seconds
  analytics: true,
});

// Next.js middleware
import { NextRequest, NextResponse } from "next/server";

export async function middleware(request: NextRequest) {
  const ip = request.headers.get("x-forwarded-for") ?? "anonymous";
  const { success, limit, remaining, reset } = await ratelimit.limit(ip);

  if (!success) {
    return NextResponse.json({ error: "Rate limited" }, {
      status: 429,
      headers: {
        "X-RateLimit-Limit": limit.toString(),
        "X-RateLimit-Remaining": remaining.toString(),
        "X-RateLimit-Reset": reset.toString(),
      },
    });
  }

  return NextResponse.next();
}
```

## QStash (Message Queue)

```typescript
import { Client } from "@upstash/qstash";

const qstash = new Client({ token: process.env.QSTASH_TOKEN! });

// Publish message to endpoint
await qstash.publishJSON({
  url: "https://myapp.com/api/process",
  body: { userId: "123", action: "send-welcome-email" },
  retries: 3,
  delay: "10s",
});

// Schedule recurring job
await qstash.schedules.create({
  destination: "https://myapp.com/api/cleanup",
  cron: "0 0 * * *", // Daily at midnight
});

// Receiver — verify signature
import { Receiver } from "@upstash/qstash";

const receiver = new Receiver({
  currentSigningKey: process.env.QSTASH_CURRENT_SIGNING_KEY!,
  nextSigningKey: process.env.QSTASH_NEXT_SIGNING_KEY!,
});

export async function POST(request: Request) {
  const body = await request.text();
  const signature = request.headers.get("upstash-signature")!;
  const isValid = await receiver.verify({ body, signature });

  if (!isValid) return new Response("Unauthorized", { status: 401 });

  const data = JSON.parse(body);
  // Process message...
  return new Response("OK");
}
```

## Upstash Vector

```typescript
import { Index } from "@upstash/vector";

const index = new Index({
  url: process.env.UPSTASH_VECTOR_REST_URL!,
  token: process.env.UPSTASH_VECTOR_REST_TOKEN!,
});

// Upsert vectors
await index.upsert([
  { id: "doc-1", vector: embedding, metadata: { title: "Doc 1", category: "tech" } },
  { id: "doc-2", vector: embedding2, metadata: { title: "Doc 2", category: "science" } },
]);

// Query similar vectors
const results = await index.query({
  vector: queryEmbedding,
  topK: 5,
  includeMetadata: true,
  filter: "category = 'tech'",
});
```

## Caching Pattern

```typescript
import { Redis } from "@upstash/redis";

const redis = Redis.fromEnv();

async function cachedFetch<T>(key: string, fetcher: () => Promise<T>, ttl = 300): Promise<T> {
  const cached = await redis.get<T>(key);
  if (cached) return cached;

  const data = await fetcher();
  await redis.set(key, data, { ex: ttl });
  return data;
}

// Usage
const posts = await cachedFetch("posts:latest", () => db.query.posts.findMany(), 60);
```

## Additional Resources

- Upstash docs: https://upstash.com/docs
- QStash: https://upstash.com/docs/qstash
- Upstash Vector: https://upstash.com/docs/vector
