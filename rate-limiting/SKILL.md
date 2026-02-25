---
name: rate-limiting
description: Rate limiting and throttling patterns covering token bucket, sliding window, fixed window algorithms, Redis-based distributed rate limiting, Express/Fastify middleware, API quota management, DDoS protection strategies, and client-side request debouncing.
---

# Rate Limiting & Throttling

This skill should be used when implementing rate limiting, throttling, or request quotas in APIs and applications. It covers algorithms, middleware patterns, and distributed rate limiting.

## When to Use This Skill

Use this skill when you need to:

- Protect APIs from abuse and DDoS
- Implement per-user or per-API-key rate limits
- Build tiered rate limiting for API plans
- Add distributed rate limiting with Redis
- Implement client-side request throttling

## Express Rate Limiting

```typescript
import rateLimit from "express-rate-limit";
import RedisStore from "rate-limit-redis";
import { createClient } from "redis";

const redis = createClient({ url: process.env.REDIS_URL });
await redis.connect();

// Basic rate limiter
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 minutes
  max: 100,                   // 100 requests per window
  standardHeaders: "draft-7", // RateLimit-* headers
  legacyHeaders: false,
  store: new RedisStore({ sendCommand: (...args) => redis.sendCommand(args) }),
  message: { error: "Too many requests, please try again later" },
  keyGenerator: (req) => req.user?.id ?? req.ip,
});

app.use("/api/", apiLimiter);

// Stricter limit for auth endpoints
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
  message: { error: "Too many login attempts" },
});
app.use("/api/auth/login", authLimiter);
```

## Redis Sliding Window

```typescript
class SlidingWindowRateLimiter {
  constructor(
    private redis: RedisClient,
    private windowMs: number,
    private maxRequests: number,
  ) {}

  async isAllowed(key: string): Promise<{ allowed: boolean; remaining: number; resetMs: number }> {
    const now = Date.now();
    const windowStart = now - this.windowMs;
    const redisKey = `ratelimit:${key}`;

    const multi = this.redis.multi();
    multi.zRemRangeByScore(redisKey, 0, windowStart);
    multi.zAdd(redisKey, { score: now, value: `${now}:${Math.random()}` });
    multi.zCard(redisKey);
    multi.expire(redisKey, Math.ceil(this.windowMs / 1000));

    const results = await multi.exec();
    const count = results[2] as number;

    if (count > this.maxRequests) {
      await this.redis.zRemRangeByRank(redisKey, -1, -1);
      return { allowed: false, remaining: 0, resetMs: this.windowMs };
    }

    return { allowed: true, remaining: this.maxRequests - count, resetMs: this.windowMs };
  }
}

// Middleware usage
const limiter = new SlidingWindowRateLimiter(redis, 60_000, 60);

app.use(async (req, res, next) => {
  const key = req.user?.id ?? req.ip;
  const result = await limiter.isAllowed(key);

  res.set("RateLimit-Limit", String(60));
  res.set("RateLimit-Remaining", String(result.remaining));

  if (!result.allowed) {
    return res.status(429).json({ error: "Rate limit exceeded" });
  }
  next();
});
```

## Token Bucket Algorithm

```typescript
class TokenBucket {
  private tokens: number;
  private lastRefill: number;

  constructor(
    private capacity: number,
    private refillRate: number,
  ) {
    this.tokens = capacity;
    this.lastRefill = Date.now();
  }

  consume(tokens = 1): boolean {
    this.refill();
    if (this.tokens >= tokens) {
      this.tokens -= tokens;
      return true;
    }
    return false;
  }

  private refill() {
    const now = Date.now();
    const elapsed = (now - this.lastRefill) / 1000;
    this.tokens = Math.min(this.capacity, this.tokens + elapsed * this.refillRate);
    this.lastRefill = now;
  }
}
```

## Tiered API Rate Limits

```typescript
interface RateLimitTier {
  requestsPerMinute: number;
  requestsPerDay: number;
}

const tiers: Record<string, RateLimitTier> = {
  free:       { requestsPerMinute: 10,  requestsPerDay: 1000 },
  pro:        { requestsPerMinute: 60,  requestsPerDay: 10000 },
  enterprise: { requestsPerMinute: 300, requestsPerDay: 100000 },
};

async function tieredRateLimiter(req: Request, res: Response, next: NextFunction) {
  const user = req.user;
  const tier = tiers[user?.plan ?? "free"];

  const minuteKey = `rate:min:${user?.id ?? req.ip}`;
  const minuteCount = await redis.incr(minuteKey);
  if (minuteCount === 1) await redis.expire(minuteKey, 60);

  if (minuteCount > tier.requestsPerMinute) {
    return res.status(429).json({
      error: "Rate limit exceeded",
      limit: tier.requestsPerMinute,
      upgrade: user?.plan !== "enterprise" ? "Upgrade for higher limits" : undefined,
    });
  }

  res.set("X-RateLimit-Limit", String(tier.requestsPerMinute));
  res.set("X-RateLimit-Remaining", String(Math.max(0, tier.requestsPerMinute - minuteCount)));
  next();
}
```

## Client-Side Throttling

```typescript
// Debounce — wait until user stops typing
function debounce<T extends (...args: any[]) => any>(fn: T, delayMs: number) {
  let timer: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delayMs);
  };
}

// Throttle — max once per interval
function throttle<T extends (...args: any[]) => any>(fn: T, intervalMs: number) {
  let lastCall = 0;
  return (...args: Parameters<T>) => {
    const now = Date.now();
    if (now - lastCall >= intervalMs) {
      lastCall = now;
      fn(...args);
    }
  };
}
```

## Additional Resources

- express-rate-limit: https://github.com/express-rate-limit/express-rate-limit
- IETF Rate Limit Headers: https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/
- Token Bucket: https://en.wikipedia.org/wiki/Token_bucket
