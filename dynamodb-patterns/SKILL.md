---
name: dynamodb-patterns
description: AWS DynamoDB patterns covering single-table design, GSI/LSI indexes, query/scan operations, transactions, TTL, streams, batch operations, and cost optimization.
---

# DynamoDB Patterns

This skill should be used when building applications with AWS DynamoDB. It covers single-table design, indexes, queries, transactions, streams, and batch operations.

## When to Use This Skill

Use this skill when you need to:

- Design DynamoDB tables with access patterns
- Use single-table design with composite keys
- Query with GSI and LSI indexes
- Handle transactions and batch operations
- Optimize cost with TTL and projections

## Setup

```bash
npm install @aws-sdk/client-dynamodb @aws-sdk/lib-dynamodb
```

## Client Setup

```typescript
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, GetCommand, PutCommand, QueryCommand, DeleteCommand } from "@aws-sdk/lib-dynamodb";

const client = new DynamoDBClient({ region: "us-east-1" });
const docClient = DynamoDBDocumentClient.from(client);
const TABLE = "MyApp";
```

## Single-Table Design

```typescript
// Entity: User     PK: USER#<id>         SK: PROFILE
// Entity: Post     PK: USER#<id>         SK: POST#<postId>
// Entity: Comment  PK: POST#<postId>     SK: COMMENT#<commentId>

// Create user
await docClient.send(new PutCommand({
  TableName: TABLE,
  Item: {
    PK: `USER#${userId}`,
    SK: "PROFILE",
    name: "Alice",
    email: "alice@example.com",
    GSI1PK: `EMAIL#alice@example.com`,
    GSI1SK: `USER#${userId}`,
    entityType: "User",
    createdAt: new Date().toISOString(),
  },
}));

// Get user profile
const result = await docClient.send(new GetCommand({
  TableName: TABLE,
  Key: { PK: `USER#${userId}`, SK: "PROFILE" },
}));
```

## Query Operations

```typescript
// Get all posts by user
const posts = await docClient.send(new QueryCommand({
  TableName: TABLE,
  KeyConditionExpression: "PK = :pk AND begins_with(SK, :sk)",
  ExpressionAttributeValues: { ":pk": `USER#${userId}`, ":sk": "POST#" },
  ScanIndexForward: false, // newest first
  Limit: 20,
}));

// Pagination
let lastKey = undefined;
do {
  const result = await docClient.send(new QueryCommand({
    TableName: TABLE,
    KeyConditionExpression: "PK = :pk",
    ExpressionAttributeValues: { ":pk": `USER#${userId}` },
    Limit: 25,
    ExclusiveStartKey: lastKey,
  }));
  items.push(...(result.Items || []));
  lastKey = result.LastEvaluatedKey;
} while (lastKey);
```

## GSI Query

```typescript
// Find user by email (GSI1)
const result = await docClient.send(new QueryCommand({
  TableName: TABLE,
  IndexName: "GSI1",
  KeyConditionExpression: "GSI1PK = :pk",
  ExpressionAttributeValues: { ":pk": `EMAIL#alice@example.com` },
}));
```

## Transactions

```typescript
import { TransactWriteCommand } from "@aws-sdk/lib-dynamodb";

await docClient.send(new TransactWriteCommand({
  TransactItems: [
    {
      Put: {
        TableName: TABLE,
        Item: { PK: `POST#${postId}`, SK: "METADATA", title: "New Post", authorId: userId },
      },
    },
    {
      Update: {
        TableName: TABLE,
        Key: { PK: `USER#${userId}`, SK: "PROFILE" },
        UpdateExpression: "SET postCount = postCount + :inc",
        ExpressionAttributeValues: { ":inc": 1 },
      },
    },
  ],
}));
```

## Batch Operations

```typescript
import { BatchWriteCommand } from "@aws-sdk/lib-dynamodb";

const items = users.map((u) => ({
  PutRequest: {
    Item: { PK: `USER#${u.id}`, SK: "PROFILE", name: u.name, email: u.email },
  },
}));

// Batch write (max 25 items)
for (let i = 0; i < items.length; i += 25) {
  await docClient.send(new BatchWriteCommand({
    RequestItems: { [TABLE]: items.slice(i, i + 25) },
  }));
}
```

## TTL

```typescript
await docClient.send(new PutCommand({
  TableName: TABLE,
  Item: {
    PK: `SESSION#${sessionId}`,
    SK: "DATA",
    userId,
    ttl: Math.floor(Date.now() / 1000) + 3600, // expires in 1 hour
  },
}));
```

## Additional Resources

- DynamoDB: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/
- Single-table design: https://www.alexdebrie.com/posts/dynamodb-single-table/
- Best practices: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html
