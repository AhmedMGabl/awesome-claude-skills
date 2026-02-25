---
name: openapi-spec
description: OpenAPI 3.1 specification authoring covering schema definition, path operations, request/response bodies, authentication schemes, reusable components, code generation with openapi-typescript, validation with Zod, and API-first development workflows.
---

# OpenAPI Specification

This skill should be used when writing or working with OpenAPI (Swagger) specifications. It covers schema authoring, code generation, validation, and API-first development.

## When to Use This Skill

Use this skill when you need to:

- Write OpenAPI 3.1 specifications
- Generate TypeScript types from API specs
- Validate requests against schemas
- Implement API-first development workflows
- Document REST APIs with OpenAPI

## OpenAPI 3.1 Specification

```yaml
# openapi.yaml
openapi: "3.1.0"
info:
  title: Task Management API
  version: "1.0.0"
  description: API for managing tasks and projects

servers:
  - url: https://api.example.com/v1
    description: Production
  - url: http://localhost:3000/v1
    description: Development

paths:
  /tasks:
    get:
      operationId: listTasks
      summary: List all tasks
      tags: [Tasks]
      parameters:
        - $ref: "#/components/parameters/PageParam"
        - $ref: "#/components/parameters/LimitParam"
        - name: status
          in: query
          schema:
            $ref: "#/components/schemas/TaskStatus"
      responses:
        "200":
          description: Task list
          content:
            application/json:
              schema:
                type: object
                required: [data, meta]
                properties:
                  data:
                    type: array
                    items:
                      $ref: "#/components/schemas/Task"
                  meta:
                    $ref: "#/components/schemas/PaginationMeta"
        "401":
          $ref: "#/components/responses/Unauthorized"

    post:
      operationId: createTask
      summary: Create a task
      tags: [Tasks]
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/CreateTask"
      responses:
        "201":
          description: Task created
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Task"
        "400":
          $ref: "#/components/responses/ValidationError"
        "401":
          $ref: "#/components/responses/Unauthorized"

  /tasks/{taskId}:
    get:
      operationId: getTask
      summary: Get a task by ID
      tags: [Tasks]
      parameters:
        - name: taskId
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        "200":
          description: Task details
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Task"
        "404":
          $ref: "#/components/responses/NotFound"

components:
  schemas:
    Task:
      type: object
      required: [id, title, status, createdAt]
      properties:
        id:
          type: string
          format: uuid
        title:
          type: string
          minLength: 1
          maxLength: 200
        description:
          type: string
        status:
          $ref: "#/components/schemas/TaskStatus"
        priority:
          type: string
          enum: [low, medium, high]
          default: medium
        assigneeId:
          type: string
          format: uuid
        createdAt:
          type: string
          format: date-time
        updatedAt:
          type: string
          format: date-time

    CreateTask:
      type: object
      required: [title]
      properties:
        title:
          type: string
          minLength: 1
          maxLength: 200
        description:
          type: string
        priority:
          type: string
          enum: [low, medium, high]
        assigneeId:
          type: string
          format: uuid

    TaskStatus:
      type: string
      enum: [todo, in_progress, done, cancelled]

    PaginationMeta:
      type: object
      required: [page, limit, total]
      properties:
        page:
          type: integer
        limit:
          type: integer
        total:
          type: integer

    Error:
      type: object
      required: [code, message]
      properties:
        code:
          type: string
        message:
          type: string
        details:
          type: array
          items:
            type: object
            properties:
              field:
                type: string
              message:
                type: string

  parameters:
    PageParam:
      name: page
      in: query
      schema:
        type: integer
        minimum: 1
        default: 1
    LimitParam:
      name: limit
      in: query
      schema:
        type: integer
        minimum: 1
        maximum: 100
        default: 20

  responses:
    Unauthorized:
      description: Authentication required
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/Error"
    NotFound:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/Error"
    ValidationError:
      description: Validation failed
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/Error"

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

## Code Generation with openapi-typescript

```bash
# Generate types from OpenAPI spec
npx openapi-typescript openapi.yaml -o src/api/types.ts
```

```typescript
// src/api/client.ts
import createClient from "openapi-fetch";
import type { paths } from "./types";

const client = createClient<paths>({
  baseUrl: "https://api.example.com/v1",
  headers: { Authorization: `Bearer ${token}` },
});

// Fully type-safe API calls
const { data, error } = await client.GET("/tasks", {
  params: { query: { status: "todo", page: 1 } },
});

const { data: task } = await client.POST("/tasks", {
  body: { title: "New task", priority: "high" },
});

const { data: single } = await client.GET("/tasks/{taskId}", {
  params: { path: { taskId: "uuid-here" } },
});
```

## Request Validation with Zod

```typescript
// Generated or hand-written Zod schemas matching OpenAPI
import { z } from "zod";

const CreateTaskSchema = z.object({
  title: z.string().min(1).max(200),
  description: z.string().optional(),
  priority: z.enum(["low", "medium", "high"]).optional(),
  assigneeId: z.string().uuid().optional(),
});

// Express middleware
app.post("/v1/tasks", (req, res) => {
  const result = CreateTaskSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(400).json({
      code: "VALIDATION_ERROR",
      message: "Invalid request body",
      details: result.error.issues.map((i) => ({
        field: i.path.join("."),
        message: i.message,
      })),
    });
  }
  // result.data is typed correctly
  createTask(result.data);
});
```

## Additional Resources

- OpenAPI 3.1: https://spec.openapis.org/oas/v3.1.0
- openapi-typescript: https://openapi-ts.dev/
- Swagger Editor: https://editor.swagger.io/
- Redocly: https://redocly.com/
