---
name: logging-structured
description: Structured logging patterns covering JSON logging, log levels, context propagation, request tracing, correlation IDs, log aggregation, Winston/Pino for Node.js, Python logging, and production logging best practices for observability.
---

# Structured Logging

This skill should be used when setting up logging infrastructure for applications. It covers structured JSON logging, context propagation, and production logging patterns.

## When to Use This Skill

Use this skill when you need to:

- Set up structured logging for applications
- Implement request tracing with correlation IDs
- Configure log levels and filtering
- Integrate with log aggregation services
- Add context to logs for debugging

## Log Levels

```
LEVEL     WHEN TO USE                              PRODUCTION DEFAULT
─────     ────────────────────────────────         ──────────────────
fatal     App is crashing, unrecoverable           Always on
error     Operation failed, needs attention         Always on
warn      Degraded behavior, potential issue        Always on
info      Significant business events              Usually on
debug     Detailed diagnostic information          Off (enable per-request)
trace     Very detailed, step-by-step execution    Off (rarely needed)
```

## Node.js with Pino (Fastest)

```typescript
import pino from "pino";

// Base logger
const logger = pino({
  level: process.env.LOG_LEVEL ?? "info",
  formatters: {
    level: (label) => ({ level: label }),
  },
  timestamp: pino.stdTimeFunctions.isoTime,
  redact: {
    paths: ["password", "token", "authorization", "cookie", "*.password"],
    censor: "[REDACTED]",
  },
});

// Child logger with context
const requestLogger = logger.child({
  service: "api",
  version: process.env.APP_VERSION,
});

// Usage
requestLogger.info({ userId: "123", action: "login" }, "User logged in");
// Output: {"level":"info","time":"2024-01-15T10:30:00.000Z","service":"api","userId":"123","action":"login","msg":"User logged in"}

requestLogger.error({ err: error, orderId: "456" }, "Payment processing failed");
```

## Express Middleware (Request Logging)

```typescript
import { randomUUID } from "crypto";
import pino from "pino";
import pinoHttp from "pino-http";

const httpLogger = pinoHttp({
  logger: pino({ level: "info" }),
  genReqId: (req) => req.headers["x-request-id"] ?? randomUUID(),
  customProps: (req) => ({
    correlationId: req.id,
    userAgent: req.headers["user-agent"],
  }),
  customLogLevel: (_req, res, err) => {
    if (res.statusCode >= 500 || err) return "error";
    if (res.statusCode >= 400) return "warn";
    return "info";
  },
  customSuccessMessage: (req, res) =>
    `${req.method} ${req.url} ${res.statusCode}`,
  redact: ["req.headers.authorization", "req.headers.cookie"],
  serializers: {
    req: (req) => ({
      method: req.method,
      url: req.url,
      query: req.query,
    }),
    res: (res) => ({
      statusCode: res.statusCode,
    }),
  },
});

app.use(httpLogger);

// Access logger in route handlers
app.get("/api/users/:id", (req, res) => {
  req.log.info({ userId: req.params.id }, "Fetching user");
  // ...
});
```

## Correlation ID Pattern

```typescript
import { AsyncLocalStorage } from "async_hooks";

interface RequestContext {
  correlationId: string;
  userId?: string;
  traceId?: string;
}

const asyncLocalStorage = new AsyncLocalStorage<RequestContext>();

// Middleware to set context
function contextMiddleware(req: Request, _res: Response, next: NextFunction) {
  const context: RequestContext = {
    correlationId: req.headers["x-correlation-id"] as string ?? randomUUID(),
    userId: req.user?.id,
  };
  asyncLocalStorage.run(context, () => next());
}

// Logger automatically includes context
function createContextLogger(baseLogger: pino.Logger) {
  return new Proxy(baseLogger, {
    get(target, prop) {
      if (["info", "warn", "error", "debug"].includes(prop as string)) {
        return (obj: object, msg?: string) => {
          const ctx = asyncLocalStorage.getStore();
          const enriched = ctx ? { ...ctx, ...obj } : obj;
          return (target as any)[prop](enriched, msg);
        };
      }
      return (target as any)[prop];
    },
  });
}
```

## Python Structured Logging

```python
import logging
import json
from datetime import datetime, timezone

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname.lower(),
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        # Add extra fields
        for key in record.__dict__:
            if key not in logging.LogRecord.__dict__ and key not in ("message", "args"):
                log_data[key] = getattr(record, key)
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

# Setup
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger = logging.getLogger("app")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Usage
logger.info("User created", extra={"user_id": "123", "email": "user@example.com"})
logger.error("Payment failed", extra={"order_id": "456", "amount": 99.99}, exc_info=True)
```

## What to Log

```
ALWAYS LOG:
  - Request/response (method, path, status, duration)
  - Authentication events (login, logout, failed attempts)
  - Business events (order placed, payment processed)
  - Errors with full context
  - External service calls (API, database, cache)

NEVER LOG:
  - Passwords or secrets
  - Full credit card numbers
  - Personal health information
  - Session tokens or API keys
  - Raw request bodies with sensitive data

CONTEXT TO INCLUDE:
  - Correlation/request ID (for tracing)
  - User ID (for user-scoped debugging)
  - Service name and version
  - Environment (dev/staging/prod)
  - Duration of operations
  - Input parameters (sanitized)
```

## Log Aggregation Integration

```typescript
// Pino transport for production (stdout → log aggregator)
// In production, pipe stdout to your log aggregator:
// node app.js | npx pino-datadog-transport
// node app.js | npx pino-elasticsearch

// For development, pretty-print:
// node app.js | npx pino-pretty

// Docker/Kubernetes: stdout goes to container log driver
// which forwards to CloudWatch, Datadog, Elastic, etc.
```

## Additional Resources

- Pino (Node.js): https://getpino.io/
- Winston (Node.js): https://github.com/winstonjs/winston
- Python Logging: https://docs.python.org/3/library/logging.html
- structlog (Python): https://www.structlog.org/
- 12 Factor App Logs: https://12factor.net/logs
