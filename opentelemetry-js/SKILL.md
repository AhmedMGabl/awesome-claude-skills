---
name: opentelemetry-js
description: OpenTelemetry JavaScript SDK patterns covering trace instrumentation, span creation, context propagation, metrics collection, log correlation, auto-instrumentation for Express/Fastify/Next.js, custom exporters, and collector configuration.
---

# OpenTelemetry JS

This skill should be used when instrumenting JavaScript/TypeScript applications with OpenTelemetry. It covers tracing, metrics, logs, auto-instrumentation, and exporter configuration.

## When to Use This Skill

Use this skill when you need to:

- Add distributed tracing to Node.js applications
- Collect custom metrics (counters, histograms, gauges)
- Auto-instrument Express, Fastify, or Next.js
- Export telemetry to Jaeger, Zipkin, or OTLP backends
- Propagate trace context across service boundaries

## SDK Setup

```typescript
// instrumentation.ts
import { NodeSDK } from "@opentelemetry/sdk-node";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";
import { OTLPMetricExporter } from "@opentelemetry/exporter-metrics-otlp-http";
import { PeriodicExportingMetricReader } from "@opentelemetry/sdk-metrics";
import { getNodeAutoInstrumentations } from "@opentelemetry/auto-instrumentations-node";
import { Resource } from "@opentelemetry/resources";
import {
  ATTR_SERVICE_NAME,
  ATTR_SERVICE_VERSION,
} from "@opentelemetry/semantic-conventions";

const sdk = new NodeSDK({
  resource: new Resource({
    [ATTR_SERVICE_NAME]: "my-api",
    [ATTR_SERVICE_VERSION]: "1.0.0",
  }),
  traceExporter: new OTLPTraceExporter({
    url: "http://localhost:4318/v1/traces",
  }),
  metricReader: new PeriodicExportingMetricReader({
    exporter: new OTLPMetricExporter({
      url: "http://localhost:4318/v1/metrics",
    }),
    exportIntervalMillis: 30000,
  }),
  instrumentations: [
    getNodeAutoInstrumentations({
      "@opentelemetry/instrumentation-http": { enabled: true },
      "@opentelemetry/instrumentation-express": { enabled: true },
      "@opentelemetry/instrumentation-pg": { enabled: true },
    }),
  ],
});

sdk.start();

process.on("SIGTERM", () => {
  sdk.shutdown().then(() => process.exit(0));
});
```

## Custom Spans

```typescript
import { trace, SpanStatusCode, SpanKind } from "@opentelemetry/api";

const tracer = trace.getTracer("my-api", "1.0.0");

// Simple span
async function processOrder(orderId: string) {
  return tracer.startActiveSpan("processOrder", async (span) => {
    try {
      span.setAttribute("order.id", orderId);

      // Child span
      const items = await tracer.startActiveSpan("fetchItems", async (childSpan) => {
        const result = await db.query("SELECT * FROM items WHERE order_id = $1", [orderId]);
        childSpan.setAttribute("items.count", result.rows.length);
        childSpan.end();
        return result.rows;
      });

      // Add events
      span.addEvent("order.validated", { "items.count": items.length });

      const total = calculateTotal(items);
      span.setAttribute("order.total", total);

      await chargePayment(orderId, total);
      span.addEvent("payment.charged");

      span.setStatus({ code: SpanStatusCode.OK });
      return { orderId, total, items: items.length };
    } catch (error) {
      span.setStatus({
        code: SpanStatusCode.ERROR,
        message: error instanceof Error ? error.message : "Unknown error",
      });
      span.recordException(error as Error);
      throw error;
    } finally {
      span.end();
    }
  });
}

// External service span
async function callPaymentService(amount: number) {
  return tracer.startActiveSpan(
    "payment.charge",
    { kind: SpanKind.CLIENT, attributes: { "payment.amount": amount } },
    async (span) => {
      try {
        const result = await fetch("https://payments.example.com/charge", {
          method: "POST",
          body: JSON.stringify({ amount }),
        });
        span.setAttribute("http.status_code", result.status);
        span.end();
        return result.json();
      } catch (error) {
        span.recordException(error as Error);
        span.end();
        throw error;
      }
    },
  );
}
```

## Custom Metrics

```typescript
import { metrics } from "@opentelemetry/api";

const meter = metrics.getMeter("my-api", "1.0.0");

// Counter
const requestCounter = meter.createCounter("http.requests.total", {
  description: "Total number of HTTP requests",
});

// Histogram
const requestDuration = meter.createHistogram("http.request.duration", {
  description: "HTTP request duration in milliseconds",
  unit: "ms",
});

// Up-down counter (gauge-like)
const activeConnections = meter.createUpDownCounter("connections.active", {
  description: "Number of active connections",
});

// Observable gauge
meter.createObservableGauge("system.memory.usage", {
  description: "Memory usage in bytes",
  unit: "bytes",
  callback: (result) => {
    const usage = process.memoryUsage();
    result.observe(usage.heapUsed, { type: "heap" });
    result.observe(usage.rss, { type: "rss" });
  },
});

// Usage in middleware
function metricsMiddleware(req, res, next) {
  const start = Date.now();
  activeConnections.add(1);

  res.on("finish", () => {
    const duration = Date.now() - start;
    requestCounter.add(1, {
      method: req.method,
      route: req.route?.path ?? req.path,
      status: res.statusCode,
    });
    requestDuration.record(duration, {
      method: req.method,
      route: req.route?.path ?? req.path,
    });
    activeConnections.add(-1);
  });

  next();
}
```

## Context Propagation

```typescript
import { context, propagation, trace } from "@opentelemetry/api";

// Extract context from incoming request
function extractContext(req: Request) {
  const carrier: Record<string, string> = {};
  req.headers.forEach((value, key) => {
    carrier[key] = value;
  });
  return propagation.extract(context.active(), carrier);
}

// Inject context into outgoing request
function injectContext(headers: Record<string, string>) {
  propagation.inject(context.active(), headers);
  return headers;
}

// Example: propagating context across services
async function callDownstreamService(data: unknown) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  injectContext(headers);

  return fetch("http://downstream-service/api/process", {
    method: "POST",
    headers,
    body: JSON.stringify(data),
  });
}
```

## Express Integration

```typescript
import express from "express";
import { trace } from "@opentelemetry/api";

// Auto-instrumented by @opentelemetry/instrumentation-express
const app = express();

app.get("/api/users/:id", async (req, res) => {
  const span = trace.getActiveSpan();
  span?.setAttribute("user.id", req.params.id);

  const user = await db.users.findById(req.params.id);
  if (!user) {
    span?.setAttribute("error.type", "not_found");
    return res.status(404).json({ error: "Not found" });
  }

  res.json(user);
});
```

## Additional Resources

- OpenTelemetry JS docs: https://opentelemetry.io/docs/languages/js/
- Auto-instrumentation: https://opentelemetry.io/docs/languages/js/automatic/
- Semantic conventions: https://opentelemetry.io/docs/specs/semconv/
