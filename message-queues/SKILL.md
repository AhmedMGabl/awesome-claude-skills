---
name: message-queues
description: This skill should be used when implementing message queues, event-driven architectures, or asynchronous communication patterns including RabbitMQ, Redis Streams (BullMQ), AWS SQS, Kafka, dead letter queues, idempotency, fan-out/fan-in, pub/sub, and backpressure handling.
---

# Message Queues & Event-Driven Architecture

Guide for implementing message queue systems and event-driven patterns in Node.js.

## When to Use This Skill

- Decouple services with asynchronous messaging (pub/sub or point-to-point)
- Build reliable pipelines with retries and dead letter queues
- Handle backpressure in high-throughput systems
- Ensure exactly-once processing with idempotent consumers
- Implement fan-out/fan-in for parallel workloads

**Pub/Sub** broadcasts messages to all subscribers (event notifications, cache invalidation). **Point-to-Point** delivers each message to exactly one consumer (task queues, load distribution).

## RabbitMQ Publisher/Consumer

```javascript
import amqp from 'amqplib';

const EXCHANGE = 'app.events';
const DLX = 'app.dlx';

async function createPublisher() {
  const conn = await amqp.connect(process.env.RABBITMQ_URL);
  const ch = await conn.createChannel();
  await ch.assertExchange(EXCHANGE, 'topic', { durable: true });
  function publish(routingKey, payload) {
    ch.publish(EXCHANGE, routingKey, Buffer.from(JSON.stringify({
      id: crypto.randomUUID(), timestamp: new Date().toISOString(), ...payload,
    })), { persistent: true, contentType: 'application/json' });
  }
  return { publish, close: () => conn.close() };
}

async function createConsumer(queue, routingKeys, handler) {
  const conn = await amqp.connect(process.env.RABBITMQ_URL);
  const ch = await conn.createChannel();
  // Dead letter exchange for failed messages
  await ch.assertExchange(DLX, 'fanout', { durable: true });
  await ch.assertQueue('app.dead-letters', { durable: true });
  await ch.bindQueue('app.dead-letters', DLX, '');
  // Main queue with DLX routing
  await ch.assertExchange(EXCHANGE, 'topic', { durable: true });
  await ch.assertQueue(queue, {
    durable: true,
    arguments: { 'x-dead-letter-exchange': DLX },
  });
  for (const key of routingKeys) {
    await ch.bindQueue(queue, EXCHANGE, key);
  }
  await ch.prefetch(10); // Backpressure control
  ch.consume(queue, async (msg) => {
    if (!msg) return;
    try {
      await handler(JSON.parse(msg.content.toString()), msg.fields.routingKey);
      ch.ack(msg);
    } catch (err) {
      console.error('Processing failed:', err.message);
      ch.nack(msg, false, false); // Send to DLQ
    }
  });
}

const pub = await createPublisher();
pub.publish('order.created', { orderId: '123', total: 49.99 });
await createConsumer('notifications', ['order.created', 'order.shipped'], async (msg) => {
  await sendNotification(msg);
});
```

## BullMQ Worker with Retries

```javascript
import { Queue, Worker } from 'bullmq';
import IORedis from 'ioredis';

const connection = new IORedis(process.env.REDIS_URL, { maxRetriesPerRequest: null });
const orderQueue = new Queue('orders', {
  connection,
  defaultJobOptions: {
    attempts: 5,
    backoff: { type: 'exponential', delay: 2000 },
    removeOnComplete: { age: 86400, count: 500 },
    removeOnFail: { age: 604800 },
  },
});

await orderQueue.add('process-order', { orderId: '456', items: [{ sku: 'W-1', qty: 2 }] });
await orderQueue.add('cleanup', {}, { repeat: { pattern: '0 */6 * * *' }, jobId: 'stale-cleanup' });

const worker = new Worker('orders', async (job) => {
  switch (job.name) {
    case 'process-order': return fulfillOrder(job.data);
    case 'cleanup': return cleanupStaleOrders();
    default: throw new Error(`Unknown job: ${job.name}`);
  }
}, { connection, concurrency: 5, limiter: { max: 20, duration: 1000 } });

worker.on('failed', (job, err) => {
  console.error(`Job ${job?.id} failed (attempt ${job?.attemptsMade}):`, err.message);
});
```

## Kafka Producer/Consumer (KafkaJS)

```javascript
import { Kafka, Partitioners } from 'kafkajs';

const kafka = new Kafka({
  clientId: 'order-service',
  brokers: process.env.KAFKA_BROKERS.split(','),
});

const producer = kafka.producer({
  createPartitioner: Partitioners.DefaultPartitioner,
  idempotent: true, // Exactly-once semantics
});
await producer.connect();

async function publishEvent(topic, key, payload) {
  await producer.send({
    topic,
    messages: [{
      key, // Ensures ordering within a partition
      value: JSON.stringify({ id: crypto.randomUUID(), ...payload }),
      headers: { 'content-type': 'application/json' },
    }],
  });
}

const consumer = kafka.consumer({ groupId: 'payment-service' });
await consumer.connect();
await consumer.subscribe({ topics: ['order-events'], fromBeginning: false });
await consumer.run({
  partitionsConsumedConcurrently: 3,
  eachMessage: async ({ topic, partition, message }) => {
    const event = JSON.parse(message.value.toString());
    switch (event.type) {
      case 'ORDER_CREATED': return initiatePayment(event);
      case 'ORDER_CANCELLED': return refundPayment(event);
    }
  },
});

process.on('SIGTERM', async () => {
  await consumer.disconnect();
  await producer.disconnect();
});
```

## AWS SQS

```javascript
import { SQSClient, SendMessageCommand, ReceiveMessageCommand, DeleteMessageCommand } from '@aws-sdk/client-sqs';

const sqs = new SQSClient({ region: process.env.AWS_REGION });
const QUEUE_URL = process.env.SQS_QUEUE_URL;

async function sendMessage(payload) {
  await sqs.send(new SendMessageCommand({
    QueueUrl: QUEUE_URL, MessageBody: JSON.stringify(payload),
    MessageGroupId: payload.orderId, MessageDeduplicationId: payload.eventId,
  }));
}

async function pollMessages(handler) {
  while (true) {
    const { Messages = [] } = await sqs.send(new ReceiveMessageCommand({
      QueueUrl: QUEUE_URL, MaxNumberOfMessages: 10,
      WaitTimeSeconds: 20, VisibilityTimeout: 60,
    }));
    for (const msg of Messages) {
      try {
        await handler(JSON.parse(msg.Body));
        await sqs.send(new DeleteMessageCommand({
          QueueUrl: QUEUE_URL, ReceiptHandle: msg.ReceiptHandle,
        }));
      } catch (err) {
        console.error('Processing failed:', err.message);
      }
    }
  }
}
```

## Dead Letter Queue Pattern

```javascript
async function processDLQ(dlqHandler) {
  const conn = await amqp.connect(process.env.RABBITMQ_URL);
  const ch = await conn.createChannel();
  await ch.prefetch(1);
  ch.consume('app.dead-letters', async (msg) => {
    if (!msg) return;
    const death = msg.properties.headers?.['x-death']?.[0];
    const action = await dlqHandler({
      payload: JSON.parse(msg.content.toString()),
      originalQueue: death?.queue,
      reason: death?.reason,
    });
    if (action === 'retry') {
      ch.publish(EXCHANGE, death?.['routing-keys']?.[0] ?? '', msg.content, msg.properties);
    }
    ch.ack(msg);
  });
}
```

## Idempotent Consumer Pattern

```javascript
import crypto from 'node:crypto';

async function handleIdempotent(messageId, payload, processFn) {
  const key = messageId ?? crypto.createHash('sha256')
    .update(JSON.stringify(payload)).digest('hex');
  const wasSet = await redis.set(`processed:${key}`, 'pending', 'EX', 86400, 'NX');
  if (wasSet !== 'OK') return { skipped: true };
  try {
    const result = await processFn(payload);
    await redis.set(`processed:${key}`, 'completed', 'EX', 86400);
    return result;
  } catch (err) {
    await redis.del(`processed:${key}`);
    throw err;
  }
}

async function orderHandler(message) {
  return handleIdempotent(message.id, message, async (data) => {
    await db.orders.create({ data: { id: data.orderId, total: data.total } });
  });
}
```

## Fan-Out / Fan-In

```javascript
async function fanOut(orderId, items) {
  const taskIds = await Promise.all(items.map(async (item) => {
    const job = await processingQueue.add('check-inventory', {
      parentOrderId: orderId, sku: item.sku, qty: item.qty,
    });
    return job.id;
  }));
  await redis.sadd(`fanout:${orderId}`, ...taskIds);
  await redis.expire(`fanout:${orderId}`, 3600);
}

async function fanIn(orderId, taskId, result) {
  await redis.hset(`results:${orderId}`, taskId, JSON.stringify(result));
  await redis.srem(`fanout:${orderId}`, taskId);
  if (await redis.scard(`fanout:${orderId}`) === 0) {
    const all = Object.values(await redis.hgetall(`results:${orderId}`));
    await finalizeOrder(orderId, all.map((r) => JSON.parse(r)));
    await redis.del(`fanout:${orderId}`, `results:${orderId}`);
  }
}
```

## Best Practices

- **Set message TTL** to prevent unbounded queue growth; **use dead letter queues** for exhausted retries
- **Implement idempotency** on every consumer to handle redeliveries
- **Set prefetch/concurrency limits** to control backpressure
- **Use durable queues and persistent messages** for data that must not be lost
- **Monitor queue depth and consumer lag** as key operational metrics
- **Include correlation IDs** in headers for tracing; **version message schemas** for independent deploys

## Additional Resources

- RabbitMQ Tutorials: https://www.rabbitmq.com/tutorials
- BullMQ Documentation: https://docs.bullmq.io/
- KafkaJS: https://kafka.js.org/docs/getting-started
- AWS SQS Developer Guide: https://docs.aws.amazon.com/sqs/
