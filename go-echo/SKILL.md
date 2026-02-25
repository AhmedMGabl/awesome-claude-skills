---
name: go-echo
description: Go Echo patterns covering high-performance routing, middleware, request binding, validation, error handling, WebSockets, and Swagger documentation.
---

# Go Echo

This skill should be used when building web APIs with Go Echo framework. It covers routing, middleware, binding, validation, error handling, and documentation.

## When to Use This Skill

Use this skill when you need to:

- Build high-performance HTTP APIs with Echo
- Bind and validate request data automatically
- Add built-in middleware for JWT, CORS, and logging
- Handle errors with centralized error handlers
- Generate Swagger/OpenAPI documentation

## Setup

```bash
go get github.com/labstack/echo/v4
go get github.com/labstack/echo/v4/middleware
```

## Basic Server

```go
package main

import (
    "net/http"
    "github.com/labstack/echo/v4"
    emw "github.com/labstack/echo/v4/middleware"
)

func main() {
    e := echo.New()

    e.Use(emw.Logger())
    e.Use(emw.Recover())
    e.Use(emw.CORSWithConfig(emw.CORSConfig{
        AllowOrigins: []string{"http://localhost:3000"},
        AllowMethods: []string{http.MethodGet, http.MethodPost, http.MethodPut, http.MethodDelete},
    }))

    api := e.Group("/api")
    api.GET("/users", listUsers)
    api.GET("/users/:id", getUser)
    api.POST("/users", createUser)
    api.PUT("/users/:id", updateUser)
    api.DELETE("/users/:id", deleteUser)

    e.Logger.Fatal(e.Start(":8080"))
}
```

## Request Binding and Validation

```go
type CreateUserInput struct {
    Name  string `json:"name" validate:"required,min=2"`
    Email string `json:"email" validate:"required,email"`
    Age   int    `json:"age" validate:"required,gte=18"`
}

func createUser(c echo.Context) error {
    var input CreateUserInput
    if err := c.Bind(&input); err != nil {
        return echo.NewHTTPError(http.StatusBadRequest, "invalid request body")
    }
    if err := c.Validate(&input); err != nil {
        return echo.NewHTTPError(http.StatusBadRequest, err.Error())
    }

    user, err := userService.Create(input)
    if err != nil {
        return echo.NewHTTPError(http.StatusInternalServerError, err.Error())
    }
    return c.JSON(http.StatusCreated, user)
}

func getUser(c echo.Context) error {
    id := c.Param("id")
    user, err := userService.GetByID(id)
    if err != nil {
        return echo.NewHTTPError(http.StatusNotFound, "user not found")
    }
    return c.JSON(http.StatusOK, user)
}

func listUsers(c echo.Context) error {
    page, _ := strconv.Atoi(c.QueryParam("page"))
    if page < 1 { page = 1 }
    users, err := userService.List(page, 10)
    if err != nil {
        return echo.NewHTTPError(http.StatusInternalServerError, err.Error())
    }
    return c.JSON(http.StatusOK, map[string]interface{}{"users": users, "page": page})
}
```

## JWT Middleware

```go
import "github.com/labstack/echo-jwt/v4"

// Protected group
restricted := e.Group("/api/admin")
restricted.Use(echojwt.WithConfig(echojwt.Config{
    SigningKey: []byte("secret-key"),
}))

restricted.GET("/dashboard", func(c echo.Context) error {
    token := c.Get("user").(*jwt.Token)
    claims := token.Claims.(jwt.MapClaims)
    userID := claims["sub"].(string)
    return c.JSON(http.StatusOK, map[string]string{"userID": userID})
})
```

## Custom Error Handler

```go
e.HTTPErrorHandler = func(err error, c echo.Context) {
    code := http.StatusInternalServerError
    message := "Internal Server Error"

    var he *echo.HTTPError
    if errors.As(err, &he) {
        code = he.Code
        if m, ok := he.Message.(string); ok {
            message = m
        }
    }

    c.JSON(code, map[string]interface{}{
        "error":   true,
        "message": message,
    })
}
```

## Additional Resources

- Echo: https://echo.labstack.com/
- Guide: https://echo.labstack.com/docs
- Middleware: https://echo.labstack.com/docs/category/middleware
