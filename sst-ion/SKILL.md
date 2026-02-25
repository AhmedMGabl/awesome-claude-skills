---
name: sst-ion
description: SST Ion patterns covering infrastructure as code with TypeScript, linking resources, Next.js/Astro/Remix deployment, API routes, queues, cron jobs, buckets, and AWS/Cloudflare deployment.
---

# SST Ion

This skill should be used when deploying full-stack applications with SST Ion. It covers infrastructure as TypeScript, resource linking, framework deployment, and cloud resource management.

## When to Use This Skill

Use this skill when you need to:

- Deploy full-stack apps to AWS or Cloudflare
- Define infrastructure as TypeScript code
- Link cloud resources to application code
- Deploy Next.js, Astro, or Remix applications
- Set up queues, crons, buckets, and databases

## Infrastructure Definition

```typescript
// sst.config.ts
/// <reference path="./.sst/platform/config.d.ts" />

export default $config({
  app(input) {
    return {
      name: "my-app",
      removal: input?.stage === "production" ? "retain" : "remove",
      home: "aws",
    };
  },
  async run() {
    // Database
    const database = new sst.aws.Postgres("Database", {
      scaling: { min: "0.5 ACU", max: "4 ACU" },
    });

    // Storage
    const bucket = new sst.aws.Bucket("Uploads", {
      access: "public",
    });

    // Queue
    const queue = new sst.aws.Queue("EmailQueue");
    queue.subscribe("src/subscribers/email.handler");

    // Cron job
    new sst.aws.Cron("DailyCleanup", {
      schedule: "rate(1 day)",
      job: "src/jobs/cleanup.handler",
    });

    // API
    const api = new sst.aws.Function("Api", {
      handler: "src/api/index.handler",
      url: true,
      link: [database, bucket, queue],
    });

    // Next.js site
    const site = new sst.aws.Nextjs("Site", {
      link: [database, bucket, api],
      environment: {
        NEXT_PUBLIC_API_URL: api.url,
      },
    });

    return {
      api: api.url,
      site: site.url,
    };
  },
});
```

## Resource Linking

```typescript
// src/api/index.ts
import { Resource } from "sst";

// Access linked resources with full type safety
const dbUrl = Resource.Database.url;
const bucketName = Resource.Uploads.name;

// Use in handlers
export async function handler(event: APIGatewayEvent) {
  const db = createClient(Resource.Database.url);
  const users = await db.query("SELECT * FROM users");

  return {
    statusCode: 200,
    body: JSON.stringify(users),
  };
}
```

## API Routes

```typescript
// src/api/routes.ts
import { Resource } from "sst";
import { Hono } from "hono";

const app = new Hono();

app.get("/users", async (c) => {
  const db = createClient(Resource.Database.url);
  const users = await db.query("SELECT * FROM users LIMIT 50");
  return c.json(users);
});

app.post("/upload", async (c) => {
  const body = await c.req.parseBody();
  const file = body.file as File;

  const command = new PutObjectCommand({
    Bucket: Resource.Uploads.name,
    Key: `uploads/${file.name}`,
    Body: Buffer.from(await file.arrayBuffer()),
  });

  await s3.send(command);
  return c.json({ key: `uploads/${file.name}` });
});

export default app;
```

## Queue Subscribers

```typescript
// src/subscribers/email.ts
import { Resource } from "sst";

export async function handler(event: SQSEvent) {
  for (const record of event.Records) {
    const { to, subject, body } = JSON.parse(record.body);

    await sendEmail({
      from: "noreply@example.com",
      to,
      subject,
      html: body,
    });
  }
}

// Sending to queue from anywhere
import { SQSClient, SendMessageCommand } from "@aws-sdk/client-sqs";

const sqs = new SQSClient({});

await sqs.send(new SendMessageCommand({
  QueueUrl: Resource.EmailQueue.url,
  MessageBody: JSON.stringify({
    to: "user@example.com",
    subject: "Welcome",
    body: "<h1>Welcome!</h1>",
  }),
}));
```

## Framework Deployment

```typescript
// Next.js
const nextApp = new sst.aws.Nextjs("Web", {
  link: [database, bucket],
  domain: "example.com",
});

// Astro
const astroApp = new sst.aws.Astro("Docs", {
  link: [database],
  domain: "docs.example.com",
});

// Remix
const remixApp = new sst.aws.Remix("App", {
  link: [database, bucket],
});

// Static site
const staticSite = new sst.aws.StaticSite("Landing", {
  build: {
    command: "npm run build",
    output: "dist",
  },
  domain: "landing.example.com",
});
```

## CLI Commands

```bash
# Start dev mode
npx sst dev

# Deploy to stage
npx sst deploy --stage production

# Remove stage
npx sst remove --stage staging

# Open SST console
npx sst console
```

## Additional Resources

- SST: https://sst.dev/
- SST components: https://sst.dev/docs/components
- SST examples: https://sst.dev/examples
