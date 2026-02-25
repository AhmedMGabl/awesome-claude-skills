---
name: rust-development
description: Rust development covering ownership and borrowing, lifetimes, traits, error handling with Result/Option, async with tokio, structs and enums, pattern matching, cargo workspace, testing, and production-ready systems programming patterns.
---

# Rust Development Skill

This skill provides comprehensive guidance for building production-quality Rust applications. It covers core language concepts, async programming, web services, testing, and tooling. All code examples are runnable and follow idiomatic Rust conventions.

---

## 1. Project Setup

### Single Binary Project

```bash
cargo new my-app
cd my-app
```

### Library Crate

```bash
cargo new my-lib --lib
```

### Cargo.toml — Dependency Management

```toml
[package]
name = "my-app"
version = "0.1.0"
edition = "2021"
rust-version = "1.75"
authors = ["Your Name <you@example.com>"]
description = "A production Rust service"
license = "MIT"

[dependencies]
tokio = { version = "1", features = ["full"] }
axum = "0.7"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
thiserror = "1"
anyhow = "1"
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }
uuid = { version = "1", features = ["v4", "serde"] }

[dev-dependencies]
tokio-test = "0.4"
tower = { version = "0.4", features = ["util"] }
http-body-util = "0.1"

[profile.release]
lto = true
codegen-units = 1
strip = true
panic = "abort"
```

### Cargo Workspace

For multi-crate projects, define a workspace in the root `Cargo.toml`:

```toml
[workspace]
members = [
    "crates/api",
    "crates/core",
    "crates/db",
]
resolver = "2"

[workspace.dependencies]
serde = { version = "1", features = ["derive"] }
tokio = { version = "1", features = ["full"] }
tracing = "0.1"
```

Each member crate references workspace dependencies:

```toml
# crates/api/Cargo.toml
[package]
name = "api"
version = "0.1.0"
edition = "2021"

[dependencies]
serde.workspace = true
tokio.workspace = true
core = { path = "../core" }
```

Build and run workspace members:

```bash
cargo build -p api
cargo run -p api
cargo test --workspace
```

---

## 2. Ownership, Borrowing, and Lifetimes

### Ownership Rules

Each value in Rust has exactly one owner. When the owner goes out of scope, the value is dropped. Assignment moves ownership for non-Copy types.

```rust
fn demonstrate_ownership() {
    // String is heap-allocated; assignment moves ownership.
    let s1 = String::from("hello");
    let s2 = s1; // s1 is moved to s2; s1 is no longer valid.
    // println!("{s1}"); // compile error: value used after move
    println!("{s2}");

    // Integers implement Copy, so assignment copies the value.
    let x = 42;
    let y = x; // x is still valid.
    println!("{x} {y}");

    // Passing a String to a function moves it.
    let name = String::from("Rust");
    take_ownership(name);
    // println!("{name}"); // compile error: name was moved

    // Clone to retain ownership when a deep copy is acceptable.
    let original = String::from("data");
    let cloned = original.clone();
    println!("{original} {cloned}");
}

fn take_ownership(s: String) {
    println!("Took ownership of: {s}");
} // s is dropped here
```

### Borrowing — References

Borrowing grants temporary access without transferring ownership. Shared references (`&T`) allow multiple readers. Mutable references (`&mut T`) allow exactly one writer and no concurrent readers.

```rust
fn demonstrate_borrowing() {
    let mut data = vec![1, 2, 3];

    // Shared (immutable) borrows — multiple allowed simultaneously.
    let r1 = &data;
    let r2 = &data;
    println!("Shared: {r1:?} {r2:?}");

    // Mutable borrow — exclusive access required.
    let r3 = &mut data;
    r3.push(4);
    println!("Mutated: {r3:?}");

    // Function borrowing patterns.
    let total = sum_slice(&data);
    println!("Sum: {total}");

    append_value(&mut data, 5);
    println!("After append: {data:?}");
}

fn sum_slice(values: &[i32]) -> i32 {
    values.iter().sum()
}

fn append_value(values: &mut Vec<i32>, val: i32) {
    values.push(val);
}
```

### Lifetimes

Lifetimes ensure references remain valid. The compiler infers most lifetimes, but explicit annotations are required when the relationship between input and output lifetimes is ambiguous.

```rust
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() >= y.len() { x } else { y }
}

struct Excerpt<'a> {
    text: &'a str,
}

impl<'a> Excerpt<'a> {
    fn first_word(&self) -> &str {
        self.text.split_whitespace().next().unwrap_or("")
    }
}

fn demonstrate_lifetimes() {
    let novel = String::from("Call me Ishmael. Some years ago...");
    let first_sentence;
    {
        let excerpt = Excerpt {
            text: novel.split('.').next().unwrap(),
        };
        first_sentence = excerpt.first_word();
    }
    println!("First word: {first_sentence}");

    let result = longest("long string", "short");
    println!("Longest: {result}");
}
```

---

## 3. Structs, Enums, Pattern Matching, and Destructuring

### Structs

```rust
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct User {
    pub id: Uuid,
    pub email: String,
    pub name: String,
    pub role: Role,
}

impl User {
    pub fn new(email: impl Into<String>, name: impl Into<String>) -> Self {
        Self {
            id: Uuid::new_v4(),
            email: email.into(),
            name: name.into(),
            role: Role::Viewer,
        }
    }

    pub fn is_admin(&self) -> bool {
        matches!(self.role, Role::Admin)
    }

    pub fn promote(&mut self) {
        self.role = match self.role {
            Role::Viewer => Role::Editor,
            Role::Editor => Role::Admin,
            Role::Admin => Role::Admin,
        };
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct UserId(pub Uuid);

pub struct Authenticated;
```

### Enums

```rust
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum Role {
    Viewer,
    Editor,
    Admin,
}

#[derive(Debug)]
pub enum Command {
    Quit,
    Echo(String),
    Move { x: i32, y: i32 },
    Color(u8, u8, u8),
}
```

### Pattern Matching and Destructuring

```rust
fn handle_command(cmd: Command) -> String {
    match cmd {
        Command::Quit => "Goodbye".to_string(),
        Command::Echo(msg) => msg,
        Command::Move { x, y } => format!("Moving to ({x}, {y})"),
        Command::Color(r, g, b) => format!("#{r:02x}{g:02x}{b:02x}"),
    }
}

fn demonstrate_patterns() {
    let (a, b, c) = (1, "hello", 3.14);
    println!("{a} {b} {c}");

    let user = User::new("alice@example.com", "Alice");
    let User { ref email, ref name, .. } = user;
    println!("{name} <{email}>");

    let maybe_value: Option<i32> = Some(42);
    if let Some(v) = maybe_value {
        println!("Got: {v}");
    }

    let config_value: Option<&str> = Some("production");
    let Some(env) = config_value else {
        println!("No environment configured");
        return;
    };
    println!("Environment: {env}");

    let temperature = 35;
    let description = match temperature {
        t if t < 0 => "freezing",
        0..=15 => "cold",
        16..=25 => "comfortable",
        26..=35 => "warm",
        _ => "hot",
    };
    println!("Weather: {description}");

    let points = vec![(1, 2), (3, 4), (5, 6)];
    for (i, (x, y)) in points.iter().enumerate() {
        println!("Point {i}: ({x}, {y})");
    }
}
```

---

## 4. Traits and Generics

### Defining and Implementing Traits

```rust
use std::fmt;

pub trait Summary {
    fn summarize(&self) -> String;

    fn preview(&self) -> String {
        let s = self.summarize();
        if s.len() > 50 {
            format!("{}...", &s[..50])
        } else {
            s
        }
    }
}

pub trait Validate {
    type Error;
    fn validate(&self) -> Result<(), Self::Error>;
}

#[derive(Debug)]
pub struct Article {
    pub title: String,
    pub body: String,
}

impl Summary for Article {
    fn summarize(&self) -> String {
        format!("{}: {}", self.title, &self.body[..self.body.len().min(100)])
    }
}

impl fmt::Display for Article {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "[Article] {}", self.title)
    }
}
```

### Generics and Trait Bounds

```rust
fn print_summary(item: &impl Summary) {
    println!("{}", item.summarize());
}

fn print_summary_verbose<T: Summary>(item: &T) {
    println!("{}", item.summarize());
}

fn process_item<T>(item: &T) -> String
where
    T: Summary + fmt::Display + fmt::Debug,
{
    tracing::debug!(?item, "Processing item");
    format!("{} — {}", item, item.summarize())
}

fn create_default_article() -> impl Summary {
    Article {
        title: "Default".to_string(),
        body: "No content yet.".to_string(),
    }
}
```

### Dynamic Dispatch with `dyn`

```rust
pub struct NotificationService {
    channels: Vec<Box<dyn NotificationChannel>>,
}

pub trait NotificationChannel: Send + Sync {
    fn send(&self, message: &str) -> Result<(), String>;
    fn name(&self) -> &str;
}

pub struct EmailChannel { smtp_host: String }

impl NotificationChannel for EmailChannel {
    fn send(&self, message: &str) -> Result<(), String> {
        println!("Sending email via {}: {message}", self.smtp_host);
        Ok(())
    }
    fn name(&self) -> &str { "email" }
}

pub struct SlackChannel { webhook_url: String }

impl NotificationChannel for SlackChannel {
    fn send(&self, message: &str) -> Result<(), String> {
        println!("Posting to Slack {}: {message}", self.webhook_url);
        Ok(())
    }
    fn name(&self) -> &str { "slack" }
}

impl NotificationService {
    pub fn new() -> Self {
        Self { channels: Vec::new() }
    }

    pub fn add_channel(&mut self, channel: Box<dyn NotificationChannel>) {
        self.channels.push(channel);
    }

    pub fn broadcast(&self, message: &str) {
        for channel in &self.channels {
            if let Err(e) = channel.send(message) {
                eprintln!("Failed to send via {}: {e}", channel.name());
            }
        }
    }
}
```

---

## 5. Error Handling

### Result, Option, and the `?` Operator

```rust
use std::fs;

fn read_config_value(path: &str, key: &str) -> Result<String, Box<dyn std::error::Error>> {
    let contents = fs::read_to_string(path)?;
    let value = contents
        .lines()
        .find(|line| line.starts_with(key))
        .ok_or_else(|| format!("Key '{key}' not found"))?
        .split('=')
        .nth(1)
        .ok_or_else(|| format!("Malformed line for key '{key}'"))?
        .trim()
        .to_string();
    Ok(value)
}

fn parse_port(input: Option<&str>) -> u16 {
    input
        .and_then(|s| s.parse::<u16>().ok())
        .unwrap_or(8080)
}
```

### Typed Errors with `thiserror`

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("User not found: {id}")]
    UserNotFound { id: String },

    #[error("Validation failed: {0}")]
    Validation(String),

    #[error("Database error")]
    Database(#[source] Box<dyn std::error::Error + Send + Sync>),

    #[error("Unauthorized: {reason}")]
    Unauthorized { reason: String },

    #[error(transparent)]
    Internal(#[from] anyhow::Error),
}

impl axum::response::IntoResponse for AppError {
    fn into_response(self) -> axum::response::Response {
        use axum::http::StatusCode;
        let (status, message) = match &self {
            AppError::UserNotFound { .. } => (StatusCode::NOT_FOUND, self.to_string()),
            AppError::Validation(_) => (StatusCode::BAD_REQUEST, self.to_string()),
            AppError::Unauthorized { .. } => (StatusCode::UNAUTHORIZED, self.to_string()),
            AppError::Database(_) | AppError::Internal(_) => {
                tracing::error!(?self, "Internal error");
                (StatusCode::INTERNAL_SERVER_ERROR, "Internal server error".into())
            }
        };
        (status, axum::Json(serde_json::json!({ "error": message }))).into_response()
    }
}
```

### Application-Level Errors with `anyhow`

```rust
use anyhow::{Context, Result};

fn load_and_process() -> Result<()> {
    let config = fs::read_to_string("config.toml")
        .context("Failed to read configuration file")?;
    let port: u16 = config
        .lines()
        .find(|l| l.starts_with("port"))
        .context("Missing 'port' in config")?
        .split('=')
        .nth(1)
        .context("Malformed port line")?
        .trim()
        .parse()
        .context("Invalid port number")?;
    println!("Starting on port {port}");
    Ok(())
}
```

---

## 6. Collections, Iterators, and Closures

### Vec and HashMap

```rust
use std::collections::HashMap;

fn demonstrate_collections() {
    let mut scores: Vec<i32> = Vec::new();
    scores.push(95);
    scores.push(87);
    scores.push(92);
    scores.extend([88, 76, 91]);

    if let Some(&top) = scores.first() {
        println!("First score: {top}");
    }

    let mut word_counts: HashMap<String, usize> = HashMap::new();
    let text = "the quick brown fox jumps over the lazy fox";
    for word in text.split_whitespace() {
        *word_counts.entry(word.to_string()).or_insert(0) += 1;
    }
    println!("Word counts: {word_counts:?}");

    let mut settings: HashMap<&str, String> = HashMap::new();
    settings.entry("theme").or_insert_with(|| "dark".to_string());
}
```

### Iterator Chains and Closures

```rust
#[derive(Debug, Clone)]
struct Product {
    name: String,
    price: f64,
    in_stock: bool,
}

fn demonstrate_iterators() {
    let products = vec![
        Product { name: "Laptop".into(), price: 999.99, in_stock: true },
        Product { name: "Mouse".into(), price: 29.99, in_stock: true },
        Product { name: "Monitor".into(), price: 449.99, in_stock: false },
        Product { name: "Keyboard".into(), price: 79.99, in_stock: true },
        Product { name: "Webcam".into(), price: 59.99, in_stock: true },
    ];

    let affordable: Vec<String> = products.iter()
        .filter(|p| p.in_stock && p.price < 100.0)
        .map(|p| format!("{} (${:.2})", p.name, p.price))
        .collect();
    println!("Affordable: {affordable:?}");

    let total: f64 = products.iter()
        .filter(|p| p.in_stock)
        .fold(0.0, |acc, p| acc + p.price);
    println!("Total in-stock value: ${total:.2}");

    let (in_stock, out_of_stock): (Vec<_>, Vec<_>) =
        products.iter().partition(|p| p.in_stock);
    println!("In stock: {}, Out: {}", in_stock.len(), out_of_stock.len());

    let tags: Vec<Vec<&str>> = vec![
        vec!["rust", "systems"],
        vec!["async", "tokio"],
        vec!["web", "axum"],
    ];
    let all_tags: Vec<&str> = tags.iter().flat_map(|t| t.iter().copied()).collect();
    println!("All tags: {all_tags:?}");

    let first_expensive = products.iter().find(|p| p.price > 500.0);
    println!("First expensive: {first_expensive:?}");

    let names: Vec<&str> = vec!["alpha", "beta", "gamma"];
    let values: Vec<i32> = vec![1, 2, 3];
    let pairs: HashMap<&str, i32> = names.into_iter().zip(values).collect();
    println!("Pairs: {pairs:?}");

    let min_price = 50.0;
    let price_filter = |p: &&Product| p.price >= min_price;
    let count = products.iter().filter(price_filter).count();
    println!("Products >= ${min_price}: {count}");
}
```

---

## 7. Async Programming with Tokio

### Basic Async Runtime and Spawning

```rust
use tokio::time::{self, Duration};

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_env_filter("info")
        .init();

    tracing::info!("Application starting");

    let handle_a = tokio::spawn(async {
        time::sleep(Duration::from_millis(100)).await;
        "Task A complete"
    });

    let handle_b = tokio::spawn(async {
        time::sleep(Duration::from_millis(50)).await;
        42
    });

    let result_a = handle_a.await.expect("Task A panicked");
    let result_b = handle_b.await.expect("Task B panicked");
    tracing::info!(%result_a, %result_b, "Tasks finished");
}
```

### `tokio::select!` for Racing Futures

```rust
use tokio::sync::mpsc;
use tokio::time::{self, Duration};

async fn event_loop() {
    let (_tx, mut rx) = mpsc::channel::<String>(32);
    let mut interval = time::interval(Duration::from_secs(5));
    let shutdown = tokio::signal::ctrl_c();
    tokio::pin!(shutdown);

    loop {
        tokio::select! {
            Some(msg) = rx.recv() => {
                tracing::info!(%msg, "Received message");
            }
            _ = interval.tick() => {
                tracing::debug!("Heartbeat tick");
            }
            _ = &mut shutdown => {
                tracing::info!("Shutting down gracefully");
                break;
            }
        }
    }
}
```

### Channels — mpsc and oneshot

```rust
use tokio::sync::{mpsc, oneshot};

#[derive(Debug)]
enum DbCommand {
    Get { key: String, reply: oneshot::Sender<Option<String>> },
    Set { key: String, value: String, reply: oneshot::Sender<()> },
}

async fn db_actor(mut rx: mpsc::Receiver<DbCommand>) {
    let mut store = std::collections::HashMap::new();
    while let Some(cmd) = rx.recv().await {
        match cmd {
            DbCommand::Get { key, reply } => {
                let _ = reply.send(store.get(&key).cloned());
            }
            DbCommand::Set { key, value, reply } => {
                store.insert(key, value);
                let _ = reply.send(());
            }
        }
    }
}

async fn use_db_actor() {
    let (tx, rx) = mpsc::channel(64);
    tokio::spawn(db_actor(rx));

    let (reply_tx, reply_rx) = oneshot::channel();
    tx.send(DbCommand::Set {
        key: "name".into(), value: "Rust".into(), reply: reply_tx,
    }).await.unwrap();
    reply_rx.await.unwrap();

    let (reply_tx, reply_rx) = oneshot::channel();
    tx.send(DbCommand::Get {
        key: "name".into(), reply: reply_tx,
    }).await.unwrap();
    let result = reply_rx.await.unwrap();
    println!("Got: {result:?}");
}
```

### Shared State with `Arc<Mutex<T>>`

```rust
use std::sync::Arc;
use tokio::sync::Mutex;

#[derive(Debug, Default)]
struct AppState {
    request_count: u64,
    active_connections: u32,
}

async fn demonstrate_shared_state() {
    let state = Arc::new(Mutex::new(AppState::default()));

    let mut handles = Vec::new();
    for i in 0..10 {
        let state = Arc::clone(&state);
        handles.push(tokio::spawn(async move {
            let mut guard = state.lock().await;
            guard.request_count += 1;
            tracing::info!(task = i, count = guard.request_count, "Incremented");
        }));
    }

    for handle in handles {
        handle.await.unwrap();
    }

    let final_state = state.lock().await;
    println!("Final count: {}", final_state.request_count);
}
```

---

## 8. HTTP with Axum

### Application Setup with Shared State

```rust
use axum::{
    extract::{Json, Path, Query, State},
    http::StatusCode,
    middleware,
    response::IntoResponse,
    routing::{get, post, put, delete},
    Router,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::RwLock;
use uuid::Uuid;

pub type SharedState = Arc<RwLock<AppData>>;

#[derive(Debug, Default)]
pub struct AppData {
    pub users: std::collections::HashMap<Uuid, User>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct User {
    pub id: Uuid,
    pub name: String,
    pub email: String,
}

#[derive(Debug, Deserialize)]
pub struct CreateUserRequest {
    pub name: String,
    pub email: String,
}

#[derive(Debug, Deserialize)]
pub struct ListParams {
    pub page: Option<u32>,
    pub per_page: Option<u32>,
}

pub fn create_router(state: SharedState) -> Router {
    let api_routes = Router::new()
        .route("/users", get(list_users).post(create_user))
        .route("/users/{id}", get(get_user).put(update_user).delete(delete_user))
        .route("/health", get(health_check));

    Router::new()
        .nest("/api/v1", api_routes)
        .layer(middleware::from_fn(request_logging_middleware))
        .with_state(state)
}
```

### Route Handlers with Extractors

```rust
async fn health_check() -> impl IntoResponse {
    Json(serde_json::json!({ "status": "healthy" }))
}

async fn list_users(
    State(state): State<SharedState>,
    Query(params): Query<ListParams>,
) -> impl IntoResponse {
    let data = state.read().await;
    let page = params.page.unwrap_or(1);
    let per_page = params.per_page.unwrap_or(20);
    let users: Vec<&User> = data.users.values()
        .skip(((page - 1) * per_page) as usize)
        .take(per_page as usize)
        .collect();
    Json(serde_json::json!({ "users": users, "page": page, "total": data.users.len() }))
}

async fn create_user(
    State(state): State<SharedState>,
    Json(payload): Json<CreateUserRequest>,
) -> Result<impl IntoResponse, AppError> {
    if payload.name.is_empty() {
        return Err(AppError::Validation("Name cannot be empty".into()));
    }
    if !payload.email.contains('@') {
        return Err(AppError::Validation("Invalid email address".into()));
    }
    let user = User {
        id: Uuid::new_v4(),
        name: payload.name,
        email: payload.email,
    };
    let mut data = state.write().await;
    data.users.insert(user.id, user.clone());
    Ok((StatusCode::CREATED, Json(user)))
}

async fn get_user(
    State(state): State<SharedState>,
    Path(id): Path<Uuid>,
) -> Result<Json<User>, AppError> {
    let data = state.read().await;
    let user = data.users.get(&id).cloned()
        .ok_or(AppError::UserNotFound { id: id.to_string() })?;
    Ok(Json(user))
}

async fn update_user(
    State(state): State<SharedState>,
    Path(id): Path<Uuid>,
    Json(payload): Json<CreateUserRequest>,
) -> Result<Json<User>, AppError> {
    let mut data = state.write().await;
    let user = data.users.get_mut(&id)
        .ok_or(AppError::UserNotFound { id: id.to_string() })?;
    user.name = payload.name;
    user.email = payload.email;
    Ok(Json(user.clone()))
}

async fn delete_user(
    State(state): State<SharedState>,
    Path(id): Path<Uuid>,
) -> Result<StatusCode, AppError> {
    let mut data = state.write().await;
    data.users.remove(&id)
        .ok_or(AppError::UserNotFound { id: id.to_string() })?;
    Ok(StatusCode::NO_CONTENT)
}
```

### Middleware

```rust
use axum::{extract::Request, middleware::Next, response::Response};
use std::time::Instant;

async fn request_logging_middleware(req: Request, next: Next) -> Response {
    let method = req.method().clone();
    let uri = req.uri().clone();
    let start = Instant::now();
    let response = next.run(req).await;
    let elapsed = start.elapsed();
    tracing::info!(
        %method, %uri,
        status = %response.status(),
        duration_ms = elapsed.as_millis(),
        "Request completed"
    );
    response
}
```

### Server Entrypoint with Graceful Shutdown

```rust
#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter("info,tower_http=debug")
        .init();

    let state: SharedState = Arc::new(RwLock::new(AppData::default()));
    let app = create_router(state);
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await?;

    tracing::info!("Listening on http://0.0.0.0:3000");
    axum::serve(listener, app)
        .with_graceful_shutdown(async {
            tokio::signal::ctrl_c().await
                .expect("Failed to listen for Ctrl+C");
            tracing::info!("Shutdown signal received");
        })
        .await?;
    Ok(())
}
```

---

## 9. Testing

### Unit Tests

Unit tests live in the same file as the code they test, inside a `#[cfg(test)]` module.

```rust
pub fn validate_email(email: &str) -> Result<(), String> {
    if email.is_empty() {
        return Err("Email cannot be empty".into());
    }
    if !email.contains('@') {
        return Err("Email must contain @".into());
    }
    if email.starts_with('@') || email.ends_with('@') {
        return Err("@ cannot be at start or end".into());
    }
    Ok(())
}

pub fn slugify(input: &str) -> String {
    input
        .to_lowercase()
        .chars()
        .map(|c| if c.is_alphanumeric() { c } else { '-' })
        .collect::<String>()
        .split('-')
        .filter(|s| !s.is_empty())
        .collect::<Vec<_>>()
        .join("-")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn valid_email_passes() {
        assert!(validate_email("user@example.com").is_ok());
    }

    #[test]
    fn empty_email_fails() {
        let err = validate_email("").unwrap_err();
        assert_eq!(err, "Email cannot be empty");
    }

    #[test]
    fn email_without_at_fails() {
        assert!(validate_email("invalid").is_err());
    }

    #[test]
    fn email_at_boundary_fails() {
        assert!(validate_email("@start.com").is_err());
        assert!(validate_email("end@").is_err());
    }

    #[test]
    fn slugify_basic() {
        assert_eq!(slugify("Hello World"), "hello-world");
    }

    #[test]
    fn slugify_special_characters() {
        assert_eq!(slugify("Rust & Cargo!"), "rust-cargo");
    }

    #[test]
    fn slugify_multiple_spaces() {
        assert_eq!(slugify("  too   many   spaces  "), "too-many-spaces");
    }

    #[test]
    #[should_panic(expected = "index out of bounds")]
    fn out_of_bounds_panics() {
        let v: Vec<i32> = vec![1, 2, 3];
        let _ = v[10];
    }
}
```

### Async Tests and HTTP Handler Tests

```rust
#[cfg(test)]
mod api_tests {
    use super::*;
    use axum::body::Body;
    use axum::http::{Request, StatusCode};
    use http_body_util::BodyExt;
    use tower::ServiceExt;

    fn setup_app() -> Router {
        let state: SharedState = Arc::new(RwLock::new(AppData::default()));
        create_router(state)
    }

    #[tokio::test]
    async fn health_check_returns_ok() {
        let app = setup_app();
        let request = Request::builder()
            .uri("/api/v1/health")
            .body(Body::empty()).unwrap();
        let response = app.oneshot(request).await.unwrap();
        assert_eq!(response.status(), StatusCode::OK);
    }

    #[tokio::test]
    async fn create_and_get_user() {
        let state: SharedState = Arc::new(RwLock::new(AppData::default()));
        let app = create_router(state.clone());

        let create_req = Request::builder()
            .method("POST")
            .uri("/api/v1/users")
            .header("content-type", "application/json")
            .body(Body::from(serde_json::to_string(&serde_json::json!({
                "name": "Alice", "email": "alice@example.com"
            })).unwrap()))
            .unwrap();

        let response = app.clone().oneshot(create_req).await.unwrap();
        assert_eq!(response.status(), StatusCode::CREATED);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let user: User = serde_json::from_slice(&body).unwrap();
        assert_eq!(user.name, "Alice");

        let get_req = Request::builder()
            .uri(&format!("/api/v1/users/{}", user.id))
            .body(Body::empty()).unwrap();
        let response = app.oneshot(get_req).await.unwrap();
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let fetched: User = serde_json::from_slice(&body).unwrap();
        assert_eq!(fetched.id, user.id);
        assert_eq!(fetched.email, "alice@example.com");
    }

    #[tokio::test]
    async fn get_nonexistent_user_returns_404() {
        let app = setup_app();
        let id = Uuid::new_v4();
        let request = Request::builder()
            .uri(&format!("/api/v1/users/{id}"))
            .body(Body::empty()).unwrap();
        let response = app.oneshot(request).await.unwrap();
        assert_eq!(response.status(), StatusCode::NOT_FOUND);
    }

    #[tokio::test]
    async fn create_user_with_invalid_email_returns_400() {
        let app = setup_app();
        let request = Request::builder()
            .method("POST")
            .uri("/api/v1/users")
            .header("content-type", "application/json")
            .body(Body::from(serde_json::to_string(&serde_json::json!({
                "name": "Bob", "email": "not-an-email"
            })).unwrap()))
            .unwrap();
        let response = app.oneshot(request).await.unwrap();
        assert_eq!(response.status(), StatusCode::BAD_REQUEST);
    }
}
```

### Integration Tests

Place integration tests in `tests/` at the crate root. Each file is compiled as a separate crate.

```rust
// tests/integration_test.rs
use my_app::{create_router, SharedState, AppData};
use std::sync::Arc;
use tokio::sync::RwLock;

#[tokio::test]
async fn full_user_lifecycle() {
    let state: SharedState = Arc::new(RwLock::new(AppData::default()));
    let app = create_router(state);
    // Create -> Update -> List -> Delete -> Verify deletion
    // Each step uses app.clone().oneshot(request) as shown above.
}
```

### Mocking with Traits

```rust
#[async_trait::async_trait]
pub trait UserRepository: Send + Sync {
    async fn find_by_id(&self, id: Uuid) -> Result<Option<User>, AppError>;
    async fn save(&self, user: &User) -> Result<(), AppError>;
}

pub struct PostgresUserRepo { /* pool: sqlx::PgPool */ }

#[async_trait::async_trait]
impl UserRepository for PostgresUserRepo {
    async fn find_by_id(&self, _id: Uuid) -> Result<Option<User>, AppError> { todo!() }
    async fn save(&self, _user: &User) -> Result<(), AppError> { todo!() }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;
    use tokio::sync::Mutex;

    struct MockUserRepo {
        users: Mutex<HashMap<Uuid, User>>,
    }

    impl MockUserRepo {
        fn new() -> Self { Self { users: Mutex::new(HashMap::new()) } }

        async fn with_user(self, user: User) -> Self {
            self.users.lock().await.insert(user.id, user);
            self
        }
    }

    #[async_trait::async_trait]
    impl UserRepository for MockUserRepo {
        async fn find_by_id(&self, id: Uuid) -> Result<Option<User>, AppError> {
            Ok(self.users.lock().await.get(&id).cloned())
        }
        async fn save(&self, user: &User) -> Result<(), AppError> {
            self.users.lock().await.insert(user.id, user.clone());
            Ok(())
        }
    }

    #[tokio::test]
    async fn find_existing_user() {
        let user = User { id: Uuid::new_v4(), name: "Test".into(), email: "test@example.com".into() };
        let repo = MockUserRepo::new().with_user(user.clone()).await;
        let found = repo.find_by_id(user.id).await.unwrap();
        assert_eq!(found.unwrap().name, "Test");
    }

    #[tokio::test]
    async fn find_missing_user_returns_none() {
        let repo = MockUserRepo::new();
        let found = repo.find_by_id(Uuid::new_v4()).await.unwrap();
        assert!(found.is_none());
    }
}
```

Run tests:

```bash
cargo test                     # Run all tests
cargo test --lib               # Unit tests only
cargo test --test integration  # Specific integration test file
cargo test -- --nocapture      # Show println output
cargo test user                # Run tests with "user" in the name
```

---

## 10. Cargo Tools

### Formatting

```bash
# Format all code according to rustfmt defaults.
cargo fmt

# Check formatting without modifying files (useful in CI).
cargo fmt -- --check
```

Configure formatting in `rustfmt.toml`:

```toml
edition = "2021"
max_width = 100
use_field_init_shorthand = true
```

### Linting with Clippy

```bash
# Run the linter.
cargo clippy

# Treat all warnings as errors (for CI).
cargo clippy -- -D warnings

# Apply automatic fixes where possible.
cargo clippy --fix --allow-dirty
```

Configure lint levels in `Cargo.toml`:

```toml
[lints.clippy]
pedantic = { level = "warn", priority = -1 }
missing_errors_doc = "allow"
must_use_candidate = "allow"
module_name_repetitions = "allow"
```

Or in `clippy.toml`:

```toml
too-many-arguments-threshold = 8
type-complexity-threshold = 300
```

### Documentation

```bash
# Generate and open documentation in browser.
cargo doc --open

# Include private items (useful during development).
cargo doc --document-private-items
```

Write doc comments with examples that double as tests:

```rust
/// Calculates the factorial of a non-negative integer.
///
/// # Arguments
///
/// * `n` - The non-negative integer.
///
/// # Panics
///
/// Panics if the result overflows `u64`.
///
/// # Examples
///
/// ```
/// use my_lib::factorial;
/// assert_eq!(factorial(0), 1);
/// assert_eq!(factorial(5), 120);
/// ```
pub fn factorial(n: u64) -> u64 {
    (1..=n).product()
}
```

Run documentation tests:

```bash
cargo test --doc
```

### Benchmarking

Add to `Cargo.toml`:

```toml
[dev-dependencies]
criterion = { version = "0.5", features = ["html_reports"] }

[[bench]]
name = "my_benchmark"
harness = false
```

Create `benches/my_benchmark.rs`:

```rust
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn fibonacci(n: u64) -> u64 {
    match n {
        0 => 0,
        1 => 1,
        _ => fibonacci(n - 1) + fibonacci(n - 2),
    }
}

fn bench_fibonacci(c: &mut Criterion) {
    c.bench_function("fibonacci 20", |b| {
        b.iter(|| fibonacci(black_box(20)))
    });
}

criterion_group!(benches, bench_fibonacci);
criterion_main!(benches);
```

```bash
cargo bench
```

### Additional Cargo Commands

```bash
# Check compilation without producing binaries (fast feedback).
cargo check

# Build in release mode with optimizations.
cargo build --release

# Audit dependencies for known security vulnerabilities.
cargo install cargo-audit
cargo audit

# Show the dependency tree.
cargo tree

# Update dependencies within semver constraints.
cargo update

# Remove build artifacts.
cargo clean

# Expand macros for debugging derive output.
cargo install cargo-expand
cargo expand
```

---

## Quick Reference — Idiomatic Patterns

| Pattern | Example |
|---|---|
| Newtype wrapper | `struct UserId(Uuid);` |
| Builder pattern | `Config::builder().port(8080).build()` |
| From/Into conversion | `impl From<DbRow> for User { ... }` |
| Deref for smart wrappers | `impl Deref for AppState { type Target = Inner; ... }` |
| Type state pattern | `Connection<Disconnected>` -> `Connection<Connected>` |
| Error propagation | `let val = fallible_op().context("step failed")?;` |
| Structured logging | `tracing::info!(user_id = %id, "Created user");` |
| Graceful shutdown | `tokio::select!` with `ctrl_c()` signal |
