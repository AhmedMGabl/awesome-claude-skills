---
name: rust-axum
description: Rust Axum patterns covering routing, extractors, state management, middleware with Tower, error handling, WebSockets, and integration with SQLx and Tokio.
---

# Rust Axum

This skill should be used when building web APIs with Rust Axum. It covers routing, extractors, state, Tower middleware, error handling, and database integration.

## When to Use This Skill

Use this skill when you need to:

- Build async web APIs with Axum and Tokio
- Use extractors for typed request data
- Add Tower middleware layers
- Handle errors with custom types
- Integrate with SQLx for database access

## Setup

```toml
# Cargo.toml
[dependencies]
axum = "0.7"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
tower-http = { version = "0.5", features = ["cors", "trace"] }
```

## Basic Server

```rust
use axum::{
    routing::{get, post, put, delete},
    Router,
};

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/api/users", get(list_users).post(create_user))
        .route("/api/users/:id", get(get_user).put(update_user).delete(delete_user));

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
```

## Extractors

```rust
use axum::{
    extract::{Path, Query, State, Json},
    http::StatusCode,
    response::IntoResponse,
};
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
struct Pagination {
    page: Option<u32>,
    limit: Option<u32>,
}

#[derive(Deserialize)]
struct CreateUser {
    name: String,
    email: String,
}

#[derive(Serialize)]
struct User {
    id: i64,
    name: String,
    email: String,
}

async fn get_user(Path(id): Path<i64>) -> impl IntoResponse {
    Json(User { id, name: "Alice".into(), email: "alice@example.com".into() })
}

async fn list_users(Query(pagination): Query<Pagination>) -> impl IntoResponse {
    let page = pagination.page.unwrap_or(1);
    let limit = pagination.limit.unwrap_or(10);
    Json(serde_json::json!({"page": page, "limit": limit}))
}

async fn create_user(Json(input): Json<CreateUser>) -> impl IntoResponse {
    (StatusCode::CREATED, Json(serde_json::json!({
        "name": input.name,
        "email": input.email
    })))
}
```

## Shared State

```rust
use std::sync::Arc;
use sqlx::PgPool;

#[derive(Clone)]
struct AppState {
    db: PgPool,
}

#[tokio::main]
async fn main() {
    let pool = PgPool::connect("postgres://localhost/mydb").await.unwrap();
    let state = AppState { db: pool };

    let app = Router::new()
        .route("/api/users", get(list_users))
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

async fn list_users(State(state): State<AppState>) -> impl IntoResponse {
    let users = sqlx::query_as!(User, "SELECT id, name, email FROM users")
        .fetch_all(&state.db)
        .await
        .unwrap();
    Json(users)
}
```

## Error Handling

```rust
use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
    Json,
};

enum AppError {
    NotFound(String),
    BadRequest(String),
    Internal(anyhow::Error),
}

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        let (status, message) = match self {
            AppError::NotFound(msg) => (StatusCode::NOT_FOUND, msg),
            AppError::BadRequest(msg) => (StatusCode::BAD_REQUEST, msg),
            AppError::Internal(err) => (StatusCode::INTERNAL_SERVER_ERROR, err.to_string()),
        };
        (status, Json(serde_json::json!({"error": message}))).into_response()
    }
}

async fn get_user(Path(id): Path<i64>) -> Result<Json<User>, AppError> {
    let user = find_user(id)
        .ok_or_else(|| AppError::NotFound(format!("User {} not found", id)))?;
    Ok(Json(user))
}
```

## Middleware with Tower

```rust
use tower_http::{cors::CorsLayer, trace::TraceLayer};
use axum::http::Method;

let app = Router::new()
    .route("/api/users", get(list_users))
    .layer(TraceLayer::new_for_http())
    .layer(
        CorsLayer::new()
            .allow_origin(["http://localhost:3000".parse().unwrap()])
            .allow_methods([Method::GET, Method::POST, Method::PUT, Method::DELETE])
    );
```

## Nested Routers

```rust
fn user_routes() -> Router<AppState> {
    Router::new()
        .route("/", get(list_users).post(create_user))
        .route("/:id", get(get_user).put(update_user).delete(delete_user))
}

fn post_routes() -> Router<AppState> {
    Router::new()
        .route("/", get(list_posts).post(create_post))
        .route("/:id", get(get_post))
}

let app = Router::new()
    .nest("/api/users", user_routes())
    .nest("/api/posts", post_routes())
    .with_state(state);
```

## Additional Resources

- Axum: https://github.com/tokio-rs/axum
- Docs: https://docs.rs/axum/
- Examples: https://github.com/tokio-rs/axum/tree/main/examples
