---
name: trigger-dev
description: Trigger.dev background jobs covering task definition, scheduling, event triggers, concurrency control, retries, idempotency, webhook handling, AI/LLM integration, and deployment patterns.
---

# Trigger.dev

This skill should be used when implementing background jobs with Trigger.dev. It covers task definition, scheduling, event triggers, concurrency, and deployment.

## When to Use This Skill

Use this skill when you need to:

- Run long-running background tasks
- Schedule recurring jobs (cron)
- Process webhooks reliably
- Build AI/LLM pipelines with retries
- Handle event-driven workflows

## Setup

```bash
npx trigger.dev@latest init
```

```typescript
// trigger.config.ts
import { defineConfig } from "@trigger.dev/sdk/v3";

export default defineConfig({
  project: "proj_xxx",
  runtime: "node",
  logLevel: "log",
  retries: {
    enabledInDev: true,
    default: { maxAttempts: 3, factor: 2, minTimeoutInMs: 1000, maxTimeoutInMs: 10000 },
  },
});
```

## Define Tasks

```typescript
// src/trigger/tasks.ts
import { task, logger } from "@trigger.dev/sdk/v3";

export const processOrder = task({
  id: "process-order",
  retry: { maxAttempts: 5 },
  run: async (payload: { orderId: string; userId: string }) => {
    logger.info("Processing order", { orderId: payload.orderId });

    const order = await db.orders.findById(payload.orderId);
    if (!order) throw new Error(`Order ${payload.orderId} not found`);

    await chargePayment(order);
    await sendConfirmationEmail(order);
    await updateInventory(order.items);

    logger.info("Order processed", { orderId: payload.orderId });
    return { success: true, orderId: payload.orderId };
  },
});
```

## Trigger Tasks

```typescript
// From your API route
import { processOrder } from "@/trigger/tasks";

// Trigger and forget
await processOrder.trigger({ orderId: "order_123", userId: "user_abc" });

// Trigger and wait for result
const handle = await processOrder.triggerAndWait({ orderId: "order_123", userId: "user_abc" });
if (handle.ok) {
  console.log("Result:", handle.output);
}

// Batch trigger
await processOrder.batchTrigger([
  { payload: { orderId: "order_1", userId: "user_a" } },
  { payload: { orderId: "order_2", userId: "user_b" } },
]);
```

## Scheduled Tasks (Cron)

```typescript
import { schedules } from "@trigger.dev/sdk/v3";

export const dailyReport = schedules.task({
  id: "daily-report",
  cron: "0 9 * * *", // 9am UTC daily
  run: async () => {
    const stats = await generateDailyStats();
    await sendSlackReport(stats);
    return stats;
  },
});
```

## Concurrency Control

```typescript
export const syncUser = task({
  id: "sync-user",
  queue: { concurrencyLimit: 5 },
  run: async (payload: { userId: string }) => {
    // Only 5 sync-user tasks run at a time
    await syncUserToExternalSystem(payload.userId);
  },
});
```

## Sub-Tasks (Fan-out)

```typescript
import { task } from "@trigger.dev/sdk/v3";

export const processCSV = task({
  id: "process-csv",
  run: async (payload: { fileUrl: string }) => {
    const rows = await parseCSV(payload.fileUrl);

    // Fan out to sub-tasks
    const results = await processRow.batchTriggerAndWait(
      rows.map((row) => ({ payload: { row } })),
    );

    const succeeded = results.runs.filter((r) => r.ok).length;
    return { total: rows.length, succeeded };
  },
});

export const processRow = task({
  id: "process-row",
  run: async (payload: { row: Record<string, string> }) => {
    await importRow(payload.row);
    return { imported: true };
  },
});
```

## AI/LLM Integration

```typescript
import { task } from "@trigger.dev/sdk/v3";
import Anthropic from "@anthropic-ai/sdk";

export const generateSummary = task({
  id: "generate-summary",
  retry: { maxAttempts: 3 },
  run: async (payload: { documentId: string }) => {
    const doc = await db.documents.findById(payload.documentId);
    const anthropic = new Anthropic();

    const message = await anthropic.messages.create({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1024,
      messages: [{ role: "user", content: `Summarize: ${doc.content}` }],
    });

    const summary = message.content[0].type === "text" ? message.content[0].text : "";
    await db.documents.update(payload.documentId, { summary });
    return { summary };
  },
});
```

## Additional Resources

- Trigger.dev docs: https://trigger.dev/docs
- Tasks: https://trigger.dev/docs/tasks
- Deployment: https://trigger.dev/docs/deploy
