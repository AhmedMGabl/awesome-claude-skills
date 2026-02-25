---
name: serverless-patterns
description: Serverless architecture patterns covering AWS Lambda function design, cold start optimization, API Gateway integration, event-driven workflows with Step Functions, DynamoDB single-table design, SQS/SNS fan-out, Vercel/Netlify serverless functions, and cost optimization strategies.
---

# Serverless Patterns

This skill should be used when designing serverless architectures and functions. It covers Lambda patterns, event-driven workflows, DynamoDB design, and multi-cloud serverless approaches.

## When to Use This Skill

Use this skill when you need to:

- Design AWS Lambda function handlers
- Build event-driven serverless workflows
- Optimize cold starts and performance
- Implement DynamoDB single-table design
- Create Step Functions state machines
- Deploy serverless functions on Vercel/Netlify

## Lambda Handler Patterns

```typescript
import { APIGatewayProxyHandlerV2, SQSHandler, EventBridgeHandler } from "aws-lambda";

// API Gateway handler with middleware pattern
const handler: APIGatewayProxyHandlerV2 = async (event) => {
  try {
    const body = JSON.parse(event.body ?? "{}");
    const userId = event.requestContext.authorizer?.jwt?.claims?.sub;

    if (!userId) return { statusCode: 401, body: JSON.stringify({ error: "Unauthorized" }) };

    const result = await processRequest(userId, body);
    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(result),
    };
  } catch (error) {
    console.error("Handler error:", error);
    return { statusCode: 500, body: JSON.stringify({ error: "Internal error" }) };
  }
};

// SQS consumer (batch processing)
const sqsHandler: SQSHandler = async (event) => {
  const results = await Promise.allSettled(
    event.Records.map(async (record) => {
      const message = JSON.parse(record.body);
      await processMessage(message);
    }),
  );

  // Return failed items for retry (partial batch failure)
  const failures = results
    .map((r, i) => (r.status === "rejected" ? event.Records[i].messageId : null))
    .filter(Boolean);

  return { batchItemFailures: failures.map((id) => ({ itemIdentifier: id! })) };
};

// EventBridge handler
const eventHandler: EventBridgeHandler<"OrderCreated", OrderEvent, void> = async (event) => {
  const order = event.detail;
  await sendConfirmationEmail(order);
  await updateInventory(order.items);
};
```

## Cold Start Optimization

```typescript
// Initialize outside handler (reused across invocations)
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient } from "@aws-sdk/lib-dynamodb";

const client = new DynamoDBClient({});
const ddb = DynamoDBDocumentClient.from(client);

// Lazy initialization pattern
let cachedConfig: AppConfig | undefined;
async function getConfig(): Promise<AppConfig> {
  if (!cachedConfig) {
    cachedConfig = await fetchConfig();
  }
  return cachedConfig;
}

// Keep functions small and focused
// Use layers for shared dependencies
// Prefer ARM64 (Graviton2) — 20% cheaper, often faster
// Set memory to 1024-1769 MB for CPU-bound tasks (1 vCPU at 1769 MB)
```

## DynamoDB Single-Table Design

```typescript
import { PutCommand, QueryCommand, GetCommand } from "@aws-sdk/lib-dynamodb";

// Single table with generic PK/SK
// PK              SK                  Data
// USER#123        PROFILE             name, email, plan
// USER#123        ORDER#2024-001      total, status, items
// USER#123        ORDER#2024-002      total, status, items
// ORDER#2024-001  ORDER#2024-001      full order details (GSI)

async function createUser(user: User) {
  await ddb.send(new PutCommand({
    TableName: TABLE,
    Item: {
      PK: `USER#${user.id}`,
      SK: "PROFILE",
      GSI1PK: `EMAIL#${user.email}`,
      GSI1SK: `USER#${user.id}`,
      ...user,
      type: "User",
    },
    ConditionExpression: "attribute_not_exists(PK)",
  }));
}

async function getUserOrders(userId: string) {
  const result = await ddb.send(new QueryCommand({
    TableName: TABLE,
    KeyConditionExpression: "PK = :pk AND begins_with(SK, :sk)",
    ExpressionAttributeValues: { ":pk": `USER#${userId}`, ":sk": "ORDER#" },
    ScanIndexForward: false,
  }));
  return result.Items;
}
```

## Step Functions Workflow

```json
{
  "Comment": "Order processing workflow",
  "StartAt": "ValidateOrder",
  "States": {
    "ValidateOrder": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123:function:validate-order",
      "Next": "ProcessPayment",
      "Catch": [{ "ErrorEquals": ["ValidationError"], "Next": "OrderFailed" }]
    },
    "ProcessPayment": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123:function:process-payment",
      "Next": "ParallelFulfillment",
      "Retry": [{ "ErrorEquals": ["PaymentRetryable"], "MaxAttempts": 3, "BackoffRate": 2 }],
      "Catch": [{ "ErrorEquals": ["States.ALL"], "Next": "OrderFailed" }]
    },
    "ParallelFulfillment": {
      "Type": "Parallel",
      "Branches": [
        { "StartAt": "SendConfirmation", "States": { "SendConfirmation": { "Type": "Task", "Resource": "arn:aws:lambda:us-east-1:123:function:send-email", "End": true } } },
        { "StartAt": "UpdateInventory", "States": { "UpdateInventory": { "Type": "Task", "Resource": "arn:aws:lambda:us-east-1:123:function:update-inventory", "End": true } } }
      ],
      "Next": "OrderComplete"
    },
    "OrderComplete": { "Type": "Succeed" },
    "OrderFailed": { "Type": "Fail", "Error": "OrderProcessingFailed" }
  }
}
```

## Vercel Serverless Functions

```typescript
// api/users/[id]/route.ts (Next.js App Router)
import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest, { params }: { params: { id: string } }) {
  const user = await db.user.findUnique({ where: { id: params.id } });
  if (!user) return NextResponse.json({ error: "Not found" }, { status: 404 });
  return NextResponse.json(user);
}

// Edge function (runs on CDN edge)
export const runtime = "edge";

export async function GET(req: NextRequest) {
  const country = req.geo?.country ?? "US";
  const data = await fetch(`https://api.example.com/content?region=${country}`);
  return NextResponse.json(await data.json());
}
```

## Additional Resources

- AWS Lambda docs: https://docs.aws.amazon.com/lambda/
- Serverless Framework: https://www.serverless.com/
- SST: https://sst.dev/
- DynamoDB single-table: https://www.alexdebrie.com/posts/dynamodb-single-table/
