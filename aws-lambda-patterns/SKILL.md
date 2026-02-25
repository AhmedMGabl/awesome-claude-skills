---
name: aws-lambda-patterns
description: AWS Lambda patterns covering handler design, event sources, API Gateway integration, layers, cold start optimization, DynamoDB triggers, SQS processing, and testing.
---

# AWS Lambda Patterns

This skill should be used when building serverless applications with AWS Lambda. It covers handler design, event sources, API Gateway, layers, cold starts, triggers, and testing.

## When to Use This Skill

Use this skill when you need to:

- Design Lambda handler functions
- Integrate with API Gateway, SQS, DynamoDB Streams
- Optimize cold start performance
- Use Lambda layers for shared code
- Test Lambda functions locally

## Handler Pattern (TypeScript)

```typescript
import { APIGatewayProxyHandlerV2 } from "aws-lambda";

export const handler: APIGatewayProxyHandlerV2 = async (event) => {
  try {
    const body = JSON.parse(event.body || "{}");
    const result = await processRequest(body);

    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(result),
    };
  } catch (error) {
    console.error("Handler error:", error);
    return {
      statusCode: error instanceof ValidationError ? 400 : 500,
      body: JSON.stringify({ error: error.message }),
    };
  }
};
```

## Handler Pattern (Python)

```python
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        result = process_request(body)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(result),
        }
    except ValidationError as e:
        return {"statusCode": 400, "body": json.dumps({"error": str(e)})}
    except Exception as e:
        logger.error(f"Handler error: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": "Internal error"})}
```

## SQS Event Processing

```typescript
import { SQSHandler } from "aws-lambda";

export const handler: SQSHandler = async (event) => {
  const failures: string[] = [];

  for (const record of event.Records) {
    try {
      const message = JSON.parse(record.body);
      await processMessage(message);
    } catch (error) {
      console.error(`Failed record ${record.messageId}:`, error);
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
```

## DynamoDB Stream Trigger

```typescript
import { DynamoDBStreamHandler } from "aws-lambda";
import { unmarshall } from "@aws-sdk/util-dynamodb";

export const handler: DynamoDBStreamHandler = async (event) => {
  for (const record of event.Records) {
    if (record.eventName === "INSERT" || record.eventName === "MODIFY") {
      const newImage = unmarshall(record.dynamodb!.NewImage!);
      await syncToSearchIndex(newImage);
    }
    if (record.eventName === "REMOVE") {
      const oldImage = unmarshall(record.dynamodb!.OldImage!);
      await removeFromSearchIndex(oldImage.id);
    }
  }
};
```

## Cold Start Optimization

```typescript
// Initialize outside handler (reused across invocations)
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient } from "@aws-sdk/lib-dynamodb";

const client = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(client);

// Use provisioned concurrency for latency-sensitive functions
// Use ARM64 architecture for better price-performance
// Keep deployment package small - use layers for dependencies
```

## SAM Template

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Runtime: nodejs20.x
    Timeout: 30
    MemorySize: 256
    Architectures: [arm64]
    Environment:
      Variables:
        TABLE_NAME: !Ref UsersTable

Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: src/handlers/api.handler
      Events:
        GetUsers:
          Type: Api
          Properties:
            Path: /users
            Method: get
        CreateUser:
          Type: Api
          Properties:
            Path: /users
            Method: post
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref UsersTable

  QueueProcessor:
    Type: AWS::Serverless::Function
    Properties:
      Handler: src/handlers/queue.handler
      Events:
        SQSEvent:
          Type: SQS
          Properties:
            Queue: !GetAtt ProcessingQueue.Arn
            BatchSize: 10
            FunctionResponseTypes: [ReportBatchItemFailures]

  UsersTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: users
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - { AttributeName: pk, AttributeType: S }
        - { AttributeName: sk, AttributeType: S }
      KeySchema:
        - { AttributeName: pk, KeyType: HASH }
        - { AttributeName: sk, KeyType: RANGE }

  ProcessingQueue:
    Type: AWS::SQS::Queue
```

## Testing

```typescript
import { handler } from "./api";
import { APIGatewayProxyEventV2 } from "aws-lambda";

describe("API handler", () => {
  it("should return users", async () => {
    const event = {
      requestContext: { http: { method: "GET" } },
      pathParameters: {},
    } as unknown as APIGatewayProxyEventV2;

    const result = await handler(event, {} as any, {} as any);
    expect(result.statusCode).toBe(200);
  });
});
```

## Additional Resources

- Lambda: https://docs.aws.amazon.com/lambda/latest/dg/
- SAM: https://docs.aws.amazon.com/serverless-application-model/
- Best Practices: https://docs.aws.amazon.com/lambda/latest/operatorguide/
