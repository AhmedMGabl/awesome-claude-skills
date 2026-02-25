---
name: apache-kafka
description: Apache Kafka patterns covering producers, consumers, consumer groups, topics, partitions, Kafka Streams, Connect, Schema Registry, and event-driven architectures.
---

# Apache Kafka

This skill should be used when building event-driven systems with Apache Kafka. It covers producers, consumers, consumer groups, Kafka Streams, Connect, and Schema Registry.

## When to Use This Skill

Use this skill when you need to:

- Build event-driven microservice architectures
- Implement reliable message streaming
- Process real-time data with Kafka Streams
- Use Schema Registry for data contracts
- Configure Kafka Connect for data integration

## Producer

```typescript
import { Kafka, Partitioners } from "kafkajs";

const kafka = new Kafka({
  clientId: "my-app",
  brokers: ["localhost:9092"],
});

const producer = kafka.producer({
  createPartitioner: Partitioners.DefaultPartitioner,
  idempotent: true,
});

await producer.connect();

// Send single message
await producer.send({
  topic: "orders",
  messages: [
    {
      key: "order-123",
      value: JSON.stringify({ orderId: "123", total: 49.99 }),
      headers: { "event-type": "order.created" },
    },
  ],
});

// Send batch
await producer.sendBatch({
  topicMessages: [
    {
      topic: "orders",
      messages: [
        { key: "order-124", value: JSON.stringify({ orderId: "124", total: 99.50 }) },
        { key: "order-125", value: JSON.stringify({ orderId: "125", total: 25.00 }) },
      ],
    },
  ],
});

await producer.disconnect();
```

## Consumer

```typescript
const consumer = kafka.consumer({ groupId: "order-processors" });
await consumer.connect();
await consumer.subscribe({ topics: ["orders"], fromBeginning: false });

await consumer.run({
  eachMessage: async ({ topic, partition, message }) => {
    const event = JSON.parse(message.value.toString());
    const eventType = message.headers?.["event-type"]?.toString();

    console.log({
      topic,
      partition,
      offset: message.offset,
      key: message.key?.toString(),
      eventType,
      event,
    });

    await processOrder(event);
  },
});

// Batch processing
await consumer.run({
  eachBatch: async ({ batch, resolveOffset, heartbeat }) => {
    for (const message of batch.messages) {
      await processMessage(message);
      resolveOffset(message.offset);
      await heartbeat();
    }
  },
});
```

## Topic Administration

```typescript
const admin = kafka.admin();
await admin.connect();

await admin.createTopics({
  topics: [
    {
      topic: "orders",
      numPartitions: 6,
      replicationFactor: 3,
      configEntries: [
        { name: "retention.ms", value: String(7 * 24 * 60 * 60 * 1000) },
        { name: "cleanup.policy", value: "delete" },
      ],
    },
    {
      topic: "order-snapshots",
      numPartitions: 6,
      replicationFactor: 3,
      configEntries: [
        { name: "cleanup.policy", value: "compact" },
      ],
    },
  ],
});

const topics = await admin.listTopics();
const metadata = await admin.fetchTopicMetadata({ topics: ["orders"] });
```

## Exactly-Once Semantics

```typescript
const producer = kafka.producer({
  idempotent: true,
  transactionalId: "order-processor-tx",
  maxInFlightRequests: 1,
});

await producer.connect();

const transaction = await producer.transaction();
try {
  await transaction.send({
    topic: "processed-orders",
    messages: [{ key: "order-123", value: JSON.stringify(processedOrder) }],
  });
  await transaction.sendOffsets({
    consumerGroupId: "order-processors",
    topics: [{ topic: "orders", partitions: [{ partition: 0, offset: "42" }] }],
  });
  await transaction.commit();
} catch (err) {
  await transaction.abort();
  throw err;
}
```

## Docker Compose Setup

```yaml
services:
  kafka:
    image: confluentinc/cp-kafka:7.6.0
    ports:
      - "9092:9092"
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka:9093
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      CLUSTER_ID: MkU3OEVBNTcwNTJENDM2Qk
```

## Additional Resources

- Kafka: https://kafka.apache.org/documentation/
- KafkaJS: https://kafka.js.org/docs/getting-started
- Confluent: https://docs.confluent.io/
