---
name: redis-streams
description: Redis Streams patterns covering consumer groups, message acknowledgment, pending entry lists, stream trimming, event sourcing, and real-time data processing pipelines.
---

# Redis Streams

This skill should be used when building event-driven systems with Redis Streams. It covers consumer groups, message acknowledgment, pending entries, trimming, and real-time processing.

## When to Use This Skill

Use this skill when you need to:

- Build event-driven architectures with Redis Streams
- Implement consumer groups for distributed processing
- Handle message acknowledgment and retries
- Build real-time data processing pipelines
- Use streams for event sourcing patterns

## Stream Basics

```typescript
import Redis from "ioredis";

const redis = new Redis();

// Add messages to stream
await redis.xadd("orders", "*", "orderId", "123", "total", "49.99", "status", "pending");
await redis.xadd("orders", "*", "orderId", "124", "total", "99.50", "status", "pending");

// Read messages (from beginning)
const messages = await redis.xrange("orders", "-", "+");
// Returns: [['1234567890-0', ['orderId', '123', 'total', '49.99', 'status', 'pending']], ...]

// Read last N messages
const recent = await redis.xrevrange("orders", "+", "-", "COUNT", 10);

// Read new messages (blocking)
const newMessages = await redis.xread("BLOCK", 5000, "STREAMS", "orders", "$");
```

## Consumer Groups

```typescript
// Create consumer group ($ = only new messages, 0 = all messages)
await redis.xgroup("CREATE", "orders", "order-processors", "$", "MKSTREAM");

// Read as consumer in group
async function processMessages(groupName: string, consumerName: string) {
  while (true) {
    const results = await redis.xreadgroup(
      "GROUP", groupName, consumerName,
      "COUNT", 10,
      "BLOCK", 5000,
      "STREAMS", "orders", ">"
    );

    if (!results) continue;

    for (const [stream, messages] of results) {
      for (const [id, fields] of messages) {
        const data = Object.fromEntries(
          fields.reduce((acc, val, i) =>
            i % 2 === 0 ? [...acc, [val, fields[i + 1]]] : acc, [])
        );

        await handleOrder(data);

        // Acknowledge message
        await redis.xack("orders", groupName, id);
      }
    }
  }
}

// Run multiple consumers
processMessages("order-processors", "consumer-1");
processMessages("order-processors", "consumer-2");
```

## Pending Entry List (PEL)

```typescript
// Check pending messages
const pending = await redis.xpending("orders", "order-processors");
// Returns: [totalPending, minId, maxId, [[consumer, count], ...]]

// Detailed pending info
const details = await redis.xpending(
  "orders", "order-processors", "-", "+", 10
);
// Returns: [[id, consumer, idleTime, deliveryCount], ...]

// Claim stale messages (idle > 60s)
const claimed = await redis.xclaim(
  "orders", "order-processors", "consumer-3",
  60000, // min idle time ms
  "1234567890-0", "1234567891-0"
);

// Auto-claim stale messages
const [cursor, autoClaimed] = await redis.xautoclaim(
  "orders", "order-processors", "consumer-3",
  60000, // min idle time ms
  "0-0", // start ID
  "COUNT", 10
);
```

## Stream Trimming

```typescript
// Trim to max length (approximate for performance)
await redis.xtrim("orders", "MAXLEN", "~", 10000);

// Trim by minimum ID
await redis.xtrim("orders", "MINID", "~", "1234567890-0");

// Add with auto-trim
await redis.xadd("orders", "MAXLEN", "~", 10000, "*",
  "orderId", "125", "total", "75.00", "status", "pending"
);
```

## Event Sourcing Pattern

```typescript
interface DomainEvent {
  type: string;
  aggregateId: string;
  data: Record<string, string>;
  timestamp: number;
}

async function appendEvent(stream: string, event: DomainEvent) {
  const fields = [
    "type", event.type,
    "aggregateId", event.aggregateId,
    "timestamp", String(event.timestamp),
    ...Object.entries(event.data).flat(),
  ];
  return redis.xadd(stream, "*", ...fields);
}

async function replayEvents(stream: string, aggregateId: string) {
  const messages = await redis.xrange(stream, "-", "+");
  return messages
    .map(([id, fields]) => parseFields(id, fields))
    .filter((e) => e.aggregateId === aggregateId);
}

// Usage
await appendEvent("account-events", {
  type: "DEPOSIT",
  aggregateId: "acc-001",
  data: { amount: "100.00", currency: "USD" },
  timestamp: Date.now(),
});
```

## Stream Info

```typescript
// Stream metadata
const info = await redis.xinfo("STREAM", "orders");

// Consumer group info
const groups = await redis.xinfo("GROUPS", "orders");

// Consumer info within group
const consumers = await redis.xinfo("CONSUMERS", "orders", "order-processors");
```

## Additional Resources

- Redis Streams: https://redis.io/docs/data-types/streams/
- Consumer Groups: https://redis.io/docs/data-types/streams-tutorial/
- ioredis: https://github.com/redis/ioredis
