---
name: redis-patterns
description: Advanced Redis patterns covering pub/sub messaging, Streams with consumer groups, Lua scripting, RedisJSON, RediSearch full-text search, RedisTimeSeries, pipeline batching, and cluster configuration.
---

# Redis Patterns

This skill should be used when implementing advanced Redis features beyond basic caching -- including event-driven streaming, atomic scripting, JSON document storage, full-text and vector search, time-series data, and production cluster setup.

## When to Use This Skill

- Building event-driven systems with durable message streams
- Implementing atomic multi-step operations without race conditions
- Storing and querying JSON documents natively in Redis
- Adding full-text or vector similarity search to an application
- Collecting time-series metrics or sensor data
- Optimizing throughput with batched pipeline commands
- Deploying Redis in a sharded cluster environment

## Pub/Sub Messaging

Use separate client instances for publisher and subscriber. A subscriber connection is dedicated and cannot issue other commands.

```typescript
import { Redis } from "ioredis";

const publisher = new Redis();
const subscriber = new Redis();

// Pattern subscribe -- wildcard channel matching
subscriber.psubscribe("orders:*");

subscriber.on("pmessage", (_pattern, channel, message) => {
  const event = JSON.parse(message);
  console.log(`[${channel}]`, event);
});

await publisher.publish(
  "orders:created",
  JSON.stringify({ orderId: "ord_1", total: 49.99 }),
);
```

## Redis Streams with Consumer Groups

Streams provide durable, replayable event logs. Consumer groups allow multiple workers to share processing load with acknowledgement tracking.

```typescript
const STREAM = "events:orders";
const GROUP = "order-processors";
const CONSUMER = `worker-${process.pid}`;

// Create stream and group (safe to call repeatedly)
await redis.xgroup("CREATE", STREAM, GROUP, "$", "MKSTREAM").catch(() => {});

// Producer -- append event
await redis.xadd(STREAM, "*", "type", "order.created", "orderId", "ord_1");

// Consumer -- read pending messages for this group
async function processMessages() {
  const results = await redis.xreadgroup(
    "GROUP", GROUP, CONSUMER,
    "COUNT", "10", "BLOCK", "2000",
    "STREAMS", STREAM, ">",
  );

  for (const [, entries] of results ?? []) {
    for (const [id, fields] of entries) {
      const event = Object.fromEntries(
        fields.reduce<[string, string][]>((acc, v, i, a) =>
          i % 2 === 0 ? [...acc, [v, a[i + 1]]] : acc, [])
      );
      console.log("Processing", event);
      await redis.xack(STREAM, GROUP, id);
    }
  }
}
```

## Lua Scripting for Atomic Operations

Lua scripts execute atomically on the Redis server, eliminating race conditions for compare-and-swap style operations.

```typescript
// Atomic inventory decrement -- only if stock > 0
const decrementStock = redis.defineCommand("decrementStock", {
  numberOfKeys: 1,
  lua: `
    local stock = tonumber(redis.call("GET", KEYS[1]))
    if stock and stock >= tonumber(ARGV[1]) then
      return redis.call("DECRBY", KEYS[1], ARGV[1])
    end
    return -1
  `,
});

const remaining = await (redis as any).decrementStock("stock:sku:ABC", 2);
if (remaining === -1) throw new Error("Insufficient stock");
```

## RedisJSON Document Storage

RedisJSON stores native JSON trees, enabling partial reads and atomic updates on nested paths without full document serialization.

```typescript
await redis.call("JSON.SET", "user:42", "$", JSON.stringify({
  name: "Alice",
  roles: ["editor"],
  address: { city: "Berlin" },
}));

// Read nested path
const city = await redis.call("JSON.GET", "user:42", "$.address.city");

// Append to array without fetching the whole document
await redis.call("JSON.ARRAPPEND", "user:42", "$.roles", '"admin"');
```

## RediSearch Full-Text and Vector Search

RediSearch indexes Redis hashes or JSON documents for full-text queries, numeric filters, and k-NN vector similarity.

```typescript
// Create index on JSON documents
await redis.call(
  "FT.CREATE", "idx:products", "ON", "JSON", "PREFIX", "1", "product:",
  "SCHEMA",
    "$.name", "AS", "name", "TEXT", "WEIGHT", "2.0",
    "$.price", "AS", "price", "NUMERIC", "SORTABLE",
    "$.embedding", "AS", "embedding", "VECTOR", "FLAT", "6",
      "TYPE", "FLOAT32", "DIM", "128", "DISTANCE_METRIC", "COSINE",
);

// Full-text search with price filter
const results = await redis.call(
  "FT.SEARCH", "idx:products",
  "@name:(wireless headphones) @price:[20 200]",
  "LIMIT", "0", "10",
);
```

## Pipeline and Batching

Pipelines batch multiple commands into one network round-trip. Use when issuing many independent commands in sequence.

```typescript
const pipeline = redis.pipeline();

pipeline.set("key:a", "1", "EX", 60);
pipeline.set("key:b", "2", "EX", 60);
pipeline.incr("counter:daily");
pipeline.lpush("queue:jobs", JSON.stringify({ jobId: "j1" }));

const results = await pipeline.exec();
// results: [[null, "OK"], [null, "OK"], [null, 1], [null, 1]]
```

## RedisTimeSeries

Store and query time-stamped numeric data with automatic downsampling and retention policies.

```typescript
// Create series with 30-day retention
await redis.call("TS.CREATE", "sensor:temp:room1",
  "RETENTION", "2592000000",
  "LABELS", "room", "room1", "type", "temperature",
);

// Add data point (* uses server time)
await redis.call("TS.ADD", "sensor:temp:room1", "*", "22.4");

// Query range with 1-hour average aggregation
const data = await redis.call(
  "TS.RANGE", "sensor:temp:room1",
  Date.now() - 86400000, Date.now(),
  "AGGREGATION", "avg", "3600000",
);
```

## Cluster Configuration

Redis Cluster shards data across nodes using hash slots. Use `ioredis` cluster mode for transparent slot routing.

```typescript
import { Cluster } from "ioredis";

const cluster = new Cluster([
  { host: "redis-node-1", port: 6379 },
  { host: "redis-node-2", port: 6379 },
  { host: "redis-node-3", port: 6379 },
], {
  redisOptions: { password: process.env.REDIS_PASSWORD },
  scaleReads: "slave",
  maxRedirections: 6,
});

// Hash tags force co-location of related keys on the same slot
await cluster.set("{user:42}:profile", JSON.stringify(profile));
await cluster.set("{user:42}:sessions", JSON.stringify(sessions));
```

## Connection Pooling

ioredis manages connection lifecycle internally. Tune these options for production workloads.

```typescript
const redis = new Redis({
  host: process.env.REDIS_HOST,
  port: 6379,
  password: process.env.REDIS_PASSWORD,
  tls: process.env.NODE_ENV === "production" ? {} : undefined,
  lazyConnect: true,
  maxRetriesPerRequest: 3,
  retryStrategy: (times) => Math.min(times * 100, 3000),
  enableReadyCheck: true,
  keepAlive: 30000,
});

await redis.connect();
process.on("SIGTERM", () => redis.quit());
```

## References

- Redis Streams: https://redis.io/docs/data-types/streams/
- RedisJSON: https://redis.io/docs/data-types/json/
- RediSearch: https://redis.io/docs/interact/search-and-query/
- RedisTimeSeries: https://redis.io/docs/data-types/timeseries/
- ioredis: https://github.com/redis/ioredis
