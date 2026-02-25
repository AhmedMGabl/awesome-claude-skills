---
name: stripe-payments
description: Stripe payment integration covering Checkout Sessions, Payment Intents, subscriptions, webhooks, customer management, invoicing, Connect for marketplaces, and production-ready payment patterns with TypeScript.
---

# Stripe Payments

This skill should be used when integrating payment processing into applications. It covers Stripe Checkout, Payment Intents, subscriptions, webhooks, and marketplace patterns.

## When to Use This Skill

Use this skill when you need to:

- Accept one-time payments or subscriptions
- Implement Stripe Checkout or embedded payment forms
- Handle webhooks for payment events
- Manage customers and payment methods
- Build marketplace payments with Stripe Connect
- Create invoices and billing portals

## Setup

```bash
npm install stripe @stripe/stripe-js @stripe/react-stripe-js
```

```typescript
// lib/stripe.ts (server-side)
import Stripe from "stripe";

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: "2024-12-18.acacia",
});

// lib/stripe-client.ts (client-side)
import { loadStripe } from "@stripe/stripe-js";
export const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!);
```

## Checkout Sessions

```typescript
// Create Checkout Session (server)
import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const { priceId, userId } = await req.json();

  // Find or create customer
  let customer = await findCustomerByUserId(userId);
  if (!customer) {
    customer = await stripe.customers.create({
      metadata: { userId },
    });
    await saveCustomerId(userId, customer.id);
  }

  const session = await stripe.checkout.sessions.create({
    customer: customer.id,
    mode: "subscription", // or "payment" for one-time
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: `${process.env.APP_URL}/billing?success=true&session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.APP_URL}/billing?canceled=true`,
    subscription_data: {
      trial_period_days: 14,
      metadata: { userId },
    },
    allow_promotion_codes: true,
  });

  return NextResponse.json({ url: session.url });
}

// Client-side redirect
async function handleCheckout(priceId: string) {
  const res = await fetch("/api/checkout", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ priceId, userId: user.id }),
  });
  const { url } = await res.json();
  window.location.href = url;
}
```

## Payment Intents (Custom Forms)

```typescript
// Server: create Payment Intent
export async function POST(req: NextRequest) {
  const { amount, currency = "usd" } = await req.json();

  const paymentIntent = await stripe.paymentIntents.create({
    amount: Math.round(amount * 100), // cents
    currency,
    automatic_payment_methods: { enabled: true },
    metadata: { orderId: "order_123" },
  });

  return NextResponse.json({ clientSecret: paymentIntent.client_secret });
}

// Client: React payment form
import { Elements, PaymentElement, useStripe, useElements } from "@stripe/react-stripe-js";

function CheckoutForm() {
  const stripe = useStripe();
  const elements = useElements();
  const [error, setError] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!stripe || !elements) return;

    setProcessing(true);
    const { error } = await stripe.confirmPayment({
      elements,
      confirmParams: { return_url: `${window.location.origin}/payment/success` },
    });

    if (error) {
      setError(error.message ?? "Payment failed");
      setProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <PaymentElement />
      <button disabled={!stripe || processing}>
        {processing ? "Processing..." : "Pay now"}
      </button>
      {error && <div className="text-red-500">{error}</div>}
    </form>
  );
}

// Wrap with Elements provider
function PaymentPage({ clientSecret }: { clientSecret: string }) {
  return (
    <Elements stripe={stripePromise} options={{ clientSecret }}>
      <CheckoutForm />
    </Elements>
  );
}
```

## Webhooks

```typescript
// app/api/webhooks/stripe/route.ts
import { headers } from "next/headers";

export async function POST(req: NextRequest) {
  const body = await req.text();
  const signature = (await headers()).get("stripe-signature")!;

  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!
    );
  } catch (err) {
    return NextResponse.json({ error: "Invalid signature" }, { status: 400 });
  }

  switch (event.type) {
    case "checkout.session.completed": {
      const session = event.data.object as Stripe.Checkout.Session;
      await handleCheckoutComplete(session);
      break;
    }
    case "customer.subscription.updated": {
      const subscription = event.data.object as Stripe.Subscription;
      await updateSubscriptionStatus(
        subscription.metadata.userId,
        subscription.status,
        subscription.current_period_end
      );
      break;
    }
    case "customer.subscription.deleted": {
      const subscription = event.data.object as Stripe.Subscription;
      await cancelUserSubscription(subscription.metadata.userId);
      break;
    }
    case "invoice.payment_failed": {
      const invoice = event.data.object as Stripe.Invoice;
      await handlePaymentFailed(invoice);
      break;
    }
    case "invoice.paid": {
      const invoice = event.data.object as Stripe.Invoice;
      await handleInvoicePaid(invoice);
      break;
    }
  }

  return NextResponse.json({ received: true });
}
```

## Subscription Management

```typescript
// Create subscription with multiple prices
const subscription = await stripe.subscriptions.create({
  customer: customerId,
  items: [{ price: "price_monthly_pro" }],
  payment_behavior: "default_incomplete",
  payment_settings: { save_default_payment_method: "on_subscription" },
  expand: ["latest_invoice.payment_intent"],
});

// Change plan (upgrade/downgrade)
const subscription = await stripe.subscriptions.retrieve(subscriptionId);
await stripe.subscriptions.update(subscriptionId, {
  items: [{ id: subscription.items.data[0].id, price: newPriceId }],
  proration_behavior: "create_prorations",
});

// Cancel subscription
await stripe.subscriptions.update(subscriptionId, {
  cancel_at_period_end: true, // Cancel at end of billing period
});

// Resume canceled subscription
await stripe.subscriptions.update(subscriptionId, {
  cancel_at_period_end: false,
});

// Customer billing portal
const portalSession = await stripe.billingPortal.sessions.create({
  customer: customerId,
  return_url: `${process.env.APP_URL}/billing`,
});
// Redirect to portalSession.url
```

## Metered Billing

```typescript
// Report usage for metered pricing
await stripe.subscriptionItems.createUsageRecord(subscriptionItemId, {
  quantity: 100, // e.g., API calls
  timestamp: Math.floor(Date.now() / 1000),
  action: "increment", // or "set"
});

// Get usage summary
const usageSummary = await stripe.subscriptionItems.listUsageRecordSummaries(
  subscriptionItemId,
  { limit: 10 }
);
```

## Stripe Connect (Marketplace)

```typescript
// Create connected account
const account = await stripe.accounts.create({
  type: "express",
  country: "US",
  email: "seller@example.com",
  capabilities: {
    card_payments: { requested: true },
    transfers: { requested: true },
  },
});

// Generate onboarding link
const accountLink = await stripe.accountLinks.create({
  account: account.id,
  refresh_url: `${process.env.APP_URL}/connect/refresh`,
  return_url: `${process.env.APP_URL}/connect/complete`,
  type: "account_onboarding",
});

// Direct charge with platform fee
const paymentIntent = await stripe.paymentIntents.create({
  amount: 10000,
  currency: "usd",
  application_fee_amount: 1000, // 10% platform fee
  transfer_data: { destination: connectedAccountId },
});

// Transfer funds
const transfer = await stripe.transfers.create({
  amount: 5000,
  currency: "usd",
  destination: connectedAccountId,
});
```

## Additional Resources

- Stripe API Reference: https://stripe.com/docs/api
- Stripe.js: https://stripe.com/docs/js
- Stripe Webhooks: https://stripe.com/docs/webhooks
- Stripe Testing: https://stripe.com/docs/testing
