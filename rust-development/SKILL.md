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