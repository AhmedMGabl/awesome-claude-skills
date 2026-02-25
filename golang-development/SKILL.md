---
name: golang-development
description: Go development covering project structure, error handling, concurrency with goroutines and channels, HTTP servers, testing, modules, interfaces, generics, and production-ready patterns for building performant applications.
---

# Go Development

This skill should be used when writing, structuring, or optimizing Go code. It covers project layout, idiomatic error handling, concurrency patterns, HTTP servers, testing, modules, generics, and production-ready Go patterns.

## When to Use This Skill

Use this skill when you need to:

- Set up Go projects with proper module structure
- Write idiomatic Go with error handling and interfaces
- Build concurrent programs with goroutines and channels
- Create HTTP servers and REST APIs
- Test Go code with the standard library and testify
- Work with generics (Go 1.18+)
- Build production-ready CLI tools and services

## Project Setup

```bash
# Initialize module
go mod init github.com/user/project

# Project structure
project/
├── cmd/
│   └── server/
│       └── main.go           # Entry point
├── internal/                  # Private packages
│   ├── handler/
│   │   └── user.go
│   ├── service/
│   │   └── user.go
│   ├── repository/
│   │   └── user.go
│   └── model/
│       └── user.go
├── pkg/                       # Public/shared packages
│   └── middleware/
│       └── auth.go
├── api/                       # OpenAPI specs, proto files
├── go.mod
├── go.sum
└── Makefile
```

### Makefile

```makefile
.PHONY: build run test lint

build:
	go build -o bin/server ./cmd/server

run:
	go run ./cmd/server

test:
	go test -v -race -cover ./...

lint:
	golangci-lint run ./...

generate:
	go generate ./...
```

## Core Patterns

### Error Handling

```go
package service

import (
	"errors"
	"fmt"
)

// Sentinel errors
var (
	ErrNotFound     = errors.New("not found")
	ErrUnauthorized = errors.New("unauthorized")
	ErrConflict     = errors.New("conflict")
)

// Custom error type
type ValidationError struct {
	Field   string
	Message string
}

func (e *ValidationError) Error() string {
	return fmt.Sprintf("validation error: %s - %s", e.Field, e.Message)
}

// Wrapping errors with context
func (s *UserService) GetUser(id int64) (*User, error) {
	user, err := s.repo.FindByID(id)
	if err != nil {
		if errors.Is(err, ErrNotFound) {
			return nil, fmt.Errorf("user %d: %w", id, ErrNotFound)
		}
		return nil, fmt.Errorf("get user %d: %w", id, err)
	}
	return user, nil
}

// Checking errors
func handleError(err error) {
	if errors.Is(err, ErrNotFound) {
		// Handle not found
	}

	var valErr *ValidationError
	if errors.As(err, &valErr) {
		// Handle validation error with access to Field, Message
		fmt.Println(valErr.Field, valErr.Message)
	}
}
```

### Interfaces

```go
// Small, focused interfaces (Go convention)
type Reader interface {
	Read(p []byte) (n int, err error)
}

type Writer interface {
	Write(p []byte) (n int, err error)
}

type ReadWriter interface {
	Reader
	Writer
}

// Repository interface (defined by consumer, not provider)
type UserRepository interface {
	FindByID(ctx context.Context, id int64) (*User, error)
	FindByEmail(ctx context.Context, email string) (*User, error)
	Create(ctx context.Context, user *User) error
	Update(ctx context.Context, user *User) error
	Delete(ctx context.Context, id int64) error
}

// Service using the interface
type UserService struct {
	repo   UserRepository
	logger *slog.Logger
}

func NewUserService(repo UserRepository, logger *slog.Logger) *UserService {
	return &UserService{repo: repo, logger: logger}
}
```

### Structs and Methods

```go
package model

import "time"

type User struct {
	ID        int64     `json:"id" db:"id"`
	Email     string    `json:"email" db:"email"`
	Name      string    `json:"name" db:"name"`
	Role      string    `json:"role" db:"role"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
	UpdatedAt time.Time `json:"updated_at" db:"updated_at"`
}

// Constructor with validation
func NewUser(email, name string) (*User, error) {
	if email == "" {
		return nil, &ValidationError{Field: "email", Message: "required"}
	}
	return &User{
		Email:     email,
		Name:      name,
		Role:      "user",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}, nil
}

// Value receiver for reads
func (u User) IsAdmin() bool {
	return u.Role == "admin"
}

// Pointer receiver for mutations
func (u *User) SetRole(role string) {
	u.Role = role
	u.UpdatedAt = time.Now()
}
```

## Concurrency

### Goroutines and Channels

```go
package main

import (
	"context"
	"fmt"
	"sync"
	"time"
)

// Fan-out/fan-in
func processItems(items []string) []Result {
	results := make(chan Result, len(items))
	var wg sync.WaitGroup

	for _, item := range items {
		wg.Add(1)
		go func(item string) {
			defer wg.Done()
			results <- process(item)
		}(item)
	}

	go func() {
		wg.Wait()
		close(results)
	}()

	var out []Result
	for r := range results {
		out = append(out, r)
	}
	return out
}

// Worker pool
func workerPool(ctx context.Context, jobs <-chan Job, numWorkers int) <-chan Result {
	results := make(chan Result)
	var wg sync.WaitGroup

	for i := 0; i < numWorkers; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for {
				select {
				case job, ok := <-jobs:
					if !ok {
						return
					}
					results <- processJob(job)
				case <-ctx.Done():
					return
				}
			}
		}()
	}

	go func() {
		wg.Wait()
		close(results)
	}()

	return results
}

// Context with timeout
func fetchWithTimeout(url string) ([]byte, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		return nil, err
	}

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	return io.ReadAll(resp.Body)
}

// errgroup for parallel operations
import "golang.org/x/sync/errgroup"

func fetchAll(ctx context.Context, urls []string) ([][]byte, error) {
	g, ctx := errgroup.WithContext(ctx)
	results := make([][]byte, len(urls))

	for i, url := range urls {
		i, url := i, url // capture loop vars
		g.Go(func() error {
			data, err := fetchWithTimeout(url)
			if err != nil {
				return fmt.Errorf("fetch %s: %w", url, err)
			}
			results[i] = data
			return nil
		})
	}

	if err := g.Wait(); err != nil {
		return nil, err
	}
	return results, nil
}
```

### sync Primitives

```go
// Mutex for shared state
type SafeCounter struct {
	mu    sync.RWMutex
	count map[string]int
}

func (c *SafeCounter) Inc(key string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.count[key]++
}

func (c *SafeCounter) Get(key string) int {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.count[key]
}

// sync.Once for one-time initialization
var (
	instance *Database
	once     sync.Once
)

func GetDB() *Database {
	once.Do(func() {
		instance = connectDB()
	})
	return instance
}
```

## HTTP Server

```go
package main

import (
	"context"
	"encoding/json"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"time"
)

func main() {
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))

	mux := http.NewServeMux()

	// Routes (Go 1.22+ method patterns)
	mux.HandleFunc("GET /api/users", listUsers)
	mux.HandleFunc("POST /api/users", createUser)
	mux.HandleFunc("GET /api/users/{id}", getUser)
	mux.HandleFunc("PUT /api/users/{id}", updateUser)
	mux.HandleFunc("DELETE /api/users/{id}", deleteUser)
	mux.HandleFunc("GET /health", healthCheck)

	// Middleware stack
	handler := loggingMiddleware(logger)(
		recoveryMiddleware()(
			corsMiddleware()(mux),
		),
	)

	srv := &http.Server{
		Addr:         ":8080",
		Handler:      handler,
		ReadTimeout:  5 * time.Second,
		WriteTimeout: 10 * time.Second,
		IdleTimeout:  120 * time.Second,
	}

	// Graceful shutdown
	go func() {
		logger.Info("server starting", "addr", srv.Addr)
		if err := srv.ListenAndServe(); err != http.ErrServerClosed {
			logger.Error("server error", "err", err)
			os.Exit(1)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, os.Interrupt)
	<-quit

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	srv.Shutdown(ctx)
	logger.Info("server stopped")
}

// Handler
func getUser(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")

	user, err := userService.GetUser(r.Context(), id)
	if err != nil {
		writeError(w, err)
		return
	}

	writeJSON(w, http.StatusOK, user)
}

// JSON helpers
func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(v)
}

func writeError(w http.ResponseWriter, err error) {
	switch {
	case errors.Is(err, ErrNotFound):
		writeJSON(w, http.StatusNotFound, map[string]string{"error": err.Error()})
	case errors.Is(err, ErrUnauthorized):
		writeJSON(w, http.StatusUnauthorized, map[string]string{"error": err.Error()})
	default:
		writeJSON(w, http.StatusInternalServerError, map[string]string{"error": "internal error"})
	}
}

// Middleware
func loggingMiddleware(logger *slog.Logger) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			start := time.Now()
			next.ServeHTTP(w, r)
			logger.Info("request",
				"method", r.Method,
				"path", r.URL.Path,
				"duration", time.Since(start),
			)
		})
	}
}

func recoveryMiddleware() func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			defer func() {
				if err := recover(); err != nil {
					writeJSON(w, http.StatusInternalServerError, map[string]string{"error": "internal error"})
				}
			}()
			next.ServeHTTP(w, r)
		})
	}
}
```

## Generics (Go 1.18+)

```go
// Generic function
func Filter[T any](items []T, fn func(T) bool) []T {
	var result []T
	for _, item := range items {
		if fn(item) {
			result = append(result, item)
		}
	}
	return result
}

func Map[T, U any](items []T, fn func(T) U) []U {
	result := make([]U, len(items))
	for i, item := range items {
		result[i] = fn(item)
	}
	return result
}

// Type constraints
type Number interface {
	~int | ~int32 | ~int64 | ~float32 | ~float64
}

func Sum[T Number](nums []T) T {
	var total T
	for _, n := range nums {
		total += n
	}
	return total
}

// Generic data structures
type Stack[T any] struct {
	items []T
}

func (s *Stack[T]) Push(item T) {
	s.items = append(s.items, item)
}

func (s *Stack[T]) Pop() (T, bool) {
	if len(s.items) == 0 {
		var zero T
		return zero, false
	}
	item := s.items[len(s.items)-1]
	s.items = s.items[:len(s.items)-1]
	return item, true
}

// Generic repository
type Repository[T any, ID comparable] interface {
	FindByID(ctx context.Context, id ID) (*T, error)
	Create(ctx context.Context, entity *T) error
	Update(ctx context.Context, entity *T) error
	Delete(ctx context.Context, id ID) error
}
```

## Testing

```go
package service_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestUserService_GetUser(t *testing.T) {
	// Table-driven tests
	tests := []struct {
		name    string
		id      int64
		want    *User
		wantErr error
	}{
		{
			name: "existing user",
			id:   1,
			want: &User{ID: 1, Name: "Alice", Email: "alice@test.com"},
		},
		{
			name:    "not found",
			id:      999,
			wantErr: ErrNotFound,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			repo := &mockUserRepo{users: map[int64]*User{
				1: {ID: 1, Name: "Alice", Email: "alice@test.com"},
			}}
			svc := NewUserService(repo, slog.Default())

			got, err := svc.GetUser(context.Background(), tt.id)

			if tt.wantErr != nil {
				require.ErrorIs(t, err, tt.wantErr)
				return
			}
			require.NoError(t, err)
			assert.Equal(t, tt.want.Name, got.Name)
			assert.Equal(t, tt.want.Email, got.Email)
		})
	}
}

// Mock implementation
type mockUserRepo struct {
	users map[int64]*User
}

func (m *mockUserRepo) FindByID(ctx context.Context, id int64) (*User, error) {
	user, ok := m.users[id]
	if !ok {
		return nil, ErrNotFound
	}
	return user, nil
}

// Benchmarks
func BenchmarkFilter(b *testing.B) {
	items := make([]int, 10000)
	for i := range items {
		items[i] = i
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		Filter(items, func(n int) bool { return n%2 == 0 })
	}
}

// Test with cleanup
func TestWithTempDB(t *testing.T) {
	db := setupTestDB(t)
	t.Cleanup(func() {
		db.Close()
	})

	// test using db...
}
```

## Structured Logging (slog)

```go
import "log/slog"

// JSON logger for production
logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
	Level: slog.LevelInfo,
}))

// Structured logging
logger.Info("user created",
	"user_id", user.ID,
	"email", user.Email,
)

logger.Error("failed to create user",
	"err", err,
	"email", email,
)

// Logger with context
reqLogger := logger.With("request_id", requestID, "method", r.Method)
reqLogger.Info("handling request")
```

## Additional Resources

- Go documentation: https://go.dev/doc/
- Effective Go: https://go.dev/doc/effective_go
- Go by Example: https://gobyexample.com/
- Standard library: https://pkg.go.dev/std
- golangci-lint: https://golangci-lint.run/
