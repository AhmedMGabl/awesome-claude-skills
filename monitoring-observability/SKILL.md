---
name: monitoring-observability
description: This skill should be used when implementing monitoring, logging, metrics, distributed tracing, alerting, and observability best practices for production applications.
---

# Monitoring & Observability

Complete guide for implementing comprehensive observability in production applications using logs, metrics, and traces.

## When to Use This Skill

- Set up application logging
- Implement metrics collection
- Add distributed tracing
- Create monitoring dashboards
- Configure alerting rules
- Monitor application health
- Debug production issues
- Optimize application performance

## The Three Pillars of Observability

1. **Logs** - Discrete events with timestamps
2. **Metrics** - Numerical measurements over time
3. **Traces** - Request paths through distributed systems

## Structured Logging

### Node.js with Winston

```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { service: 'user-service' },
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
  ],
});

if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple(),
  }));
}

// Usage
logger.info('User logged in', {
  userId: '123',
  email: 'user@example.com',
  ip: req.ip
});

logger.error('Database connection failed', {
  error: err.message,
  stack: err.stack,
  database: 'users'
});
```

### Python with structlog

```python
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

# Usage
logger.info("user_logged_in",
    user_id="123",
    email="user@example.com",
    ip=request.remote_addr
)

logger.error("database_error",
    error=str(e),
    database="users",
    operation="insert"
)
```

## Metrics Collection

### Prometheus with Node.js

```javascript
const promClient = require('prom-client');
const express = require('express');

const app = express();

// Create registry
const register = new promClient.Registry();

// Default metrics
promClient.collectDefaultMetrics({ register });

// Custom metrics
const httpRequestDuration = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.1, 0.5, 1, 2, 5]
});

const httpRequestTotal = new promClient.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code']
});

const activeConnections = new promClient.Gauge({
  name: 'active_connections',
  help: 'Number of active connections'
});

register.registerMetric(httpRequestDuration);
register.registerMetric(httpRequestTotal);
register.registerMetric(activeConnections);

// Middleware
app.use((req, res, next) => {
  const start = Date.now();

  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;

    httpRequestDuration
      .labels(req.method, req.route?.path || req.path, res.statusCode)
      .observe(duration);

    httpRequestTotal
      .labels(req.method, req.route?.path || req.path, res.statusCode)
      .inc();
  });

  next();
});

// Metrics endpoint
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});

app.listen(3000);
```

### Python with Prometheus Client

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from flask import Flask, Response
import time

app = Flask(__name__)

# Metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

active_requests = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests in progress'
)

@app.before_request
def before_request():
    active_requests.inc()
    request.start_time = time.time()

@app.after_request
def after_request(response):
    active_requests.dec()

    duration = time.time() - request.start_time
    request_duration.labels(
        request.method,
        request.endpoint
    ).observe(duration)

    request_count.labels(
        request.method,
        request.endpoint,
        response.status_code
    ).inc()

    return response

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype='text/plain')
```

## Distributed Tracing

### OpenTelemetry (Node.js)

```javascript
const opentelemetry = require('@opentelemetry/api');
const { NodeTracerProvider } = require('@opentelemetry/sdk-trace-node');
const { JaegerExporter } = require('@opentelemetry/exporter-jaeger');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');

// Configure tracer
const provider = new NodeTracerProvider({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'user-service',
  }),
});

const exporter = new JaegerExporter({
  endpoint: 'http://localhost:14268/api/traces',
});

provider.addSpanProcessor(
  new opentelemetry.SimpleSpanProcessor(exporter)
);

provider.register();

const tracer = opentelemetry.trace.getTracer('user-service');

// Usage
async function getUserById(userId) {
  const span = tracer.startSpan('getUserById');
  span.setAttribute('user.id', userId);

  try {
    const user = await db.users.findOne({ id: userId });
    span.setStatus({ code: opentelemetry.SpanStatusCode.OK });
    return user;
  } catch (error) {
    span.setStatus({
      code: opentelemetry.SpanStatusCode.ERROR,
      message: error.message,
    });
    span.recordException(error);
    throw error;
  } finally {
    span.end();
  }
}

// HTTP middleware
app.use((req, res, next) => {
  const span = tracer.startSpan(`HTTP ${req.method} ${req.path}`);

  res.on('finish', () => {
    span.setAttribute('http.status_code', res.statusCode);
    span.end();
  });

  next();
});
```

## Docker Compose Monitoring Stack

```yaml
version: '3.8'

services:
  # Application
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - JAEGER_ENDPOINT=http://jaeger:14268/api/traces
      - LOKI_URL=http://loki:3100
    depends_on:
      - prometheus
      - loki
      - jaeger

  # Prometheus (Metrics)
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  # Grafana (Dashboards)
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
    depends_on:
      - prometheus
      - loki

  # Loki (Logs)
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - loki-data:/loki
    command: -config.file=/etc/loki/local-config.yaml

  # Promtail (Log collector)
  promtail:
    image: grafana/promtail:latest
    volumes:
      - /var/log:/var/log
      - ./promtail-config.yml:/etc/promtail/config.yml
    command: -config.file=/etc/promtail/config.yml

  # Jaeger (Traces)
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # UI
      - "14268:14268"  # Collector HTTP
    environment:
      - COLLECTOR_ZIPKIN_HOST_PORT=:9411

  # Alertmanager (Alerts)
  alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'

volumes:
  prometheus-data:
  grafana-data:
  loki-data:
```

### prometheus.yml

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - '/etc/prometheus/rules/*.yml'

scrape_configs:
  - job_name: 'app'
    static_configs:
      - targets: ['app:3000']

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

## Alerting Rules

### prometheus-rules.yml

```yaml
groups:
  - name: app_alerts
    interval: 30s
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: rate(http_requests_total{status_code=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} requests/second"

      # High response time
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time"
          description: "95th percentile response time is {{ $value }}s"

      # High memory usage
      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value | humanizePercentage }}"

      # Service down
      - alert: ServiceDown
        expr: up{job="app"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
          description: "{{ $labels.job }} has been down for more than 1 minute"
```

### alertmanager.yml

```yaml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'default'

  routes:
    - match:
        severity: critical
      receiver: 'critical'
      continue: true

    - match:
        severity: warning
      receiver: 'warning'

receivers:
  - name: 'default'
    email_configs:
      - to: 'team@example.com'
        from: 'alerts@example.com'
        smarthost: 'smtp.gmail.com:587'
        auth_username: 'alerts@example.com'
        auth_password: 'password'

  - name: 'critical'
    pagerduty_configs:
      - service_key: 'your-pagerduty-key'

  - name: 'warning'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#alerts'
        title: 'Warning Alert'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

## Health Checks

### HTTP Health Endpoint

```javascript
// Node.js
app.get('/health', async (req, res) => {
  const health = {
    uptime: process.uptime(),
    timestamp: Date.now(),
    status: 'OK',
    checks: {}
  };

  try {
    // Check database
    await db.ping();
    health.checks.database = { status: 'OK' };
  } catch (error) {
    health.checks.database = {
      status: 'ERROR',
      message: error.message
    };
    health.status = 'ERROR';
  }

  try {
    // Check Redis
    await redis.ping();
    health.checks.redis = { status: 'OK' };
  } catch (error) {
    health.checks.redis = {
      status: 'ERROR',
      message: error.message
    };
    health.status = 'ERROR';
  }

  const statusCode = health.status === 'OK' ? 200 : 503;
  res.status(statusCode).json(health);
});

// Readiness check
app.get('/ready', async (req, res) => {
  // Check if app is ready to receive traffic
  if (isReady) {
    res.status(200).send('Ready');
  } else {
    res.status(503).send('Not ready');
  }
});

// Liveness check
app.get('/live', (req, res) => {
  // Simple check if process is alive
  res.status(200).send('Alive');
});
```

## Grafana Dashboards

### Dashboard JSON (HTTP Metrics)

```json
{
  "dashboard": {
    "title": "HTTP Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status_code=~\"5..\"}[5m])"
          }
        ]
      },
      {
        "title": "Response Time (p95)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "Active Connections",
        "type": "stat",
        "targets": [
          {
            "expr": "active_connections"
          }
        ]
      }
    ]
  }
}
```

## Best Practices

### Logging Best Practices

✅ Use structured logging (JSON)
✅ Include contextual information (user ID, request ID, etc.)
✅ Set appropriate log levels
✅ Avoid logging sensitive data (passwords, tokens)
✅ Use correlation IDs for distributed tracing
✅ Log errors with stack traces
✅ Aggregate logs centrally
✅ Set up log rotation

### Metrics Best Practices

✅ Use appropriate metric types (counter, gauge, histogram)
✅ Include relevant labels (but not too many)
✅ Use consistent naming conventions
✅ Avoid high-cardinality labels (e.g., user IDs)
✅ Set up dashboards for key metrics
✅ Define SLIs and SLOs
✅ Monitor the four golden signals:
  - Latency
  - Traffic
  - Errors
  - Saturation

### Alerting Best Practices

✅ Alert on symptoms, not causes
✅ Set meaningful thresholds
✅ Avoid alert fatigue (too many alerts)
✅ Include actionable context in alerts
✅ Route alerts appropriately by severity
✅ Use escalation policies
✅ Document runbooks for common alerts
✅ Review and tune alerts regularly

## Observability Checklist

### Application Level

- [ ] Structured logging implemented
- [ ] Request IDs for correlation
- [ ] Metrics endpoints exposed
- [ ] Health checks configured
- [ ] Error tracking (Sentry, Rollbar)
- [ ] Performance monitoring (APM)

### Infrastructure Level

- [ ] Prometheus scraping configured
- [ ] Grafana dashboards created
- [ ] Alerting rules defined
- [ ] Log aggregation (Loki, ELK)
- [ ] Distributed tracing (Jaeger)
- [ ] Resource monitoring (CPU, memory, disk)

### Operations Level

- [ ] On-call rotation defined
- [ ] Runbooks documented
- [ ] Incident response process
- [ ] Post-mortem template
- [ ] SLIs and SLOs defined
- [ ] Alert escalation policies

## Quick Start

### 1. Basic Logging (5 minutes)

```bash
npm install winston
# Add structured logging to app
```

### 2. Add Metrics (10 minutes)

```bash
npm install prom-client
# Add metrics endpoint
# Configure Prometheus scraping
```

### 3. Deploy Monitoring Stack (15 minutes)

```bash
# Use docker-compose.yml above
docker-compose up -d
```

### 4. Create Dashboard (10 minutes)

- Access Grafana at http://localhost:3001
- Add Prometheus datasource
- Import dashboard or create custom

### 5. Set Up Alerts (15 minutes)

- Define alerting rules in Prometheus
- Configure Alertmanager
- Test alert delivery

## Tools Comparison

| Tool | Purpose | Best For |
|------|---------|----------|
| Prometheus | Metrics | Time-series data, alerting |
| Grafana | Visualization | Dashboards, multiple datasources |
| Loki | Logs | Log aggregation, Grafana integration |
| ELK Stack | Logs | Advanced search, large scale |
| Jaeger | Traces | Distributed tracing |
| OpenTelemetry | All | Vendor-neutral observability |
| Datadog | All | Managed solution, easy setup |
| New Relic | APM | Application performance monitoring |

## Resources

- Prometheus: https://prometheus.io/
- Grafana: https://grafana.com/
- OpenTelemetry: https://opentelemetry.io/
- Jaeger: https://www.jaegertracing.io/
- Loki: https://grafana.com/oss/loki/
- Google SRE Book: https://sre.google/books/
