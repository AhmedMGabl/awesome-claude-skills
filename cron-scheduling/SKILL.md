---
name: cron-scheduling
description: Job scheduling and cron patterns covering cron expression syntax, Node.js schedulers (node-cron, BullMQ), Python schedulers (APScheduler, Celery Beat), distributed job queues, idempotent jobs, retry strategies, monitoring, and production scheduling best practices.
---

# Cron & Job Scheduling

This skill should be used when implementing scheduled tasks, background jobs, or distributed job queues. It covers cron syntax, scheduling libraries, and production patterns.

## When to Use This Skill

Use this skill when you need to:

- Schedule recurring tasks (cleanup, reports, sync)
- Build background job queues
- Implement distributed task processing
- Set up cron expressions
- Monitor and manage scheduled jobs

## Cron Expression Syntax

```
┌───────── minute (0-59)
│ ┌─────── hour (0-23)
│ │ ┌───── day of month (1-31)
│ │ │ ┌─── month (1-12)
│ │ │ │ ┌─ day of week (0-7, 0 and 7 = Sunday)
│ │ │ │ │
* * * * *

EXAMPLES:
  */5 * * * *       Every 5 minutes
  0 * * * *         Every hour (at minute 0)
  0 0 * * *         Daily at midnight
  0 9 * * 1-5       Weekdays at 9am
  0 0 1 * *         First day of every month
  0 0 * * 0         Every Sunday at midnight
  30 2 * * *        Daily at 2:30am
  0 */6 * * *       Every 6 hours
  0 9,17 * * *      At 9am and 5pm
  0 0 1,15 * *      1st and 15th of each month

SPECIAL CHARACTERS:
  *     Any value
  ,     List separator (1,3,5)
  -     Range (1-5)
  /     Step (*/5 = every 5)
  L     Last (last day of month)
  W     Weekday nearest to given day
  #     Nth weekday (2#3 = third Tuesday)
```

## Node.js with BullMQ (Production)

```typescript
import { Queue, Worker } from "bullmq";
import IORedis from "ioredis";

const connection = new IORedis(process.env.REDIS_URL!);

// Define queue
const emailQueue = new Queue("email", {
  connection,
  defaultJobOptions: {
    attempts: 3,
    backoff: { type: "exponential", delay: 1000 },
    removeOnComplete: { age: 86400, count: 1000 },
    removeOnFail: { age: 604800 },
  },
});

// Add job
await emailQueue.add("welcome", { userId: "123", email: "user@example.com" });

// Add scheduled/recurring job
await emailQueue.add("daily-digest", {}, {
  repeat: { pattern: "0 9 * * *" }, // Daily at 9am
  jobId: "daily-digest",            // Prevent duplicates
});

// Process jobs
const worker = new Worker("email", async (job) => {
  switch (job.name) {
    case "welcome":
      await sendWelcomeEmail(job.data);
      break;
    case "daily-digest":
      await sendDailyDigest();
      break;
  }
}, {
  connection,
  concurrency: 5,
  limiter: { max: 10, duration: 1000 }, // Rate limit: 10/sec
});

worker.on("completed", (job) => console.log(`Job ${job.id} completed`));
worker.on("failed", (job, err) => console.error(`Job ${job?.id} failed:`, err));
```

## Python with Celery

```python
# celery_app.py
from celery import Celery
from celery.schedules import crontab

app = Celery("tasks", broker=os.environ["REDIS_URL"])

app.conf.beat_schedule = {
    "daily-cleanup": {
        "task": "tasks.cleanup_expired_sessions",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2am
    },
    "hourly-sync": {
        "task": "tasks.sync_external_data",
        "schedule": crontab(minute=0),  # Every hour
    },
    "weekly-report": {
        "task": "tasks.generate_weekly_report",
        "schedule": crontab(hour=9, minute=0, day_of_week=1),  # Monday 9am
    },
}

@app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_notification(self, user_id: str, message: str):
    try:
        # Process task
        notify_user(user_id, message)
    except ConnectionError as e:
        self.retry(exc=e)
```

## Idempotent Job Pattern

```typescript
// Jobs should be safe to run multiple times
async function processPayment(job: Job) {
  const { paymentId } = job.data;

  // Check if already processed (idempotency key)
  const existing = await db.payment.findUnique({ where: { id: paymentId } });
  if (existing?.status === "completed") {
    return { skipped: true, reason: "Already processed" };
  }

  // Process with lock to prevent concurrent execution
  const lock = await acquireLock(`payment:${paymentId}`, 30000);
  if (!lock) throw new Error("Could not acquire lock");

  try {
    await db.$transaction(async (tx) => {
      await tx.payment.update({
        where: { id: paymentId },
        data: { status: "processing" },
      });
      await chargeCustomer(paymentId);
      await tx.payment.update({
        where: { id: paymentId },
        data: { status: "completed", completedAt: new Date() },
      });
    });
  } finally {
    await releaseLock(lock);
  }
}
```

## Job Monitoring

```typescript
// BullMQ dashboard with Bull Board
import { createBullBoard } from "@bull-board/api";
import { BullMQAdapter } from "@bull-board/api/bullMQAdapter";
import { ExpressAdapter } from "@bull-board/express";

const serverAdapter = new ExpressAdapter();
createBullBoard({
  queues: [
    new BullMQAdapter(emailQueue),
    new BullMQAdapter(paymentQueue),
  ],
  serverAdapter,
});

app.use("/admin/queues", serverAdapter.getRouter());
```

## Additional Resources

- BullMQ: https://docs.bullmq.io/
- Celery: https://docs.celeryq.dev/
- Crontab Guru: https://crontab.guru/
- node-cron: https://github.com/kelektiv/node-cron
