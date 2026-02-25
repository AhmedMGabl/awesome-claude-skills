---
name: grpc-apis
description: This skill should be used when building gRPC APIs with TypeScript and Node.js, covering Protocol Buffers (proto3) definitions, server and client implementation with nice-grpc, all four RPC types (unary, server streaming, client streaming, bidirectional), gRPC error handling with status codes, interceptors and middleware, metadata and headers, health checks, gRPC-Web for browser clients, and the Connect protocol for HTTP-compatible gRPC.
---

# gRPC API Development

This skill should be used when building gRPC APIs with TypeScript and Node.js. It covers end-to-end service development from proto definitions through server and client implementation, including all streaming patterns, production-ready error handling, interceptors, health checks, and browser-compatible transports.

## When to Use This Skill

Use this skill when you need to:

- Define gRPC services with Protocol Buffers (proto3)
- Implement gRPC servers in Node.js/TypeScript
- Build typed gRPC clients with deadline and retry support
- Handle all four RPC types: unary, server streaming, client streaming, bidirectional
- Map errors to gRPC status codes with rich error details
- Add interceptors for authentication, logging, and tracing
- Pass metadata and headers between client and server
- Implement gRPC health checking protocol
- Serve gRPC to browsers via gRPC-Web or Connect protocol
- Generate TypeScript types from proto definitions

## Project Setup

```bash
# Install dependencies
npm install nice-grpc nice-grpc-server-health nice-grpc-client-middleware-deadline
npm install @grpc/proto-loader @grpc/grpc-js google-protobuf
npm install -D ts-proto protobufjs @bufbuild/protoc-gen-es

# Project structure
src/
├── proto/
│   ├── buf.yaml                # Buf configuration
│   ├── buf.gen.yaml            # Code generation config
│   └── myservice/
│       └── v1/
│           └── service.proto   # Service definition
├── gen/                        # Generated TypeScript code
├── server/
│   ├── index.ts                # Server entry point
│   ├── handlers/               # RPC handler implementations
│   └── interceptors/           # Server interceptors
├── client/
│   ├── index.ts                # Client factory
│   └── interceptors/           # Client middleware
└── shared/
    └── errors.ts               # Error utilities
```

## Protocol Buffers Definition

```protobuf
// proto/taskservice/v1/task.proto
syntax = "proto3";

package taskservice.v1;

import "google/protobuf/timestamp.proto";
import "google/protobuf/empty.proto";
import "google/protobuf/field_mask.proto";

service TaskService {
  // Unary RPCs
  rpc CreateTask(CreateTaskRequest) returns (Task);
  rpc GetTask(GetTaskRequest) returns (Task);
  rpc UpdateTask(UpdateTaskRequest) returns (Task);
  rpc DeleteTask(DeleteTaskRequest) returns (google.protobuf.Empty);

  // Server streaming — returns tasks matching a filter
  rpc WatchTasks(WatchTasksRequest) returns (stream TaskEvent);

  // Client streaming — upload multiple tasks in a batch
  rpc BatchCreateTasks(stream CreateTaskRequest) returns (BatchCreateTasksResponse);

  // Bidirectional streaming — collaborative task editing
  rpc CollaborateOnTask(stream TaskAction) returns (stream TaskUpdate);
}

// Enums
enum TaskStatus {
  TASK_STATUS_UNSPECIFIED = 0;
  TASK_STATUS_PENDING = 1;
  TASK_STATUS_IN_PROGRESS = 2;
  TASK_STATUS_COMPLETED = 3;
  TASK_STATUS_CANCELLED = 4;
}

enum Priority {
  PRIORITY_UNSPECIFIED = 0;
  PRIORITY_LOW = 1;
  PRIORITY_MEDIUM = 2;
  PRIORITY_HIGH = 3;
  PRIORITY_CRITICAL = 4;
}

// Messages
message Task {
  string id = 1;
  string title = 2;
  string description = 3;
  TaskStatus status = 4;
  Priority priority = 5;
  string assignee_id = 6;
  repeated string labels = 7;
  google.protobuf.Timestamp created_at = 8;
  google.protobuf.Timestamp updated_at = 9;
  google.protobuf.Timestamp due_date = 10;
}

message CreateTaskRequest {
  string title = 1;
  string description = 2;
  Priority priority = 3;
  string assignee_id = 4;
  repeated string labels = 5;
  google.protobuf.Timestamp due_date = 6;
}

message GetTaskRequest {
  string id = 1;
}

message UpdateTaskRequest {
  Task task = 1;
  google.protobuf.FieldMask update_mask = 2;
}

message DeleteTaskRequest {
  string id = 1;
}

message WatchTasksRequest {
  string project_id = 1;
  repeated TaskStatus statuses = 2;
}

message TaskEvent {
  enum EventType {
    EVENT_TYPE_UNSPECIFIED = 0;
    EVENT_TYPE_CREATED = 1;
    EVENT_TYPE_UPDATED = 2;
    EVENT_TYPE_DELETED = 3;
  }
  EventType type = 1;
  Task task = 2;
  google.protobuf.Timestamp occurred_at = 3;
}

message BatchCreateTasksResponse {
  repeated Task tasks = 1;
  int32 created_count = 2;
  int32 failed_count = 3;
}

message TaskAction {
  string task_id = 1;
  oneof action {
    string update_title = 2;
    string update_description = 3;
    TaskStatus update_status = 4;
    string add_label = 5;
  }
}

message TaskUpdate {
  string task_id = 1;
  string updated_by = 2;
  string field = 3;
  string old_value = 4;
  string new_value = 5;
  google.protobuf.Timestamp updated_at = 6;
}
```

## Code Generation with Buf

```yaml
# proto/buf.yaml
version: v2
lint:
  use:
    - STANDARD
breaking:
  use:
    - FILE
```

```yaml
# proto/buf.gen.yaml
version: v2
plugins:
  - local: protoc-gen-ts_proto
    out: ../gen
    opt:
      - outputServices=nice-grpc
      - outputServices=generic-definitions
      - useExactTypes=false
      - esModuleInterop=true
      - env=node
```

```bash
# Generate TypeScript code from proto definitions
npx buf generate proto

# Alternatively, with protoc directly
protoc \
  --plugin=protoc-gen-ts_proto=./node_modules/.bin/protoc-gen-ts_proto \
  --ts_proto_out=./src/gen \
  --ts_proto_opt=outputServices=nice-grpc,outputServices=generic-definitions,useExactTypes=false,esModuleInterop=true \
  -I./proto \
  proto/taskservice/v1/task.proto
```

## Server Implementation

### Unary RPC Handlers

```typescript
// src/server/handlers/task-handlers.ts
import { ServerError, Status } from "nice-grpc";
import type { CallContext } from "nice-grpc";
import type {
  TaskServiceImplementation,
  CreateTaskRequest,
  GetTaskRequest,
  UpdateTaskRequest,
  DeleteTaskRequest,
  Task,
} from "../../gen/taskservice/v1/task.js";
import { TaskStore } from "../store.js";

const store = new TaskStore();

export const taskHandlers: TaskServiceImplementation = {
  async createTask(
    request: CreateTaskRequest,
    context: CallContext,
  ): Promise<Task> {
    if (!request.title) {
      throw new ServerError(
        Status.INVALID_ARGUMENT,
        "title is required",
      );
    }

    const userId = context.metadata.get("x-user-id");
    if (!userId) {
      throw new ServerError(Status.UNAUTHENTICATED, "missing user identity");
    }

    const task = await store.create({
      ...request,
      createdBy: userId,
    });

    // Set response metadata
    context.header.set("x-task-id", task.id);

    return task;
  },

  async getTask(
    request: GetTaskRequest,
    context: CallContext,
  ): Promise<Task> {
    if (!request.id) {
      throw new ServerError(Status.INVALID_ARGUMENT, "id is required");
    }

    const task = await store.findById(request.id);
    if (!task) {
      throw new ServerError(
        Status.NOT_FOUND,
        `task ${request.id} not found`,
      );
    }

    return task;
  },

  async updateTask(
    request: UpdateTaskRequest,
    context: CallContext,
  ): Promise<Task> {
    if (!request.task?.id) {
      throw new ServerError(Status.INVALID_ARGUMENT, "task.id is required");
    }

    const existing = await store.findById(request.task.id);
    if (!existing) {
      throw new ServerError(
        Status.NOT_FOUND,
        `task ${request.task.id} not found`,
      );
    }

    // Apply field mask to update only specified fields
    const fieldsToUpdate = request.updateMask?.paths ?? [];
    const updated = await store.update(
      request.task.id,
      request.task,
      fieldsToUpdate,
    );

    return updated;
  },

  async deleteTask(
    request: DeleteTaskRequest,
    context: CallContext,
  ): Promise<{}> {
    if (!request.id) {
      throw new ServerError(Status.INVALID_ARGUMENT, "id is required");
    }

    const existed = await store.delete(request.id);
    if (!existed) {
      throw new ServerError(
        Status.NOT_FOUND,
        `task ${request.id} not found`,
      );
    }

    return {};
  },

  // Streaming handlers shown in next sections
  watchTasks: undefined as any,
  batchCreateTasks: undefined as any,
  collaborateOnTask: undefined as any,
};
```

### Server Streaming RPC

```typescript
// Server streaming — server sends a stream of events to the client
async *watchTasks(
  request: WatchTasksRequest,
  context: CallContext,
): AsyncIterable<TaskEvent> {
  if (!request.projectId) {
    throw new ServerError(
      Status.INVALID_ARGUMENT,
      "project_id is required",
    );
  }

  const statusFilter = new Set(request.statuses);

  // Create an event subscription for this project
  const events = store.subscribe(request.projectId);

  try {
    for await (const event of events) {
      // Check if client cancelled the stream
      context.signal.throwIfAborted();

      // Apply status filter
      if (statusFilter.size > 0 && !statusFilter.has(event.task.status)) {
        continue;
      }

      yield event;
    }
  } finally {
    events.unsubscribe();
  }
},
```

### Client Streaming RPC

```typescript
// Client streaming — client sends a stream of requests, server responds once
async batchCreateTasks(
  requests: AsyncIterable<CreateTaskRequest>,
  context: CallContext,
): Promise<BatchCreateTasksResponse> {
  const tasks: Task[] = [];
  let failedCount = 0;

  for await (const request of requests) {
    context.signal.throwIfAborted();

    if (!request.title) {
      failedCount++;
      continue;
    }

    const task = await store.create(request);
    tasks.push(task);
  }

  return {
    tasks,
    createdCount: tasks.length,
    failedCount,
  };
},
```

### Bidirectional Streaming RPC

```typescript
// Bidirectional streaming — both client and server stream simultaneously
async *collaborateOnTask(
  actions: AsyncIterable<TaskAction>,
  context: CallContext,
): AsyncIterable<TaskUpdate> {
  const userId = context.metadata.get("x-user-id") ?? "anonymous";

  for await (const action of actions) {
    context.signal.throwIfAborted();

    const task = await store.findById(action.taskId);
    if (!task) continue;

    let field = "";
    let oldValue = "";
    let newValue = "";

    if (action.updateTitle !== undefined) {
      field = "title";
      oldValue = task.title;
      newValue = action.updateTitle;
      await store.update(action.taskId, { title: action.updateTitle }, ["title"]);
    } else if (action.updateDescription !== undefined) {
      field = "description";
      oldValue = task.description;
      newValue = action.updateDescription;
      await store.update(action.taskId, { description: action.updateDescription }, ["description"]);
    } else if (action.updateStatus !== undefined) {
      field = "status";
      oldValue = String(task.status);
      newValue = String(action.updateStatus);
      await store.update(action.taskId, { status: action.updateStatus }, ["status"]);
    } else if (action.addLabel !== undefined) {
      field = "labels";
      oldValue = task.labels.join(",");
      newValue = [...task.labels, action.addLabel].join(",");
      await store.addLabel(action.taskId, action.addLabel);
    }

    yield {
      taskId: action.taskId,
      updatedBy: userId,
      field,
      oldValue,
      newValue,
      updatedAt: { seconds: BigInt(Math.floor(Date.now() / 1000)), nanos: 0 },
    };
  }
},
```

### Server Entry Point

```typescript
// src/server/index.ts
import { createServer } from "nice-grpc";
import { HealthDefinition, HealthServiceImpl } from "nice-grpc-server-health";
import {
  TaskServiceDefinition,
} from "../gen/taskservice/v1/task.js";
import { taskHandlers } from "./handlers/task-handlers.js";
import { loggingInterceptor } from "./interceptors/logging.js";
import { authInterceptor } from "./interceptors/auth.js";

const PORT = process.env.GRPC_PORT ?? "50051";

function startServer(): void {
  const server = createServer();

  // Register interceptors (applied in order)
  server.with(loggingInterceptor).with(authInterceptor);

  // Register service handlers
  server.add(TaskServiceDefinition, taskHandlers);

  // Register health check service
  const healthImpl = HealthServiceImpl({
    "taskservice.v1.TaskService": "SERVING",
  });
  server.add(HealthDefinition, healthImpl);

  server.listen(`0.0.0.0:${PORT}`);
  console.log(`gRPC server listening on port ${PORT}`);

  // Graceful shutdown
  function shutdown(): void {
    console.log("Shutting down gRPC server...");
    server.shutdown().then(() => {
      console.log("Server stopped");
      process.exit(0);
    });
  }

  process.on("SIGTERM", shutdown);
  process.on("SIGINT", shutdown);
}

startServer();
```

## Client Implementation

### Client Factory

```typescript
// src/client/index.ts
import { createChannel, createClient, Metadata } from "nice-grpc";
import { deadlineMiddleware } from "nice-grpc-client-middleware-deadline";
import {
  TaskServiceDefinition,
  type TaskServiceClient,
} from "../gen/taskservice/v1/task.js";
import { retryMiddleware } from "./interceptors/retry.js";
import { authMiddleware } from "./interceptors/auth.js";

interface ClientOptions {
  address: string;
  defaultDeadlineMs?: number;
  token?: string;
}

function createTaskClient(options: ClientOptions): TaskServiceClient {
  const channel = createChannel(options.address);

  const client = createClient(
    TaskServiceDefinition,
    channel,
    {
      "*": {
        middlewares: [
          deadlineMiddleware,
          retryMiddleware,
          authMiddleware(options.token),
        ],
        deadline: options.defaultDeadlineMs
          ? Date.now() + options.defaultDeadlineMs
          : undefined,
      },
    },
  );

  return client;
}

export { createTaskClient };
```

### Unary Client Calls

```typescript
// src/client/usage.ts
import { Metadata } from "nice-grpc";
import { createTaskClient } from "./index.js";

const client = createTaskClient({
  address: "localhost:50051",
  defaultDeadlineMs: 5000,
  token: "my-auth-token",
});

// Create a task
async function createTask(): Promise<void> {
  const task = await client.createTask({
    title: "Implement gRPC service",
    description: "Build the task management API",
    priority: 3, // HIGH
    assigneeId: "user-123",
    labels: ["backend", "grpc"],
    dueDate: { seconds: BigInt(Math.floor(Date.now() / 1000) + 86400), nanos: 0 },
  });

  console.log("Created task:", task.id);
}

// Get a task with custom deadline
async function getTask(id: string): Promise<void> {
  const task = await client.getTask(
    { id },
    { deadline: Date.now() + 2000 }, // 2 second deadline
  );

  console.log("Task:", task.title, "Status:", task.status);
}

// Update specific fields using field mask
async function updateTaskStatus(id: string): Promise<void> {
  const task = await client.updateTask({
    task: { id, status: 2 }, // IN_PROGRESS
    updateMask: { paths: ["status"] },
  });

  console.log("Updated task:", task.id, "to status:", task.status);
}

// Pass custom metadata
async function getTaskWithMetadata(id: string): Promise<void> {
  const metadata = new Metadata();
  metadata.set("x-request-id", crypto.randomUUID());
  metadata.set("x-user-id", "user-456");

  const task = await client.getTask({ id }, { metadata });
  console.log("Task:", task.title);
}
```

### Streaming Client Calls

```typescript
// Server streaming — consume a stream of events from the server
async function watchTaskUpdates(projectId: string): Promise<void> {
  const abortController = new AbortController();

  // Stop watching after 60 seconds
  setTimeout(() => abortController.abort(), 60_000);

  const stream = client.watchTasks(
    { projectId, statuses: [1, 2] }, // PENDING and IN_PROGRESS
    { signal: abortController.signal },
  );

  for await (const event of stream) {
    console.log(`Event: ${event.type}, Task: ${event.task?.title}`);
  }
}

// Client streaming — send a batch of tasks
async function batchCreate(): Promise<void> {
  async function* generateTasks() {
    const titles = ["Task A", "Task B", "Task C", "Task D"];
    for (const title of titles) {
      yield {
        title,
        description: `Auto-generated: ${title}`,
        priority: 2, // MEDIUM
        assigneeId: "",
        labels: ["batch"],
        dueDate: undefined,
      };
    }
  }

  const response = await client.batchCreateTasks(generateTasks());
  console.log(`Created: ${response.createdCount}, Failed: ${response.failedCount}`);
}

// Bidirectional streaming — send actions and receive updates simultaneously
async function collaborateOnTask(taskId: string): Promise<void> {
  const abortController = new AbortController();

  async function* generateActions() {
    yield {
      taskId,
      updateTitle: "Updated title",
      updateDescription: undefined,
      updateStatus: undefined,
      addLabel: undefined,
    };

    await new Promise((resolve) => setTimeout(resolve, 1000));

    yield {
      taskId,
      updateTitle: undefined,
      updateDescription: undefined,
      updateStatus: 2, // IN_PROGRESS
      addLabel: undefined,
    };

    await new Promise((resolve) => setTimeout(resolve, 500));

    yield {
      taskId,
      updateTitle: undefined,
      updateDescription: undefined,
      updateStatus: undefined,
      addLabel: "reviewed",
    };
  }

  const updates = client.collaborateOnTask(generateActions(), {
    signal: abortController.signal,
  });

  for await (const update of updates) {
    console.log(`${update.updatedBy} changed ${update.field}: ${update.oldValue} -> ${update.newValue}`);
  }
}
```

## Error Handling with Status Codes

### gRPC Status Code Reference

```
OK (0)                  — Success
CANCELLED (1)           — Cancelled by client
UNKNOWN (2)             — Unknown error (default for unmapped errors)
INVALID_ARGUMENT (3)    — Client sent invalid data
DEADLINE_EXCEEDED (4)   — Deadline expired before completion
NOT_FOUND (5)           — Requested resource does not exist
ALREADY_EXISTS (6)      — Resource already exists (conflict)
PERMISSION_DENIED (7)   — Caller lacks permission
RESOURCE_EXHAUSTED (8)  — Rate limit or quota exceeded
FAILED_PRECONDITION (9) — Operation rejected due to system state
ABORTED (10)            — Concurrency conflict (retry may succeed)
OUT_OF_RANGE (11)       — Value outside valid range
UNIMPLEMENTED (12)      — Method not implemented
INTERNAL (13)           — Internal server error
UNAVAILABLE (14)        — Service temporarily unavailable (retry)
DATA_LOSS (15)          — Unrecoverable data loss
UNAUTHENTICATED (16)    — Missing or invalid authentication
```

### Throwing Errors on the Server

```typescript
// src/shared/errors.ts
import { ServerError, Status } from "nice-grpc";

function notFound(resource: string, id: string): ServerError {
  return new ServerError(
    Status.NOT_FOUND,
    `${resource} with id '${id}' not found`,
  );
}

function invalidArgument(field: string, reason: string): ServerError {
  return new ServerError(
    Status.INVALID_ARGUMENT,
    `invalid ${field}: ${reason}`,
  );
}

function alreadyExists(resource: string, field: string, value: string): ServerError {
  return new ServerError(
    Status.ALREADY_EXISTS,
    `${resource} with ${field} '${value}' already exists`,
  );
}

function permissionDenied(action: string): ServerError {
  return new ServerError(
    Status.PERMISSION_DENIED,
    `not permitted to ${action}`,
  );
}

function resourceExhausted(limit: string): ServerError {
  return new ServerError(
    Status.RESOURCE_EXHAUSTED,
    `rate limit exceeded: ${limit}`,
  );
}

function failedPrecondition(reason: string): ServerError {
  return new ServerError(
    Status.FAILED_PRECONDITION,
    reason,
  );
}

export {
  notFound,
  invalidArgument,
  alreadyExists,
  permissionDenied,
  resourceExhausted,
  failedPrecondition,
};
```

### Handling Errors on the Client

```typescript
import { ClientError, Status } from "nice-grpc";

async function getTaskSafely(id: string): Promise<Task | null> {
  try {
    return await client.getTask({ id });
  } catch (error) {
    if (error instanceof ClientError) {
      switch (error.code) {
        case Status.NOT_FOUND:
          console.log(`Task ${id} not found`);
          return null;

        case Status.DEADLINE_EXCEEDED:
          console.log("Request timed out, retrying...");
          return client.getTask(
            { id },
            { deadline: Date.now() + 10000 },
          );

        case Status.UNAVAILABLE:
          console.log("Service unavailable, backing off...");
          await new Promise((resolve) => setTimeout(resolve, 2000));
          return client.getTask({ id });

        case Status.UNAUTHENTICATED:
          console.log("Authentication expired");
          throw error;

        case Status.PERMISSION_DENIED:
          console.log("Access denied for task", id);
          throw error;

        default:
          console.error(`Unexpected gRPC error: ${error.code} - ${error.message}`);
          throw error;
      }
    }
    throw error;
  }
}
```

## Interceptors and Middleware

### Server Interceptors

```typescript
// src/server/interceptors/logging.ts
import type { ServerMiddlewareCall, CallContext } from "nice-grpc";

async function* loggingInterceptor<Request, Response>(
  call: ServerMiddlewareCall<Request, Response>,
  context: CallContext,
): AsyncGenerator<Response, Response | void, undefined> {
  const start = Date.now();
  const method = call.method.path;
  const requestId = context.metadata.get("x-request-id") ?? "unknown";

  console.log(`[${requestId}] --> ${method}`);

  try {
    const result = yield* call.next(call.request, context);
    const duration = Date.now() - start;
    console.log(`[${requestId}] <-- ${method} OK (${duration}ms)`);
    return result;
  } catch (error) {
    const duration = Date.now() - start;
    console.error(`[${requestId}] <-- ${method} ERROR (${duration}ms):`, error);
    throw error;
  }
}

export { loggingInterceptor };
```

```typescript
// src/server/interceptors/auth.ts
import { ServerError, Status } from "nice-grpc";
import type { ServerMiddlewareCall, CallContext } from "nice-grpc";

// Methods that do not require authentication
const PUBLIC_METHODS = new Set([
  "/grpc.health.v1.Health/Check",
  "/grpc.health.v1.Health/Watch",
]);

async function* authInterceptor<Request, Response>(
  call: ServerMiddlewareCall<Request, Response>,
  context: CallContext,
): AsyncGenerator<Response, Response | void, undefined> {
  if (PUBLIC_METHODS.has(call.method.path)) {
    return yield* call.next(call.request, context);
  }

  const token = context.metadata.get("authorization");
  if (!token) {
    throw new ServerError(
      Status.UNAUTHENTICATED,
      "missing authorization metadata",
    );
  }

  const bearerToken = token.startsWith("Bearer ")
    ? token.slice(7)
    : token;

  const user = await verifyToken(bearerToken);
  if (!user) {
    throw new ServerError(
      Status.UNAUTHENTICATED,
      "invalid or expired token",
    );
  }

  // Make user info available to handlers via metadata
  context.metadata.set("x-user-id", user.id);
  context.metadata.set("x-user-role", user.role);

  return yield* call.next(call.request, context);
}

export { authInterceptor };
```

```typescript
// src/server/interceptors/rate-limit.ts
import { ServerError, Status } from "nice-grpc";
import type { ServerMiddlewareCall, CallContext } from "nice-grpc";

const REQUEST_COUNTS = new Map<string, { count: number; resetAt: number }>();
const MAX_REQUESTS = 100;
const WINDOW_MS = 60_000;

async function* rateLimitInterceptor<Request, Response>(
  call: ServerMiddlewareCall<Request, Response>,
  context: CallContext,
): AsyncGenerator<Response, Response | void, undefined> {
  const clientId = context.metadata.get("x-user-id")
    ?? context.peer
    ?? "unknown";

  const now = Date.now();
  const entry = REQUEST_COUNTS.get(clientId);

  if (entry && now < entry.resetAt) {
    if (entry.count >= MAX_REQUESTS) {
      const retryAfterSeconds = Math.ceil((entry.resetAt - now) / 1000);
      context.header.set("retry-after", String(retryAfterSeconds));
      throw new ServerError(
        Status.RESOURCE_EXHAUSTED,
        `rate limit exceeded, retry after ${retryAfterSeconds}s`,
      );
    }
    entry.count++;
  } else {
    REQUEST_COUNTS.set(clientId, { count: 1, resetAt: now + WINDOW_MS });
  }

  return yield* call.next(call.request, context);
}

export { rateLimitInterceptor };
```

### Client Middleware

```typescript
// src/client/interceptors/retry.ts
import { ClientError, Status } from "nice-grpc";
import type { ClientMiddlewareCall, CallOptions } from "nice-grpc";

const RETRYABLE_CODES = new Set([
  Status.UNAVAILABLE,
  Status.ABORTED,
  Status.DEADLINE_EXCEEDED,
]);

const MAX_RETRIES = 3;
const BASE_DELAY_MS = 100;

async function* retryMiddleware<Request, Response>(
  call: ClientMiddlewareCall<Request, Response>,
  options: CallOptions,
): AsyncGenerator<Response, Response | void, undefined> {
  let lastError: unknown;

  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    if (attempt > 0) {
      // Exponential backoff with jitter
      const delay = BASE_DELAY_MS * Math.pow(2, attempt - 1);
      const jitter = Math.random() * delay * 0.1;
      await new Promise((resolve) => setTimeout(resolve, delay + jitter));
    }

    try {
      return yield* call.next(call.request, options);
    } catch (error) {
      lastError = error;
      if (error instanceof ClientError && RETRYABLE_CODES.has(error.code)) {
        console.log(`Retry ${attempt + 1}/${MAX_RETRIES} for ${call.method.path}`);
        continue;
      }
      throw error;
    }
  }

  throw lastError;
}

export { retryMiddleware };
```

```typescript
// src/client/interceptors/auth.ts
import { Metadata } from "nice-grpc";
import type { ClientMiddlewareCall, CallOptions } from "nice-grpc";

function authMiddleware(token?: string) {
  return async function* <Request, Response>(
    call: ClientMiddlewareCall<Request, Response>,
    options: CallOptions,
  ): AsyncGenerator<Response, Response | void, undefined> {
    if (!token) {
      return yield* call.next(call.request, options);
    }

    const metadata = options.metadata ?? new Metadata();
    metadata.set("authorization", `Bearer ${token}`);

    return yield* call.next(call.request, {
      ...options,
      metadata,
    });
  };
}

export { authMiddleware };
```

## Metadata and Headers

### Sending and Receiving Metadata

```typescript
// Server — reading request metadata and setting response headers
async function createTask(
  request: CreateTaskRequest,
  context: CallContext,
): Promise<Task> {
  // Read request metadata
  const requestId = context.metadata.get("x-request-id");
  const userAgent = context.metadata.get("user-agent");
  const locale = context.metadata.get("x-locale") ?? "en-US";

  console.log(`Request ${requestId} from ${userAgent}, locale: ${locale}`);

  const task = await store.create(request);

  // Set response headers (sent before the response body)
  context.header.set("x-task-id", task.id);
  context.header.set("x-request-id", requestId ?? "");

  // Set response trailers (sent after the response body)
  context.trailer.set("x-processing-time-ms", String(Date.now() - startTime));

  return task;
}

// Client — sending metadata and reading response headers
async function createTaskWithMetadata(): Promise<void> {
  const metadata = new Metadata();
  metadata.set("x-request-id", crypto.randomUUID());
  metadata.set("x-locale", "en-US");
  metadata.set("x-idempotency-key", "unique-key-123");

  const task = await client.createTask(
    {
      title: "New task",
      description: "Created with metadata",
      priority: 2,
      assigneeId: "",
      labels: [],
      dueDate: undefined,
    },
    { metadata },
  );

  console.log("Created task:", task.id);
}
```

### Binary Metadata

```typescript
// Binary metadata values use keys ending in "-bin"
const metadata = new Metadata();

// String metadata
metadata.set("x-request-id", "abc-123");

// Binary metadata (automatically base64-encoded)
const traceContext = new Uint8Array([0, 0, 147, 231, 7, 99]);
metadata.set("x-trace-context-bin", Buffer.from(traceContext).toString("base64"));
```

## Health Checks

### Standard gRPC Health Check

```typescript
// src/server/health.ts
import { createServer } from "nice-grpc";
import {
  HealthDefinition,
  HealthServiceImpl,
  ServingStatus,
} from "nice-grpc-server-health";

const server = createServer();

// Create health service with initial statuses
const healthImpl = HealthServiceImpl({
  // Empty string is the overall server status
  "": ServingStatus.SERVING,
  "taskservice.v1.TaskService": ServingStatus.SERVING,
});

server.add(HealthDefinition, healthImpl);

// Update health status dynamically based on dependency checks
async function updateHealthStatus(): Promise<void> {
  const dbHealthy = await checkDatabaseConnection();
  const cacheHealthy = await checkCacheConnection();

  if (dbHealthy && cacheHealthy) {
    healthImpl.setStatus("taskservice.v1.TaskService", ServingStatus.SERVING);
  } else {
    healthImpl.setStatus("taskservice.v1.TaskService", ServingStatus.NOT_SERVING);
  }
}

// Run health check periodically
setInterval(updateHealthStatus, 30_000);
```

### Client Health Check

```typescript
// Check server health from the client
import { createChannel, createClient } from "nice-grpc";
import { HealthDefinition } from "nice-grpc-server-health";

const channel = createChannel("localhost:50051");
const healthClient = createClient(HealthDefinition, channel);

async function checkHealth(): Promise<boolean> {
  try {
    const response = await healthClient.check(
      { service: "taskservice.v1.TaskService" },
      { deadline: Date.now() + 2000 },
    );
    return response.status === 1; // SERVING
  } catch {
    return false;
  }
}

// Watch health status changes via server streaming
async function watchHealth(): Promise<void> {
  const stream = healthClient.watch({
    service: "taskservice.v1.TaskService",
  });

  for await (const response of stream) {
    console.log("Health status:", response.status === 1 ? "SERVING" : "NOT_SERVING");
  }
}
```

### Kubernetes Health Probe

```yaml
# Kubernetes deployment with gRPC health checks
apiVersion: apps/v1
kind: Deployment
metadata:
  name: task-service
spec:
  template:
    spec:
      containers:
        - name: task-service
          ports:
            - containerPort: 50051
              protocol: TCP
          livenessProbe:
            grpc:
              port: 50051
              service: "taskservice.v1.TaskService"
            initialDelaySeconds: 10
            periodSeconds: 15
          readinessProbe:
            grpc:
              port: 50051
              service: "taskservice.v1.TaskService"
            initialDelaySeconds: 5
            periodSeconds: 10
          startupProbe:
            grpc:
              port: 50051
            failureThreshold: 30
            periodSeconds: 2
```

## gRPC-Web for Browsers

### Server Setup with Envoy Proxy

```yaml
# envoy.yaml — proxies gRPC-Web requests to the gRPC backend
static_resources:
  listeners:
    - name: listener_0
      address:
        socket_address:
          address: 0.0.0.0
          port_value: 8080
      filter_chains:
        - filters:
            - name: envoy.filters.network.http_connection_manager
              typed_config:
                "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
                codec_type: auto
                stat_prefix: ingress_http
                route_config:
                  name: local_route
                  virtual_hosts:
                    - name: local_service
                      domains: ["*"]
                      routes:
                        - match:
                            prefix: "/"
                          route:
                            cluster: grpc_service
                            timeout: 30s
                      cors:
                        allow_origin_string_match:
                          - prefix: "*"
                        allow_methods: "GET, PUT, DELETE, POST, OPTIONS"
                        allow_headers: "authorization, content-type, x-grpc-web, grpc-timeout"
                        expose_headers: "grpc-status, grpc-message"
                        max_age: "1728000"
                http_filters:
                  - name: envoy.filters.http.grpc_web
                    typed_config:
                      "@type": type.googleapis.com/envoy.extensions.filters.http.grpc_web.v3.GrpcWeb
                  - name: envoy.filters.http.cors
                    typed_config:
                      "@type": type.googleapis.com/envoy.extensions.filters.http.cors.v3.Cors
                  - name: envoy.filters.http.router
                    typed_config:
                      "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router
  clusters:
    - name: grpc_service
      connect_timeout: 5s
      type: logical_dns
      lb_policy: round_robin
      typed_extension_protocol_options:
        envoy.extensions.upstreams.http.v3.HttpProtocolOptions:
          "@type": type.googleapis.com/envoy.extensions.upstreams.http.v3.HttpProtocolOptions
          explicit_http_config:
            http2_protocol_options: {}
      load_assignment:
        cluster_name: grpc_service
        endpoints:
          - lb_endpoints:
              - endpoint:
                  address:
                    socket_address:
                      address: task-service
                      port_value: 50051
```

### Browser Client with grpc-web

```typescript
// src/web-client/index.ts
import { GrpcWebFetchTransport } from "@protobuf-ts/grpcweb-transport";
import { TaskServiceClient } from "../gen/taskservice/v1/task.client.js";

const transport = new GrpcWebFetchTransport({
  baseUrl: "http://localhost:8080",
  format: "binary",
});

const client = new TaskServiceClient(transport);

// Unary call from the browser
async function getTask(id: string): Promise<void> {
  const { response } = await client.getTask(
    { id },
    {
      meta: {
        authorization: `Bearer ${getAuthToken()}`,
        "x-request-id": crypto.randomUUID(),
      },
      timeout: 5000,
    },
  );

  console.log("Task:", response.title);
}

// Server streaming from the browser
async function watchTasks(projectId: string): Promise<void> {
  const abortController = new AbortController();
  const stream = client.watchTasks(
    { projectId, statuses: [] },
    { abort: abortController.signal },
  );

  for await (const event of stream.responses) {
    console.log("Event:", event.type, event.task?.title);
    updateUI(event);
  }
}
```

## Connect Protocol

Connect is an HTTP-compatible RPC protocol that works with standard HTTP libraries, curl, and browsers without a proxy.

### Server with ConnectRPC (Fastify)

```typescript
// src/connect-server/index.ts
import { fastify } from "fastify";
import { fastifyConnectPlugin } from "@connectrpc/connect-fastify";
import { ConnectRouter, ConnectError, Code } from "@connectrpc/connect";
import { TaskService } from "../gen/taskservice/v1/task_connect.js";

function registerRoutes(router: ConnectRouter): void {
  router.service(TaskService, {
    async createTask(request, context) {
      const userId = context.requestHeader.get("x-user-id");
      if (!request.title) {
        throw new ConnectError(
          "title is required",
          Code.InvalidArgument,
        );
      }

      const task = await store.create({ ...request, createdBy: userId });

      context.responseHeader.set("x-task-id", task.id);
      return task;
    },

    async getTask(request) {
      const task = await store.findById(request.id);
      if (!task) {
        throw new ConnectError(
          `task ${request.id} not found`,
          Code.NotFound,
        );
      }
      return task;
    },

    async *watchTasks(request, context) {
      const events = store.subscribe(request.projectId);
      try {
        for await (const event of events) {
          if (context.signal.aborted) break;
          yield event;
        }
      } finally {
        events.unsubscribe();
      }
    },
  });
}

async function startServer(): Promise<void> {
  const server = fastify();

  await server.register(fastifyConnectPlugin, {
    routes: registerRoutes,
  });

  await server.listen({ host: "0.0.0.0", port: 8080 });
  console.log("Connect server listening on port 8080");
}

startServer();
```

### Connect Client (Works Everywhere)

```typescript
// src/connect-client/index.ts
import { createClient } from "@connectrpc/connect";
import { createConnectTransport } from "@connectrpc/connect-web";
import { TaskService } from "../gen/taskservice/v1/task_connect.js";

// Browser or Node.js — uses standard HTTP
const transport = createConnectTransport({
  baseUrl: "http://localhost:8080",
});

const client = createClient(TaskService, transport);

// Unary call — works with fetch, curl, and any HTTP client
async function getTask(id: string): Promise<void> {
  const task = await client.getTask(
    { id },
    {
      headers: new Headers({
        authorization: `Bearer ${token}`,
      }),
      timeoutMs: 5000,
    },
  );

  console.log("Task:", task.title);
}

// Server streaming — uses standard HTTP streaming
async function watchTasks(projectId: string): Promise<void> {
  for await (const event of client.watchTasks({ projectId, statuses: [] })) {
    console.log("Event:", event.type, event.task?.title);
  }
}
```

### Testing Connect Services with curl

```bash
# Unary call with JSON (Connect protocol supports JSON by default)
curl -X POST http://localhost:8080/taskservice.v1.TaskService/GetTask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer my-token" \
  -d '{"id": "task-123"}'

# Create a task
curl -X POST http://localhost:8080/taskservice.v1.TaskService/CreateTask \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New task from curl",
    "description": "Testing the Connect protocol",
    "priority": "PRIORITY_HIGH"
  }'
```

## Additional Resources

- gRPC docs: https://grpc.io/docs/
- Proto3 language guide: https://protobuf.dev/programming-guides/proto3/
- nice-grpc (TypeScript): https://github.com/deeplay-io/nice-grpc
- Buf (proto management): https://buf.build/
- ConnectRPC: https://connectrpc.com/
- gRPC-Web: https://github.com/grpc/grpc-web
- gRPC health checking protocol: https://github.com/grpc/grpc/blob/master/doc/health-checking.md
