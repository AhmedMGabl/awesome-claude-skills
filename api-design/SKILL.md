---
name: api-design
description: REST API design best practices covering resource naming, HTTP methods, status codes, pagination, filtering, versioning, HATEOAS, error responses, rate limiting, authentication headers, OpenAPI contracts, and API evolution strategies.
---

# API Design Best Practices

This skill should be used when designing REST APIs, defining contracts, or establishing API conventions. It covers resource design, pagination, versioning, error formats, and API evolution.

## When to Use This Skill

Use this skill when you need to:

- Design RESTful API endpoints
- Define consistent error response formats
- Implement pagination, filtering, and sorting
- Plan API versioning strategies
- Write OpenAPI/Swagger specifications
- Establish API conventions for a team

## URL and Resource Design

```
RESOURCE NAMING RULES:
- Use plural nouns: /users, /orders, /products
- Use kebab-case: /order-items, /user-profiles
- Nest for relationships: /users/:id/orders
- Max 2 levels deep: /users/:id/orders (not /users/:id/orders/:id/items)
- Use query params for cross-cutting: ?include=author&fields=title,body

GOOD:
  GET    /api/v1/users           → List users
  POST   /api/v1/users           → Create user
  GET    /api/v1/users/:id       → Get user
  PATCH  /api/v1/users/:id       → Update user
  DELETE /api/v1/users/:id       → Delete user
  GET    /api/v1/users/:id/orders → List user's orders

BAD:
  GET    /api/v1/getUsers        → Verb in URL
  POST   /api/v1/user/create     → Verb + singular
  GET    /api/v1/users/:id/orders/:id/items/:id  → Too deep
```

## HTTP Status Codes

```
SUCCESS:
  200 OK              → GET, PATCH (return updated resource)
  201 Created         → POST (return created resource + Location header)
  204 No Content      → DELETE (no body)

CLIENT ERROR:
  400 Bad Request     → Validation errors, malformed JSON
  401 Unauthorized    → Missing or invalid auth token
  403 Forbidden       → Valid auth but insufficient permissions
  404 Not Found       → Resource doesn't exist
  409 Conflict        → Duplicate resource, state conflict
  422 Unprocessable   → Semantic validation (business rules)
  429 Too Many Reqs   → Rate limited (include Retry-After header)

SERVER ERROR:
  500 Internal Error  → Unexpected server failure
  502 Bad Gateway     → Upstream service failure
  503 Unavailable     → Maintenance or overloaded
```

## Error Response Format

```typescript
// Consistent error response (RFC 7807 Problem Details)
interface ErrorResponse {
  type: string;       // URI reference identifying error type
  title: string;      // Short human-readable summary
  status: number;     // HTTP status code
  detail: string;     // Human-readable explanation
  instance?: string;  // URI reference for this occurrence
  errors?: Record<string, string[]>;  // Field-level validation errors
}

// Examples
// 400 Validation Error
{
  "type": "https://api.example.com/errors/validation",
  "title": "Validation Failed",
  "status": 400,
  "detail": "The request body contains invalid fields",
  "errors": {
    "email": ["Must be a valid email address"],
    "age": ["Must be between 18 and 120"]
  }
}

// 404 Not Found
{
  "type": "https://api.example.com/errors/not-found",
  "title": "Resource Not Found",
  "status": 404,
  "detail": "User with id '123' does not exist"
}

// 429 Rate Limited
{
  "type": "https://api.example.com/errors/rate-limited",
  "title": "Rate Limit Exceeded",
  "status": 429,
  "detail": "You have exceeded 100 requests per minute"
}
// + Header: Retry-After: 30
```

## Pagination

```typescript
// Cursor-based pagination (preferred for large datasets)
// GET /api/v1/posts?limit=20&cursor=eyJpZCI6MTAwfQ

interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    next_cursor: string | null;  // null means no more pages
    has_more: boolean;
    limit: number;
  };
}

// Offset-based pagination (simpler but slower on large tables)
// GET /api/v1/posts?page=3&per_page=20

interface OffsetPaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
  };
}
```

## Filtering and Sorting

```
FILTERING:
  GET /api/v1/products?category=electronics&min_price=100&max_price=500
  GET /api/v1/users?role=admin&status=active
  GET /api/v1/orders?created_after=2024-01-01&created_before=2024-12-31

SORTING:
  GET /api/v1/products?sort=price         → Ascending by price
  GET /api/v1/products?sort=-created_at   → Descending by created_at
  GET /api/v1/products?sort=-rating,price → By rating desc, then price asc

FIELD SELECTION:
  GET /api/v1/users?fields=id,name,email  → Only return specified fields

SEARCH:
  GET /api/v1/products?q=wireless+headphones  → Full-text search

INCLUDE RELATIONS:
  GET /api/v1/posts?include=author,comments   → Embed related resources
```

## Versioning

```
STRATEGIES (pick one):

1. URL Path (most common, clearest):
   GET /api/v1/users
   GET /api/v2/users

2. Header-based:
   GET /api/users
   Accept: application/vnd.myapp.v2+json

3. Query parameter:
   GET /api/users?version=2

EVOLUTION RULES:
- Adding fields is NOT a breaking change
- Removing or renaming fields IS a breaking change
- Changing field types IS a breaking change
- Adding optional query params is NOT a breaking change
- Adding required params IS a breaking change
- Use sunset headers to deprecate: Sunset: Sat, 31 Dec 2025 23:59:59 GMT
```

## Authentication Headers

```
PATTERNS:

Bearer Token (JWT/OAuth):
  Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

API Key:
  X-API-Key: sk_live_abc123
  # Or in query: ?api_key=sk_live_abc123 (less secure, logged in URLs)

Rate Limit Headers (response):
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 95
  X-RateLimit-Reset: 1640995200
  Retry-After: 30  (on 429 responses)

CORS Headers:
  Access-Control-Allow-Origin: https://app.example.com
  Access-Control-Allow-Methods: GET, POST, PATCH, DELETE
  Access-Control-Allow-Headers: Authorization, Content-Type
  Access-Control-Max-Age: 86400
```

## OpenAPI Specification

```yaml
openapi: "3.1.0"
info:
  title: My API
  version: "1.0.0"

paths:
  /api/v1/users:
    get:
      summary: List users
      tags: [Users]
      parameters:
        - name: page
          in: query
          schema: { type: integer, default: 1, minimum: 1 }
        - name: per_page
          in: query
          schema: { type: integer, default: 20, minimum: 1, maximum: 100 }
      responses:
        "200":
          description: Paginated list of users
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items: { $ref: "#/components/schemas/User" }
                  pagination:
                    $ref: "#/components/schemas/Pagination"

    post:
      summary: Create user
      tags: [Users]
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: "#/components/schemas/CreateUser" }
      responses:
        "201":
          description: Created
          content:
            application/json:
              schema: { $ref: "#/components/schemas/User" }
        "400":
          description: Validation error
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Error" }

components:
  schemas:
    User:
      type: object
      properties:
        id: { type: string, format: uuid }
        name: { type: string }
        email: { type: string, format: email }
        created_at: { type: string, format: date-time }
    CreateUser:
      type: object
      required: [name, email]
      properties:
        name: { type: string, minLength: 1, maxLength: 100 }
        email: { type: string, format: email }
    Error:
      type: object
      properties:
        type: { type: string }
        title: { type: string }
        status: { type: integer }
        detail: { type: string }
```

## Additional Resources

- Microsoft REST API Guidelines: https://github.com/microsoft/api-guidelines
- JSON:API Specification: https://jsonapi.org/
- RFC 7807 Problem Details: https://www.rfc-editor.org/rfc/rfc7807
- OpenAPI Specification: https://swagger.io/specification/
