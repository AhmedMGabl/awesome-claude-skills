---
name: cassandra-patterns
description: Apache Cassandra patterns covering data modeling, partition keys, clustering columns, CQL queries, materialized views, lightweight transactions, and driver configuration.
---

# Cassandra Patterns

This skill should be used when building distributed databases with Apache Cassandra. It covers data modeling, partition keys, CQL, materialized views, and driver configuration.

## When to Use This Skill

Use this skill when you need to:

- Design tables for query-driven data modeling
- Use partition and clustering keys effectively
- Write CQL queries for time-series and wide-row data
- Implement lightweight transactions
- Configure Node.js/Python Cassandra drivers

## Data Modeling

```cql
-- Users table (lookup by id)
CREATE TABLE users (
  user_id UUID,
  email TEXT,
  name TEXT,
  created_at TIMESTAMP,
  PRIMARY KEY (user_id)
);

-- Users by email (query pattern)
CREATE TABLE users_by_email (
  email TEXT,
  user_id UUID,
  name TEXT,
  PRIMARY KEY (email)
);

-- Time-series: messages per conversation
CREATE TABLE messages (
  conversation_id UUID,
  sent_at TIMESTAMP,
  message_id TIMEUUID,
  sender_id UUID,
  content TEXT,
  PRIMARY KEY (conversation_id, sent_at, message_id)
) WITH CLUSTERING ORDER BY (sent_at DESC, message_id DESC);

-- Wide rows: user activity feed
CREATE TABLE user_feed (
  user_id UUID,
  bucket TEXT,           -- '2024-01' for monthly bucketing
  activity_time TIMESTAMP,
  activity_type TEXT,
  details MAP<TEXT, TEXT>,
  PRIMARY KEY ((user_id, bucket), activity_time)
) WITH CLUSTERING ORDER BY (activity_time DESC);
```

## CQL Queries

```cql
-- Insert
INSERT INTO users (user_id, email, name, created_at)
VALUES (uuid(), 'alice@example.com', 'Alice', toTimestamp(now()));

-- Insert with TTL (auto-expire)
INSERT INTO sessions (session_id, user_id, data)
VALUES ('abc123', some_uuid, 'session_data')
USING TTL 3600;

-- Select with range query on clustering key
SELECT * FROM messages
WHERE conversation_id = some_uuid
  AND sent_at > '2024-01-01'
ORDER BY sent_at DESC
LIMIT 50;

-- Batch (same partition key)
BEGIN BATCH
  INSERT INTO users (user_id, email, name) VALUES (some_uuid, 'bob@example.com', 'Bob');
  INSERT INTO users_by_email (email, user_id, name) VALUES ('bob@example.com', some_uuid, 'Bob');
APPLY BATCH;

-- Lightweight transaction (compare-and-set)
INSERT INTO users (user_id, email, name)
VALUES (uuid(), 'alice@example.com', 'Alice')
IF NOT EXISTS;

UPDATE users SET name = 'Alice Smith'
WHERE user_id = some_uuid
IF name = 'Alice';
```

## Node.js Driver

```typescript
import { Client, types } from "cassandra-driver";

const client = new Client({
  contactPoints: ["cassandra-1", "cassandra-2"],
  localDataCenter: "dc1",
  keyspace: "myapp",
  queryOptions: { consistency: types.consistencies.localQuorum },
});

await client.connect();

// Prepared statement (recommended for repeated queries)
const query = "SELECT * FROM messages WHERE conversation_id = ? AND sent_at > ? LIMIT ?";
const result = await client.execute(query, [conversationId, startDate, 50], { prepare: true });

for (const row of result.rows) {
  console.log(row.content, row.sent_at);
}

// Batch
const queries = [
  { query: "INSERT INTO users (user_id, email, name) VALUES (?, ?, ?)", params: [id, email, name] },
  { query: "INSERT INTO users_by_email (email, user_id, name) VALUES (?, ?, ?)", params: [email, id, name] },
];
await client.batch(queries, { prepare: true });

// Paging
let pageState: Buffer | undefined;
do {
  const result = await client.execute(
    "SELECT * FROM messages WHERE conversation_id = ?",
    [conversationId],
    { prepare: true, fetchSize: 100, pageState }
  );
  processRows(result.rows);
  pageState = result.pageState;
} while (pageState);
```

## Docker Compose

```yaml
services:
  cassandra:
    image: cassandra:4.1
    ports:
      - "9042:9042"
    environment:
      CASSANDRA_CLUSTER_NAME: MyCluster
      CASSANDRA_DC: dc1
    volumes:
      - cassandra-data:/var/lib/cassandra

volumes:
  cassandra-data:
```

## Additional Resources

- Cassandra: https://cassandra.apache.org/doc/latest/
- Data Modeling: https://cassandra.apache.org/doc/latest/data_modeling/
- Node.js Driver: https://docs.datastax.com/en/developer/nodejs-driver/
