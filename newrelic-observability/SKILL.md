---
name: newrelic-observability
description: New Relic observability patterns covering APM instrumentation, custom events, NRQL queries, dashboards, alerts, SLIs, distributed tracing, and browser monitoring.
---

# New Relic Observability

This skill should be used when implementing observability with New Relic. It covers APM instrumentation, custom events, NRQL queries, dashboards, alerts, SLIs, distributed tracing, and browser monitoring.

## When to Use This Skill

Use this skill when you need to:

- Instrument applications with APM and distributed tracing
- Record custom events and attributes
- Query telemetry data with NRQL
- Create dashboards and alert policies
- Define SLIs and error budgets

## APM Instrumentation (Node.js)

```typescript
// newrelic.js (must be first require)
"use strict";

exports.config = {
  app_name: ["My Application"],
  license_key: process.env.NEW_RELIC_LICENSE_KEY,
  distributed_tracing: { enabled: true },
  logging: { level: "info" },
  allow_all_headers: true,
  attributes: {
    exclude: [
      "request.headers.cookie",
      "request.headers.authorization",
    ],
  },
};
```

```typescript
import newrelic from "newrelic";

// Custom transaction
newrelic.startBackgroundTransaction("processOrder", "Orders", async () => {
  const transaction = newrelic.getTransaction();

  try {
    newrelic.addCustomAttributes({
      orderId: order.id,
      customerId: order.customerId,
      totalAmount: order.total,
    });

    await processPayment(order);
    await fulfillOrder(order);

    newrelic.recordCustomEvent("OrderProcessed", {
      orderId: order.id,
      processingTimeMs: Date.now() - startTime,
    });
  } catch (error) {
    newrelic.noticeError(error, { orderId: order.id });
    throw error;
  } finally {
    transaction.end();
  }
});
```

## Custom Events and Metrics

```typescript
// Record custom event
newrelic.recordCustomEvent("UserAction", {
  userId: user.id,
  action: "checkout",
  cartValue: cart.total,
  itemCount: cart.items.length,
});

// Record metric
newrelic.recordMetric("Custom/Queue/Size", queueSize);
newrelic.recordMetric("Custom/Cache/HitRate", hitRate);

// Increment counter
newrelic.incrementMetric("Custom/Errors/PaymentFailed");

// Add custom attributes to current transaction
newrelic.addCustomAttributes({
  "user.tier": user.subscriptionTier,
  "feature.flag": featureEnabled,
});
```

## NRQL Queries

```sql
-- Error rate by endpoint
SELECT percentage(count(*), WHERE error IS true)
FROM Transaction
WHERE appName = 'My Application'
FACET request.uri
SINCE 1 hour ago

-- Response time percentiles
SELECT percentile(duration, 50, 95, 99)
FROM Transaction
WHERE appName = 'My Application'
FACET request.uri
SINCE 24 hours ago TIMESERIES

-- Custom event analysis
SELECT average(processingTimeMs), count(*)
FROM OrderProcessed
FACET cases(WHERE totalAmount < 100 AS 'Small',
            WHERE totalAmount < 500 AS 'Medium',
            WHERE totalAmount >= 500 AS 'Large')
SINCE 7 days ago

-- Apdex score over time
SELECT apdex(duration, 0.5)
FROM Transaction
WHERE appName = 'My Application'
SINCE 24 hours ago TIMESERIES

-- Distributed trace analysis
SELECT count(*)
FROM Span
WHERE entity.name = 'My Application'
FACET span.kind, name
SINCE 1 hour ago
```

## Alert Conditions

```json
{
  "name": "High Error Rate",
  "type": "static",
  "nrql": {
    "query": "SELECT percentage(count(*), WHERE error IS true) FROM Transaction WHERE appName = 'My Application'"
  },
  "critical": {
    "operator": "above",
    "threshold": 5,
    "threshold_duration": 300,
    "threshold_occurrences": "all"
  },
  "warning": {
    "operator": "above",
    "threshold": 2,
    "threshold_duration": 300,
    "threshold_occurrences": "all"
  }
}
```

## SLI/SLO Definition

```json
{
  "name": "API Availability",
  "description": "Percentage of successful API requests",
  "sli": {
    "good_events": "SELECT count(*) FROM Transaction WHERE httpResponseCode < 500 AND appName = 'My Application'",
    "valid_events": "SELECT count(*) FROM Transaction WHERE appName = 'My Application'"
  },
  "objectives": [
    { "target": 99.9, "timeWindow": { "rolling": { "count": 28, "unit": "DAY" } } }
  ]
}
```

## Deployment Markers

```bash
# Record deployment
curl -X POST "https://api.newrelic.com/v2/applications/${APP_ID}/deployments.json" \
  -H "Api-Key:${NEW_RELIC_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"deployment\": {
      \"revision\": \"${GIT_SHA}\",
      \"user\": \"${DEPLOYER}\",
      \"description\": \"${COMMIT_MSG}\"
    }
  }"
```

## Additional Resources

- New Relic Docs: https://docs.newrelic.com/
- NRQL Reference: https://docs.newrelic.com/docs/nrql/get-started/introduction-nrql-new-relics-query-language/
- Node.js Agent: https://docs.newrelic.com/docs/apm/agents/nodejs-agent/
