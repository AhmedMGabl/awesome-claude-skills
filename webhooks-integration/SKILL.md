---
name: webhooks-integration
description: Webhook implementation patterns covering signature verification (HMAC-SHA256), idempotent processing, retry handling with exponential backoff, webhook delivery systems, Stripe/GitHub/Slack webhook patterns, dead letter queues, event logging, and webhook testing strategies.
---

# Webhooks Integration

This skill should be used when implementing webhook receivers or senders. It covers signature verification, idempotent processing, retry logic, and common provider patterns.

## When to Use This Skill

Use this skill when you need to:

- Receive webhooks from third-party services
- Verify webhook signatures securely
- Process webhooks idempotently
- Build a webhook delivery system
- Handle webhook retries and failures

## Webhook Receiver

```typescript
import crypto from "crypto";
import { Request, Response } from "express";

// Verify HMAC-SHA256 signature
function verifySignature(payload: string, signature: string, secret: string): boolean {
  const expected = crypto.createHmac("sha256", secret).update(payload).digest("hex");
  const sig = signature.replace("sha256=", "");
  return crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(expected));
}

// Generic webhook endpoint
app.post("/api/webhooks/:provider", express.raw({ type: "application/json" }), async (req: Request, res: Response) => {
  const provider = req.params.provider;
  const body = req.body.toString();
  const signature = req.headers["x-signature-256"] as string ?? req.headers["x-hub-signature-256"] as string ?? "";

  // Verify signature
  const secret = getWebhookSecret(provider);
  if (!verifySignature(body, signature, secret)) {
    return res.status(401).json({ error: "Invalid signature" });
  }

  // Idempotency check
  const eventId = req.headers["x-webhook-id"] as string ?? req.headers["x-request-id"] as string;
  if (eventId) {
    const processed = await redis.get(`webhook:${eventId}`);
    if (processed) return res.status(200).json({ status: "already processed" });
  }

  // Respond immediately, process async
  res.status(200).json({ received: true });

  try {
    const event = JSON.parse(body);
    await processWebhookEvent(provider, event);

    if (eventId) {
      await redis.set(`webhook:${eventId}`, "1", { EX: 86400 });
    }
  } catch (error) {
    console.error(`Webhook processing failed:`, error);
    // Queue for retry
    await webhookQueue.add("retry", { provider, body, eventId });
  }
});
```

## Stripe Webhook Handler

```typescript
import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

app.post("/api/webhooks/stripe", express.raw({ type: "application/json" }), async (req, res) => {
  const sig = req.headers["stripe-signature"] as string;

  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(req.body, sig, process.env.STRIPE_WEBHOOK_SECRET!);
  } catch (err) {
    return res.status(400).send(`Webhook Error: ${(err as Error).message}`);
  }

  // Respond immediately
  res.status(200).json({ received: true });

  switch (event.type) {
    case "checkout.session.completed": {
      const session = event.data.object as Stripe.Checkout.Session;
      await fulfillOrder(session);
      break;
    }
    case "customer.subscription.updated": {
      const subscription = event.data.object as Stripe.Subscription;
      await updateSubscription(subscription);
      break;
    }
    case "invoice.payment_failed": {
      const invoice = event.data.object as Stripe.Invoice;
      await handleFailedPayment(invoice);
      break;
    }
  }
});
```

## Webhook Sender (Delivery System)

```typescript
import { Queue, Worker } from "bullmq";

const deliveryQueue = new Queue("webhook-delivery", { connection: { url: process.env.REDIS_URL } });

// Register a webhook endpoint
interface WebhookEndpoint {
  id: string;
  url: string;
  secret: string;
  events: string[];
  active: boolean;
}

// Dispatch an event to all subscribers
async function dispatchEvent(eventType: string, payload: unknown) {
  const endpoints = await db.webhookEndpoint.findMany({
    where: { active: true, events: { has: eventType } },
  });

  for (const endpoint of endpoints) {
    await deliveryQueue.add("deliver", {
      endpointId: endpoint.id,
      url: endpoint.url,
      secret: endpoint.secret,
      eventType,
      payload,
      eventId: crypto.randomUUID(),
    }, {
      attempts: 5,
      backoff: { type: "exponential", delay: 60_000 },
    });
  }
}

// Delivery worker
const worker = new Worker("webhook-delivery", async (job) => {
  const { url, secret, eventType, payload, eventId } = job.data;
  const body = JSON.stringify({ event: eventType, data: payload, timestamp: new Date().toISOString() });
  const signature = crypto.createHmac("sha256", secret).update(body).digest("hex");

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Webhook-Id": eventId,
      "X-Webhook-Signature": `sha256=${signature}`,
      "X-Webhook-Timestamp": Date.now().toString(),
    },
    body,
    signal: AbortSignal.timeout(30_000),
  });

  if (!response.ok) {
    throw new Error(`Delivery failed: HTTP ${response.status}`);
  }

  // Log successful delivery
  await db.webhookDelivery.create({
    data: { endpointId: job.data.endpointId, eventId, status: "delivered", statusCode: response.status },
  });
}, { connection: { url: process.env.REDIS_URL } });
```

## Additional Resources

- Webhook.site (testing): https://webhook.site/
- ngrok (local testing): https://ngrok.com/
- Svix (webhook infrastructure): https://www.svix.com/
- Standard Webhooks: https://www.standardwebhooks.com/
