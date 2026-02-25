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
    // r1 and r2 are no longer used, so the mutable borrow is valid.

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

Lifetimes ensure that references remain valid for the duration they are used. The compiler infers most lifetimes, but explicit annotations are required when the relationship between input and output lifetimes is ambiguous.

```rust
// Explicit lifetime: the returned reference lives as long as the shorter
// of the two input lifetimes.
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() >= y.len() { x } else { y }
}

// Struct holding a reference must declare the lifetime.
struct Excerpt<'a> {
    text: &'a str,
}

impl<'a> Excerpt<'a> {
    // Lifetime elision: &self lifetime is implicitly assigned to the return.
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
        // excerpt is dropped here, but first_sentence borrows from novel,
        // which outlives this scope.
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

// Tuple struct for type-safe wrappers (newtype pattern).
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct UserId(pub Uuid);

// Unit struct for marker types.
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
    // Destructuring tuples.
    let (a, b, c) = (1, "hello", 3.14);
    println!("{a} {b} {c}");

    // Destructuring structs.
    let user = User::new("alice@example.com", "Alice");
    let User { ref email, ref name, .. } = user;
    println!("{name} <{email}>");

    // if-let for single-variant matching.
    let maybe_value: Option<i32> = Some(42);
    if let Some(v) = maybe_value {
        println!("Got: {v}");
    }

    // let-else for early return on mismatch.
    let config_value: Option<&str> = Some("production");
    let Some(env) = config_value else {
        println!("No environment configured");
        return;
    };
    println!("Environment: {env}");

    // Match guards.
    let temperature = 35;
    let description = match temperature {
        t if t < 0 => "freezing",
        0..=15 => "cold",
        16..=25 => "comfortable",
        26..=35 => "warm",
        _ => "hot",
    };
    println!("Weather: {description}");

    // Nested destructuring.
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

    // Default implementation.
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
// Trait bound syntax — both forms are equivalent.
fn print_summary(item: &impl Summary) {
    println!("{}", item.summarize());
}

fn print_summary_verbose<T: Summary>(item: &T) {
    println!("{}", item.summarize());
}

// Multiple bounds with where clause for readability.
fn process_item<T>(item: &T) -> String
where
    T: Summary + fmt::Display + fmt::Debug,
{
    tracing::debug!(?item, "Processing item");
    format!("{} — {}", item, item.summarize())
}

// Returning impl Trait hides the concrete type.
fn create_default_article() -> impl Summary {
    Article {
        title: "Default".to_string(),
        body: "No content yet.".to_string(),
    }
}
```

### Dynamic Dispatch with `dyn`

```rust
// Use dyn Trait when the concrete type is determined at runtime.
pub struct NotificationService {
    channels: Vec<Box<dyn NotificationChannel>>,
}

pub trait NotificationChannel: Send + Sync {
    fn send(&self, message: &str) -> Result<(), String>;
    fn name(&self) -> &str;
}

pub struct EmailChannel {
    smtp_host: String,
}

impl NotificationChannel for EmailChannel {
    fn send(&self, message: &str) -> Result<(), String> {
        println!("Sending email via {}: {message}", self.smtp_host);
        Ok(())
    }
    fn name(&self) -> &str {
        "email"
    }
}

pub struct SlackChannel {
    webhook_url: String,
}

impl NotificationChannel for SlackChannel {
    fn send(&self, message: &str) -> Result<(), String> {
        println!("Posting to Slack {}: {message}", self.webhook_url);
        Ok(())
    }
    fn name(&self) -> &str {
        "slack"
    }
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
use std::num::ParseIntError;

// The ? operator propagates errors, converting via From when needed.
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

// Option combinators for concise transformations.
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

// Convert AppError into HTTP responses for axum.
impl axum::response::IntoResponse for AppError {
    fn into_response(self) -> axum::response::Response {
        use axum::http::StatusCode;

        let (status, message) = match &self {
            AppError::UserNotFound { .. } => (StatusCode::NOT_FOUND, self.to_string()),
            AppError::Validation(_) => (StatusCode::BAD_REQUEST, self.to_string()),
            AppError::Unauthorized { .. } => (StatusCode::UNAUTHORIZED, self.to_string()),
            AppError::Database(_) | AppError::Internal(_) => {
                tracing::error!(?self, "Internal error");
                (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    "Internal server error".to_string(),
                )
            }
        };

        (status, axum::Json(serde_json::json!({ "error": message }))).into_response()
    }
}
```

### Application-Level Errors with `anyhow`

```rust
use anyhow::{Context, Result};

// anyhow::Result is ideal for application code and scripts.
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
    // Vec — growable array.
    let mut scores: Vec<i32> = Vec::new();
    scores.push(95);
    scores.push(87);
    scores.push(92);
    scores.extend([88, 76, 91]);

    // Access with bounds checking.
    if let Some(&top) = scores.first() {
        println!("First score: {top}");
    }

    // HashMap — key-value store.
    let mut word_counts: HashMap<String, usize> = HashMap::new();
    let text = "the quick brown fox jumps over the lazy fox";
    for word in text.split_whitespace() {
        *word_counts.entry(word.to_string()).or_insert(0) += 1;
    }
    println!("Word counts: {word_counts:?}");

    // entry API for conditional insertion.
    let mut settings: HashMap<&str, String> = HashMap::new();
    settings
        .entry("theme")
        .or_insert_with(|| "dark".to_string());
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

    // Filter, transform, collect.
    let affordable_available: Vec<String> = products
        .iter()
        .filter(|p| p.in_stock && p.price < 100.0)
        .map(|p| format!("{} (${:.2})", p.name, p.price))
        .collect();
    println!("Affordable: {affordable_available:?}");

    // fold to compute aggregate.
    let total_value: f64 = products
        .iter()
        .filter(|p| p.in_stock)
        .fold(0.0, |acc, p| acc + p.price);
    println!("Total in-stock value: ${total_value:.2}");

    // Partition into two collections.
    let (in_stock, out_of_stock): (Vec<_>, Vec<_>) = products
        .iter()
        .partition(|p| p.in_stock);
    println!("In stock: {}, Out: {}", in_stock.len(), out_of_stock.len());

    // flat_map for nested iteration.
    let tags: Vec<Vec<&str>> = vec![
        vec!["rust", "systems"],
        vec!["async", "tokio"],
        vec!["web", "axum"],
    ];
    let all_tags: Vec<&str> = tags.iter().flat_map(|t| t.iter().copied()).collect();
    println!("All tags: {all_tags:?}");

    // find and position.
    let first_expensive = products.iter().find(|p| p.price > 500.0);
    println!("First expensive: {first_expensive:?}");

    // enumerate and zip.
    let names: Vec<&str> = vec!["alpha", "beta", "gamma"];
    let values: Vec<i32> = vec![1, 2, 3];
    let pairs: HashMap<&str, i32> = names.into_iter().zip(values).collect();
    println!("Pairs: {pairs:?}");

    // Chaining with closures stored in variables.
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
    // Initialize structured logging.
    tracing_subscriber::fmt()
        .with_env_filter("info")
        .init();

    tracing::info!("Application starting");

    // Spawn concurrent tasks.
    let handle_a = tokio::spawn(async {
        time::sleep(Duration::from_millis(100)).await;
        "Task A complete"
    });

    let handle_b = tokio::spawn(async {
        time::sleep(Duration::from_millis(50)).await;
        42
    });

    // Await results. JoinHandle returns Result<T, JoinError>.
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
    let (tx, mut rx) = mpsc::channel::<String>(32);
    let mut interval = time::interval(Duration::from_secs(5));
    let shutdown = tokio::signal::ctrl_c();
    tokio::pin!(shutdown);

    loop {
        tokio::select! {
            // Receive a message from the channel.
            Some(msg) = rx.recv() => {
                tracing::info!(%msg, "Received message");
            }

            // Periodic tick.
            _ = interval.tick() => {
                tracing::debug!("Heartbeat tick");
            }

            // Graceful shutdown on Ctrl+C.
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
    Get {
        key: String,
        reply: oneshot::Sender<Option<String>>,
    },
    Set {
        key: String,
        value: String,
        reply: oneshot::Sender<()>,
    },
}

async fn db_actor(mut rx: mpsc::Receiver<DbCommand>) {
    let mut store = std::collections::HashMap::new();

    while let Some(cmd) = rx.recv().await {
        match cmd {
            DbCommand::Get { key, reply } => {
                let value = store.get(&key).cloned();
                let _ = reply.send(value);
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

    // Set a value.
    let (reply_tx, reply_rx) = oneshot::channel();
    tx.send(DbCommand::Set {
        key: "name".into(),
        value: "Rust".into(),
        reply: reply_tx,
    })
    .await
    .unwrap();
    reply_rx.await.unwrap();

    // Get the value back.
    let (reply_tx, reply_rx) = oneshot::channel();
    tx.send(DbCommand::Get {
        key: "name".into(),
        reply: reply_tx,
    })
    .await
    .unwrap();
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
            // Lock is held only for the duration of the block.
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

// Shared application state.
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

// Build the router with nested routes and shared state.
pub fn create_router(state: SharedState) -> Router {
    let api_routes = Router::new()
        .route("/users", get(list_users).post(create_user))
        .route(
            "/users/{id}",
            get(get_user).put(update_user).delete(delete_user),
        )
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

    let users: Vec<&User> = data
        .users
        .values()
        .skip(((page - 1) * per_page) as usize)
        .take(per_page as usize)
        .collect();

    Json(serde_json::json!({
        "users": users,
        "page": page,
        "total": data.users.len(),
    }))
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
    let user = data
        .users
        .get(&id)
        .cloned()
        .ok_or(AppError::UserNotFound { id: id.to_string() })?;
    Ok(Json(user))
}

async fn update_user(
    State(state): State<SharedState>,
    Path(id): Path<Uuid>,
    Json(payload): Json<CreateUserRequest>,
) -> Result<Json<User>, AppError> {
    let mut data = state.write().await;
    let user = data
        .users
        .get_mut(&id)
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
    data.users
        .remove(&id)
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
        %method,
        %uri,
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
            tokio::signal::ctrl_c()
                .await
                .expect("Failed to listen for Ctrl+C");
            tracing::info!("Shutdown signal received");
        })
        .await?;

    Ok(())
}
```