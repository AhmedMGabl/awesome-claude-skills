---
name: go-fiber
description: Go Fiber patterns covering Express-inspired routing, middleware, request validation, WebSockets, file uploads, template rendering, and production deployment.
---

# Go Fiber

This skill should be used when building web APIs with Go Fiber. It covers routing, middleware, validation, WebSockets, file uploads, and deployment.

## When to Use This Skill

Use this skill when you need to:

- Build fast HTTP APIs with Express-like syntax in Go
- Add middleware for auth, CORS, and rate limiting
- Handle file uploads and WebSocket connections
- Validate request bodies
- Deploy Fiber applications

## Setup

```bash
go get github.com/gofiber/fiber/v2
```

## Basic Server

```go
package main

import (
    "github.com/gofiber/fiber/v2"
    "github.com/gofiber/fiber/v2/middleware/cors"
    "github.com/gofiber/fiber/v2/middleware/logger"
    "github.com/gofiber/fiber/v2/middleware/recover"
)

func main() {
    app := fiber.New(fiber.Config{
        ErrorHandler: customErrorHandler,
    })

    app.Use(logger.New())
    app.Use(recover.New())
    app.Use(cors.New(cors.Config{
        AllowOrigins: "http://localhost:3000",
        AllowHeaders: "Origin, Content-Type, Authorization",
    }))

    api := app.Group("/api")
    api.Get("/users", getUsers)
    api.Get("/users/:id", getUser)
    api.Post("/users", createUser)
    api.Put("/users/:id", updateUser)
    api.Delete("/users/:id", deleteUser)

    app.Listen(":3000")
}
```

## Route Handlers

```go
type CreateUserRequest struct {
    Name  string `json:"name" validate:"required,min=2"`
    Email string `json:"email" validate:"required,email"`
}

func getUsers(c *fiber.Ctx) error {
    page := c.QueryInt("page", 1)
    limit := c.QueryInt("limit", 10)
    users, err := userService.List(page, limit)
    if err != nil {
        return fiber.NewError(fiber.StatusInternalServerError, err.Error())
    }
    return c.JSON(fiber.Map{"users": users, "page": page})
}

func getUser(c *fiber.Ctx) error {
    id := c.Params("id")
    user, err := userService.GetByID(id)
    if err != nil {
        return fiber.NewError(fiber.StatusNotFound, "user not found")
    }
    return c.JSON(user)
}

func createUser(c *fiber.Ctx) error {
    var req CreateUserRequest
    if err := c.BodyParser(&req); err != nil {
        return fiber.NewError(fiber.StatusBadRequest, "invalid body")
    }
    user, err := userService.Create(req.Name, req.Email)
    if err != nil {
        return fiber.NewError(fiber.StatusInternalServerError, err.Error())
    }
    return c.Status(fiber.StatusCreated).JSON(user)
}
```

## Auth Middleware

```go
func AuthRequired() fiber.Handler {
    return func(c *fiber.Ctx) error {
        token := c.Get("Authorization")
        if token == "" {
            return fiber.NewError(fiber.StatusUnauthorized, "missing token")
        }
        claims, err := validateToken(token)
        if err != nil {
            return fiber.NewError(fiber.StatusUnauthorized, "invalid token")
        }
        c.Locals("userID", claims.UserID)
        return c.Next()
    }
}

// Use it
api := app.Group("/api", AuthRequired())
```

## Error Handler

```go
func customErrorHandler(c *fiber.Ctx, err error) error {
    code := fiber.StatusInternalServerError
    message := "Internal Server Error"

    var fiberErr *fiber.Error
    if errors.As(err, &fiberErr) {
        code = fiberErr.Code
        message = fiberErr.Message
    }

    return c.Status(code).JSON(fiber.Map{
        "error":   true,
        "message": message,
    })
}
```

## Additional Resources

- Fiber: https://gofiber.io/
- API: https://docs.gofiber.io/
- Middleware: https://docs.gofiber.io/category/-middleware
