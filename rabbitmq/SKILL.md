---
name: rabbitmq
description: RabbitMQ message broker covering exchanges, queues, routing, publish/subscribe, work queues, RPC, dead letter handling, priority queues, and Node.js/Python client patterns.
---

# RabbitMQ

This skill should be used when implementing message-driven architectures with RabbitMQ. It covers exchanges, queues, routing patterns, dead letters, and client libraries.

## When to Use This Skill

Use this skill when you need to:

- Decouple services with message queues
- Implement pub/sub or work queue patterns
- Handle background job processing
- Set up dead letter queues for failed messages
- Build event-driven microservices

## Setup (Node.js with amqplib)

```typescript
import amqp from "amqplib";

const connection = await amqp.connect(process.env.RABBITMQ_URL ?? "amqp://localhost");
const channel = await connection.createChannel();
```

## Work Queue (Task Distribution)

```typescript
// Producer
const queue = "tasks";
await channel.assertQueue(queue, { durable: true });

channel.sendToQueue(queue, Buffer.from(JSON.stringify({ taskId: "123", type: "email" })), {
  persistent: true,
  contentType: "application/json",
});

// Consumer
await channel.prefetch(1); // Fair dispatch
channel.consume(queue, async (msg) => {
  if (!msg) return;
  const task = JSON.parse(msg.content.toString());

  try {
    await processTask(task);
    channel.ack(msg);
  } catch (error) {
    // Requeue on failure (up to a limit via dead letter)
    channel.nack(msg, false, false);
  }
});
```

## Publish/Subscribe (Fanout)

```typescript
// Publisher
const exchange = "notifications";
await channel.assertExchange(exchange, "fanout", { durable: true });

channel.publish(exchange, "", Buffer.from(JSON.stringify({
  event: "user.signup",
  userId: "abc",
})));

// Subscriber
const { queue } = await channel.assertQueue("", { exclusive: true });
await channel.bindQueue(queue, exchange, "");

channel.consume(queue, (msg) => {
  if (!msg) return;
  const event = JSON.parse(msg.content.toString());
  console.log("Received:", event);
  channel.ack(msg);
});
```

## Topic Routing

```typescript
const exchange = "events";
await channel.assertExchange(exchange, "topic", { durable: true });

// Publish with routing key
channel.publish(exchange, "order.created", Buffer.from(JSON.stringify({ orderId: "1" })));
channel.publish(exchange, "order.shipped", Buffer.from(JSON.stringify({ orderId: "1" })));
channel.publish(exchange, "user.created", Buffer.from(JSON.stringify({ userId: "a" })));

// Subscribe to order.* events
const { queue } = await channel.assertQueue("order-service", { durable: true });
await channel.bindQueue(queue, exchange, "order.*");

channel.consume(queue, (msg) => {
  if (!msg) return;
  console.log(`${msg.fields.routingKey}:`, JSON.parse(msg.content.toString()));
  channel.ack(msg);
});
```

## Dead Letter Queue

```typescript
// Dead letter exchange
await channel.assertExchange("dlx", "direct", { durable: true });
await channel.assertQueue("dead-letters", { durable: true });
await channel.bindQueue("dead-letters", "dlx", "failed");

// Main queue with dead letter config
await channel.assertQueue("tasks", {
  durable: true,
  arguments: {
    "x-dead-letter-exchange": "dlx",
    "x-dead-letter-routing-key": "failed",
    "x-message-ttl": 30000, // 30s TTL
    "x-max-length": 10000,
  },
});
```

## RPC Pattern

```typescript
// Client
async function rpcCall(payload: unknown): Promise<unknown> {
  const correlationId = crypto.randomUUID();
  const { queue: replyQueue } = await channel.assertQueue("", { exclusive: true });

  return new Promise((resolve) => {
    channel.consume(replyQueue, (msg) => {
      if (msg?.properties.correlationId === correlationId) {
        resolve(JSON.parse(msg.content.toString()));
      }
    }, { noAck: true });

    channel.sendToQueue("rpc_queue", Buffer.from(JSON.stringify(payload)), {
      correlationId,
      replyTo: replyQueue,
    });
  });
}

// Server
channel.consume("rpc_queue", async (msg) => {
  if (!msg) return;
  const request = JSON.parse(msg.content.toString());
  const result = await processRequest(request);

  channel.sendToQueue(msg.properties.replyTo, Buffer.from(JSON.stringify(result)), {
    correlationId: msg.properties.correlationId,
  });
  channel.ack(msg);
});
```

## Connection Management

```typescript
// Graceful shutdown
process.on("SIGINT", async () => {
  await channel.close();
  await connection.close();
  process.exit(0);
});

// Reconnection logic
connection.on("close", () => {
  console.log("Connection closed, reconnecting...");
  setTimeout(connect, 5000);
});
```

## Additional Resources

- RabbitMQ tutorials: https://www.rabbitmq.com/tutorials
- amqplib docs: https://amqp-node.github.io/amqplib/
- Exchange types: https://www.rabbitmq.com/tutorials/amqp-concepts#exchanges
