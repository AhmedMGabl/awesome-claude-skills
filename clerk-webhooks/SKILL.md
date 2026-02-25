---
name: clerk-webhooks
description: Clerk webhook integration covering user lifecycle events, organization events, session events, Svix signature verification, Next.js API route handling, and event-driven user sync patterns.
---

# Clerk Webhooks

This skill should be used when handling Clerk authentication webhooks. It covers event types, signature verification, user sync, and integration patterns.

## When to Use This Skill

Use this skill when you need to:

- Sync Clerk users to a database on creation/update
- Handle organization membership changes
- Process session and authentication events
- Verify webhook signatures with Svix
- Build event-driven auth workflows

## Next.js Webhook Handler

```typescript
// app/api/webhooks/clerk/route.ts
import { Webhook } from "svix";
import { headers } from "next/headers";
import type { WebhookEvent } from "@clerk/nextjs/server";

export async function POST(req: Request) {
  const WEBHOOK_SECRET = process.env.CLERK_WEBHOOK_SECRET;
  if (!WEBHOOK_SECRET) throw new Error("Missing CLERK_WEBHOOK_SECRET");

  // Get Svix headers
  const headerPayload = await headers();
  const svixId = headerPayload.get("svix-id");
  const svixTimestamp = headerPayload.get("svix-timestamp");
  const svixSignature = headerPayload.get("svix-signature");

  if (!svixId || !svixTimestamp || !svixSignature) {
    return new Response("Missing svix headers", { status: 400 });
  }

  // Verify signature
  const payload = await req.json();
  const body = JSON.stringify(payload);
  const wh = new Webhook(WEBHOOK_SECRET);

  let event: WebhookEvent;
  try {
    event = wh.verify(body, {
      "svix-id": svixId,
      "svix-timestamp": svixTimestamp,
      "svix-signature": svixSignature,
    }) as WebhookEvent;
  } catch {
    return new Response("Invalid signature", { status: 400 });
  }

  // Handle events
  switch (event.type) {
    case "user.created":
      await handleUserCreated(event.data);
      break;
    case "user.updated":
      await handleUserUpdated(event.data);
      break;
    case "user.deleted":
      await handleUserDeleted(event.data);
      break;
    case "organization.created":
      await handleOrgCreated(event.data);
      break;
    case "organizationMembership.created":
      await handleMemberAdded(event.data);
      break;
    case "session.created":
      await handleSessionCreated(event.data);
      break;
  }

  return new Response("OK", { status: 200 });
}
```

## User Sync Handlers

```typescript
import { db } from "@/lib/db";

async function handleUserCreated(data: any) {
  const { id, email_addresses, first_name, last_name, image_url } = data;

  const primaryEmail = email_addresses.find(
    (e: any) => e.id === data.primary_email_address_id,
  )?.email_address;

  await db.user.create({
    data: {
      clerkId: id,
      email: primaryEmail,
      name: [first_name, last_name].filter(Boolean).join(" ") || null,
      avatar: image_url,
    },
  });
}

async function handleUserUpdated(data: any) {
  const { id, email_addresses, first_name, last_name, image_url } = data;

  const primaryEmail = email_addresses.find(
    (e: any) => e.id === data.primary_email_address_id,
  )?.email_address;

  await db.user.update({
    where: { clerkId: id },
    data: {
      email: primaryEmail,
      name: [first_name, last_name].filter(Boolean).join(" ") || null,
      avatar: image_url,
    },
  });
}

async function handleUserDeleted(data: any) {
  await db.user.delete({ where: { clerkId: data.id } });
}
```

## Organization Events

```typescript
async function handleOrgCreated(data: any) {
  await db.organization.create({
    data: {
      clerkOrgId: data.id,
      name: data.name,
      slug: data.slug,
      imageUrl: data.image_url,
    },
  });
}

async function handleMemberAdded(data: any) {
  const { organization, public_user_data, role } = data;

  await db.orgMember.create({
    data: {
      orgId: organization.id,
      userId: public_user_data.user_id,
      role: role,
    },
  });
}
```

## Express Handler

```typescript
import express from "express";
import { Webhook } from "svix";

const app = express();

app.post(
  "/api/webhooks/clerk",
  express.raw({ type: "application/json" }),
  async (req, res) => {
    const wh = new Webhook(process.env.CLERK_WEBHOOK_SECRET!);

    try {
      const event = wh.verify(req.body, {
        "svix-id": req.headers["svix-id"] as string,
        "svix-timestamp": req.headers["svix-timestamp"] as string,
        "svix-signature": req.headers["svix-signature"] as string,
      }) as WebhookEvent;

      await processEvent(event);
      res.status(200).json({ received: true });
    } catch {
      res.status(400).json({ error: "Invalid webhook" });
    }
  },
);
```

## Additional Resources

- Clerk webhooks: https://clerk.com/docs/webhooks/overview
- Event types: https://clerk.com/docs/webhooks/sync-data
- Svix verification: https://docs.svix.com/receiving/verifying-payloads
