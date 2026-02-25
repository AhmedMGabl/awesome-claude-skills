---
name: nats-messaging
description: NATS messaging patterns covering pub/sub, request/reply, JetStream persistent messaging, key-value store, object store, and microservice communication.
---

# NATS Messaging

This skill should be used when building distributed systems with NATS messaging. It covers pub/sub, request/reply, JetStream, key-value store, and microservice communication.

## When to Use This Skill

Use this skill when you need to:

- Implement lightweight pub/sub messaging
- Use request/reply for synchronous communication
- Persist messages with JetStream
- Use NATS key-value and object stores
- Build microservice communication patterns

## Setup (Node.js)

```bash
npm install nats
```

## Connection

```typescript
import { connect, StringCodec } from "nats";

const nc = await connect({ servers: "nats://localhost:4222" });
const sc = StringCodec();
```

## Pub/Sub

```typescript
// Subscriber
const sub = nc.subscribe("events.user.created");
(async () => {
  for await (const msg of sub) {
    const data = JSON.parse(sc.decode(msg.data));
    console.log("User created:", data);
  }
})();

// Publisher
nc.publish("events.user.created", sc.encode(JSON.stringify({
  userId: 1, name: "Alice", email: "alice@example.com",
})));

// Wildcard subscription
const sub = nc.subscribe("events.user.>");  // all user events
const sub = nc.subscribe("events.*.created"); // all created events
```

## Request/Reply

```typescript
// Service (responder)
const sub = nc.subscribe("api.users.get");
(async () => {
  for await (const msg of sub) {
    const { userId } = JSON.parse(sc.decode(msg.data));
    const user = await findUser(userId);
    msg.respond(sc.encode(JSON.stringify(user)));
  }
})();

// Client (requester)
const response = await nc.request("api.users.get",
  sc.encode(JSON.stringify({ userId: 1 })),
  { timeout: 5000 }
);
const user = JSON.parse(sc.decode(response.data));
```

## JetStream (Persistent Messaging)

```typescript
const jsm = await nc.jetstreamManager();

// Create stream
await jsm.streams.add({
  name: "ORDERS",
  subjects: ["orders.>"],
  retention: "limits",
  max_msgs: 100000,
  max_age: 7 * 24 * 60 * 60 * 1_000_000_000, // 7 days in nanoseconds
});

const js = nc.jetstream();

// Publish to stream
await js.publish("orders.created", sc.encode(JSON.stringify({
  orderId: 42, items: [{ sku: "ABC", qty: 2 }],
})));

// Durable consumer
const consumer = await js.consumers.get("ORDERS", "order-processor");
const messages = await consumer.consume();
for await (const msg of messages) {
  const order = JSON.parse(sc.decode(msg.data));
  await processOrder(order);
  msg.ack();
}
```

## Key-Value Store

```typescript
const js = nc.jetstream();
const kv = await js.views.kv("config");

// Set values
await kv.put("app.feature.dark-mode", sc.encode("true"));
await kv.put("app.max-upload-size", sc.encode("10485760"));

// Get values
const entry = await kv.get("app.feature.dark-mode");
const value = sc.decode(entry!.value);

// Watch for changes
const watch = await kv.watch();
(async () => {
  for await (const entry of watch) {
    console.log(`${entry.key} = ${sc.decode(entry.value)}`);
  }
})();

// Delete
await kv.delete("app.feature.dark-mode");
```

## Graceful Shutdown

```typescript
process.on("SIGTERM", async () => {
  await nc.drain();
  process.exit(0);
});
```

## Additional Resources

- NATS: https://docs.nats.io/
- JetStream: https://docs.nats.io/nats-concepts/jetstream
- Node.js client: https://github.com/nats-io/nats.js
