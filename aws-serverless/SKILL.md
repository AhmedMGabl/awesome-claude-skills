---
name: aws-serverless
description: AWS serverless development covering Lambda functions, API Gateway, DynamoDB, S3, SQS/SNS, Step Functions, EventBridge, CDK/SAM infrastructure, and production-ready serverless architecture patterns.
---

# AWS Serverless Development

This skill should be used when building serverless applications on AWS. It covers Lambda, API Gateway, DynamoDB, event-driven architectures, infrastructure as code with CDK/SAM, and production-ready patterns.

## When to Use This Skill

Use this skill when you need to:

- Build AWS Lambda functions (Node.js, Python, Go)
- Configure API Gateway REST and HTTP APIs
- Design DynamoDB tables and access patterns
- Implement event-driven architectures with SQS, SNS, EventBridge
- Orchestrate workflows with Step Functions
- Define infrastructure with AWS CDK or SAM
- Handle authentication with Cognito
- Optimize cost and performance of serverless workloads

## Lambda Functions

### Node.js Handler

```typescript
// src/handlers/getUser.ts
import { APIGatewayProxyHandlerV2 } from "aws-lambda";
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, GetCommand } from "@aws-sdk/lib-dynamodb";

const client = DynamoDBDocumentClient.from(new DynamoDBClient({}));
const TABLE_NAME = process.env.USERS_TABLE!;

export const handler: APIGatewayProxyHandlerV2 = async (event) => {
  const userId = event.pathParameters?.id;
  if (!userId) {
    return { statusCode: 400, body: JSON.stringify({ error: "Missing id" }) };
  }

  try {
    const result = await client.send(new GetCommand({
      TableName: TABLE_NAME,
      Key: { pk: `USER#${userId}`, sk: `PROFILE` },
    }));

    if (!result.Item) {
      return { statusCode: 404, body: JSON.stringify({ error: "User not found" }) };
    }

    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(result.Item),
    };
  } catch (err) {
    console.error("Error fetching user:", err);
    return { statusCode: 500, body: JSON.stringify({ error: "Internal error" }) };
  }
};
```

### Python Handler

```python
# src/handlers/process_order.py
import json
import os
import boto3
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["ORDERS_TABLE"])
sqs = boto3.client("sqs")

def handler(event, context):
    """Process new order from API Gateway."""
    try:
        body = json.loads(event["body"])
        order_id = context.aws_request_id

        # Save to DynamoDB
        item = {
            "pk": f"ORDER#{order_id}",
            "sk": "DETAILS",
            "order_id": order_id,
            "user_id": body["user_id"],
            "items": body["items"],
            "total": str(body["total"]),
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        }
        table.put_item(Item=item)

        # Send to processing queue
        sqs.send_message(
            QueueUrl=os.environ["PROCESSING_QUEUE_URL"],
            MessageBody=json.dumps({"order_id": order_id, "action": "process"}),
        )

        return {
            "statusCode": 201,
            "body": json.dumps({"order_id": order_id, "status": "pending"}),
        }
    except Exception as e:
        print(f"Error: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": "Internal error"})}
```

### Lambda Best Practices

```typescript
// Initialize SDK clients OUTSIDE the handler (reuse across invocations)
const ddbClient = DynamoDBDocumentClient.from(new DynamoDBClient({}));
const s3Client = new S3Client({});

// Middleware pattern with middy
import middy from "@middy/core";
import httpJsonBodyParser from "@middy/http-json-body-parser";
import httpErrorHandler from "@middy/http-error-handler";
import validator from "@middy/validator";

const baseHandler = async (event) => {
  // event.body is already parsed
  const { name, email } = event.body;
  // ... business logic
  return { statusCode: 200, body: JSON.stringify({ success: true }) };
};

export const handler = middy(baseHandler)
  .use(httpJsonBodyParser())
  .use(validator({ eventSchema: createUserSchema }))
  .use(httpErrorHandler());
```

## DynamoDB

### Single-Table Design

```typescript
// Table: AppTable
// pk (partition key) | sk (sort key) | GSI1PK | GSI1SK | data...

// Access patterns:
// 1. Get user by ID:          pk=USER#123, sk=PROFILE
// 2. Get user's orders:       pk=USER#123, sk=begins_with(ORDER#)
// 3. Get order by ID:         pk=ORDER#abc, sk=DETAILS
// 4. Get orders by status:    GSI1PK=STATUS#pending, GSI1SK=begins_with(2024-)
// 5. Get user by email:       GSI1PK=EMAIL#user@test.com, GSI1SK=USER

// Write operations
import { PutCommand, QueryCommand, UpdateCommand } from "@aws-sdk/lib-dynamodb";

// Create user
await client.send(new PutCommand({
  TableName: TABLE_NAME,
  Item: {
    pk: `USER#${userId}`,
    sk: "PROFILE",
    GSI1PK: `EMAIL#${email}`,
    GSI1SK: `USER`,
    name,
    email,
    createdAt: new Date().toISOString(),
  },
  ConditionExpression: "attribute_not_exists(pk)", // Prevent overwrites
}));

// Query user's orders
const orders = await client.send(new QueryCommand({
  TableName: TABLE_NAME,
  KeyConditionExpression: "pk = :pk AND begins_with(sk, :sk)",
  ExpressionAttributeValues: {
    ":pk": `USER#${userId}`,
    ":sk": "ORDER#",
  },
  ScanIndexForward: false, // Newest first
  Limit: 20,
}));

// Update with conditional expression
await client.send(new UpdateCommand({
  TableName: TABLE_NAME,
  Key: { pk: `ORDER#${orderId}`, sk: "DETAILS" },
  UpdateExpression: "SET #status = :new, updatedAt = :now",
  ConditionExpression: "#status = :old",
  ExpressionAttributeNames: { "#status": "status" },
  ExpressionAttributeValues: {
    ":new": "shipped",
    ":old": "processing",
    ":now": new Date().toISOString(),
  },
}));
```

## Event-Driven Patterns

### SQS Consumer

```typescript
// src/handlers/processQueue.ts
import { SQSHandler, SQSRecord } from "aws-lambda";

export const handler: SQSHandler = async (event) => {
  const failures: string[] = [];

  for (const record of event.Records) {
    try {
      await processRecord(record);
    } catch (err) {
      console.error(`Failed to process ${record.messageId}:`, err);
      failures.push(record.messageId);
    }
  }

  // Partial batch failure reporting
  if (failures.length > 0) {
    return {
      batchItemFailures: failures.map((id) => ({ itemIdentifier: id })),
    };
  }
};

async function processRecord(record: SQSRecord): Promise<void> {
  const body = JSON.parse(record.body);
  // Process message...
}
```

### EventBridge Rules

```typescript
// CDK: EventBridge rule for order events
const orderRule = new events.Rule(this, "OrderRule", {
  eventPattern: {
    source: ["orders.service"],
    detailType: ["OrderCreated", "OrderShipped"],
  },
});

orderRule.addTarget(new targets.LambdaFunction(notifyFn));
orderRule.addTarget(new targets.SqsQueue(analyticsQueue));

// Publish event
import { EventBridgeClient, PutEventsCommand } from "@aws-sdk/client-eventbridge";

const eb = new EventBridgeClient({});
await eb.send(new PutEventsCommand({
  Entries: [{
    Source: "orders.service",
    DetailType: "OrderCreated",
    Detail: JSON.stringify({ orderId, userId, total }),
    EventBusName: process.env.EVENT_BUS_NAME,
  }],
}));
```

### Step Functions

```json
{
  "Comment": "Order processing workflow",
  "StartAt": "ValidateOrder",
  "States": {
    "ValidateOrder": {
      "Type": "Task",
      "Resource": "${ValidateOrderFunctionArn}",
      "Next": "CheckInventory",
      "Catch": [{
        "ErrorEquals": ["ValidationError"],
        "Next": "OrderFailed"
      }]
    },
    "CheckInventory": {
      "Type": "Task",
      "Resource": "${CheckInventoryFunctionArn}",
      "Next": "ProcessPayment",
      "Retry": [{
        "ErrorEquals": ["States.TaskFailed"],
        "IntervalSeconds": 2,
        "MaxAttempts": 3,
        "BackoffRate": 2
      }]
    },
    "ProcessPayment": {
      "Type": "Task",
      "Resource": "${ProcessPaymentFunctionArn}",
      "Next": "SendConfirmation"
    },
    "SendConfirmation": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sns:publish",
      "Parameters": {
        "TopicArn": "${NotificationTopicArn}",
        "Message.$": "$.confirmationMessage"
      },
      "End": true
    },
    "OrderFailed": {
      "Type": "Task",
      "Resource": "${HandleFailureFunctionArn}",
      "End": true
    }
  }
}
```

## AWS CDK Infrastructure

```typescript
// lib/serverless-stack.ts
import * as cdk from "aws-cdk-lib";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as nodejs from "aws-cdk-lib/aws-lambda-nodejs";
import * as dynamodb from "aws-cdk-lib/aws-dynamodb";
import * as apigateway from "aws-cdk-lib/aws-apigatewayv2";
import * as integrations from "aws-cdk-lib/aws-apigatewayv2-integrations";
import * as sqs from "aws-cdk-lib/aws-sqs";
import { Construct } from "constructs";

export class ServerlessStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // DynamoDB table
    const table = new dynamodb.Table(this, "AppTable", {
      partitionKey: { name: "pk", type: dynamodb.AttributeType.STRING },
      sortKey: { name: "sk", type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      pointInTimeRecovery: true,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    table.addGlobalSecondaryIndex({
      indexName: "GSI1",
      partitionKey: { name: "GSI1PK", type: dynamodb.AttributeType.STRING },
      sortKey: { name: "GSI1SK", type: dynamodb.AttributeType.STRING },
    });

    // Dead letter queue
    const dlq = new sqs.Queue(this, "DLQ", {
      retentionPeriod: cdk.Duration.days(14),
    });

    // Processing queue
    const queue = new sqs.Queue(this, "ProcessingQueue", {
      visibilityTimeout: cdk.Duration.seconds(30),
      deadLetterQueue: { queue: dlq, maxReceiveCount: 3 },
    });

    // Lambda function (Node.js with esbuild bundling)
    const getUserFn = new nodejs.NodejsFunction(this, "GetUser", {
      entry: "src/handlers/getUser.ts",
      runtime: lambda.Runtime.NODEJS_20_X,
      architecture: lambda.Architecture.ARM_64,
      memorySize: 256,
      timeout: cdk.Duration.seconds(10),
      environment: {
        USERS_TABLE: table.tableName,
        NODE_OPTIONS: "--enable-source-maps",
      },
      bundling: {
        minify: true,
        sourceMap: true,
      },
    });

    // Grant permissions
    table.grantReadData(getUserFn);
    queue.grantSendMessages(getUserFn);

    // HTTP API
    const api = new apigateway.HttpApi(this, "Api", {
      corsPreflight: {
        allowOrigins: ["https://app.example.com"],
        allowMethods: [apigateway.CorsHttpMethod.ANY],
        allowHeaders: ["Authorization", "Content-Type"],
      },
    });

    api.addRoutes({
      path: "/users/{id}",
      methods: [apigateway.HttpMethod.GET],
      integration: new integrations.HttpLambdaIntegration("GetUser", getUserFn),
    });

    // Outputs
    new cdk.CfnOutput(this, "ApiUrl", { value: api.apiEndpoint });
  }
}
```

## SAM Template

```yaml
# template.yaml
AWSTemplateFormatVersion: "2010-09-09"
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Runtime: nodejs20.x
    Architecture: arm64
    MemorySize: 256
    Timeout: 10
    Tracing: Active
    Environment:
      Variables:
        TABLE_NAME: !Ref AppTable

Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: dist/handlers/api.handler
      Events:
        GetUser:
          Type: HttpApi
          Properties:
            Path: /users/{id}
            Method: GET
        CreateUser:
          Type: HttpApi
          Properties:
            Path: /users
            Method: POST
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref AppTable
    Metadata:
      BuildMethod: esbuild
      BuildProperties:
        Minify: true
        Target: es2022
        EntryPoints:
          - src/handlers/api.ts

  AppTable:
    Type: AWS::DynamoDB::Table
    Properties:
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: pk
          AttributeType: S
        - AttributeName: sk
          AttributeType: S
      KeySchema:
        - AttributeName: pk
          KeyType: HASH
        - AttributeName: sk
          KeyType: RANGE
      PointInTimeRecoverySpecification:
        PointInTimeRecoveryEnabled: true

Outputs:
  ApiUrl:
    Value: !Sub "https://${ServerlessHttpApi}.execute-api.${AWS::Region}.amazonaws.com"
```

## Cost and Performance Tips

```markdown
- Use ARM64 (Graviton2) for ~20% lower cost and better performance
- Set memory based on profiling (Lambda Power Tuning tool)
- Use reserved concurrency to prevent runaway costs
- Enable Provisioned Concurrency for latency-sensitive endpoints
- Use DynamoDB PAY_PER_REQUEST for unpredictable workloads
- Use S3 lifecycle policies to move old data to cheaper storage
- Enable X-Ray tracing for debugging distributed systems
- Use Lambda Layers for shared dependencies (reduces deployment size)
- Prefer HTTP API over REST API (~70% cheaper, lower latency)
- Use DynamoDB TTL for automatic cleanup of expired items
```

## Additional Resources

- AWS Lambda docs: https://docs.aws.amazon.com/lambda/
- DynamoDB design: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html
- AWS CDK: https://docs.aws.amazon.com/cdk/
- SAM: https://docs.aws.amazon.com/serverless-application-model/
- Serverless patterns: https://serverlessland.com/patterns
