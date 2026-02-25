---
name: inngest-functions
description: Inngest serverless function patterns covering event-driven workflows, step functions, fan-out, scheduled cron jobs, retries, concurrency control, throttling, and integration with Next.js and other frameworks.
---

# Inngest Functions

This skill should be used when building event-driven serverless workflows with Inngest. It covers step functions, scheduling, retries, concurrency, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Build reliable event-driven workflows
- Chain async steps with automatic retries
- Schedule cron jobs and delayed functions
- Control concurrency and throttling
- Integrate with Next.js, Remix, or Express

## Setup

```bash
npm install inngest
```

```typescript
// inngest/client.ts
import { Inngest } from "inngest";

export const inngest = new Inngest({ id: "my-app" });
```

## Basic Function

```typescript
import { inngest } from "./client";

export const helloWorld = inngest.createFunction(
  { id: "hello-world" },
  { event: "app/hello" },
  async ({ event, step }) => {
    const greeting = `Hello, ${event.data.name}!`;
    return { message: greeting };
  }
);

// Send event
await inngest.send({
  name: "app/hello",
  data: { name: "Alice" },
});
```

## Step Functions

```typescript
export const processOrder = inngest.createFunction(
  { id: "process-order" },
  { event: "order/created" },
  async ({ event, step }) => {
    // Each step is retried independently
    const payment = await step.run("charge-payment", async () => {
      return await stripe.paymentIntents.create({
        amount: event.data.amount,
        currency: "usd",
        customer: event.data.customerId,
      });
    });

    // Wait for external event
    const confirmation = await step.waitForEvent("wait-for-confirmation", {
      event: "order/confirmed",
      match: "data.orderId",
      timeout: "24h",
    });

    if (!confirmation) {
      await step.run("cancel-payment", async () => {
        await stripe.refunds.create({ payment_intent: payment.id });
      });
      return { status: "cancelled" };
    }

    await step.run("fulfill-order", async () => {
      await fulfillmentService.process(event.data.orderId);
    });

    await step.run("send-confirmation-email", async () => {
      await sendEmail({
        to: event.data.email,
        subject: "Order Confirmed",
        template: "order-confirmation",
        data: { orderId: event.data.orderId },
      });
    });

    return { status: "completed", paymentId: payment.id };
  }
);
```

## Scheduling and Delays

```typescript
// Cron function
export const dailyReport = inngest.createFunction(
  { id: "daily-report" },
  { cron: "0 9 * * *" }, // Every day at 9 AM
  async ({ step }) => {
    const report = await step.run("generate-report", async () => {
      return await generateDailyReport();
    });

    await step.run("send-report", async () => {
      await sendEmail({ to: "team@example.com", report });
    });
  }
);

// Sleep/delay
export const welcomeSequence = inngest.createFunction(
  { id: "welcome-sequence" },
  { event: "user/signup" },
  async ({ event, step }) => {
    await step.run("send-welcome", async () => {
      await sendEmail({ to: event.data.email, template: "welcome" });
    });

    await step.sleep("wait-1-day", "1d");

    await step.run("send-tips", async () => {
      await sendEmail({ to: event.data.email, template: "tips" });
    });

    await step.sleep("wait-3-days", "3d");

    await step.run("send-offer", async () => {
      await sendEmail({ to: event.data.email, template: "upgrade-offer" });
    });
  }
);
```

## Concurrency and Throttling

```typescript
export const processWebhook = inngest.createFunction(
  {
    id: "process-webhook",
    concurrency: {
      limit: 10,
      key: "event.data.accountId",
    },
    throttle: {
      limit: 100,
      period: "1m",
    },
    retries: 3,
  },
  { event: "webhook/received" },
  async ({ event, step }) => {
    await step.run("process", async () => {
      return processWebhookData(event.data);
    });
  }
);
```

## Fan-out Pattern

```typescript
export const batchProcess = inngest.createFunction(
  { id: "batch-process" },
  { event: "batch/start" },
  async ({ event, step }) => {
    const items = await step.run("fetch-items", async () => {
      return await db.items.findMany({ where: { status: "pending" } });
    });

    // Fan out: send event for each item
    await step.sendEvent("fan-out",
      items.map((item) => ({
        name: "batch/process-item",
        data: { itemId: item.id },
      }))
    );

    return { dispatched: items.length };
  }
);

export const processItem = inngest.createFunction(
  { id: "process-item", concurrency: { limit: 5 } },
  { event: "batch/process-item" },
  async ({ event, step }) => {
    await step.run("process", async () => {
      return processSingleItem(event.data.itemId);
    });
  }
);
```

## Next.js Integration

```typescript
// app/api/inngest/route.ts
import { serve } from "inngest/next";
import { inngest } from "@/inngest/client";
import { processOrder, dailyReport, welcomeSequence } from "@/inngest/functions";

export const { GET, POST, PUT } = serve({
  client: inngest,
  functions: [processOrder, dailyReport, welcomeSequence],
});
```

## Additional Resources

- Inngest: https://www.inngest.com/
- Step functions: https://www.inngest.com/docs/features/inngest-functions/steps-workflows
- Concurrency: https://www.inngest.com/docs/guides/concurrency
