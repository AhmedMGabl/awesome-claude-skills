---
name: api-gateway
description: API gateway patterns covering request routing, rate limiting, authentication middleware, request/response transformation, load balancing, circuit breaking, API composition, Kong/AWS API Gateway configuration, and BFF (Backend for Frontend) architecture.
---

# API Gateway

This skill should be used when implementing or configuring API gateways. It covers routing, rate limiting, authentication, transformation, and BFF patterns.

## When to Use This Skill

Use this skill when you need to:

- Route requests to multiple microservices
- Implement cross-cutting concerns (auth, rate limiting)
- Transform API requests/responses
- Set up AWS API Gateway or Kong
- Implement Backend for Frontend (BFF) pattern

## Express API Gateway

```typescript
import express from "express";
import { createProxyMiddleware } from "http-proxy-middleware";

const app = express();

// Authentication middleware
app.use("/api", authenticateRequest);

// Rate limiting
app.use("/api", rateLimiter({ windowMs: 60_000, max: 100 }));

// Route to microservices
app.use(
  "/api/users",
  createProxyMiddleware({
    target: process.env.USER_SERVICE_URL,
    pathRewrite: { "^/api/users": "" },
    changeOrigin: true,
  }),
);

app.use(
  "/api/orders",
  createProxyMiddleware({
    target: process.env.ORDER_SERVICE_URL,
    pathRewrite: { "^/api/orders": "" },
    changeOrigin: true,
  }),
);

app.use(
  "/api/products",
  createProxyMiddleware({
    target: process.env.PRODUCT_SERVICE_URL,
    pathRewrite: { "^/api/products": "" },
    changeOrigin: true,
  }),
);
```

## API Composition (BFF Pattern)

```typescript
// Aggregate data from multiple services into one response
app.get("/api/dashboard", async (req, res) => {
  const userId = req.user.id;

  // Fetch from multiple services in parallel
  const [user, orders, recommendations] = await Promise.all([
    fetch(`${USER_SERVICE}/users/${userId}`).then((r) => r.json()),
    fetch(`${ORDER_SERVICE}/orders?userId=${userId}&limit=5`).then((r) => r.json()),
    fetch(`${PRODUCT_SERVICE}/recommendations/${userId}`).then((r) => r.json()),
  ]);

  res.json({
    user: { name: user.name, avatar: user.avatar },
    recentOrders: orders.items,
    recommendations: recommendations.items.slice(0, 4),
  });
});
```

## AWS API Gateway (CDK)

```typescript
import * as cdk from "aws-cdk-lib";
import * as apigateway from "aws-cdk-lib/aws-apigateway";
import * as lambda from "aws-cdk-lib/aws-lambda";

const api = new apigateway.RestApi(this, "MyApi", {
  restApiName: "My Service",
  deployOptions: {
    stageName: "v1",
    throttlingRateLimit: 1000,
    throttlingBurstLimit: 500,
  },
  defaultCorsPreflightOptions: {
    allowOrigins: apigateway.Cors.ALL_ORIGINS,
    allowMethods: apigateway.Cors.ALL_METHODS,
  },
});

// Lambda integration
const usersHandler = new lambda.Function(this, "UsersHandler", {
  runtime: lambda.Runtime.NODEJS_22_X,
  handler: "index.handler",
  code: lambda.Code.fromAsset("lambda/users"),
});

const users = api.root.addResource("users");
users.addMethod("GET", new apigateway.LambdaIntegration(usersHandler));
users.addMethod("POST", new apigateway.LambdaIntegration(usersHandler));

// API Key and usage plan
const apiKey = api.addApiKey("MyApiKey");
const plan = api.addUsagePlan("UsagePlan", {
  throttle: { rateLimit: 100, burstLimit: 50 },
  quota: { limit: 10000, period: apigateway.Period.MONTH },
});
plan.addApiKey(apiKey);
plan.addApiStage({ stage: api.deploymentStage });
```

## Gateway Patterns

```
PATTERN                DESCRIPTION
──────────────────────────────────────────────────────
API Composition        Aggregate multiple service calls
Request Routing        Route to correct microservice
Rate Limiting          Throttle requests per client
Authentication         Verify tokens, API keys
Circuit Breaking       Fail fast when service is down
Request Transform      Modify headers, body, path
Response Caching       Cache responses at gateway level
Load Balancing         Distribute across instances
BFF                    Dedicated gateway per client type

WHEN TO USE BFF:
  Mobile app    → /api/mobile/*   (optimized payloads)
  Web app       → /api/web/*      (full payloads)
  Third-party   → /api/v1/*       (stable, versioned)
```

## Additional Resources

- Kong Gateway: https://docs.konghq.com/
- AWS API Gateway: https://docs.aws.amazon.com/apigateway/
- Express Gateway: https://www.express-gateway.io/
