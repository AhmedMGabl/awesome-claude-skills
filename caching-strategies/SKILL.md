---
name: caching-strategies
description: Caching strategy patterns covering HTTP cache headers (Cache-Control, ETag, stale-while-revalidate), CDN caching, application-level caching with Redis, in-memory LRU caches, cache invalidation patterns, React Query/SWR data caching, and cache stampede prevention.
---

# Caching Strategies

This skill should be used when implementing caching at any layer of the stack. It covers HTTP caching, CDN, application-level Redis caching, client-side data caching, and invalidation patterns.

## When to Use This Skill

Use this skill when you need to:

- Set proper HTTP cache headers
- Implement CDN caching strategies
- Add application-level Redis caching
- Cache API responses in React (SWR/React Query)
- Design cache invalidation patterns
- Prevent cache stampede

## HTTP Cache Headers

```typescript
// Immutable assets (JS/CSS with content hash)
app.use("/assets", (req, res, next) => {
  res.set("Cache-Control", "public, max-age=31536000, immutable");
  next();
});

// API responses — short cache with revalidation
app.get("/api/products", (req, res) => {
  res.set("Cache-Control", "public, max-age=60, stale-while-revalidate=300");
  res.json(products);
});

// User-specific data — private, no CDN
app.get("/api/profile", authenticate, (req, res) => {
  res.set("Cache-Control", "private, max-age=0, must-revalidate");
  res.set("ETag", generateETag(userData));
  res.json(userData);
});

// Never cache
app.get("/api/auth/session", (req, res) => {
  res.set("Cache-Control", "no-store");
  res.json(session);
});
```

## Application-Level Caching (Redis)

```typescript
class CacheService {
  constructor(private redis: RedisClient) {}

  async get<T>(key: string): Promise<T | null> {
    const cached = await this.redis.get(`cache:${key}`);
    return cached ? JSON.parse(cached) : null;
  }

  async set(key: string, value: unknown, ttlSeconds: number) {
    await this.redis.set(`cache:${key}`, JSON.stringify(value), { EX: ttlSeconds });
  }

  async getOrSet<T>(key: string, ttlSeconds: number, fetcher: () => Promise<T>): Promise<T> {
    const cached = await this.get<T>(key);
    if (cached !== null) return cached;

    const value = await fetcher();
    await this.set(key, value, ttlSeconds);
    return value;
  }

  async invalidate(pattern: string) {
    const keys = await this.redis.keys(`cache:${pattern}`);
    if (keys.length > 0) await this.redis.del(keys);
  }
}

// Usage
const cache = new CacheService(redis);

app.get("/api/products/:id", async (req, res) => {
  const product = await cache.getOrSet(
    `product:${req.params.id}`,
    300,  // 5 minutes
    () => db.product.findUnique({ where: { id: req.params.id } }),
  );
  res.json(product);
});

// Invalidate on update
app.put("/api/products/:id", async (req, res) => {
  const updated = await db.product.update({ where: { id: req.params.id }, data: req.body });
  await cache.invalidate(`product:${req.params.id}`);
  await cache.invalidate("products:list:*");
  res.json(updated);
});
```

## Cache Stampede Prevention

```typescript
// Mutex lock to prevent multiple fetches
async function getOrSetWithLock<T>(
  cache: CacheService,
  key: string,
  ttl: number,
  fetcher: () => Promise<T>,
): Promise<T> {
  const cached = await cache.get<T>(key);
  if (cached !== null) return cached;

  const lockKey = `lock:${key}`;
  const acquired = await cache.redis.set(lockKey, "1", { NX: true, EX: 30 });

  if (!acquired) {
    // Another process is fetching; wait and retry
    await new Promise((r) => setTimeout(r, 100));
    return getOrSetWithLock(cache, key, ttl, fetcher);
  }

  try {
    const value = await fetcher();
    await cache.set(key, value, ttl);
    return value;
  } finally {
    await cache.redis.del(lockKey);
  }
}
```

## React Query (TanStack Query)

```tsx
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

// Cached query with stale-while-revalidate
function useProducts(category?: string) {
  return useQuery({
    queryKey: ["products", { category }],
    queryFn: () => fetchProducts(category),
    staleTime: 5 * 60 * 1000,       // Fresh for 5 minutes
    gcTime: 30 * 60 * 1000,         // Keep in cache 30 minutes
    refetchOnWindowFocus: false,
  });
}

// Mutation with cache invalidation
function useUpdateProduct() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateProductDto) =>
      fetch(`/api/products/${data.id}`, { method: "PUT", body: JSON.stringify(data) }),
    onSuccess: (_, variables) => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ["products"] });
      queryClient.invalidateQueries({ queryKey: ["product", variables.id] });
    },
  });
}
```

## Cache Strategy Reference

```
STRATEGY          USE CASE                    PATTERN
─────────────────────────────────────────────────────────
Cache-Aside       General purpose             Read: check cache → miss → fetch → store
Write-Through     Strong consistency          Write: update DB + cache atomically
Write-Behind      High write throughput       Write: update cache → async flush to DB
Read-Through      Transparent caching         Cache fetches from DB on miss
Refresh-Ahead     Predictable access          Pre-fetch before TTL expires

INVALIDATION:
  TTL-based       Set expiry, let it expire naturally
  Event-based     Invalidate on write/update events
  Tag-based       Group keys by tags, invalidate by tag
  Versioned       Include version in cache key
```

## Additional Resources

- MDN Cache-Control: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control
- TanStack Query: https://tanstack.com/query/latest
- SWR: https://swr.vercel.app/
- Caching best practices: https://aws.amazon.com/caching/best-practices/
