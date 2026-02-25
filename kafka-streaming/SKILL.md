---
name: kafka-streaming
description: Apache Kafka event streaming covering producers, consumers, consumer groups, topics, partitions, exactly-once semantics, Kafka Streams, Schema Registry, and KafkaJS/confluent-kafka patterns.
---

# Apache Kafka

This skill should be used when implementing event streaming with Apache Kafka. It covers producers, consumers, consumer groups, topics, partitions, and stream processing.

## When to Use This Skill

Use this skill when you need to:

- Build event-driven architectures at scale
- Implement event sourcing or CQRS
- Process real-time data streams
- Decouple microservices with durable messaging
- Build data pipelines with exactly-once delivery

## Setup (KafkaJS)

```typescript
import { Kafka, Partitioners } from "kafkajs";

const kafka = new Kafka({
  clientId: "my-app",
  brokers: (process.env.KAFKA_BROKERS ?? "localhost:9092").split(","),
  ssl: process.env.KAFKA_SSL === "true",
  sasl: process.env.KAFKA_USERNAME ? {
    mechanism: "plain",
    username: process.env.KAFKA_USERNAME,
    password: process.env.KAFKA_PASSWORD!,
  } : undefined,
});
```

## Producer

```typescript
const producer = kafka.producer({
  createPartitioner: Partitioners.DefaultPartitioner,
  idempotent: true, // Exactly-once semantics
});

await producer.connect();

// Send single message
await producer.send({
  topic: "orders",
  messages: [
    {
      key: orderId, // Partition key for ordering
      value: JSON.stringify({ orderId, userId, items, total }),
      headers: { source: "order-service", version: "1" },
    },
  ],
});

// Send batch
await producer.sendBatch({
  topicMessages: [
    {
      topic: "orders",
      messages: orders.map((order) => ({
        key: order.id,
        value: JSON.stringify(order),
      })),
    },
  ],
});

await producer.disconnect();
```

## Consumer

```typescript
const consumer = kafka.consumer({ groupId: "order-processor" });

await consumer.connect();
await consumer.subscribe({ topics: ["orders"], fromBeginning: false });

await consumer.run({
  eachMessage: async ({ topic, partition, message }) => {
    const order = JSON.parse(message.value!.toString());
    const key = message.key?.toString();

    console.log(`Processing order ${key} from partition ${partition}`);

    await processOrder(order);
  },
});
```

## Batch Consumer

```typescript
await consumer.run({
  eachBatch: async ({ batch, resolveOffset, heartbeat, commitOffsetsIfNecessary }) => {
    for (const message of batch.messages) {
      const data = JSON.parse(message.value!.toString());
      await processMessage(data);

      resolveOffset(message.offset);
      await heartbeat();
    }

    await commitOffsetsIfNecessary();
  },
});
```

## Topic Administration

```typescript
const admin = kafka.admin();
await admin.connect();

// Create topic
await admin.createTopics({
  topics: [
    {
      topic: "orders",
      numPartitions: 6,
      replicationFactor: 3,
      configEntries: [
        { name: "retention.ms", value: "604800000" }, // 7 days
        { name: "cleanup.policy", value: "delete" },
      ],
    },
    {
      topic: "order-events",
      numPartitions: 6,
      replicationFactor: 3,
      configEntries: [
        { name: "cleanup.policy", value: "compact" },
      ],
    },
  ],
});

// List topics
const topics = await admin.listTopics();

// Describe consumer group
const groups = await admin.describeGroups(["order-processor"]);
```

## Error Handling & Dead Letter Queue

```typescript
const dlqProducer = kafka.producer();
await dlqProducer.connect();

await consumer.run({
  eachMessage: async ({ topic, partition, message }) => {
    try {
      const data = JSON.parse(message.value!.toString());
      await processMessage(data);
    } catch (error) {
      // Send to dead letter topic
      await dlqProducer.send({
        topic: `${topic}.dlq`,
        messages: [{
          key: message.key,
          value: message.value,
          headers: {
            ...message.headers,
            "dlq.reason": String(error),
            "dlq.original-topic": topic,
            "dlq.original-partition": String(partition),
            "dlq.original-offset": message.offset,
          },
        }],
      });
    }
  },
});
```

## Graceful Shutdown

```typescript
const shutdown = async () => {
  await consumer.disconnect();
  await producer.disconnect();
  process.exit(0);
};

process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);
```

## Additional Resources

- KafkaJS docs: https://kafka.js.org/docs/getting-started
- Kafka documentation: https://kafka.apache.org/documentation/
- Confluent docs: https://docs.confluent.io/platform/current/overview.html
