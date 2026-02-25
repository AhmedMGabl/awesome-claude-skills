---
name: cron-jobs
description: Cron job and task scheduling covering node-cron and cron syntax, BullMQ repeatable jobs, Agenda.js MongoDB scheduler, pg-boss PostgreSQL job queues, distributed locking, retry strategies, dead letter handling, monitoring, and serverless cron with Vercel and AWS.
---

# Cron Jobs & Task Scheduling

This skill should be used when implementing scheduled tasks and background job processing. It covers cron syntax, job queues, distributed scheduling, retries, and monitoring.

## When to Use This Skill

Use this skill when you need to:

- Schedule recurring tasks (cleanup, reports, syncs)
- Process background jobs with retries
- Implement distributed job scheduling
- Set up serverless cron triggers
- Monitor and manage scheduled tasks

## Cron Syntax

```
┌──────── minute (0-59)
│ ┌────── hour (0-23)
│ │ ┌──── day of month (1-31)
│ │ │ ┌── month (1-12)
│ │ │ │ ┌ day of week (0-7, 0 and 7 = Sunday)
│ │ │ │ │
* * * * *

EXAMPLES:
*/5 * * * *     Every 5 minutes
0 * * * *       Every hour
0 0 * * *       Every day at midnight
0 9 * * 1-5     Weekdays at 9am
0 0 1 * *       First day of each month
```

## node-cron

```typescript
import cron from "node-cron";

// Run every day at midnight
cron.schedule("0 0 * * *", async () => {
  console.log("Running daily cleanup...");
  await db.sessions.deleteMany({
    where: { expiresAt: { lt: new Date() } },
  });
});

// Run every 5 minutes
cron.schedule("*/5 * * * *", async () => {
  await syncExternalData();
});

// Validate cron expression
const isValid = cron.validate("0 0 * * *"); // true
```

## BullMQ Repeatable Jobs

```typescript
import { Queue, Worker } from "bullmq";
import { Redis } from "ioredis";

const connection = new Redis(process.env.REDIS_URL);

const schedulerQueue = new Queue("scheduler", { connection });

// Add repeatable jobs
await schedulerQueue.add("daily-report", { type: "summary" }, {
  repeat: { pattern: "0 9 * * *" }, // Every day at 9am
  removeOnComplete: 100,
  removeOnFail: 500,
});

await schedulerQueue.add("sync-users", {}, {
  repeat: { every: 300000 }, // Every 5 minutes
});

// Process jobs
const worker = new Worker("scheduler", async (job) => {
  switch (job.name) {
    case "daily-report":
      await generateDailyReport();
      break;
    case "sync-users":
      await syncUsers();
      break;
  }
}, {
  connection,
  concurrency: 5,
  limiter: { max: 10, duration: 1000 },
});

worker.on("failed", (job, err) => {
  console.error(`Job ${job?.id} failed:`, err.message);
});
```

## pg-boss (PostgreSQL Job Queue)

```typescript
import PgBoss from "pg-boss";

const boss = new PgBoss(process.env.DATABASE_URL);
await boss.start();

// Schedule a recurring job
await boss.schedule("daily-cleanup", "0 0 * * *");

// One-time delayed job
await boss.send("send-email", { to: "user@example.com", subject: "Welcome" }, {
  retryLimit: 3,
  retryDelay: 60,
  expireInMinutes: 30,
});

// Process jobs
await boss.work("daily-cleanup", async (job) => {
  await cleanupExpiredRecords();
});

await boss.work("send-email", { teamConcurrency: 5 }, async (job) => {
  await sendEmail(job.data);
});
```

## Distributed Locking

```typescript
// Prevent duplicate execution across instances
async function withDistributedLock(
  redis: Redis,
  lockKey: string,
  ttlMs: number,
  fn: () => Promise<void>,
) {
  const lockValue = crypto.randomUUID();
  const acquired = await redis.set(
    `lock:${lockKey}`,
    lockValue,
    "PX",
    ttlMs,
    "NX",
  );

  if (!acquired) {
    console.log(`Lock ${lockKey} already held, skipping`);
    return;
  }

  try {
    await fn();
  } finally {
    // Only release if we still hold the lock
    const current = await redis.get(`lock:${lockKey}`);
    if (current === lockValue) {
      await redis.del(`lock:${lockKey}`);
    }
  }
}
```

## Serverless Cron (Vercel)

```typescript
// app/api/cron/cleanup/route.ts
import { NextResponse } from "next/server";

export async function GET(request: Request) {
  const authHeader = request.headers.get("authorization");
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  await cleanupExpiredSessions();
  return NextResponse.json({ success: true });
}
```

```json
// vercel.json
{ "crons": [{ "path": "/api/cron/cleanup", "schedule": "0 0 * * *" }] }
```

## Additional Resources

- node-cron: https://github.com/node-cron/node-cron
- BullMQ: https://docs.bullmq.io/
- pg-boss: https://github.com/timgit/pg-boss
