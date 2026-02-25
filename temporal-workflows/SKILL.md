---
name: temporal-workflows
description: Temporal workflow patterns covering workflow definitions, activities, signals, queries, timers, child workflows, retry policies, saga compensation, and TypeScript/Go SDK integration for durable execution.
---

# Temporal Workflows

This skill should be used when building durable, fault-tolerant workflows with Temporal. It covers workflow definitions, activities, signals, timers, sagas, and SDK integration.

## When to Use This Skill

Use this skill when you need to:

- Build long-running, fault-tolerant workflows
- Orchestrate microservice interactions
- Handle retries and compensation logic
- Schedule timers and cron workflows
- Implement saga patterns for distributed transactions

## Workflow Definition

```typescript
import { proxyActivities, sleep, defineSignal, setHandler, condition } from "@temporalio/workflow";
import type * as activities from "./activities";

const { sendEmail, chargePayment, fulfillOrder, refundPayment } = proxyActivities<typeof activities>({
  startToCloseTimeout: "30s",
  retry: {
    maximumAttempts: 3,
    initialInterval: "1s",
    backoffCoefficient: 2,
  },
});

export async function orderWorkflow(order: Order): Promise<OrderResult> {
  // Step 1: Process payment
  const paymentResult = await chargePayment({
    amount: order.total,
    customerId: order.customerId,
  });

  // Step 2: Fulfill order
  try {
    const fulfillment = await fulfillOrder({
      orderId: order.id,
      items: order.items,
    });

    // Step 3: Send confirmation
    await sendEmail({
      to: order.email,
      subject: "Order Confirmed",
      body: `Your order ${order.id} has been placed.`,
    });

    return { status: "completed", paymentId: paymentResult.id, trackingNumber: fulfillment.tracking };
  } catch (err) {
    // Compensate: refund payment
    await refundPayment({ paymentId: paymentResult.id });
    throw err;
  }
}
```

## Activities

```typescript
// activities.ts
import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_KEY!);

export async function chargePayment(input: { amount: number; customerId: string }) {
  const charge = await stripe.paymentIntents.create({
    amount: input.amount,
    currency: "usd",
    customer: input.customerId,
    confirm: true,
  });
  return { id: charge.id, status: charge.status };
}

export async function fulfillOrder(input: { orderId: string; items: Item[] }) {
  const response = await fetch("https://warehouse.api/fulfill", {
    method: "POST",
    body: JSON.stringify(input),
  });
  if (!response.ok) throw new Error("Fulfillment failed");
  return response.json();
}

export async function sendEmail(input: { to: string; subject: string; body: string }) {
  await emailClient.send(input);
}

export async function refundPayment(input: { paymentId: string }) {
  await stripe.refunds.create({ payment_intent: input.paymentId });
}
```

## Signals and Queries

```typescript
import { defineSignal, defineQuery, setHandler, condition } from "@temporalio/workflow";

// Define signals and queries
const approveSignal = defineSignal<[{ approvedBy: string }]>("approve");
const rejectSignal = defineSignal<[{ reason: string }]>("reject");
const statusQuery = defineQuery<string>("status");

export async function approvalWorkflow(request: ApprovalRequest): Promise<ApprovalResult> {
  let status = "pending";
  let approval: { approvedBy: string } | undefined;
  let rejection: { reason: string } | undefined;

  // Handle signals
  setHandler(approveSignal, (data) => {
    approval = data;
    status = "approved";
  });

  setHandler(rejectSignal, (data) => {
    rejection = data;
    status = "rejected";
  });

  // Handle queries
  setHandler(statusQuery, () => status);

  // Send notification and wait
  await sendNotification({ to: request.approver, request });

  // Wait for signal or timeout
  const gotResponse = await condition(() => status !== "pending", "24h");

  if (!gotResponse) {
    status = "expired";
    return { status: "expired" };
  }

  if (status === "approved") {
    await processApproval(request);
    return { status: "approved", approvedBy: approval!.approvedBy };
  }

  return { status: "rejected", reason: rejection!.reason };
}
```

## Child Workflows

```typescript
import { executeChild, startChild } from "@temporalio/workflow";

export async function parentWorkflow(orders: Order[]): Promise<BatchResult> {
  // Execute child workflows in parallel
  const results = await Promise.all(
    orders.map((order) =>
      executeChild(orderWorkflow, {
        workflowId: `order-${order.id}`,
        args: [order],
      })
    )
  );

  // Or start child and get handle
  const handle = await startChild(longRunningWorkflow, {
    workflowId: "long-task-1",
    args: [data],
  });

  // Signal the child
  await handle.signal(approveSignal, { approvedBy: "system" });

  return { processed: results.length };
}
```

## Timers and Cron

```typescript
import { sleep } from "@temporalio/workflow";

export async function reminderWorkflow(userId: string): Promise<void> {
  // Wait for 24 hours
  await sleep("24h");

  await sendReminder({ userId, message: "Don't forget to complete your profile!" });

  // Wait another week
  await sleep("7d");

  await sendReminder({ userId, message: "Last reminder: complete your profile." });
}

// Cron workflow - started with cronSchedule option
export async function dailyReportWorkflow(): Promise<void> {
  const report = await generateDailyReport();
  await sendReport({ report, recipients: ["team@example.com"] });
}
```

## Worker Setup

```typescript
// worker.ts
import { Worker } from "@temporalio/worker";
import * as activities from "./activities";

async function run() {
  const worker = await Worker.create({
    workflowsPath: require.resolve("./workflows"),
    activities,
    taskQueue: "main-queue",
    maxConcurrentActivityTaskExecutions: 10,
    maxConcurrentWorkflowTaskExecutions: 5,
  });

  await worker.run();
}

run().catch(console.error);
```

## Client Usage

```typescript
// client.ts
import { Client } from "@temporalio/client";

const client = new Client();

// Start a workflow
const handle = await client.workflow.start(orderWorkflow, {
  workflowId: `order-${orderId}`,
  taskQueue: "main-queue",
  args: [order],
});

// Get result
const result = await handle.result();

// Query workflow state
const status = await handle.query(statusQuery);

// Signal workflow
await handle.signal(approveSignal, { approvedBy: "admin" });
```

## Additional Resources

- Temporal: https://temporal.io/
- TypeScript SDK: https://docs.temporal.io/develop/typescript
- Temporal concepts: https://docs.temporal.io/concepts
