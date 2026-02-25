---
name: go-sqlc
description: Go sqlc patterns covering type-safe SQL query generation, migrations, custom types, batch operations, joins, transactions, and PostgreSQL/MySQL/SQLite support.
---

# Go sqlc

This skill should be used when building Go applications with sqlc for type-safe database access. It covers query generation, migrations, custom types, batch operations, and transactions.

## When to Use This Skill

Use this skill when you need to:

- Generate type-safe Go code from SQL queries
- Work with PostgreSQL, MySQL, or SQLite in Go
- Handle joins, aggregations, and batch operations
- Use custom types and enums with sqlc
- Manage database migrations alongside sqlc

## Setup

```bash
go install github.com/sqlc-dev/sqlc/cmd/sqlc@latest
```

## Configuration

```yaml
# sqlc.yaml
version: "2"
sql:
  - engine: "postgresql"
    queries: "query/"
    schema: "schema/"
    gen:
      go:
        package: "db"
        out: "internal/db"
        sql_package: "pgx/v5"
        emit_json_tags: true
        emit_empty_slices: true
```

## Schema Definition

```sql
-- schema/001_users.sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL DEFAULT 'user',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    published BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## SQL Queries

```sql
-- query/users.sql

-- name: GetUser :one
SELECT id, name, email, role, created_at
FROM users
WHERE id = $1;

-- name: ListUsers :many
SELECT id, name, email, role, created_at
FROM users
ORDER BY created_at DESC
LIMIT $1 OFFSET $2;

-- name: CreateUser :one
INSERT INTO users (name, email, role)
VALUES ($1, $2, $3)
RETURNING id, name, email, role, created_at;

-- name: UpdateUser :one
UPDATE users
SET name = $2, email = $3
WHERE id = $1
RETURNING id, name, email, role, created_at;

-- name: DeleteUser :exec
DELETE FROM users WHERE id = $1;

-- name: CountUsers :one
SELECT count(*) FROM users;
```

## Joins and Complex Queries

```sql
-- query/posts.sql

-- name: GetPostWithAuthor :one
SELECT
    p.id, p.title, p.body, p.published, p.created_at,
    u.name AS author_name, u.email AS author_email
FROM posts p
JOIN users u ON u.id = p.user_id
WHERE p.id = $1;

-- name: ListPostsByUser :many
SELECT id, title, body, published, created_at
FROM posts
WHERE user_id = $1
ORDER BY created_at DESC;

-- name: ListPublishedPosts :many
SELECT
    p.id, p.title, p.body, p.created_at,
    u.name AS author_name
FROM posts p
JOIN users u ON u.id = p.user_id
WHERE p.published = true
ORDER BY p.created_at DESC
LIMIT $1 OFFSET $2;
```

## Using Generated Code

```go
package main

import (
    "context"
    "log"

    "github.com/jackc/pgx/v5/pgxpool"
    "myapp/internal/db"
)

func main() {
    ctx := context.Background()
    pool, err := pgxpool.New(ctx, "postgres://localhost:5432/mydb")
    if err != nil {
        log.Fatal(err)
    }
    defer pool.Close()

    queries := db.New(pool)

    // Create a user
    user, err := queries.CreateUser(ctx, db.CreateUserParams{
        Name:  "Alice",
        Email: "alice@example.com",
        Role:  "admin",
    })
    if err != nil {
        log.Fatal(err)
    }

    // List users with pagination
    users, err := queries.ListUsers(ctx, db.ListUsersParams{
        Limit:  10,
        Offset: 0,
    })
    if err != nil {
        log.Fatal(err)
    }

    // Get post with author info
    post, err := queries.GetPostWithAuthor(ctx, 1)
    if err != nil {
        log.Fatal(err)
    }
    log.Printf("Post by %s: %s", post.AuthorName, post.Title)
}
```

## Transactions

```go
func CreatePostWithTags(ctx context.Context, pool *pgxpool.Pool, params CreatePostParams) error {
    tx, err := pool.Begin(ctx)
    if err != nil {
        return err
    }
    defer tx.Rollback(ctx)

    queries := db.New(tx)

    post, err := queries.CreatePost(ctx, db.CreatePostParams{
        UserID: params.UserID,
        Title:  params.Title,
        Body:   params.Body,
    })
    if err != nil {
        return err
    }

    for _, tag := range params.Tags {
        err := queries.AddPostTag(ctx, db.AddPostTagParams{
            PostID: post.ID,
            Tag:    tag,
        })
        if err != nil {
            return err
        }
    }

    return tx.Commit(ctx)
}
```

## Batch Operations

```sql
-- name: CreateUsers :batchone
INSERT INTO users (name, email, role)
VALUES ($1, $2, $3)
RETURNING id, name, email, role, created_at;
```

```go
// Use batch insert
batch := queries.CreateUsers(ctx, []db.CreateUsersParams{
    {Name: "Alice", Email: "alice@example.com", Role: "user"},
    {Name: "Bob", Email: "bob@example.com", Role: "user"},
})
batch.QueryRow(func(i int, user db.User, err error) {
    if err != nil {
        log.Printf("row %d: %v", i, err)
        return
    }
    log.Printf("created: %s", user.Name)
})
```

## Generate Code

```bash
sqlc generate
sqlc vet        # validate queries
sqlc diff       # show pending changes
```

## Additional Resources

- sqlc: https://sqlc.dev/
- Docs: https://docs.sqlc.dev/
- Playground: https://play.sqlc.dev/
