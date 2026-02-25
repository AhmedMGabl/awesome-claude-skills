---
name: sentry-monitoring
description: Sentry error monitoring covering SDK setup, error boundaries, performance tracing, custom contexts, breadcrumbs, release tracking, source maps, and alerting for React, Next.js, and Node.js applications.
---

# Sentry Monitoring

This skill should be used when integrating Sentry for error monitoring and performance tracking. It covers SDK setup, error boundaries, tracing, and alerting.

## When to Use This Skill

Use this skill when you need to:

- Track errors and exceptions in production
- Monitor application performance with tracing
- Set up error boundaries in React applications
- Configure alerts and issue management
- Debug production issues with breadcrumbs and context

## Next.js Setup

```typescript
// sentry.client.config.ts
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 1.0,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  integrations: [
    Sentry.replayIntegration(),
    Sentry.browserTracingIntegration(),
  ],
});

// sentry.server.config.ts
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 1.0,
  profilesSampleRate: 1.0,
});
```

## Error Boundaries (React)

```tsx
import * as Sentry from "@sentry/react";

// Wrap app
function App() {
  return (
    <Sentry.ErrorBoundary
      fallback={({ error, resetError }) => (
        <div>
          <h2>Something went wrong</h2>
          <p>{error.message}</p>
          <button onClick={resetError}>Try again</button>
        </div>
      )}
      onError={(error, componentStack) => {
        console.error("Caught by boundary:", error, componentStack);
      }}
    >
      <Router />
    </Sentry.ErrorBoundary>
  );
}
```

## Manual Error Capture

```typescript
import * as Sentry from "@sentry/nextjs";

// Capture exception with context
try {
  await processPayment(orderId);
} catch (error) {
  Sentry.captureException(error, {
    tags: { component: "payment", orderId },
    extra: { userId: user.id, amount: order.total },
    level: "error",
  });
  throw error;
}

// Capture message
Sentry.captureMessage("User exceeded rate limit", {
  level: "warning",
  tags: { userId: user.id },
});

// Set user context
Sentry.setUser({ id: user.id, email: user.email, username: user.name });

// Add breadcrumb
Sentry.addBreadcrumb({
  category: "navigation",
  message: `Navigated to ${path}`,
  level: "info",
});
```

## Performance Tracing

```typescript
import * as Sentry from "@sentry/node";

async function processOrder(orderId: string) {
  return Sentry.startSpan(
    { name: "processOrder", op: "function" },
    async (span) => {
      span.setAttribute("order.id", orderId);

      const order = await Sentry.startSpan(
        { name: "fetchOrder", op: "db.query" },
        () => db.order.findUnique({ where: { id: orderId } }),
      );

      await Sentry.startSpan(
        { name: "chargePayment", op: "http.client" },
        () => chargeStripe(order),
      );

      await Sentry.startSpan(
        { name: "sendConfirmation", op: "queue.publish" },
        () => emailQueue.add("confirmation", { orderId }),
      );

      return order;
    },
  );
}
```

## API Route Integration

```typescript
// Next.js API route with Sentry
import { withSentry } from "@sentry/nextjs";

export const GET = withSentry(async (request: Request) => {
  // Errors automatically captured
  const data = await fetchData();
  return Response.json(data);
});
```

## Source Maps

```javascript
// next.config.mjs
import { withSentryConfig } from "@sentry/nextjs";

export default withSentryConfig(nextConfig, {
  org: "my-org",
  project: "my-project",
  silent: true,
  hideSourceMaps: true,
  widenClientFileUpload: true,
});
```

## Additional Resources

- Sentry docs: https://docs.sentry.io/
- Next.js SDK: https://docs.sentry.io/platforms/javascript/guides/nextjs/
- Performance: https://docs.sentry.io/product/performance/
