---
name: go-gin
description: Go Gin patterns covering HTTP routing, middleware, request binding, validation, error handling, file uploads, grouping, and production deployment.
---

# Go Gin

This skill should be used when building web APIs with Go Gin. It covers routing, middleware, request binding, validation, error handling, and deployment.

## When to Use This Skill

Use this skill when you need to:

- Build high-performance HTTP APIs with Gin
- Bind and validate request data
- Add auth, logging, and recovery middleware
- Handle file uploads and static files
- Group routes with shared middleware

## Setup

```bash
go get github.com/gin-gonic/gin
```

## Basic Server

```go
package main

import (
    "net/http"
    "github.com/gin-gonic/gin"
)

func main() {
    r := gin.Default() // includes Logger and Recovery middleware

    api := r.Group("/api")
    {
        api.GET("/users", listUsers)
        api.GET("/users/:id", getUser)
        api.POST("/users", createUser)
        api.PUT("/users/:id", updateUser)
        api.DELETE("/users/:id", deleteUser)
    }

    r.Run(":8080")
}
```

## Request Binding and Validation

```go
type CreateUserInput struct {
    Name  string `json:"name" binding:"required,min=2,max=50"`
    Email string `json:"email" binding:"required,email"`
    Age   int    `json:"age" binding:"required,gte=18"`
}

func createUser(c *gin.Context) {
    var input CreateUserInput
    if err := c.ShouldBindJSON(&input); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    user := User{Name: input.Name, Email: input.Email, Age: input.Age}
    if err := db.Create(&user).Error; err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to create user"})
        return
    }

    c.JSON(http.StatusCreated, user)
}

func getUser(c *gin.Context) {
    id := c.Param("id")
    var user User
    if err := db.First(&user, "id = ?", id).Error; err != nil {
        c.JSON(http.StatusNotFound, gin.H{"error": "user not found"})
        return
    }
    c.JSON(http.StatusOK, user)
}

func listUsers(c *gin.Context) {
    page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
    limit, _ := strconv.Atoi(c.DefaultQuery("limit", "10"))
    offset := (page - 1) * limit

    var users []User
    db.Limit(limit).Offset(offset).Find(&users)
    c.JSON(http.StatusOK, gin.H{"users": users, "page": page})
}
```

## Auth Middleware

```go
func AuthMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        token := c.GetHeader("Authorization")
        if token == "" {
            c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "missing token"})
            return
        }

        claims, err := validateJWT(strings.TrimPrefix(token, "Bearer "))
        if err != nil {
            c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "invalid token"})
            return
        }

        c.Set("userID", claims.UserID)
        c.Next()
    }
}

// Use it
protected := r.Group("/api", AuthMiddleware())
```

## Error Handling

```go
func ErrorHandler() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Next()
        if len(c.Errors) > 0 {
            err := c.Errors.Last()
            c.JSON(http.StatusInternalServerError, gin.H{
                "error": err.Error(),
            })
        }
    }
}
```

## Additional Resources

- Gin: https://gin-gonic.com/
- Docs: https://gin-gonic.com/docs/
- Examples: https://github.com/gin-gonic/examples
