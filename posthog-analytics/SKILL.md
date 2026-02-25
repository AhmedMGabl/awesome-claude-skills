---
name: posthog-analytics
description: PostHog product analytics covering event tracking, feature flags, A/B testing, session replay, user identification, group analytics, and React/Next.js integration patterns.
---

# PostHog Analytics

This skill should be used when integrating PostHog for product analytics. It covers event tracking, feature flags, experiments, session replay, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Track product events and user behavior
- Implement feature flags and A/B tests
- Record and replay user sessions
- Analyze funnels and user journeys
- Build data-driven product features

## Next.js Setup

```typescript
// app/providers.tsx
"use client";
import posthog from "posthog-js";
import { PostHogProvider as PHProvider } from "posthog-js/react";
import { useEffect } from "react";

export function PostHogProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
      api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST || "https://us.i.posthog.com",
      capture_pageview: false, // Manual pageview tracking
      capture_pageleave: true,
    });
  }, []);

  return <PHProvider client={posthog}>{children}</PHProvider>;
}

// app/layout.tsx
export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <PostHogProvider>{children}</PostHogProvider>
      </body>
    </html>
  );
}
```

## Event Tracking

```typescript
import { usePostHog } from "posthog-js/react";

function ProductPage({ product }: { product: Product }) {
  const posthog = usePostHog();

  const handleAddToCart = () => {
    addToCart(product);
    posthog.capture("item_added_to_cart", {
      product_id: product.id,
      product_name: product.name,
      price: product.price,
      category: product.category,
    });
  };

  const handlePurchase = (order: Order) => {
    posthog.capture("purchase_completed", {
      order_id: order.id,
      total: order.total,
      items: order.items.length,
      $set: { total_purchases: order.customerPurchaseCount },
    });
  };

  return (
    <div>
      <h1>{product.name}</h1>
      <button onClick={handleAddToCart}>Add to Cart</button>
    </div>
  );
}
```

## User Identification

```typescript
import posthog from "posthog-js";

// Identify user after login
function onLogin(user: User) {
  posthog.identify(user.id, {
    email: user.email,
    name: user.name,
    plan: user.plan,
    company: user.company,
  });
}

// Group analytics (company-level)
function onOrgJoin(org: Organization) {
  posthog.group("company", org.id, {
    name: org.name,
    plan: org.plan,
    employee_count: org.size,
  });
}

// Reset on logout
function onLogout() {
  posthog.reset();
}
```

## Feature Flags

```tsx
import { useFeatureFlagEnabled, useFeatureFlagPayload } from "posthog-js/react";

function Dashboard() {
  const showNewDashboard = useFeatureFlagEnabled("new-dashboard");
  const dashboardConfig = useFeatureFlagPayload("new-dashboard");

  if (showNewDashboard) {
    return <NewDashboard config={dashboardConfig} />;
  }
  return <LegacyDashboard />;
}

// Server-side feature flags (Next.js)
import { PostHog } from "posthog-node";

const posthogServer = new PostHog(process.env.POSTHOG_KEY!, {
  host: process.env.POSTHOG_HOST,
});

export async function getServerSideProps(context) {
  const flags = await posthogServer.getAllFlags(userId);
  return { props: { flags } };
}
```

## A/B Testing

```tsx
function PricingPage() {
  const posthog = usePostHog();
  const variant = posthog.getFeatureFlag("pricing-experiment");

  useEffect(() => {
    posthog.capture("pricing_page_viewed", { variant });
  }, [variant]);

  if (variant === "annual-first") return <AnnualFirstPricing />;
  if (variant === "monthly-first") return <MonthlyFirstPricing />;
  return <DefaultPricing />;
}
```

## Session Replay

```typescript
posthog.init(POSTHOG_KEY, {
  session_recording: {
    maskAllInputs: true,
    maskTextSelector: ".sensitive-data",
    recordCrossOriginIframes: true,
  },
});
```

## Server-Side Tracking

```typescript
import { PostHog } from "posthog-node";

const posthog = new PostHog(process.env.POSTHOG_KEY!, {
  host: process.env.POSTHOG_HOST,
});

// Track server-side event
posthog.capture({
  distinctId: userId,
  event: "subscription_renewed",
  properties: { plan: "pro", amount: 29.99, period: "monthly" },
});

// Flush before shutdown
await posthog.shutdown();
```

## Additional Resources

- PostHog docs: https://posthog.com/docs
- React SDK: https://posthog.com/docs/libraries/react
- Feature flags: https://posthog.com/docs/feature-flags
