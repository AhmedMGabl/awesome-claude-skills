---
name: go-chi
description: Go Chi router patterns covering lightweight routing, middleware stack, URL parameters, subrouters, request context, and RESTful API patterns.
---

# Go Chi Router

This skill should be used when building HTTP APIs with Go Chi router. It covers routing, middleware, URL params, subrouters, and RESTful patterns.

## When to Use This Skill

Use this skill when you need to:

- Build RESTful APIs with a lightweight Go router
- Compose middleware chains
- Use URL parameters and subrouters
- Integrate with net/http handlers
- Build modular API structures

## Setup

```bash
go get github.com/go-chi/chi/v5
go get github.com/go-chi/chi/v5/middleware
```

## Basic Server

```go
package main

import (
    "net/http"
    "github.com/go-chi/chi/v5"
    "github.com/go-chi/chi/v5/middleware"
)

func main() {
    r := chi.NewRouter()

    r.Use(middleware.Logger)
    r.Use(middleware.Recoverer)
    r.Use(middleware.RequestID)
    r.Use(middleware.RealIP)
    r.Use(middleware.Timeout(30 * time.Second))

    r.Route("/api/users", func(r chi.Router) {
        r.Get("/", listUsers)
        r.Post("/", createUser)
        r.Route("/{userID}", func(r chi.Router) {
            r.Use(UserCtx)
            r.Get("/", getUser)
            r.Put("/", updateUser)
            r.Delete("/", deleteUser)
        })
    })

    http.ListenAndServe(":8080", r)
}
```

## Route Handlers

```go
func listUsers(w http.ResponseWriter, r *http.Request) {
    users, err := userRepo.List(r.Context())
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }
    render.JSON(w, r, users)
}

func getUser(w http.ResponseWriter, r *http.Request) {
    user := r.Context().Value("user").(*User)
    render.JSON(w, r, user)
}

func createUser(w http.ResponseWriter, r *http.Request) {
    var input CreateUserInput
    if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
        http.Error(w, "invalid body", http.StatusBadRequest)
        return
    }
    user, err := userRepo.Create(r.Context(), input)
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }
    w.WriteHeader(http.StatusCreated)
    render.JSON(w, r, user)
}
```

## Context Middleware

```go
func UserCtx(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        userID := chi.URLParam(r, "userID")
        user, err := userRepo.GetByID(r.Context(), userID)
        if err != nil {
            http.Error(w, "user not found", http.StatusNotFound)
            return
        }
        ctx := context.WithValue(r.Context(), "user", user)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

## Auth Middleware

```go
func AuthRequired(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        token := r.Header.Get("Authorization")
        if token == "" {
            http.Error(w, "unauthorized", http.StatusUnauthorized)
            return
        }
        claims, err := validateToken(strings.TrimPrefix(token, "Bearer "))
        if err != nil {
            http.Error(w, "invalid token", http.StatusUnauthorized)
            return
        }
        ctx := context.WithValue(r.Context(), "claims", claims)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}

// Protected routes
r.Group(func(r chi.Router) {
    r.Use(AuthRequired)
    r.Get("/api/profile", getProfile)
    r.Put("/api/profile", updateProfile)
})
```

## Additional Resources

- Chi: https://go-chi.io/
- GitHub: https://github.com/go-chi/chi
- Middleware: https://github.com/go-chi/chi#middlewares
