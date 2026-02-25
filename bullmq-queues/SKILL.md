---
name: bullmq-queues
description: BullMQ job queues covering queue creation, workers, job scheduling, rate limiting, prioritization, flow dependencies, events, retries, and Redis-backed distributed task processing.
---

# BullMQ Queues

This skill should be used when building job queues and background processing with BullMQ. It covers queues, workers, scheduling, flows, and production patterns.

## When to Use This Skill

Use this skill when you need to:

- Process background jobs with Redis
- Schedule recurring or delayed tasks
- Build job pipelines with dependencies
- Implement rate limiting and prioritization
- Handle retries and dead letter queues

## Basic Queue and Worker

```typescript
import { Queue, Worker } from "bullmq";
import IORedis from "ioredis";

const connection = new IORedis({ host: "localhost", port: 6379, maxRetriesPerRequest: null });

// Create queue
const emailQueue = new Queue("email", { connection });

// Add jobs
await emailQueue.add("welcome", {
  to: "user@example.com",
  subject: "Welcome!",
  template: "welcome",
});

// Add with options
await emailQueue.add(
  "invoice",
  { orderId: "123", to: "user@example.com" },
  {
    attempts: 3,
    backoff: { type: "exponential", delay: 1000 },
    removeOnComplete: { count: 1000 },
    removeOnFail: { count: 5000 },
  },
);

// Worker
const worker = new Worker(
  "email",
  async (job) => {
    console.log(`Processing ${job.name} for ${job.data.to}`);
    await sendEmail(job.data);
    return { sent: true, timestamp: Date.now() };
  },
  { connection, concurrency: 5 },
);

worker.on("completed", (job) => console.log(`Job ${job.id} completed`));
worker.on("failed", (job, err) => console.error(`Job ${job?.id} failed:`, err.message));
```

## Scheduled and Recurring Jobs

```typescript
// Delayed job
await emailQueue.add("reminder", { userId: "123" }, {
  delay: 24 * 60 * 60 * 1000, // 24 hours
});

// Recurring job (cron)
await emailQueue.upsertJobScheduler(
  "daily-report",
  { pattern: "0 9 * * *" }, // Every day at 9 AM
  { name: "generate-report", data: { type: "daily" } },
);

// Repeatable every N milliseconds
await emailQueue.upsertJobScheduler(
  "health-check",
  { every: 30000 }, // Every 30 seconds
  { name: "ping", data: {} },
);
```

## Job Priority and Rate Limiting

```typescript
// Priority (lower = higher priority)
await queue.add("urgent", data, { priority: 1 });
await queue.add("normal", data, { priority: 5 });
await queue.add("low", data, { priority: 10 });

// Rate-limited worker
const rateLimitedWorker = new Worker("api-calls", processor, {
  connection,
  limiter: {
    max: 10,      // Max 10 jobs
    duration: 1000, // per 1 second
  },
});
```

## Flow (Job Dependencies)

```typescript
import { FlowProducer } from "bullmq";

const flowProducer = new FlowProducer({ connection });

// Parent job waits for all children
const flow = await flowProducer.add({
  name: "deploy",
  queueName: "deployment",
  data: { version: "1.0.0" },
  children: [
    {
      name: "build",
      queueName: "build",
      data: { target: "production" },
    },
    {
      name: "test",
      queueName: "testing",
      data: { suite: "integration" },
    },
    {
      name: "lint",
      queueName: "quality",
      data: { strict: true },
    },
  ],
});
// "deploy" job runs only after build, test, and lint complete
```

## Events and Progress

```typescript
import { QueueEvents } from "bullmq";

const queueEvents = new QueueEvents("email", { connection });

queueEvents.on("completed", ({ jobId, returnvalue }) => {
  console.log(`Job ${jobId} completed:`, returnvalue);
});

queueEvents.on("failed", ({ jobId, failedReason }) => {
  console.error(`Job ${jobId} failed:`, failedReason);
});

// Report progress from worker
const worker = new Worker("video", async (job) => {
  for (let i = 0; i <= 100; i += 10) {
    await processChunk(job.data, i);
    await job.updateProgress(i);
  }
}, { connection });

queueEvents.on("progress", ({ jobId, data }) => {
  console.log(`Job ${jobId}: ${data}% complete`);
});
```

## Graceful Shutdown

```typescript
async function shutdown() {
  await worker.close();
  await emailQueue.close();
  await connection.quit();
  process.exit(0);
}

process.on("SIGTERM", shutdown);
process.on("SIGINT", shutdown);
```

## Additional Resources

- BullMQ docs: https://docs.bullmq.io/
- Patterns: https://docs.bullmq.io/patterns
- Bull Board (UI): https://github.com/felixmosh/bull-board
