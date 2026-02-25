---
name: datadog-monitoring
description: Datadog monitoring patterns covering APM tracing, custom metrics, log management, dashboards, alerts, SLOs, RUM, and infrastructure monitoring configuration.
---

# Datadog Monitoring

This skill should be used when implementing monitoring with Datadog. It covers APM tracing, custom metrics, log management, dashboards, alerts, SLOs, RUM, and infrastructure monitoring.

## When to Use This Skill

Use this skill when you need to:

- Instrument applications with APM distributed tracing
- Send custom metrics and business KPIs
- Configure log collection and processing
- Create dashboards and alerting monitors
- Define SLOs and track reliability

## APM Tracing (Node.js)

```typescript
// Initialize tracer (must be first import)
import tracer from "dd-trace";

tracer.init({
  service: "my-api",
  env: process.env.NODE_ENV,
  version: process.env.APP_VERSION,
  logInjection: true,
  runtimeMetrics: true,
  profiling: true,
});

// Custom spans
const span = tracer.startSpan("custom.operation", {
  tags: {
    "resource.name": "/api/users",
    "user.id": userId,
  },
});

try {
  const result = await processRequest();
  span.setTag("result.count", result.length);
  return result;
} catch (error) {
  span.setTag("error", error);
  throw error;
} finally {
  span.finish();
}
```

## Custom Metrics

```typescript
import StatsD from "hot-shots";

const dogstatsd = new StatsD({
  host: process.env.DD_AGENT_HOST || "localhost",
  port: 8125,
  prefix: "myapp.",
  globalTags: [`env:${process.env.NODE_ENV}`],
});

// Counter
dogstatsd.increment("api.requests", 1, { endpoint: "/users", method: "GET" });

// Gauge
dogstatsd.gauge("queue.size", queueLength, { queue: "emails" });

// Histogram
dogstatsd.histogram("api.response_time", responseMs, { endpoint: "/users" });

// Distribution
dogstatsd.distribution("payment.amount", amount, { currency: "usd" });

// Set (unique values)
dogstatsd.set("users.active", userId);
```

## Log Management

```typescript
import pino from "pino";

const logger = pino({
  level: "info",
  formatters: {
    level(label) {
      return { level: label, dd: {
        trace_id: tracer.scope().active()?.context()?.toTraceId(),
        span_id: tracer.scope().active()?.context()?.toSpanId(),
        service: "my-api",
        env: process.env.NODE_ENV,
      }};
    },
  },
});

logger.info({ userId, action: "login" }, "User logged in");
logger.error({ err, requestId }, "Request failed");
```

## Monitors (Alerts)

```json
{
  "name": "High Error Rate on API",
  "type": "metric alert",
  "query": "sum(last_5m):sum:myapp.api.errors{env:production} by {endpoint}.as_count() / sum:myapp.api.requests{env:production} by {endpoint}.as_count() > 0.05",
  "message": "Error rate above 5% on {{endpoint.name}}\n\n@slack-alerts @pagerduty-oncall",
  "tags": ["team:backend", "env:production"],
  "priority": 1,
  "options": {
    "thresholds": {
      "critical": 0.05,
      "warning": 0.02
    },
    "notify_no_data": true,
    "no_data_timeframe": 10,
    "renotify_interval": 60,
    "escalation_message": "Still alerting after 1 hour"
  }
}
```

## SLO Definition

```json
{
  "name": "API Availability SLO",
  "description": "99.9% of API requests succeed",
  "type": "metric",
  "query": {
    "numerator": "sum:myapp.api.requests{env:production,status:2xx}.as_count()",
    "denominator": "sum:myapp.api.requests{env:production}.as_count()"
  },
  "target_threshold": 99.9,
  "warning_threshold": 99.95,
  "timeframe": "30d",
  "tags": ["team:backend", "service:api"]
}
```

## Docker Agent Configuration

```yaml
# docker-compose.yml
datadog-agent:
  image: gcr.io/datadoghq/agent:latest
  environment:
    - DD_API_KEY=${DD_API_KEY}
    - DD_SITE=datadoghq.com
    - DD_APM_ENABLED=true
    - DD_LOGS_ENABLED=true
    - DD_LOGS_CONFIG_CONTAINER_COLLECT_ALL=true
    - DD_PROCESS_AGENT_ENABLED=true
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock:ro
    - /proc/:/host/proc/:ro
    - /sys/fs/cgroup/:/host/sys/fs/cgroup:ro
  ports:
    - "8125:8125/udp"  # DogStatsD
    - "8126:8126"       # APM
```

## Additional Resources

- Datadog Docs: https://docs.datadoghq.com/
- APM: https://docs.datadoghq.com/tracing/
- Monitors: https://docs.datadoghq.com/monitors/
