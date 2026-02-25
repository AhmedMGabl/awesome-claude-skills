---
name: aws-lambda
description: AWS Lambda serverless functions covering handler patterns, API Gateway integration, event sources (S3, SQS, DynamoDB Streams), cold start optimization, layers, environment configuration, SAM and CDK deployment, error handling, and monitoring with CloudWatch.
---

# AWS Lambda

This skill should be used when building serverless functions with AWS Lambda. It covers handler patterns, event sources, deployment, optimization, and monitoring.

## When to Use This Skill

Use this skill when you need to:

- Build serverless API endpoints with Lambda + API Gateway
- Process events from S3, SQS, DynamoDB, or EventBridge
- Deploy Lambda functions with SAM or CDK
- Optimize cold start performance
- Monitor and debug Lambda functions

## HTTP API Handler

```typescript
// handler.ts
import { APIGatewayProxyHandlerV2 } from "aws-lambda";

export const handler: APIGatewayProxyHandlerV2 = async (event) => {
  const method = event.requestContext.http.method;
  const path = event.rawPath;

  try {
    if (method === "GET" && path === "/users") {
      const users = await db.query("SELECT * FROM users LIMIT 50");
      return { statusCode: 200, body: JSON.stringify(users) };
    }

    if (method === "POST" && path === "/users") {
      const body = JSON.parse(event.body || "{}");
      const user = await db.query(
        "INSERT INTO users (name, email) VALUES ($1, $2) RETURNING *",
        [body.name, body.email],
      );
      return { statusCode: 201, body: JSON.stringify(user) };
    }

    return { statusCode: 404, body: JSON.stringify({ error: "Not found" }) };
  } catch (error) {
    console.error("Handler error:", error);
    return { statusCode: 500, body: JSON.stringify({ error: "Internal error" }) };
  }
};
```

## SQS Event Handler

```typescript
import { SQSHandler, SQSBatchResponse } from "aws-lambda";

export const handler: SQSHandler = async (event): Promise<SQSBatchResponse> => {
  const batchItemFailures: SQSBatchResponse["batchItemFailures"] = [];

  for (const record of event.Records) {
    try {
      const body = JSON.parse(record.body);
      await processMessage(body);
    } catch (error) {
      console.error(`Failed to process ${record.messageId}:`, error);
      batchItemFailures.push({ itemIdentifier: record.messageId });
    }
  }

  return { batchItemFailures }; // Partial batch failure reporting
};
```

## S3 Event Handler

```typescript
import { S3Handler } from "aws-lambda";
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";

const s3 = new S3Client({});

export const handler: S3Handler = async (event) => {
  for (const record of event.Records) {
    const bucket = record.s3.bucket.name;
    const key = decodeURIComponent(record.s3.object.key.replace(/\+/g, " "));

    const response = await s3.send(
      new GetObjectCommand({ Bucket: bucket, Key: key }),
    );
    const content = await response.Body?.transformToString();

    console.log(`Processing ${key} from ${bucket}, size: ${record.s3.object.size}`);
    await processFile(key, content);
  }
};
```

## DynamoDB Streams Handler

```typescript
import { DynamoDBStreamHandler } from "aws-lambda";
import { unmarshall } from "@aws-sdk/util-dynamodb";

export const handler: DynamoDBStreamHandler = async (event) => {
  for (const record of event.Records) {
    const eventName = record.eventName; // INSERT, MODIFY, REMOVE

    if (record.dynamodb?.NewImage) {
      const newItem = unmarshall(record.dynamodb.NewImage as any);
      console.log(`${eventName}:`, newItem);

      if (eventName === "INSERT") {
        await onNewUser(newItem);
      }
    }
  }
};
```

## CDK Deployment

```typescript
import * as cdk from "aws-cdk-lib";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as apigateway from "aws-cdk-lib/aws-apigatewayv2";
import { NodejsFunction } from "aws-cdk-lib/aws-lambda-nodejs";

const fn = new NodejsFunction(this, "ApiHandler", {
  entry: "src/handler.ts",
  runtime: lambda.Runtime.NODEJS_20_X,
  memorySize: 256,
  timeout: cdk.Duration.seconds(30),
  environment: {
    DATABASE_URL: process.env.DATABASE_URL!,
    NODE_ENV: "production",
  },
  bundling: {
    minify: true,
    sourceMap: true,
    externalModules: ["@aws-sdk/*"], // Use Lambda-provided SDK
  },
});
```

## SAM Template

```yaml
# template.yaml
AWSTemplateFormatVersion: "2010-09-09"
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Runtime: nodejs20.x
    Timeout: 30
    MemorySize: 256

Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: dist/handler.handler
      Events:
        Api:
          Type: HttpApi
          Properties:
            Path: /{proxy+}
            Method: ANY
```

## Cold Start Optimization

```
TECHNIQUE              IMPACT        HOW
────────────────────────────────────────────────────
Smaller bundle         High          Tree-shake, minify, exclude SDK
Provisioned concur.    High          Keep instances warm (costs more)
ARM64 (Graviton)       Medium        Set architecture to arm64
Lazy initialization    Medium        Init DB connections on first use
ESM modules            Medium        Use ES modules instead of CJS
Minimal dependencies   High          Avoid heavy packages
```

## Additional Resources

- Lambda docs: https://docs.aws.amazon.com/lambda/
- SAM: https://docs.aws.amazon.com/serverless-application-model/
- CDK Lambda: https://docs.aws.amazon.com/cdk/api/v2/docs/aws-lambda-readme.html
