---
name: api-documentation-generator
description: This skill should be used when creating API documentation, generating OpenAPI/Swagger specs, building interactive API explorers, or implementing API documentation best practices.
---

# API Documentation Generator

Complete guide for creating comprehensive, interactive API documentation using OpenAPI/Swagger and modern documentation tools.

## When to Use This Skill

- Generate OpenAPI/Swagger specifications
- Create interactive API documentation
- Document REST APIs automatically
- Build API explorers and testing interfaces
- Implement API versioning documentation
- Generate client SDKs from specs
- Create API design-first workflows

## OpenAPI/Swagger Basics

### OpenAPI 3.0 Specification

```yaml
openapi: 3.0.0
info:
  title: My API
  version: 1.0.0
  description: Comprehensive API for my application
  contact:
    email: api@example.com
  license:
    name: MIT

servers:
  - url: https://api.example.com/v1
    description: Production server
  - url: https://staging-api.example.com/v1
    description: Staging server

paths:
  /users:
    get:
      summary: List all users
      tags: [Users]
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
        - name: offset
          in: query
          schema:
            type: integer
            default: 0
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  total:
                    type: integer

    post:
      summary: Create a new user
      tags: [Users]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserCreate'
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'

  /users/{userId}:
    get:
      summary: Get user by ID
      tags: [Users]
      parameters:
        - name: userId
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: User found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          description: User not found

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
        email:
          type: string
          format: email
        name:
          type: string
        createdAt:
          type: string
          format: date-time

    UserCreate:
      type: object
      required: [email, name]
      properties:
        email:
          type: string
          format: email
        name:
          type: string
        password:
          type: string
          format: password

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - bearerAuth: []
```

## Generating OpenAPI from Code

### Node.js / Express with swagger-jsdoc

```javascript
const swaggerJsdoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'My API',
      version: '1.0.0',
    },
    servers: [
      {
        url: 'http://localhost:3000',
      },
    ],
  },
  apis: ['./routes/*.js'],
};

const specs = swaggerJsdoc(options);

app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(specs));

/**
 * @swagger
 * /users:
 *   get:
 *     summary: Returns a list of users
 *     tags: [Users]
 *     responses:
 *       200:
 *         description: List of users
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 $ref: '#/components/schemas/User'
 */
app.get('/users', async (req, res) => {
  const users = await User.findAll();
  res.json(users);
});

/**
 * @swagger
 * components:
 *   schemas:
 *     User:
 *       type: object
 *       properties:
 *         id:
 *           type: string
 *         email:
 *           type: string
 *         name:
 *           type: string
 */
```

### Python / FastAPI (Automatic)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional

app = FastAPI(
    title="My API",
    description="Comprehensive API documentation",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

class User(BaseModel):
    id: str
    email: EmailStr
    name: str
    created_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123",
                "email": "user@example.com",
                "name": "John Doe",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }

@app.get("/users", response_model=List[User], tags=["Users"])
async def list_users(
    limit: int = 20,
    offset: int = 0
):
    """
    List all users with pagination.

    - **limit**: Maximum number of users to return
    - **offset**: Number of users to skip
    """
    users = get_users(limit, offset)
    return users

@app.post("/users", response_model=User, status_code=201, tags=["Users"])
async def create_user(user: UserCreate):
    """
    Create a new user.

    - **email**: Valid email address
    - **name**: User's full name
    - **password**: Strong password (min 8 characters)
    """
    new_user = create_user_in_db(user)
    return new_user

@app.get("/users/{user_id}", response_model=User, tags=["Users"])
async def get_user(user_id: str):
    """Get a specific user by ID."""
    user = find_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### Spring Boot / Java

```java
@RestController
@RequestMapping("/api/v1/users")
@Tag(name = "Users", description = "User management endpoints")
public class UserController {

    @GetMapping
    @Operation(summary = "List all users")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Users found")
    })
    public ResponseEntity<List<User>> listUsers(
        @Parameter(description = "Maximum results")
        @RequestParam(defaultValue = "20") int limit,
        @Parameter(description = "Results to skip")
        @RequestParam(defaultValue = "0") int offset
    ) {
        List<User> users = userService.findAll(limit, offset);
        return ResponseEntity.ok(users);
    }

    @PostMapping
    @Operation(summary = "Create new user")
    public ResponseEntity<User> createUser(
        @io.swagger.v3.oas.annotations.parameters.RequestBody(
            description = "User to create"
        )
        @RequestBody UserCreateDto userDto
    ) {
        User user = userService.create(userDto);
        return ResponseEntity.status(HttpStatus.CREATED).body(user);
    }
}

@Schema(description = "User object")
public class User {
    @Schema(description = "Unique identifier", example = "123")
    private String id;

    @Schema(description = "Email address", example = "user@example.com")
    private String email;

    @Schema(description = "Full name", example = "John Doe")
    private String name;
}
```

## Interactive Documentation Tools

### Swagger UI

```yaml
# docker-compose.yml for Swagger UI
version: '3.8'

services:
  swagger-ui:
    image: swaggerapi/swagger-ui
    ports:
      - "8080:8080"
    environment:
      - SWAGGER_JSON=/openapi.yaml
    volumes:
      - ./openapi.yaml:/openapi.yaml
```

### ReDoc

```html
<!DOCTYPE html>
<html>
<head>
  <title>API Documentation</title>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
  <style>
    body {
      margin: 0;
      padding: 0;
    }
  </style>
</head>
<body>
  <redoc spec-url='./openapi.yaml'></redoc>
  <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
</body>
</html>
```

### Stoplight Elements

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <title>API Reference</title>
  <script src="https://unpkg.com/@stoplight/elements/web-components.min.js"></script>
  <link rel="stylesheet" href="https://unpkg.com/@stoplight/elements/styles.min.css">
</head>
<body>
  <elements-api
    apiDescriptionUrl="./openapi.yaml"
    router="hash"
    layout="sidebar"
  />
</body>
</html>
```

## API Design Best Practices

### RESTful Conventions

```yaml
# Good API design
GET    /users              # List users
POST   /users              # Create user
GET    /users/{id}         # Get user
PUT    /users/{id}         # Update user (full)
PATCH  /users/{id}         # Update user (partial)
DELETE /users/{id}         # Delete user

# Nested resources
GET    /users/{id}/posts   # Get user's posts
POST   /users/{id}/posts   # Create post for user

# Filtering, sorting, pagination
GET /users?role=admin&sort=created_at&order=desc&page=2&limit=20

# Bad examples to avoid
GET /getUsers               # Don't use verbs
POST /user/create           # Redundant
GET /users/delete/123       # Wrong method
```

### Versioning

```yaml
# URL versioning (common)
servers:
  - url: https://api.example.com/v1
  - url: https://api.example.com/v2

# Header versioning
GET /users
Headers:
  API-Version: 2

# Query parameter versioning
GET /users?version=2

# Content negotiation
Accept: application/vnd.myapi.v2+json
```

### Error Responses

```yaml
components:
  schemas:
    Error:
      type: object
      properties:
        code:
          type: string
          example: "VALIDATION_ERROR"
        message:
          type: string
          example: "Email is required"
        details:
          type: array
          items:
            type: object
            properties:
              field:
                type: string
              message:
                type: string
          example:
            - field: "email"
              message: "Must be valid email format"

responses:
  '400':
    description: Bad request
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Error'
        example:
          code: "VALIDATION_ERROR"
          message: "Invalid request data"
          details:
            - field: "email"
              message: "Email is required"
```

## Authentication Documentation

```yaml
components:
  securitySchemes:
    # JWT Bearer Token
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: "JWT token obtained from /auth/login"

    # API Key
    apiKey:
      type: apiKey
      in: header
      name: X-API-Key

    # OAuth2
    oauth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://auth.example.com/oauth/authorize
          tokenUrl: https://auth.example.com/oauth/token
          scopes:
            read:users: Read user information
            write:users: Modify user information

# Apply globally
security:
  - bearerAuth: []

# Override per endpoint
paths:
  /public:
    get:
      security: []  # No auth required

  /admin:
    get:
      security:
        - bearerAuth: []
          oauth2: [admin]
```

## Code Generation

### Generate Client SDK

```bash
# Install OpenAPI Generator
npm install @openapitools/openapi-generator-cli -g

# Generate TypeScript client
openapi-generator-cli generate \
  -i openapi.yaml \
  -g typescript-axios \
  -o ./client

# Generate Python client
openapi-generator-cli generate \
  -i openapi.yaml \
  -g python \
  -o ./python-client

# Generate Java client
openapi-generator-cli generate \
  -i openapi.yaml \
  -g java \
  -o ./java-client
```

### Generate Server Stubs

```bash
# Node.js Express server
openapi-generator-cli generate \
  -i openapi.yaml \
  -g nodejs-express-server \
  -o ./server

# Spring Boot server
openapi-generator-cli generate \
  -i openapi.yaml \
  -g spring \
  -o ./spring-server

# Python Flask server
openapi-generator-cli generate \
  -i openapi.yaml \
  -g python-flask \
  -o ./flask-server
```

## Testing Documentation

### Try-It-Out Features

```yaml
# Add examples for testing
paths:
  /users:
    post:
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserCreate'
            examples:
              basic:
                summary: Basic user
                value:
                  email: "user@example.com"
                  name: "John Doe"
                  password: "securepass123"
              admin:
                summary: Admin user
                value:
                  email: "admin@example.com"
                  name: "Admin User"
                  password: "adminpass123"
                  role: "admin"
```

### Postman Collection Export

```bash
# Convert OpenAPI to Postman collection
npm install -g openapi-to-postmanv2

openapi2postmanv2 \
  -s openapi.yaml \
  -o postman-collection.json \
  -p

# Import postman-collection.json into Postman
```

## Complete Example: E-commerce API

```yaml
openapi: 3.0.0
info:
  title: E-commerce API
  version: 1.0.0
  description: RESTful API for e-commerce platform

servers:
  - url: https://api.shop.example.com/v1

tags:
  - name: Products
    description: Product catalog operations
  - name: Orders
    description: Order management
  - name: Cart
    description: Shopping cart operations

paths:
  /products:
    get:
      summary: List products
      tags: [Products]
      parameters:
        - name: category
          in: query
          schema:
            type: string
        - name: minPrice
          in: query
          schema:
            type: number
        - name: maxPrice
          in: query
          schema:
            type: number
        - name: sort
          in: query
          schema:
            type: string
            enum: [price_asc, price_desc, name, newest]
      responses:
        '200':
          description: Products list
          content:
            application/json:
              schema:
                type: object
                properties:
                  products:
                    type: array
                    items:
                      $ref: '#/components/schemas/Product'
                  total:
                    type: integer
                  page:
                    type: integer

  /cart:
    get:
      summary: Get cart
      tags: [Cart]
      security:
        - bearerAuth: []
      responses:
        '200':
          description: Cart contents
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Cart'

    post:
      summary: Add item to cart
      tags: [Cart]
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [productId, quantity]
              properties:
                productId:
                  type: string
                quantity:
                  type: integer
                  minimum: 1
      responses:
        '200':
          description: Item added
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Cart'

  /orders:
    get:
      summary: List orders
      tags: [Orders]
      security:
        - bearerAuth: []
      responses:
        '200':
          description: Orders list
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Order'

    post:
      summary: Create order
      tags: [Orders]
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/OrderCreate'
      responses:
        '201':
          description: Order created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Order'

components:
  schemas:
    Product:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        description:
          type: string
        price:
          type: number
          format: decimal
        category:
          type: string
        stock:
          type: integer
        images:
          type: array
          items:
            type: string
            format: uri

    Cart:
      type: object
      properties:
        items:
          type: array
          items:
            type: object
            properties:
              product:
                $ref: '#/components/schemas/Product'
              quantity:
                type: integer
        total:
          type: number
          format: decimal

    Order:
      type: object
      properties:
        id:
          type: string
        status:
          type: string
          enum: [pending, processing, shipped, delivered, cancelled]
        items:
          type: array
          items:
            type: object
            properties:
              productId:
                type: string
              quantity:
                type: integer
              price:
                type: number
        total:
          type: number
        createdAt:
          type: string
          format: date-time

    OrderCreate:
      type: object
      required: [shippingAddress, paymentMethod]
      properties:
        shippingAddress:
          type: object
          properties:
            street:
              type: string
            city:
              type: string
            postalCode:
              type: string
            country:
              type: string
        paymentMethod:
          type: string
          enum: [credit_card, paypal, bank_transfer]

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - bearerAuth: []
```

## CI/CD Integration

```yaml
# .github/workflows/api-docs.yml
name: API Documentation

on:
  push:
    branches: [main]
    paths:
      - 'openapi.yaml'
      - 'docs/**'

jobs:
  deploy-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Validate OpenAPI spec
        run: |
          npm install -g @apidevtools/swagger-cli
          swagger-cli validate openapi.yaml

      - name: Generate HTML docs
        run: |
          npm install -g redoc-cli
          redoc-cli bundle openapi.yaml -o docs/index.html

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
```

## Best Practices Summary

✅ **Use OpenAPI 3.0+** (not Swagger 2.0)
✅ **Include examples** for all request/response bodies
✅ **Document all error cases** with proper status codes
✅ **Use tags** to organize endpoints logically
✅ **Include authentication** details and examples
✅ **Version your API** clearly
✅ **Generate client SDKs** for common languages
✅ **Keep docs in sync** with code (automate)
✅ **Provide "Try it out"** functionality
✅ **Include rate limiting** information

## Tools Comparison

| Tool | Best For | Interactive | Customization |
|------|----------|-------------|---------------|
| Swagger UI | Quick setup | ✅ Excellent | Limited |
| ReDoc | Clean reading | ❌ None | Moderate |
| Stoplight | Modern UX | ✅ Good | Excellent |
| Postman | Testing | ✅ Excellent | Excellent |
| API Blueprint | Markdown-based | Via tools | Excellent |

## Resources

- OpenAPI Specification: https://swagger.io/specification/
- Swagger UI: https://swagger.io/tools/swagger-ui/
- ReDoc: https://redocly.com/redoc/
- OpenAPI Generator: https://openapi-generator.tech/
- Stoplight: https://stoplight.io/
- API Design Guide: https://cloud.google.com/apis/design
