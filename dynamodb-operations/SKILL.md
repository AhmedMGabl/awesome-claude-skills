---
name: dynamodb-operations
description: Amazon DynamoDB operations covering table design with partition and sort keys, single-table design patterns, CRUD with AWS SDK v3, query and scan operations, Global Secondary Indexes, batch operations, DynamoDB Streams, TTL, transactions, and cost optimization strategies.
---

# DynamoDB Operations

This skill should be used when working with Amazon DynamoDB. It covers table design, single-table patterns, CRUD operations, indexes, streams, and optimization.

## When to Use This Skill

Use this skill when you need to:

- Design DynamoDB tables with proper key schemas
- Implement single-table design patterns
- Perform CRUD, query, and batch operations
- Set up Global Secondary Indexes (GSIs)
- Handle DynamoDB Streams and transactions

## Table Design

```typescript
import { DynamoDBClient, CreateTableCommand } from "@aws-sdk/client-dynamodb";

const client = new DynamoDBClient({ region: "us-east-1" });

// Single-table design
await client.send(new CreateTableCommand({
  TableName: "AppTable",
  KeySchema: [
    { AttributeName: "PK", KeyType: "HASH" },
    { AttributeName: "SK", KeyType: "RANGE" },
  ],
  AttributeDefinitions: [
    { AttributeName: "PK", AttributeType: "S" },
    { AttributeName: "SK", AttributeType: "S" },
    { AttributeName: "GSI1PK", AttributeType: "S" },
    { AttributeName: "GSI1SK", AttributeType: "S" },
  ],
  GlobalSecondaryIndexes: [{
    IndexName: "GSI1",
    KeySchema: [
      { AttributeName: "GSI1PK", KeyType: "HASH" },
      { AttributeName: "GSI1SK", KeyType: "RANGE" },
    ],
    Projection: { ProjectionType: "ALL" },
  }],
  BillingMode: "PAY_PER_REQUEST",
}));
```

## CRUD Operations (SDK v3 + DynamoDB Document Client)

```typescript
import { DynamoDBDocumentClient, PutCommand, GetCommand, UpdateCommand, DeleteCommand, QueryCommand } from "@aws-sdk/lib-dynamodb";

const docClient = DynamoDBDocumentClient.from(new DynamoDBClient({}));

// Create
async function createUser(user: { id: string; email: string; name: string }) {
  await docClient.send(new PutCommand({
    TableName: "AppTable",
    Item: {
      PK: `USER#${user.id}`,
      SK: `PROFILE`,
      GSI1PK: `EMAIL#${user.email}`,
      GSI1SK: `USER#${user.id}`,
      ...user,
      createdAt: new Date().toISOString(),
    },
    ConditionExpression: "attribute_not_exists(PK)",
  }));
}

// Read
async function getUser(id: string) {
  const { Item } = await docClient.send(new GetCommand({
    TableName: "AppTable",
    Key: { PK: `USER#${id}`, SK: "PROFILE" },
  }));
  return Item;
}

// Update
async function updateUser(id: string, name: string) {
  const { Attributes } = await docClient.send(new UpdateCommand({
    TableName: "AppTable",
    Key: { PK: `USER#${id}`, SK: "PROFILE" },
    UpdateExpression: "SET #name = :name, updatedAt = :now",
    ExpressionAttributeNames: { "#name": "name" },
    ExpressionAttributeValues: { ":name": name, ":now": new Date().toISOString() },
    ReturnValues: "ALL_NEW",
  }));
  return Attributes;
}

// Delete
async function deleteUser(id: string) {
  await docClient.send(new DeleteCommand({
    TableName: "AppTable",
    Key: { PK: `USER#${id}`, SK: "PROFILE" },
  }));
}
```

## Query Patterns

```typescript
// Get all orders for a user
async function getUserOrders(userId: string) {
  const { Items } = await docClient.send(new QueryCommand({
    TableName: "AppTable",
    KeyConditionExpression: "PK = :pk AND begins_with(SK, :sk)",
    ExpressionAttributeValues: {
      ":pk": `USER#${userId}`,
      ":sk": "ORDER#",
    },
    ScanIndexForward: false,  // newest first
  }));
  return Items;
}

// Query GSI — find user by email
async function getUserByEmail(email: string) {
  const { Items } = await docClient.send(new QueryCommand({
    TableName: "AppTable",
    IndexName: "GSI1",
    KeyConditionExpression: "GSI1PK = :pk",
    ExpressionAttributeValues: { ":pk": `EMAIL#${email}` },
  }));
  return Items?.[0];
}

// Paginated query
async function getOrdersPage(userId: string, lastKey?: Record<string, any>) {
  const { Items, LastEvaluatedKey } = await docClient.send(new QueryCommand({
    TableName: "AppTable",
    KeyConditionExpression: "PK = :pk AND begins_with(SK, :sk)",
    ExpressionAttributeValues: { ":pk": `USER#${userId}`, ":sk": "ORDER#" },
    Limit: 20,
    ExclusiveStartKey: lastKey,
  }));
  return { items: Items, nextKey: LastEvaluatedKey };
}
```

## Batch Operations

```typescript
import { BatchWriteCommand, BatchGetCommand } from "@aws-sdk/lib-dynamodb";

// Batch write (max 25 items per request)
async function batchCreateItems(items: any[]) {
  const chunks = [];
  for (let i = 0; i < items.length; i += 25) {
    chunks.push(items.slice(i, i + 25));
  }

  for (const chunk of chunks) {
    await docClient.send(new BatchWriteCommand({
      RequestItems: {
        AppTable: chunk.map((item) => ({
          PutRequest: { Item: item },
        })),
      },
    }));
  }
}
```

## Transactions

```typescript
import { TransactWriteCommand } from "@aws-sdk/lib-dynamodb";

async function placeOrder(userId: string, orderId: string, amount: number) {
  await docClient.send(new TransactWriteCommand({
    TransactItems: [
      {
        Put: {
          TableName: "AppTable",
          Item: { PK: `USER#${userId}`, SK: `ORDER#${orderId}`, amount, status: "placed" },
        },
      },
      {
        Update: {
          TableName: "AppTable",
          Key: { PK: `USER#${userId}`, SK: "PROFILE" },
          UpdateExpression: "SET orderCount = orderCount + :one",
          ExpressionAttributeValues: { ":one": 1 },
        },
      },
    ],
  }));
}
```

## Single-Table Design Patterns

```
ENTITY        PK                SK              GSI1PK            GSI1SK
─────────────────────────────────────────────────────────────────────────
User          USER#<id>         PROFILE         EMAIL#<email>     USER#<id>
Order         USER#<id>         ORDER#<id>      ORDER#<id>        STATUS#<status>
Product       PROD#<id>         DETAILS         CAT#<category>    PROD#<id>
```

## Additional Resources

- DynamoDB docs: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/
- Single-table design: https://www.alexdebrie.com/posts/dynamodb-single-table/
- AWS SDK v3: https://docs.aws.amazon.com/AWSJavaScriptSDK/v3/latest/
