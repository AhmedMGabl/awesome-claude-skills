---
name: azure-functions
description: Azure Functions patterns covering HTTP triggers, timer triggers, queue bindings, Durable Functions orchestration, Cosmos DB integration, and deployment configuration.
---

# Azure Functions

This skill should be used when building serverless applications with Azure Functions. It covers HTTP triggers, timer triggers, queue bindings, Durable Functions, Cosmos DB, and deployment.

## When to Use This Skill

Use this skill when you need to:

- Build serverless APIs with HTTP triggers
- Process messages from Azure Queue Storage or Service Bus
- Orchestrate workflows with Durable Functions
- Schedule tasks with timer triggers
- Integrate with Cosmos DB and Blob Storage

## HTTP Trigger (TypeScript)

```typescript
import { app, HttpRequest, HttpResponseInit, InvocationContext } from "@azure/functions";

app.http("getUsers", {
  methods: ["GET"],
  authLevel: "anonymous",
  route: "users/{id?}",
  handler: async (request: HttpRequest, context: InvocationContext): Promise<HttpResponseInit> => {
    const id = request.params.id;

    if (id) {
      const user = await getUserById(id);
      return user
        ? { jsonBody: user }
        : { status: 404, jsonBody: { error: "Not found" } };
    }

    const page = parseInt(request.query.get("page") || "1");
    const users = await getUsers(page);
    return { jsonBody: users };
  },
});

app.http("createUser", {
  methods: ["POST"],
  authLevel: "anonymous",
  route: "users",
  handler: async (request, context) => {
    const body = (await request.json()) as CreateUserRequest;
    const user = await createUser(body);
    return { status: 201, jsonBody: user };
  },
});
```

## Timer Trigger

```typescript
app.timer("dailyCleanup", {
  schedule: "0 0 2 * * *", // 2 AM daily
  handler: async (timer, context) => {
    context.log("Running daily cleanup at:", timer.scheduleStatus?.last);
    await cleanupExpiredSessions();
    await archiveOldRecords();
  },
});
```

## Queue Trigger

```typescript
app.storageQueue("processOrder", {
  queueName: "orders",
  connection: "AzureWebJobsStorage",
  handler: async (message: unknown, context) => {
    const order = message as Order;
    context.log("Processing order:", order.id);
    await fulfillOrder(order);
  },
});

// Service Bus trigger
app.serviceBusQueue("handleEvent", {
  queueName: "events",
  connection: "ServiceBusConnection",
  handler: async (message: unknown, context) => {
    const event = message as AppEvent;
    await processEvent(event);
  },
});
```

## Durable Functions (Orchestration)

```typescript
import * as df from "durable-functions";

// Orchestrator
df.app.orchestration("orderWorkflow", function* (context) {
  const order = context.df.getInput() as Order;

  const validation = yield context.df.callActivity("validateOrder", order);
  if (!validation.isValid) {
    yield context.df.callActivity("notifyFailure", { orderId: order.id, reason: validation.error });
    return { status: "failed", reason: validation.error };
  }

  const payment = yield context.df.callActivity("processPayment", order);
  yield context.df.callActivity("fulfillOrder", { ...order, paymentId: payment.id });
  yield context.df.callActivity("sendConfirmation", order);

  return { status: "completed", paymentId: payment.id };
});

// Activity
df.app.activity("validateOrder", { handler: async (order: Order) => {
  if (!order.items?.length) return { isValid: false, error: "No items" };
  return { isValid: true };
}});

// HTTP starter
app.http("startOrder", {
  route: "orders/start",
  methods: ["POST"],
  extraInputs: [df.input.durableClient()],
  handler: async (request, context) => {
    const client = df.getClient(context);
    const order = await request.json();
    const instanceId = await client.startNew("orderWorkflow", { input: order });
    return client.createCheckStatusResponse(request, instanceId);
  },
});
```

## Cosmos DB Binding

```typescript
app.cosmosDB("onUserChange", {
  databaseName: "mydb",
  containerName: "users",
  connection: "CosmosDBConnection",
  createLeaseContainerIfNotExists: true,
  handler: async (documents: unknown[], context) => {
    for (const doc of documents) {
      context.log("User changed:", (doc as any).id);
      await syncToSearchIndex(doc);
    }
  },
});
```

## Configuration (host.json)

```json
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": { "isEnabled": true, "maxTelemetryItemsPerSecond": 20 }
    }
  },
  "extensions": {
    "queues": {
      "batchSize": 16,
      "maxDequeueCount": 5,
      "visibilityTimeout": "00:05:00"
    }
  }
}
```

## Additional Resources

- Azure Functions: https://learn.microsoft.com/en-us/azure/azure-functions/
- Durable Functions: https://learn.microsoft.com/en-us/azure/azure-functions/durable/
- Bindings: https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings
