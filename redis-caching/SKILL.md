---
name: redis-caching
description: Redis caching strategies covering cache-aside, write-through, and write-behind patterns, TTL management, cache invalidation, Redis data structures for caching, session storage, pub/sub messaging, rate limiting with Redis, and clustering for high availability.
---

# Redis Caching

This skill should be used when implementing Redis-based caching solutions. It covers caching patterns, data structures, session management, pub/sub, and production deployment.

## When to Use This Skill

Use this skill when you need to:

- Implement application-level caching with Redis
- Choose between caching strategies (cache-aside, write-through)
- Build rate limiters or session stores
- Use Redis pub/sub for real-time messaging
- Configure Redis for production workloads

## Cache-Aside Pattern

```typescript
import { Redis } from "ioredis";

const redis = new Redis({
  host: process.env.REDIS_HOST || "localhost",
  port: 6379,
  maxRetriesPerRequest: 3,
  retryStrategy: (times) => Math.min(times * 50, 2000),
});

async function getUser(userId: string) {
  const cacheKey = `user:${userId}`;

  // 1. Check cache first
  const cached = await redis.get(cacheKey);
  if (cached) return JSON.parse(cached);

  // 2. Cache miss — fetch from database
  const user = await db.users.findUnique({ where: { id: userId } });
  if (!user) return null;

  // 3. Store in cache with TTL
  await redis.set(cacheKey, JSON.stringify(user), "EX", 3600); // 1 hour

  return user;
}

// Invalidate on update
async function updateUser(userId: string, data: Partial<User>) {
  const user = await db.users.update({ where: { id: userId }, data });

  // Invalidate cache
  await redis.del(`user:${userId}`);

  return user;
}
```

## Write-Through Pattern

```typescript
async function saveUser(userId: string, data: User) {
  // Write to database AND cache simultaneously
  const [user] = await Promise.all([
    db.users.upsert({
      where: { id: userId },
      create: data,
      update: data,
    }),
    redis.set(`user:${userId}`, JSON.stringify(data), "EX", 3600),
  ]);

  return user;
}
```

## Redis Data Structures for Caching

```typescript
// Hash — structured objects
await redis.hset("user:123", {
  name: "Alice",
  email: "alice@example.com",
  role: "admin",
});
const name = await redis.hget("user:123", "name");
const user = await redis.hgetall("user:123");

// Sorted Set — leaderboards, rate windows
await redis.zadd("leaderboard", 1500, "player:1", 2300, "player:2");
const top10 = await redis.zrevrange("leaderboard", 0, 9, "WITHSCORES");

// List — recent items, queues
await redis.lpush("recent:user:123", JSON.stringify(activity));
await redis.ltrim("recent:user:123", 0, 49); // Keep last 50
const recent = await redis.lrange("recent:user:123", 0, 9);

// Set — unique collections, tags
await redis.sadd("post:123:tags", "typescript", "redis", "caching");
const tags = await redis.smembers("post:123:tags");
const hasTag = await redis.sismember("post:123:tags", "redis");
```

## Rate Limiting

```typescript
async function rateLimit(
  key: string,
  limit: number,
  windowSeconds: number,
): Promise<{ allowed: boolean; remaining: number; retryAfter?: number }> {
  const current = await redis.incr(key);

  if (current === 1) {
    await redis.expire(key, windowSeconds);
  }

  if (current > limit) {
    const ttl = await redis.ttl(key);
    return { allowed: false, remaining: 0, retryAfter: ttl };
  }

  return { allowed: true, remaining: limit - current };
}

// Sliding window rate limiter
async function slidingWindowRateLimit(
  identifier: string,
  limit: number,
  windowMs: number,
): Promise<boolean> {
  const now = Date.now();
  const key = `ratelimit:${identifier}`;

  const pipeline = redis.pipeline();
  pipeline.zremrangebyscore(key, 0, now - windowMs);
  pipeline.zadd(key, now, `${now}:${Math.random()}`);
  pipeline.zcard(key);
  pipeline.pexpire(key, windowMs);

  const results = await pipeline.exec();
  const count = results?.[2]?.[1] as number;

  return count <= limit;
}
```

## Session Storage

```typescript
import session from "express-session";
import RedisStore from "connect-redis";

const redisStore = new RedisStore({
  client: redis,
  prefix: "sess:",
  ttl: 86400, // 24 hours
});

app.use(
  session({
    store: redisStore,
    secret: process.env.SESSION_SECRET!,
    resave: false,
    saveUninitialized: false,
    cookie: { secure: true, httpOnly: true, maxAge: 86400000 },
  }),
);
```

## Pub/Sub Messaging

```typescript
const subscriber = new Redis();
const publisher = new Redis();

// Subscribe to channels
subscriber.subscribe("notifications", "chat:room:123");

subscriber.on("message", (channel, message) => {
  const data = JSON.parse(message);
  console.log(`[${channel}]`, data);
});

// Publish messages
await publisher.publish(
  "notifications",
  JSON.stringify({ type: "alert", userId: "123", text: "New message" }),
);
```

## Cache Invalidation Patterns

```
PATTERN          WHEN TO USE                HOW IT WORKS
──────────────────────────────────────────────────────────
TTL expiry       Read-heavy, tolerates      Set EX/PX on keys
                 stale data briefly
Event-driven     Write-after-update         Delete key on DB write
Tag-based        Related cache groups       Track keys by tag, bulk delete
Versioned        Schema changes             Prefix keys with version
```

## Production Configuration

```
# redis.conf highlights
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
appendonly yes
appendfsync everysec
```

## Additional Resources

- Redis docs: https://redis.io/docs/
- ioredis: https://github.com/redis/ioredis
- Upstash (serverless Redis): https://upstash.com/
