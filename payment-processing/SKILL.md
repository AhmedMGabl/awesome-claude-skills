---
name: payment-processing
description: Payment processing patterns covering Stripe Checkout, PayPal, subscription billing, metered usage billing, invoice generation, refund handling, PCI compliance, idempotent payment operations, and multi-currency support.
---

# Payment Processing

This skill should be used when implementing payment flows in web applications. It covers Stripe, PayPal, subscriptions, invoicing, refunds, and compliance patterns.

## When to Use This Skill

Use this skill when you need to:

- Implement checkout flows with Stripe
- Handle subscription billing and upgrades
- Process refunds and disputes
- Implement metered/usage-based billing
- Ensure PCI compliance

## Stripe Checkout (One-Time Payment)

```typescript
// pages/api/checkout.ts
import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

export async function POST(req: Request) {
  const { priceId, quantity = 1 } = await req.json();

  const session = await stripe.checkout.sessions.create({
    mode: "payment",
    line_items: [{ price: priceId, quantity }],
    success_url: `${process.env.APP_URL}/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.APP_URL}/cart`,
    payment_intent_data: {
      metadata: { orderId: "order_123" },
    },
  });

  return Response.json({ url: session.url });
}
```

## Subscription Billing

```typescript
// services/billing.ts
import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

// Create subscription checkout
async function createSubscription(customerId: string, priceId: string) {
  const session = await stripe.checkout.sessions.create({
    mode: "subscription",
    customer: customerId,
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: `${process.env.APP_URL}/billing?success=true`,
    cancel_url: `${process.env.APP_URL}/billing`,
    subscription_data: {
      trial_period_days: 14,
      metadata: { plan: "pro" },
    },
  });
  return session;
}

// Upgrade/downgrade subscription
async function changeSubscriptionPlan(subscriptionId: string, newPriceId: string) {
  const subscription = await stripe.subscriptions.retrieve(subscriptionId);
  const updated = await stripe.subscriptions.update(subscriptionId, {
    items: [{
      id: subscription.items.data[0].id,
      price: newPriceId,
    }],
    proration_behavior: "create_prorations",
  });
  return updated;
}

// Cancel subscription at period end
async function cancelSubscription(subscriptionId: string) {
  return stripe.subscriptions.update(subscriptionId, {
    cancel_at_period_end: true,
  });
}

// Resume cancelled subscription
async function resumeSubscription(subscriptionId: string) {
  return stripe.subscriptions.update(subscriptionId, {
    cancel_at_period_end: false,
  });
}
```

## Webhook Handler

```typescript
// pages/api/webhooks/stripe.ts
import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

export async function POST(req: Request) {
  const body = await req.text();
  const signature = req.headers.get("stripe-signature")!;

  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(body, signature, process.env.STRIPE_WEBHOOK_SECRET!);
  } catch {
    return new Response("Invalid signature", { status: 400 });
  }

  switch (event.type) {
    case "checkout.session.completed": {
      const session = event.data.object;
      if (session.mode === "subscription") {
        await activateSubscription(session.customer as string, session.subscription as string);
      } else {
        await fulfillOrder(session.metadata?.orderId ?? "");
      }
      break;
    }
    case "invoice.payment_succeeded": {
      const invoice = event.data.object;
      await recordPayment(invoice);
      break;
    }
    case "invoice.payment_failed": {
      const invoice = event.data.object;
      await handleFailedPayment(invoice);
      break;
    }
    case "customer.subscription.deleted": {
      const subscription = event.data.object;
      await deactivateSubscription(subscription.customer as string);
      break;
    }
  }

  return new Response("OK", { status: 200 });
}
```

## Metered / Usage-Based Billing

```typescript
// Report usage to Stripe
async function reportUsage(subscriptionItemId: string, quantity: number) {
  await stripe.subscriptionItems.createUsageRecord(subscriptionItemId, {
    quantity,
    timestamp: Math.floor(Date.now() / 1000),
    action: "increment",
  });
}

// Track API calls per customer
async function trackApiUsage(customerId: string) {
  const key = `usage:${customerId}:${getCurrentBillingPeriod()}`;
  const count = await redis.incr(key);

  // Report to Stripe every 100 calls (batched)
  if (count % 100 === 0) {
    const subItem = await getSubscriptionItemId(customerId);
    await reportUsage(subItem, 100);
  }

  return count;
}
```

## Refund Processing

```typescript
// Full refund
async function refundPayment(paymentIntentId: string, reason?: string) {
  return stripe.refunds.create({
    payment_intent: paymentIntentId,
    reason: reason as Stripe.RefundCreateParams.Reason,
  });
}

// Partial refund
async function partialRefund(paymentIntentId: string, amount: number) {
  return stripe.refunds.create({
    payment_intent: paymentIntentId,
    amount: Math.round(amount * 100), // Stripe uses cents
  });
}
```

## Payment Security Checklist

```
PCI COMPLIANCE:
  [ ] Never log or store raw card numbers
  [ ] Use Stripe.js / Elements for card collection (PCI SAQ-A)
  [ ] Validate webhook signatures
  [ ] Use idempotency keys for payment operations
  [ ] Enable 3D Secure for high-risk transactions
  [ ] Use HTTPS everywhere

IDEMPOTENCY:
  // Prevent double charges
  const paymentIntent = await stripe.paymentIntents.create(
    { amount: 2000, currency: "usd" },
    { idempotencyKey: `order_${orderId}` },
  );

FRAUD PREVENTION:
  [ ] Enable Stripe Radar
  [ ] Require billing address verification (AVS)
  [ ] Set up velocity checks (max charges per hour)
  [ ] Monitor for unusual patterns
```

## Additional Resources

- Stripe Docs: https://stripe.com/docs
- Stripe Testing: https://stripe.com/docs/testing
- PayPal SDK: https://developer.paypal.com/
- PCI Compliance: https://www.pcisecuritystandards.org/
