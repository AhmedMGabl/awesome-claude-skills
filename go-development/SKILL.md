---
name: go-development
description: Go development patterns covering structs, interfaces, error handling, goroutines, channels, HTTP servers, middleware, testing, database access, and CLI tools with Cobra.
---

# Go Development

This skill should be used when building applications with Go. It covers structs, interfaces, error handling, concurrency, HTTP servers, testing, and CLI tools.

## When to Use This Skill

Use this skill when you need to:

- Build HTTP APIs with net/http, Chi, or Gin
- Work with goroutines, channels, and concurrency
- Handle errors idiomatically in Go
- Write table-driven tests
- Build CLI tools with Cobra

## Setup

```bash
go mod init github.com/myorg/myapp
```

## Structs and Interfaces

```go
type User struct {
    ID        string    `json:"id" db:"id"`
    Name      string    `json:"name" db:"name"`
    Email     string    `json:"email" db:"email"`
    CreatedAt time.Time `json:"created_at" db:"created_at"`
}

type UserRepository interface {
    GetByID(ctx context.Context, id string) (*User, error)
    Create(ctx context.Context, user *User) error
    List(ctx context.Context, limit, offset int) ([]User, error)
}

type UserService struct {
    repo UserRepository
}

func NewUserService(repo UserRepository) *UserService {
    return &UserService{repo: repo}
}
```

## Error Handling

```go
var (
    ErrNotFound   = errors.New("not found")
    ErrConflict   = errors.New("already exists")
)

type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation: %s %s", e.Field, e.Message)
}

func (s *UserService) GetUser(ctx context.Context, id string) (*User, error) {
    user, err := s.repo.GetByID(ctx, id)
    if err != nil {
        return nil, fmt.Errorf("get user %s: %w", id, err)
    }
    return user, nil
}

// Caller checks errors
if errors.Is(err, ErrNotFound) { /* handle */ }
var ve *ValidationError
if errors.As(err, &ve) { /* handle */ }
```

## Goroutines and Channels

```go
func FetchAll(ctx context.Context, urls []string) []string {
    results := make(chan string, len(urls))
    var wg sync.WaitGroup

    for _, url := range urls {
        wg.Add(1)
        go func(u string) {
            defer wg.Done()
            resp, err := http.Get(u)
            if err != nil {
                results <- ""
                return
            }
            defer resp.Body.Close()
            body, _ := io.ReadAll(resp.Body)
            results <- string(body)
        }(url)
    }

    go func() { wg.Wait(); close(results) }()

    var out []string
    for r := range results {
        out = append(out, r)
    }
    return out
}
```

## HTTP Server (net/http)

```go
mux := http.NewServeMux()
mux.HandleFunc("GET /api/users/{id}", func(w http.ResponseWriter, r *http.Request) {
    id := r.PathValue("id")
    user, err := svc.GetUser(r.Context(), id)
    if err != nil {
        http.Error(w, err.Error(), http.StatusNotFound)
        return
    }
    json.NewEncoder(w).Encode(user)
})

srv := &http.Server{Addr: ":8080", Handler: mux}
srv.ListenAndServe()
```

## Middleware

```go
func LoggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s %v", r.Method, r.URL.Path, time.Since(start))
    })
}

func AuthMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        token := r.Header.Get("Authorization")
        if token == "" {
            http.Error(w, "unauthorized", http.StatusUnauthorized)
            return
        }
        ctx := context.WithValue(r.Context(), "userID", "parsed-id")
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

## Testing

```go
func TestGetUser(t *testing.T) {
    tests := []struct {
        name    string
        id      string
        want    *User
        wantErr error
    }{
        {name: "found", id: "1", want: &User{ID: "1", Name: "Alice"}, wantErr: nil},
        {name: "not found", id: "999", want: nil, wantErr: ErrNotFound},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            svc := NewUserService(&mockRepo{})
            got, err := svc.GetUser(context.Background(), tt.id)
            if !errors.Is(err, tt.wantErr) {
                t.Errorf("error = %v, want %v", err, tt.wantErr)
            }
            if tt.want != nil && got.Name != tt.want.Name {
                t.Errorf("name = %v, want %v", got.Name, tt.want.Name)
            }
        })
    }
}
```

## Additional Resources

- Go: https://go.dev/doc/
- Effective Go: https://go.dev/doc/effective_go
- Go by Example: https://gobyexample.com/
