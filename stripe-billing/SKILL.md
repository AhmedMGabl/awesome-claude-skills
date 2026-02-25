---
name: stripe-billing
description: Stripe billing covering subscription management, usage-based metering, customer portal, invoicing, proration, trial periods, webhook handling, and SaaS pricing model implementation.
---

# Stripe Billing

This skill should be used when implementing subscription billing with Stripe. It covers subscriptions, metering, customer portal, invoicing, and SaaS pricing patterns.

## When to Use This Skill

Use this skill when you need to:

- Implement subscription-based billing
- Set up usage-based metering
- Create customer self-service portals
- Handle subscription lifecycle events
- Implement free trials and proration

## Create Subscription

```typescript
import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

// Create customer
const customer = await stripe.customers.create({
  email: user.email,
  name: user.name,
  metadata: { userId: user.id },
});

// Create subscription with trial
const subscription = await stripe.subscriptions.create({
  customer: customer.id,
  items: [{ price: "price_pro_monthly" }],
  trial_period_days: 14,
  payment_behavior: "default_incomplete",
  payment_settings: { save_default_payment_method: "on_subscription" },
  expand: ["latest_invoice.payment_intent"],
});

// Return client secret for payment
const invoice = subscription.latest_invoice as Stripe.Invoice;
const paymentIntent = invoice.payment_intent as Stripe.PaymentIntent;
return { subscriptionId: subscription.id, clientSecret: paymentIntent.client_secret };
```

## Change Plan

```typescript
async function changePlan(subscriptionId: string, newPriceId: string) {
  const subscription = await stripe.subscriptions.retrieve(subscriptionId);

  return stripe.subscriptions.update(subscriptionId, {
    items: [{
      id: subscription.items.data[0].id,
      price: newPriceId,
    }],
    proration_behavior: "create_prorations",
  });
}

// Cancel at period end
async function cancelSubscription(subscriptionId: string) {
  return stripe.subscriptions.update(subscriptionId, {
    cancel_at_period_end: true,
  });
}
```

## Usage-Based Billing

```typescript
// Report usage
await stripe.subscriptionItems.createUsageRecord(
  subscriptionItemId,
  {
    quantity: 150, // API calls, tokens, etc.
    timestamp: Math.floor(Date.now() / 1000),
    action: "increment",
  },
);

// Meter events (newer API)
await stripe.billing.meterEvents.create({
  event_name: "api_requests",
  payload: {
    stripe_customer_id: customerId,
    value: "100",
  },
});
```

## Customer Portal

```typescript
// Create portal session
const session = await stripe.billingPortal.sessions.create({
  customer: customerId,
  return_url: "https://myapp.com/settings",
});

// Redirect user to session.url
```

## Webhook Handling

```typescript
// app/api/webhooks/stripe/route.ts
export async function POST(request: Request) {
  const body = await request.text();
  const signature = request.headers.get("stripe-signature")!;

  const event = stripe.webhooks.constructEvent(
    body,
    signature,
    process.env.STRIPE_WEBHOOK_SECRET!,
  );

  switch (event.type) {
    case "customer.subscription.created":
    case "customer.subscription.updated": {
      const subscription = event.data.object as Stripe.Subscription;
      await db.update(users)
        .set({
          subscriptionId: subscription.id,
          plan: subscription.items.data[0].price.lookup_key,
          status: subscription.status,
        })
        .where(eq(users.stripeCustomerId, subscription.customer as string));
      break;
    }
    case "customer.subscription.deleted": {
      const subscription = event.data.object as Stripe.Subscription;
      await db.update(users)
        .set({ plan: "free", status: "canceled" })
        .where(eq(users.stripeCustomerId, subscription.customer as string));
      break;
    }
    case "invoice.payment_failed": {
      const invoice = event.data.object as Stripe.Invoice;
      await notifyPaymentFailed(invoice.customer as string);
      break;
    }
  }

  return new Response("OK");
}
```

## Pricing Table (React)

```tsx
const plans = [
  { name: "Free", price: "$0", priceId: null, features: ["100 requests/day"] },
  { name: "Pro", price: "$29/mo", priceId: "price_pro", features: ["10K requests/day", "Priority support"] },
  { name: "Enterprise", price: "Custom", priceId: null, features: ["Unlimited", "SLA", "Dedicated"] },
];

function PricingTable() {
  return (
    <div className="grid grid-cols-3 gap-8">
      {plans.map((plan) => (
        <div key={plan.name} className="border rounded-lg p-6">
          <h3>{plan.name}</h3>
          <p className="text-3xl font-bold">{plan.price}</p>
          <ul>
            {plan.features.map((f) => <li key={f}>{f}</li>)}
          </ul>
          {plan.priceId && (
            <button onClick={() => subscribe(plan.priceId!)}>Subscribe</button>
          )}
        </div>
      ))}
    </div>
  );
}
```

## Additional Resources

- Stripe Billing docs: https://stripe.com/docs/billing
- Subscription lifecycle: https://stripe.com/docs/billing/subscriptions/overview
- Customer portal: https://stripe.com/docs/customer-management
