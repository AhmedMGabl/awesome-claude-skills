---
name: rust-actix-web
description: Rust Actix Web patterns covering HTTP routing, extractors, middleware, JSON APIs, error handling, WebSockets, database integration, and production deployment.
---

# Rust Actix Web

This skill should be used when building web APIs with Rust Actix Web. It covers routing, extractors, middleware, error handling, database integration, and deployment.

## When to Use This Skill

Use this skill when you need to:

- Build high-performance HTTP APIs with Actix Web
- Use extractors for path, query, and JSON data
- Add middleware for auth, logging, and CORS
- Handle errors with custom response types
- Integrate with databases using SQLx or Diesel

## Setup

```toml
# Cargo.toml
[dependencies]
actix-web = "4"
actix-rt = "2"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
tokio = { version = "1", features = ["full"] }
```

## Basic Server

```rust
use actix_web::{web, App, HttpServer, HttpResponse, middleware};

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .wrap(middleware::Logger::default())
            .service(
                web::scope("/api")
                    .route("/users", web::get().to(list_users))
                    .route("/users", web::post().to(create_user))
                    .route("/users/{id}", web::get().to(get_user))
                    .route("/users/{id}", web::put().to(update_user))
                    .route("/users/{id}", web::delete().to(delete_user))
            )
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}
```

## Extractors

```rust
use actix_web::{web, HttpResponse};
use serde::Deserialize;

#[derive(Deserialize)]
struct UserPath {
    id: i64,
}

#[derive(Deserialize)]
struct PaginationQuery {
    page: Option<u32>,
    limit: Option<u32>,
}

#[derive(Deserialize)]
struct CreateUserBody {
    name: String,
    email: String,
}

async fn get_user(path: web::Path<UserPath>) -> HttpResponse {
    let user_id = path.id;
    // fetch user by ID
    HttpResponse::Ok().json(serde_json::json!({"id": user_id}))
}

async fn list_users(query: web::Query<PaginationQuery>) -> HttpResponse {
    let page = query.page.unwrap_or(1);
    let limit = query.limit.unwrap_or(10);
    HttpResponse::Ok().json(serde_json::json!({"page": page, "limit": limit}))
}

async fn create_user(body: web::Json<CreateUserBody>) -> HttpResponse {
    HttpResponse::Created().json(serde_json::json!({
        "name": body.name,
        "email": body.email
    }))
}
```

## App State

```rust
use std::sync::Mutex;

struct AppState {
    db_pool: sqlx::PgPool,
    config: AppConfig,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let pool = sqlx::PgPool::connect("postgres://localhost/mydb").await.unwrap();
    let state = web::Data::new(AppState {
        db_pool: pool,
        config: AppConfig::from_env(),
    });

    HttpServer::new(move || {
        App::new()
            .app_data(state.clone())
            .route("/users", web::get().to(list_users))
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}

async fn list_users(state: web::Data<AppState>) -> HttpResponse {
    let users = sqlx::query_as!(User, "SELECT * FROM users")
        .fetch_all(&state.db_pool)
        .await
        .unwrap();
    HttpResponse::Ok().json(users)
}
```

## Error Handling

```rust
use actix_web::{HttpResponse, ResponseError};
use std::fmt;

#[derive(Debug)]
enum AppError {
    NotFound(String),
    BadRequest(String),
    Internal(String),
}

impl fmt::Display for AppError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            AppError::NotFound(msg) => write!(f, "Not found: {}", msg),
            AppError::BadRequest(msg) => write!(f, "Bad request: {}", msg),
            AppError::Internal(msg) => write!(f, "Internal error: {}", msg),
        }
    }
}

impl ResponseError for AppError {
    fn error_response(&self) -> HttpResponse {
        match self {
            AppError::NotFound(msg) => {
                HttpResponse::NotFound().json(serde_json::json!({"error": msg}))
            }
            AppError::BadRequest(msg) => {
                HttpResponse::BadRequest().json(serde_json::json!({"error": msg}))
            }
            AppError::Internal(msg) => {
                HttpResponse::InternalServerError().json(serde_json::json!({"error": msg}))
            }
        }
    }
}

async fn get_user(path: web::Path<i64>) -> Result<HttpResponse, AppError> {
    let id = path.into_inner();
    let user = find_user(id)
        .ok_or_else(|| AppError::NotFound(format!("User {} not found", id)))?;
    Ok(HttpResponse::Ok().json(user))
}
```

## Middleware

```rust
use actix_web::middleware;
use actix_cors::Cors;

App::new()
    .wrap(middleware::Logger::default())
    .wrap(
        Cors::default()
            .allowed_origin("http://localhost:3000")
            .allowed_methods(vec!["GET", "POST", "PUT", "DELETE"])
            .allowed_headers(vec!["Authorization", "Content-Type"])
            .max_age(3600)
    )
```

## Additional Resources

- Actix Web: https://actix.rs/
- Docs: https://docs.rs/actix-web/
- Examples: https://github.com/actix/examples
