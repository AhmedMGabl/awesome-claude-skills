---
name: aws-cdk
description: AWS CDK infrastructure as code covering constructs, stacks, L1/L2/L3 patterns, Lambda functions, API Gateway, DynamoDB, S3, CloudFront, custom resources, testing, and CI/CD pipelines.
---

# AWS CDK

This skill should be used when defining AWS infrastructure with the Cloud Development Kit. It covers constructs, stacks, Lambda, API Gateway, DynamoDB, S3, testing, and deployment pipelines.

## When to Use This Skill

Use this skill when you need to:

- Define AWS infrastructure in TypeScript
- Create reusable construct libraries
- Deploy serverless APIs with Lambda and API Gateway
- Set up S3 + CloudFront static hosting
- Test infrastructure with CDK assertions

## Project Setup

```bash
npx cdk init app --language typescript
npx cdk bootstrap aws://ACCOUNT/REGION
```

## Basic Stack

```typescript
// lib/api-stack.ts
import * as cdk from "aws-cdk-lib";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as apigateway from "aws-cdk-lib/aws-apigateway";
import * as dynamodb from "aws-cdk-lib/aws-dynamodb";
import { NodejsFunction } from "aws-cdk-lib/aws-lambda-nodejs";
import { Construct } from "constructs";

export class ApiStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // DynamoDB table
    const table = new dynamodb.Table(this, "ItemsTable", {
      partitionKey: { name: "PK", type: dynamodb.AttributeType.STRING },
      sortKey: { name: "SK", type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      pointInTimeRecovery: true,
    });

    table.addGlobalSecondaryIndex({
      indexName: "GSI1",
      partitionKey: { name: "GSI1PK", type: dynamodb.AttributeType.STRING },
      sortKey: { name: "GSI1SK", type: dynamodb.AttributeType.STRING },
    });

    // Lambda function
    const handler = new NodejsFunction(this, "ApiHandler", {
      entry: "lambda/api/index.ts",
      handler: "handler",
      runtime: lambda.Runtime.NODEJS_20_X,
      architecture: lambda.Architecture.ARM_64,
      memorySize: 256,
      timeout: cdk.Duration.seconds(30),
      environment: {
        TABLE_NAME: table.tableName,
        NODE_OPTIONS: "--enable-source-maps",
      },
      bundling: {
        minify: true,
        sourceMap: true,
        externalModules: ["@aws-sdk/*"],
      },
    });

    table.grantReadWriteData(handler);

    // API Gateway
    const api = new apigateway.RestApi(this, "Api", {
      restApiName: "items-api",
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
      },
    });

    const items = api.root.addResource("items");
    items.addMethod("GET", new apigateway.LambdaIntegration(handler));
    items.addMethod("POST", new apigateway.LambdaIntegration(handler));
    const item = items.addResource("{id}");
    item.addMethod("GET", new apigateway.LambdaIntegration(handler));
    item.addMethod("PUT", new apigateway.LambdaIntegration(handler));
    item.addMethod("DELETE", new apigateway.LambdaIntegration(handler));

    new cdk.CfnOutput(this, "ApiUrl", { value: api.url });
  }
}
```

## Static Site with CloudFront

```typescript
import * as s3 from "aws-cdk-lib/aws-s3";
import * as cloudfront from "aws-cdk-lib/aws-cloudfront";
import * as origins from "aws-cdk-lib/aws-cloudfront-origins";
import * as s3deploy from "aws-cdk-lib/aws-s3-deployment";
import * as acm from "aws-cdk-lib/aws-certificatemanager";
import * as route53 from "aws-cdk-lib/aws-route53";
import * as targets from "aws-cdk-lib/aws-route53-targets";

export class StaticSiteStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: StaticSiteProps) {
    super(scope, id, props);

    const bucket = new s3.Bucket(this, "SiteBucket", {
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });

    const certificate = acm.Certificate.fromCertificateArn(
      this, "Cert", props.certificateArn,
    );

    const distribution = new cloudfront.Distribution(this, "CDN", {
      defaultBehavior: {
        origin: origins.S3BucketOrigin.withOriginAccessControl(bucket),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
      },
      defaultRootObject: "index.html",
      domainNames: [props.domainName],
      certificate,
      errorResponses: [
        { httpStatus: 404, responsePagePath: "/index.html", responseHttpStatus: 200 },
      ],
    });

    new s3deploy.BucketDeployment(this, "Deploy", {
      sources: [s3deploy.Source.asset("./dist")],
      destinationBucket: bucket,
      distribution,
      distributionPaths: ["/*"],
    });

    const zone = route53.HostedZone.fromLookup(this, "Zone", {
      domainName: props.domainName,
    });

    new route53.ARecord(this, "AliasRecord", {
      zone,
      recordName: props.domainName,
      target: route53.RecordTarget.fromAlias(
        new targets.CloudFrontTarget(distribution),
      ),
    });
  }
}
```

## Reusable Construct

```typescript
// constructs/monitored-lambda.ts
export interface MonitoredLambdaProps {
  entry: string;
  handler?: string;
  environment?: Record<string, string>;
  memorySize?: number;
  timeout?: cdk.Duration;
  alarmEmail?: string;
}

export class MonitoredLambda extends Construct {
  public readonly function: NodejsFunction;

  constructor(scope: Construct, id: string, props: MonitoredLambdaProps) {
    super(scope, id);

    this.function = new NodejsFunction(this, "Function", {
      entry: props.entry,
      handler: props.handler ?? "handler",
      runtime: lambda.Runtime.NODEJS_20_X,
      architecture: lambda.Architecture.ARM_64,
      memorySize: props.memorySize ?? 256,
      timeout: props.timeout ?? cdk.Duration.seconds(30),
      environment: props.environment,
      tracing: lambda.Tracing.ACTIVE,
    });

    // Error alarm
    const errorAlarm = this.function
      .metricErrors({ period: cdk.Duration.minutes(5) })
      .createAlarm(this, "ErrorAlarm", {
        threshold: 5,
        evaluationPeriods: 1,
        alarmDescription: `${id} error rate alarm`,
      });

    if (props.alarmEmail) {
      const topic = new sns.Topic(this, "AlarmTopic");
      topic.addSubscription(new subs.EmailSubscription(props.alarmEmail));
      errorAlarm.addAlarmAction(new cw_actions.SnsAction(topic));
    }
  }
}
```

## Testing

```typescript
import { Template, Match, Capture } from "aws-cdk-lib/assertions";
import * as cdk from "aws-cdk-lib";
import { ApiStack } from "../lib/api-stack";

describe("ApiStack", () => {
  const app = new cdk.App();
  const stack = new ApiStack(app, "TestStack");
  const template = Template.fromStack(stack);

  test("creates DynamoDB table with correct key schema", () => {
    template.hasResourceProperties("AWS::DynamoDB::Table", {
      KeySchema: [
        { AttributeName: "PK", KeyType: "HASH" },
        { AttributeName: "SK", KeyType: "RANGE" },
      ],
      BillingMode: "PAY_PER_REQUEST",
    });
  });

  test("Lambda has correct runtime and memory", () => {
    template.hasResourceProperties("AWS::Lambda::Function", {
      Runtime: "nodejs20.x",
      MemorySize: 256,
      Architectures: ["arm64"],
    });
  });

  test("API Gateway has CORS configured", () => {
    template.hasResourceProperties("AWS::ApiGateway::Method", {
      HttpMethod: "OPTIONS",
    });
  });

  test("Lambda has read/write access to DynamoDB", () => {
    template.hasResourceProperties("AWS::IAM::Policy", {
      PolicyDocument: Match.objectLike({
        Statement: Match.arrayWith([
          Match.objectLike({
            Action: Match.arrayWith(["dynamodb:BatchGetItem"]),
          }),
        ]),
      }),
    });
  });
});
```

## CDK Pipeline

```typescript
import { CodePipeline, CodePipelineSource, ShellStep } from "aws-cdk-lib/pipelines";

export class PipelineStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const pipeline = new CodePipeline(this, "Pipeline", {
      pipelineName: "AppPipeline",
      synth: new ShellStep("Synth", {
        input: CodePipelineSource.gitHub("owner/repo", "main"),
        commands: ["npm ci", "npm run build", "npx cdk synth"],
      }),
    });

    pipeline.addStage(new AppStage(this, "Staging", {
      env: { account: "111111111111", region: "us-east-1" },
    }));

    pipeline.addStage(new AppStage(this, "Production", {
      env: { account: "222222222222", region: "us-east-1" },
    }), {
      pre: [new ManualApprovalStep("PromoteToProd")],
    });
  }
}
```

## CLI Commands

```bash
npx cdk synth         # Generate CloudFormation template
npx cdk diff          # Show changes vs deployed
npx cdk deploy        # Deploy stack
npx cdk deploy --all  # Deploy all stacks
npx cdk destroy       # Tear down stack
npx cdk list          # List all stacks
```

## Additional Resources

- AWS CDK docs: https://docs.aws.amazon.com/cdk/v2/guide/
- CDK Construct Hub: https://constructs.dev/
- CDK Patterns: https://cdkpatterns.com/
