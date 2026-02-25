---
name: stripe-connect
description: Stripe Connect platform development covering marketplace payments, connected account onboarding, direct and destination charges, transfer splits, payout scheduling, platform fees, account dashboards, identity verification, and webhook handling for multi-party payments.
---

# Stripe Connect

This skill should be used when building marketplace or platform payment flows with Stripe Connect. It covers account onboarding, charge types, transfers, payouts, and platform management.

## When to Use This Skill

Use this skill when you need to:

- Build a marketplace with seller payouts
- Onboard connected accounts (Express/Custom)
- Split payments between platform and sellers
- Manage platform fees and transfers
- Handle identity verification for sellers

## Account Onboarding

```typescript
import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

// Create Express connected account
async function createConnectedAccount(email: string) {
  const account = await stripe.accounts.create({
    type: "express",
    email,
    capabilities: {
      card_payments: { requested: true },
      transfers: { requested: true },
    },
    business_type: "individual",
  });

  // Generate onboarding link
  const accountLink = await stripe.accountLinks.create({
    account: account.id,
    refresh_url: `${process.env.APP_URL}/onboarding/refresh`,
    return_url: `${process.env.APP_URL}/onboarding/complete`,
    type: "account_onboarding",
  });

  return { accountId: account.id, onboardingUrl: accountLink.url };
}
```

## Destination Charges (Recommended)

```typescript
// Platform creates charge, Stripe transfers to connected account
async function createMarketplacePayment(
  amount: number,
  sellerId: string,
  platformFeePercent: number,
) {
  const platformFee = Math.round(amount * (platformFeePercent / 100));

  const paymentIntent = await stripe.paymentIntents.create({
    amount,
    currency: "usd",
    application_fee_amount: platformFee,
    transfer_data: {
      destination: sellerId, // Connected account ID (acct_xxx)
    },
    metadata: { sellerId, platformFee: platformFee.toString() },
  });

  return paymentIntent;
}
```

## Direct Charges

```typescript
// Charge created directly on connected account
async function createDirectCharge(
  amount: number,
  connectedAccountId: string,
  platformFee: number,
) {
  const paymentIntent = await stripe.paymentIntents.create(
    {
      amount,
      currency: "usd",
      application_fee_amount: platformFee,
    },
    { stripeAccount: connectedAccountId },
  );

  return paymentIntent;
}
```

## Split Payments (Separate Charges and Transfers)

```typescript
// Charge customer, then transfer to multiple sellers
async function splitPayment(
  totalAmount: number,
  splits: Array<{ sellerId: string; amount: number }>,
) {
  // 1. Charge the customer on the platform
  const paymentIntent = await stripe.paymentIntents.create({
    amount: totalAmount,
    currency: "usd",
  });

  // 2. After payment succeeds, create transfers
  for (const split of splits) {
    await stripe.transfers.create({
      amount: split.amount,
      currency: "usd",
      destination: split.sellerId,
      source_transaction: paymentIntent.latest_charge as string,
    });
  }
}
```

## Account Dashboard

```typescript
// Generate Express Dashboard login link
async function getSellerDashboard(connectedAccountId: string) {
  const loginLink = await stripe.accounts.createLoginLink(connectedAccountId);
  return loginLink.url;
}

// Check account status
async function getAccountStatus(connectedAccountId: string) {
  const account = await stripe.accounts.retrieve(connectedAccountId);
  return {
    chargesEnabled: account.charges_enabled,
    payoutsEnabled: account.payouts_enabled,
    requirements: account.requirements,
  };
}
```

## Webhook Handler

```typescript
async function handleConnectWebhook(event: Stripe.Event) {
  switch (event.type) {
    case "account.updated": {
      const account = event.data.object as Stripe.Account;
      await db.sellers.update({
        where: { stripeAccountId: account.id },
        data: {
          chargesEnabled: account.charges_enabled,
          payoutsEnabled: account.payouts_enabled,
          onboardingComplete: account.details_submitted,
        },
      });
      break;
    }
    case "payment_intent.succeeded": {
      const pi = event.data.object as Stripe.PaymentIntent;
      await db.orders.update({
        where: { paymentIntentId: pi.id },
        data: { status: "paid" },
      });
      break;
    }
    case "payout.paid": {
      const payout = event.data.object as Stripe.Payout;
      console.log(`Payout ${payout.id} completed: $${payout.amount / 100}`);
      break;
    }
  }
}
```

## Charge Types Comparison

```
TYPE           PLATFORM OWNS    REFUND BY    BEST FOR
──────────────────────────────────────────────────────────
Destination    Platform         Platform     Marketplaces
Direct         Connected acct   Seller       SaaS platforms
Separate       Platform         Platform     Multi-seller orders
```

## Additional Resources

- Stripe Connect docs: https://stripe.com/docs/connect
- Account types: https://stripe.com/docs/connect/accounts
- Testing: https://stripe.com/docs/connect/testing
