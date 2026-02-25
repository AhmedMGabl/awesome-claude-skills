---
name: rust-sqlx
description: Rust SQLx patterns covering compile-time checked queries, migrations, connection pools, transactions, custom types, PostgreSQL/MySQL/SQLite, and async database access.
---

# Rust SQLx

This skill should be used when building Rust applications with SQLx for async database access. It covers compile-time queries, migrations, connection pools, transactions, and custom types.

## When to Use This Skill

Use this skill when you need to:

- Run compile-time verified SQL queries in Rust
- Work with PostgreSQL, MySQL, or SQLite
- Manage database migrations
- Use connection pools and transactions
- Map custom types to database columns

## Setup

```toml
# Cargo.toml
[dependencies]
sqlx = { version = "0.7", features = ["runtime-tokio", "postgres", "chrono", "uuid"] }
tokio = { version = "1", features = ["full"] }
chrono = { version = "0.4", features = ["serde"] }
uuid = { version = "1", features = ["v4", "serde"] }
```

## Connection Pool

```rust
use sqlx::postgres::PgPoolOptions;

#[tokio::main]
async fn main() -> Result<(), sqlx::Error> {
    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect("postgres://user:pass@localhost/mydb")
        .await?;

    // Run migrations
    sqlx::migrate!("./migrations").run(&pool).await?;

    Ok(())
}
```

## Compile-Time Checked Queries

```rust
use sqlx::FromRow;
use chrono::{DateTime, Utc};
use uuid::Uuid;

#[derive(FromRow, Debug)]
struct User {
    id: Uuid,
    name: String,
    email: String,
    created_at: DateTime<Utc>,
}

// Compile-time checked with query_as!
async fn get_user(pool: &sqlx::PgPool, id: Uuid) -> Result<User, sqlx::Error> {
    let user = sqlx::query_as!(
        User,
        "SELECT id, name, email, created_at FROM users WHERE id = $1",
        id
    )
    .fetch_one(pool)
    .await?;
    Ok(user)
}

async fn list_users(pool: &sqlx::PgPool, limit: i64, offset: i64) -> Result<Vec<User>, sqlx::Error> {
    let users = sqlx::query_as!(
        User,
        "SELECT id, name, email, created_at FROM users ORDER BY created_at DESC LIMIT $1 OFFSET $2",
        limit,
        offset
    )
    .fetch_all(pool)
    .await?;
    Ok(users)
}

async fn create_user(pool: &sqlx::PgPool, name: &str, email: &str) -> Result<User, sqlx::Error> {
    let user = sqlx::query_as!(
        User,
        "INSERT INTO users (id, name, email) VALUES ($1, $2, $3) RETURNING id, name, email, created_at",
        Uuid::new_v4(),
        name,
        email
    )
    .fetch_one(pool)
    .await?;
    Ok(user)
}
```

## Dynamic Queries

```rust
use sqlx::QueryBuilder;

async fn search_users(pool: &sqlx::PgPool, name: Option<&str>, email: Option<&str>) -> Result<Vec<User>, sqlx::Error> {
    let mut builder = QueryBuilder::new("SELECT id, name, email, created_at FROM users WHERE 1=1");

    if let Some(name) = name {
        builder.push(" AND name ILIKE ");
        builder.push_bind(format!("%{}%", name));
    }
    if let Some(email) = email {
        builder.push(" AND email = ");
        builder.push_bind(email);
    }

    builder.push(" ORDER BY created_at DESC");

    let users = builder.build_query_as::<User>()
        .fetch_all(pool)
        .await?;
    Ok(users)
}
```

## Transactions

```rust
async fn transfer_funds(
    pool: &sqlx::PgPool,
    from_id: Uuid,
    to_id: Uuid,
    amount: f64,
) -> Result<(), sqlx::Error> {
    let mut tx = pool.begin().await?;

    sqlx::query!(
        "UPDATE accounts SET balance = balance - $1 WHERE id = $2",
        amount, from_id
    )
    .execute(&mut *tx)
    .await?;

    sqlx::query!(
        "UPDATE accounts SET balance = balance + $1 WHERE id = $2",
        amount, to_id
    )
    .execute(&mut *tx)
    .await?;

    tx.commit().await?;
    Ok(())
}
```

## Custom Types

```rust
#[derive(sqlx::Type, Debug)]
#[sqlx(type_name = "user_role", rename_all = "lowercase")]
enum UserRole {
    Admin,
    Editor,
    Viewer,
}

#[derive(FromRow)]
struct UserWithRole {
    id: Uuid,
    name: String,
    role: UserRole,
}
```

## Migrations

```bash
# Install CLI
cargo install sqlx-cli

# Create and run migrations
sqlx migrate add create_users
sqlx migrate run
sqlx migrate revert

# Prepare for offline compile-time checks
cargo sqlx prepare
```

```sql
-- migrations/001_create_users.up.sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## Additional Resources

- SQLx: https://github.com/launchbadge/sqlx
- Docs: https://docs.rs/sqlx/
- Examples: https://github.com/launchbadge/sqlx/tree/main/examples
