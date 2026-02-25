---
name: opentelemetry
description: OpenTelemetry observability covering traces, metrics, and logs instrumentation for Node.js and Python, SDK configuration, span creation, context propagation, exporters for Jaeger and OTLP, auto-instrumentation, and integration with Grafana and Datadog.
---

# OpenTelemetry

This skill should be used when implementing observability with OpenTelemetry. It covers tracing, metrics, logs, SDK setup, context propagation, and exporter configuration.

## When to Use This Skill

Use this skill when you need to:

- Add distributed tracing to microservices
- Collect application metrics (latency, throughput, errors)
- Set up auto-instrumentation for HTTP, database, and messaging
- Export telemetry to Jaeger, Grafana, or Datadog
- Implement custom spans and metrics

## Node.js SDK Setup

```typescript
// instrumentation.ts
import { NodeSDK } from "@opentelemetry/sdk-node";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";
import { OTLPMetricExporter } from "@opentelemetry/exporter-metrics-otlp-http";
import { PeriodicExportingMetricReader } from "@opentelemetry/sdk-metrics";
import { getNodeAutoInstrumentations } from "@opentelemetry/auto-instrumentations-node";
import { Resource } from "@opentelemetry/resources";
import { ATTR_SERVICE_NAME, ATTR_SERVICE_VERSION } from "@opentelemetry/semantic-conventions";

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
      "@opentelemetry/instrumentation-redis": { enabled: true },
    }),
  ],
});

sdk.start();
process.on("SIGTERM", () => sdk.shutdown());
```

## Custom Spans

```typescript
import { trace, SpanStatusCode } from "@opentelemetry/api";

const tracer = trace.getTracer("my-api");

async function processOrder(orderId: string) {
  return tracer.startActiveSpan("process-order", async (span) => {
    span.setAttribute("order.id", orderId);

    try {
      // Child span for payment
      const payment = await tracer.startActiveSpan("charge-payment", async (paymentSpan) => {
        paymentSpan.setAttribute("payment.method", "stripe");
        const result = await stripe.charges.create({ amount: 1000 });
        paymentSpan.setAttribute("payment.id", result.id);
        paymentSpan.end();
        return result;
      });

      // Child span for notification
      await tracer.startActiveSpan("send-notification", async (notifSpan) => {
        await sendEmail(orderId);
        notifSpan.end();
      });

      span.setStatus({ code: SpanStatusCode.OK });
      return payment;
    } catch (error) {
      span.setStatus({ code: SpanStatusCode.ERROR, message: (error as Error).message });
      span.recordException(error as Error);
      throw error;
    } finally {
      span.end();
    }
  });
}
```

## Custom Metrics

```typescript
import { metrics } from "@opentelemetry/api";

const meter = metrics.getMeter("my-api");

// Counter — total requests
const requestCounter = meter.createCounter("http.requests.total", {
  description: "Total HTTP requests",
});

// Histogram — request duration
const requestDuration = meter.createHistogram("http.request.duration", {
  description: "HTTP request duration in ms",
  unit: "ms",
});

// Usage in middleware
app.use((req, res, next) => {
  const start = Date.now();

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
  });

  next();
});
```

## Python Auto-Instrumentation

```python
# pip install opentelemetry-distro opentelemetry-exporter-otlp
# opentelemetry-bootstrap -a install

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

resource = Resource.create({"service.name": "my-python-api"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("process_order")
def process_order(order_id: str):
    span = trace.get_current_span()
    span.set_attribute("order.id", order_id)
    # Business logic...
```

## Docker Compose (Collector + Jaeger)

```yaml
services:
  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    ports:
      - "4317:4317"   # gRPC
      - "4318:4318"   # HTTP
    volumes:
      - ./otel-config.yaml:/etc/otel/config.yaml
    command: ["--config", "/etc/otel/config.yaml"]

  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # UI
      - "14268:14268"  # Collector
```

## Additional Resources

- OpenTelemetry docs: https://opentelemetry.io/docs/
- Node.js SDK: https://opentelemetry.io/docs/languages/js/
- Python SDK: https://opentelemetry.io/docs/languages/python/
