---
name: inngest
description: Inngest event-driven functions covering event triggers, step functions, scheduled tasks, fan-out patterns, retries, concurrency, idempotency, and integration with Next.js, Express, and Hono.
---

# Inngest

This skill should be used when building event-driven background functions with Inngest. It covers step functions, scheduling, fan-out, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Build reliable background functions triggered by events
- Create multi-step workflows with automatic retries
- Schedule recurring tasks (cron)
- Fan-out work to parallel steps
- Implement durable execution patterns

## Setup

```bash
npm install inngest
```

```typescript
// src/inngest/client.ts
import { Inngest } from "inngest";

export const inngest = new Inngest({ id: "my-app" });
```

## Define Functions

```typescript
// src/inngest/functions.ts
import { inngest } from "./client";

// Simple event-triggered function
export const sendWelcomeEmail = inngest.createFunction(
  { id: "send-welcome-email", retries: 3 },
  { event: "user/signup" },
  async ({ event, step }) => {
    const user = event.data;

    await step.run("send-email", async () => {
      await resend.emails.send({
        to: user.email,
        subject: "Welcome!",
        react: WelcomeEmail({ name: user.name }),
      });
    });

    await step.sleep("wait-3-days", "3d");

    await step.run("send-onboarding", async () => {
      await resend.emails.send({
        to: user.email,
        subject: "Getting Started",
        react: OnboardingEmail({ name: user.name }),
      });
    });
  },
);
```

## Step Functions

```typescript
export const processOrder = inngest.createFunction(
  { id: "process-order", retries: 5 },
  { event: "order/created" },
  async ({ event, step }) => {
    // Each step is independently retried
    const payment = await step.run("charge-payment", async () => {
      return stripe.charges.create({
        amount: event.data.total,
        customer: event.data.customerId,
      });
    });

    const inventory = await step.run("update-inventory", async () => {
      return updateInventory(event.data.items);
    });

    // Wait for external event (e.g., webhook)
    const shipment = await step.waitForEvent("wait-for-shipment", {
      event: "shipment/created",
      match: "data.orderId",
      timeout: "7d",
    });

    if (shipment) {
      await step.run("notify-shipped", async () => {
        await sendShippingNotification(event.data.email, shipment.data.trackingNumber);
      });
    }

    return { payment, inventory, shipment };
  },
);
```

## Scheduled Functions (Cron)

```typescript
export const dailyDigest = inngest.createFunction(
  { id: "daily-digest" },
  { cron: "0 9 * * *" }, // 9am UTC daily
  async ({ step }) => {
    const users = await step.run("get-active-users", async () => {
      return db.users.findMany({ where: { subscribed: true } });
    });

    await step.run("send-digests", async () => {
      for (const user of users) {
        const digest = await generateDigest(user.id);
        await sendDigestEmail(user.email, digest);
      }
    });
  },
);
```

## Fan-Out Pattern

```typescript
export const processCSVUpload = inngest.createFunction(
  { id: "process-csv" },
  { event: "csv/uploaded" },
  async ({ event, step }) => {
    const rows = await step.run("parse-csv", async () => {
      return parseCSV(event.data.fileUrl);
    });

    // Fan out: send events for each row
    await step.sendEvent("fan-out-rows",
      rows.map((row, i) => ({
        name: "csv/row-process",
        data: { row, index: i, uploadId: event.data.uploadId },
      })),
    );
  },
);
```

## Concurrency Control

```typescript
export const syncToExternalAPI = inngest.createFunction(
  {
    id: "sync-external",
    concurrency: { limit: 5 }, // Max 5 running at once
    throttle: { limit: 100, period: "1m" }, // Rate limit
  },
  { event: "data/sync-requested" },
  async ({ event, step }) => {
    await step.run("sync", async () => {
      await externalApi.sync(event.data);
    });
  },
);
```

## Serve (Next.js)

```typescript
// app/api/inngest/route.ts
import { serve } from "inngest/next";
import { inngest } from "@/inngest/client";
import { sendWelcomeEmail, processOrder, dailyDigest } from "@/inngest/functions";

export const { GET, POST, PUT } = serve({
  client: inngest,
  functions: [sendWelcomeEmail, processOrder, dailyDigest],
});
```

## Send Events

```typescript
// From your API routes or server actions
await inngest.send({
  name: "user/signup",
  data: { id: user.id, email: user.email, name: user.name },
});

// Batch events
await inngest.send([
  { name: "order/created", data: { orderId: "1", total: 9999 } },
  { name: "order/created", data: { orderId: "2", total: 4999 } },
]);
```

## Additional Resources

- Inngest docs: https://www.inngest.com/docs
- Step functions: https://www.inngest.com/docs/features/inngest-functions/steps-workflows
- Concurrency: https://www.inngest.com/docs/guides/concurrency
