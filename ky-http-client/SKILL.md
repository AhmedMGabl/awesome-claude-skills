---
name: ky-http-client
description: Ky HTTP client patterns covering request methods, hooks (beforeRequest, afterResponse), retry logic, timeout configuration, JSON parsing, custom instances, error handling, and migration from axios or fetch for modern browser and Node.js applications.
---

# Ky HTTP Client

This skill should be used when making HTTP requests with Ky. It covers request configuration, hooks, retry logic, error handling, and custom instances.

## When to Use This Skill

Use this skill when you need to:

- Make HTTP requests with a modern, lightweight client
- Add request/response hooks for auth tokens or logging
- Configure automatic retries with backoff
- Handle errors with typed responses
- Migrate from axios or raw fetch

## Basic Usage

```typescript
import ky from "ky";

// GET request
const users = await ky.get("https://api.example.com/users").json<User[]>();

// POST request
const newUser = await ky
  .post("https://api.example.com/users", {
    json: { name: "Alice", email: "alice@example.com" },
  })
  .json<User>();

// PUT request
const updated = await ky
  .put("https://api.example.com/users/1", {
    json: { name: "Alice Updated" },
  })
  .json<User>();

// DELETE request
await ky.delete("https://api.example.com/users/1");

// With search params
const results = await ky
  .get("https://api.example.com/search", {
    searchParams: { q: "typescript", page: 1, limit: 20 },
  })
  .json<SearchResults>();
```

## Custom Instance

```typescript
import ky from "ky";

const api = ky.create({
  prefixUrl: "https://api.example.com",
  timeout: 30000,
  retry: { limit: 3, methods: ["get"], statusCodes: [408, 429, 500, 502, 503] },
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
  hooks: {
    beforeRequest: [
      (request) => {
        const token = localStorage.getItem("auth-token");
        if (token) {
          request.headers.set("Authorization", `Bearer ${token}`);
        }
      },
    ],
    afterResponse: [
      async (_request, _options, response) => {
        if (response.status === 401) {
          // Refresh token and retry
          const newToken = await refreshToken();
          localStorage.setItem("auth-token", newToken);
        }
      },
    ],
    beforeError: [
      async (error) => {
        const { response } = error;
        if (response) {
          const body = await response.json();
          error.message = body.message || error.message;
        }
        return error;
      },
    ],
  },
});

// Usage with the custom instance
const users = await api.get("users").json<User[]>();
const user = await api.post("users", { json: { name: "Bob" } }).json<User>();
```

## Error Handling

```typescript
import ky, { HTTPError, TimeoutError } from "ky";

try {
  const data = await ky.get("https://api.example.com/data").json();
} catch (error) {
  if (error instanceof HTTPError) {
    const status = error.response.status;
    const body = await error.response.json();
    console.error(`HTTP ${status}:`, body.message);
  } else if (error instanceof TimeoutError) {
    console.error("Request timed out");
  } else {
    console.error("Network error:", error);
  }
}
```

## Retry Configuration

```typescript
import ky from "ky";

const api = ky.create({
  retry: {
    limit: 3,
    methods: ["get", "put", "delete"],
    statusCodes: [408, 413, 429, 500, 502, 503, 504],
    afterStatusCodes: [413, 429],
    maxRetryAfter: 30000,
    backoffLimit: 10000,
  },
});
```

## Streaming and Progress

```typescript
import ky from "ky";

// Download with progress
const response = await ky.get("https://example.com/large-file");
const reader = response.body?.getReader();
const contentLength = Number(response.headers.get("content-length"));

let received = 0;
const chunks: Uint8Array[] = [];

while (reader) {
  const { done, value } = await reader.read();
  if (done) break;
  chunks.push(value);
  received += value.length;
  console.log(`Progress: ${((received / contentLength) * 100).toFixed(1)}%`);
}
```

## Additional Resources

- Ky docs: https://github.com/sindresorhus/ky
- API reference: https://github.com/sindresorhus/ky#api
