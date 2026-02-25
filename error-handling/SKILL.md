---
name: error-handling
description: Error handling patterns and strategies covering custom error hierarchies, Result types, error boundaries, retry logic, circuit breakers, graceful degradation, error logging, user-friendly messages, and production error management across TypeScript, Python, Go, and Rust.
---

# Error Handling Patterns

This skill should be used when designing error handling strategies for applications. It covers custom error types, retry logic, circuit breakers, and production error patterns across languages.

## When to Use This Skill

Use this skill when you need to:

- Design error hierarchies and custom error types
- Implement retry logic with backoff
- Build circuit breaker patterns
- Create user-friendly error messages
- Set up error logging and monitoring
- Handle errors in async/concurrent code

## TypeScript Error Patterns

```typescript
// Custom error hierarchy
class AppError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode: number = 500,
    public readonly isOperational: boolean = true,
  ) {
    super(message);
    this.name = this.constructor.name;
  }
}

class NotFoundError extends AppError {
  constructor(resource: string, id: string) {
    super(`${resource} with id '${id}' not found`, "NOT_FOUND", 404);
  }
}

class ValidationError extends AppError {
  constructor(public readonly errors: Record<string, string[]>) {
    super("Validation failed", "VALIDATION_ERROR", 400);
  }
}

class ConflictError extends AppError {
  constructor(message: string) {
    super(message, "CONFLICT", 409);
  }
}

class RateLimitError extends AppError {
  constructor(public readonly retryAfter: number) {
    super("Rate limit exceeded", "RATE_LIMITED", 429);
  }
}
```

## Result Type Pattern (TypeScript)

```typescript
// Avoid exceptions for expected failures
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

function ok<T>(value: T): Result<T, never> {
  return { ok: true, value };
}

function err<E>(error: E): Result<never, E> {
  return { ok: false, error };
}

// Usage
async function parseConfig(path: string): Promise<Result<Config, string>> {
  try {
    const raw = await fs.readFile(path, "utf-8");
    const config = JSON.parse(raw);
    if (!config.apiKey) return err("Missing apiKey in config");
    return ok(config as Config);
  } catch {
    return err(`Failed to read config from ${path}`);
  }
}

const result = await parseConfig("./config.json");
if (!result.ok) {
  console.error(result.error);
  process.exit(1);
}
// result.value is typed as Config
```

## Retry with Exponential Backoff

```typescript
interface RetryOptions {
  maxAttempts: number;
  baseDelay: number;
  maxDelay: number;
  retryOn?: (error: unknown) => boolean;
}

async function withRetry<T>(
  fn: () => Promise<T>,
  options: RetryOptions,
): Promise<T> {
  const { maxAttempts, baseDelay, maxDelay, retryOn } = options;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (attempt === maxAttempts) throw error;
      if (retryOn && !retryOn(error)) throw error;

      const delay = Math.min(
        baseDelay * Math.pow(2, attempt - 1) + Math.random() * 1000,
        maxDelay,
      );
      await new Promise((r) => setTimeout(r, delay));
    }
  }
  throw new Error("Unreachable");
}

// Usage
const data = await withRetry(() => fetch("https://api.example.com/data").then(r => r.json()), {
  maxAttempts: 3,
  baseDelay: 1000,
  maxDelay: 10000,
  retryOn: (err) => err instanceof Error && err.message.includes("ECONNRESET"),
});
```

## Circuit Breaker

```typescript
class CircuitBreaker {
  private failures = 0;
  private lastFailure = 0;
  private state: "closed" | "open" | "half-open" = "closed";

  constructor(
    private readonly threshold: number = 5,
    private readonly resetTimeout: number = 30000,
  ) {}

  async call<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state === "open") {
      if (Date.now() - this.lastFailure > this.resetTimeout) {
        this.state = "half-open";
      } else {
        throw new Error("Circuit breaker is open");
      }
    }

    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  private onSuccess() {
    this.failures = 0;
    this.state = "closed";
  }

  private onFailure() {
    this.failures++;
    this.lastFailure = Date.now();
    if (this.failures >= this.threshold) {
      this.state = "open";
    }
  }
}

// Usage
const apiBreaker = new CircuitBreaker(5, 30000);
const result = await apiBreaker.call(() => fetchFromExternalAPI());
```

## Python Error Patterns

```python
from dataclasses import dataclass
from typing import TypeVar, Generic

T = TypeVar("T")

@dataclass
class AppError(Exception):
    message: str
    code: str
    status_code: int = 500

class NotFoundError(AppError):
    def __init__(self, resource: str, id: str):
        super().__init__(f"{resource} '{id}' not found", "NOT_FOUND", 404)

class ValidationError(AppError):
    def __init__(self, errors: dict[str, list[str]]):
        self.errors = errors
        super().__init__("Validation failed", "VALIDATION_ERROR", 400)

# Result pattern
@dataclass
class Ok(Generic[T]):
    value: T
    ok: bool = True

@dataclass
class Err:
    error: str
    ok: bool = False

Result = Ok[T] | Err

def divide(a: float, b: float) -> Result:
    if b == 0:
        return Err("Division by zero")
    return Ok(a / b)
```

## Go Error Patterns

```go
// Custom error types
type AppError struct {
    Code    string `json:"code"`
    Message string `json:"message"`
    Err     error  `json:"-"`
}

func (e *AppError) Error() string { return e.Message }
func (e *AppError) Unwrap() error { return e.Err }

func NewNotFound(resource, id string) *AppError {
    return &AppError{Code: "NOT_FOUND", Message: fmt.Sprintf("%s '%s' not found", resource, id)}
}

// Wrap errors with context
func (s *UserService) GetUser(id string) (*User, error) {
    user, err := s.repo.FindByID(id)
    if err != nil {
        return nil, fmt.Errorf("GetUser(%s): %w", id, err)
    }
    if user == nil {
        return nil, NewNotFound("user", id)
    }
    return user, nil
}

// Check error types
var appErr *AppError
if errors.As(err, &appErr) && appErr.Code == "NOT_FOUND" {
    // Handle not found
}
```

## React Error Boundary

```typescript
import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  fallback: ReactNode | ((error: Error, reset: () => void) => ReactNode);
  onError?: (error: Error, info: ErrorInfo) => void;
  children: ReactNode;
}

interface State {
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    this.props.onError?.(error, info);
  }

  reset = () => this.setState({ error: null });

  render() {
    if (this.state.error) {
      const { fallback } = this.props;
      return typeof fallback === "function"
        ? fallback(this.state.error, this.reset)
        : fallback;
    }
    return this.props.children;
  }
}

// Usage
<ErrorBoundary
  fallback={(error, reset) => (
    <div>
      <p>Something went wrong: {error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  )}
  onError={(error) => reportToSentry(error)}
>
  <App />
</ErrorBoundary>
```

## Error Logging Best Practices

```typescript
// Structured error logging
function logError(error: unknown, context: Record<string, unknown> = {}) {
  const errorInfo = {
    timestamp: new Date().toISOString(),
    message: error instanceof Error ? error.message : String(error),
    stack: error instanceof Error ? error.stack : undefined,
    code: error instanceof AppError ? error.code : "UNKNOWN",
    ...context,
  };

  // Development: console
  if (process.env.NODE_ENV === "development") {
    console.error(errorInfo);
    return;
  }

  // Production: structured JSON for log aggregation
  console.error(JSON.stringify(errorInfo));
}
```

## Additional Resources

- Error Handling in Node.js: https://www.joyent.com/node-js/production/design/errors
- Go Error Handling: https://go.dev/blog/error-handling-and-go
- React Error Boundaries: https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary
