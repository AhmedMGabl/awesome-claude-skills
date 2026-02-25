---
name: go-testing
description: Go testing patterns covering table-driven tests, subtests, mocking with interfaces, HTTP handler testing, benchmarks, fuzz testing, testcontainers, and golden files.
---

# Go Testing

This skill should be used when writing tests for Go applications. It covers table-driven tests, subtests, mocking, HTTP testing, benchmarks, fuzz testing, and integration testing.

## When to Use This Skill

Use this skill when you need to:

- Write table-driven tests with subtests
- Mock dependencies using interfaces
- Test HTTP handlers and middleware
- Write benchmarks and fuzz tests
- Use testcontainers for integration tests

## Table-Driven Tests

```go
func TestAdd(t *testing.T) {
    tests := []struct {
        name string
        a, b int
        want int
    }{
        {name: "positive", a: 2, b: 3, want: 5},
        {name: "negative", a: -1, b: -2, want: -3},
        {name: "zero", a: 0, b: 0, want: 0},
        {name: "mixed", a: -1, b: 5, want: 4},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := Add(tt.a, tt.b)
            if got != tt.want {
                t.Errorf("Add(%d, %d) = %d, want %d", tt.a, tt.b, got, tt.want)
            }
        })
    }
}
```

## Interface-Based Mocking

```go
// Define interface for dependency
type UserRepository interface {
    GetByID(ctx context.Context, id string) (*User, error)
    Create(ctx context.Context, user *User) error
}

// Mock implementation
type mockUserRepo struct {
    users map[string]*User
    err   error
}

func (m *mockUserRepo) GetByID(ctx context.Context, id string) (*User, error) {
    if m.err != nil {
        return nil, m.err
    }
    user, ok := m.users[id]
    if !ok {
        return nil, ErrNotFound
    }
    return user, nil
}

func (m *mockUserRepo) Create(ctx context.Context, user *User) error {
    if m.err != nil {
        return m.err
    }
    m.users[user.ID] = user
    return nil
}

func TestUserService_GetUser(t *testing.T) {
    tests := []struct {
        name    string
        repo    *mockUserRepo
        id      string
        want    *User
        wantErr error
    }{
        {
            name: "found",
            repo: &mockUserRepo{users: map[string]*User{
                "1": {ID: "1", Name: "Alice"},
            }},
            id:   "1",
            want: &User{ID: "1", Name: "Alice"},
        },
        {
            name:    "not found",
            repo:    &mockUserRepo{users: map[string]*User{}},
            id:      "999",
            wantErr: ErrNotFound,
        },
        {
            name:    "repo error",
            repo:    &mockUserRepo{err: errors.New("db down")},
            id:      "1",
            wantErr: errors.New("db down"),
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            svc := NewUserService(tt.repo)
            got, err := svc.GetUser(context.Background(), tt.id)
            if tt.wantErr != nil {
                if err == nil {
                    t.Fatal("expected error, got nil")
                }
                return
            }
            if err != nil {
                t.Fatalf("unexpected error: %v", err)
            }
            if got.Name != tt.want.Name {
                t.Errorf("name = %q, want %q", got.Name, tt.want.Name)
            }
        })
    }
}
```

## HTTP Handler Testing

```go
func TestGetUserHandler(t *testing.T) {
    repo := &mockUserRepo{users: map[string]*User{
        "1": {ID: "1", Name: "Alice", Email: "alice@example.com"},
    }}
    handler := NewUserHandler(repo)

    tests := []struct {
        name       string
        path       string
        wantStatus int
        wantBody   string
    }{
        {
            name:       "valid user",
            path:       "/users/1",
            wantStatus: http.StatusOK,
            wantBody:   `"name":"Alice"`,
        },
        {
            name:       "not found",
            path:       "/users/999",
            wantStatus: http.StatusNotFound,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            req := httptest.NewRequest(http.MethodGet, tt.path, nil)
            rec := httptest.NewRecorder()

            handler.ServeHTTP(rec, req)

            if rec.Code != tt.wantStatus {
                t.Errorf("status = %d, want %d", rec.Code, tt.wantStatus)
            }
            if tt.wantBody != "" && !strings.Contains(rec.Body.String(), tt.wantBody) {
                t.Errorf("body = %q, want to contain %q", rec.Body.String(), tt.wantBody)
            }
        })
    }
}
```

## Testing POST Requests

```go
func TestCreateUserHandler(t *testing.T) {
    body := strings.NewReader(`{"name":"Bob","email":"bob@example.com"}`)
    req := httptest.NewRequest(http.MethodPost, "/users", body)
    req.Header.Set("Content-Type", "application/json")
    rec := httptest.NewRecorder()

    handler.ServeHTTP(rec, req)

    if rec.Code != http.StatusCreated {
        t.Errorf("status = %d, want %d", rec.Code, http.StatusCreated)
    }

    var user User
    json.NewDecoder(rec.Body).Decode(&user)
    if user.Name != "Bob" {
        t.Errorf("name = %q, want %q", user.Name, "Bob")
    }
}
```

## Middleware Testing

```go
func TestAuthMiddleware(t *testing.T) {
    handler := AuthMiddleware(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
    }))

    tests := []struct {
        name       string
        authHeader string
        wantStatus int
    }{
        {name: "valid token", authHeader: "Bearer valid-token", wantStatus: http.StatusOK},
        {name: "missing token", authHeader: "", wantStatus: http.StatusUnauthorized},
        {name: "invalid token", authHeader: "Bearer bad", wantStatus: http.StatusUnauthorized},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            req := httptest.NewRequest(http.MethodGet, "/", nil)
            if tt.authHeader != "" {
                req.Header.Set("Authorization", tt.authHeader)
            }
            rec := httptest.NewRecorder()
            handler.ServeHTTP(rec, req)

            if rec.Code != tt.wantStatus {
                t.Errorf("status = %d, want %d", rec.Code, tt.wantStatus)
            }
        })
    }
}
```

## Benchmarks

```go
func BenchmarkParseConfig(b *testing.B) {
    data := loadTestConfig()
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        ParseConfig(data)
    }
}

func BenchmarkProcessItems(b *testing.B) {
    sizes := []int{10, 100, 1000, 10000}
    for _, size := range sizes {
        b.Run(fmt.Sprintf("size=%d", size), func(b *testing.B) {
            items := generateItems(size)
            b.ResetTimer()
            for i := 0; i < b.N; i++ {
                ProcessItems(items)
            }
        })
    }
}
```

## Fuzz Testing

```go
func FuzzParseEmail(f *testing.F) {
    f.Add("user@example.com")
    f.Add("name+tag@domain.co.uk")
    f.Add("")

    f.Fuzz(func(t *testing.T, input string) {
        result, err := ParseEmail(input)
        if err != nil {
            return // invalid input is fine
        }
        if result.Domain == "" {
            t.Error("parsed email has empty domain")
        }
    })
}
```

## Test Helpers

```go
func TestMain(m *testing.M) {
    // Setup before all tests
    setupTestDB()
    code := m.Run()
    // Cleanup after all tests
    teardownTestDB()
    os.Exit(code)
}

// Helper to reduce boilerplate
func assertEqual(t *testing.T, got, want interface{}) {
    t.Helper()
    if got != want {
        t.Errorf("got %v, want %v", got, want)
    }
}
```

## Running Tests

```bash
go test ./...                    # run all tests
go test -v ./pkg/...             # verbose output
go test -run TestGetUser ./...   # run specific test
go test -bench=. ./...           # run benchmarks
go test -fuzz=FuzzParse ./...    # run fuzz tests
go test -cover ./...             # show coverage
go test -race ./...              # detect data races
go test -count=1 ./...           # disable test caching
```

## Additional Resources

- Testing: https://go.dev/doc/tutorial/add-a-test
- Table-driven tests: https://go.dev/wiki/TableDrivenTests
- Fuzz testing: https://go.dev/doc/tutorial/fuzz
