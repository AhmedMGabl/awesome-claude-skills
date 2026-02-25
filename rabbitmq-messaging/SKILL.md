---
name: rabbitmq-messaging
description: RabbitMQ messaging patterns covering exchanges, queues, routing, dead letter queues, pub/sub, RPC, priority queues, and Node.js/Python client integration.
---

# RabbitMQ Messaging

This skill should be used when building message-driven systems with RabbitMQ. It covers exchanges, queues, routing, dead letter queues, pub/sub, and RPC patterns.

## When to Use This Skill

Use this skill when you need to:

- Implement async message processing
- Set up pub/sub with topic exchanges
- Handle dead letter queues for failed messages
- Build RPC request-reply patterns
- Use priority queues and delayed messages

## Setup (Node.js)

```bash
npm install amqplib
```

## Connection and Channel

```typescript
import amqplib from "amqplib";

const connection = await amqplib.connect("amqp://localhost");
const channel = await connection.createChannel();
await channel.prefetch(10);
```

## Direct Exchange (Work Queue)

```typescript
// Producer
const queue = "tasks";
await channel.assertQueue(queue, { durable: true });
channel.sendToQueue(queue, Buffer.from(JSON.stringify({ taskId: 1, data: "process" })), {
  persistent: true,
});

// Consumer
await channel.consume(queue, async (msg) => {
  if (!msg) return;
  const task = JSON.parse(msg.content.toString());
  try {
    await processTask(task);
    channel.ack(msg);
  } catch (error) {
    channel.nack(msg, false, true); // requeue
  }
});
```

## Topic Exchange (Pub/Sub)

```typescript
const exchange = "events";
await channel.assertExchange(exchange, "topic", { durable: true });

// Publisher
channel.publish(exchange, "user.created", Buffer.from(JSON.stringify({ userId: 1 })));
channel.publish(exchange, "order.completed", Buffer.from(JSON.stringify({ orderId: 42 })));

// Subscriber: all user events
const q1 = await channel.assertQueue("", { exclusive: true });
await channel.bindQueue(q1.queue, exchange, "user.*");
await channel.consume(q1.queue, (msg) => {
  console.log("User event:", msg?.fields.routingKey);
  channel.ack(msg!);
});

// Subscriber: all events
const q2 = await channel.assertQueue("", { exclusive: true });
await channel.bindQueue(q2.queue, exchange, "#");
```

## Dead Letter Queue

```typescript
// DLX setup
await channel.assertExchange("dlx", "direct", { durable: true });
await channel.assertQueue("dead-letters", { durable: true });
await channel.bindQueue("dead-letters", "dlx", "failed");

// Main queue with DLX
await channel.assertQueue("tasks", {
  durable: true,
  arguments: {
    "x-dead-letter-exchange": "dlx",
    "x-dead-letter-routing-key": "failed",
    "x-message-ttl": 30000, // 30s TTL
  },
});

// Consumer with retry logic
await channel.consume("tasks", async (msg) => {
  if (!msg) return;
  const retries = (msg.properties.headers?.["x-retry-count"] || 0);
  try {
    await processTask(JSON.parse(msg.content.toString()));
    channel.ack(msg);
  } catch (error) {
    if (retries < 3) {
      channel.publish("", "tasks", msg.content, {
        headers: { "x-retry-count": retries + 1 },
        persistent: true,
      });
      channel.ack(msg);
    } else {
      channel.nack(msg, false, false); // send to DLX
    }
  }
});
```

## RPC Pattern

```typescript
// Server
await channel.assertQueue("rpc_queue");
await channel.consume("rpc_queue", async (msg) => {
  if (!msg) return;
  const input = JSON.parse(msg.content.toString());
  const result = await compute(input);
  channel.sendToQueue(msg.properties.replyTo, Buffer.from(JSON.stringify(result)), {
    correlationId: msg.properties.correlationId,
  });
  channel.ack(msg);
});

// Client
const replyQueue = await channel.assertQueue("", { exclusive: true });
const correlationId = crypto.randomUUID();

channel.sendToQueue("rpc_queue", Buffer.from(JSON.stringify({ x: 10 })), {
  replyTo: replyQueue.queue,
  correlationId,
});
```

## Graceful Shutdown

```typescript
process.on("SIGTERM", async () => {
  await channel.close();
  await connection.close();
  process.exit(0);
});
```

## Additional Resources

- RabbitMQ: https://www.rabbitmq.com/docs
- Tutorials: https://www.rabbitmq.com/tutorials
- amqplib: https://amqp-node.github.io/amqplib/
