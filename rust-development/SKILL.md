---
name: rust-development
description: This skill should be used when writing, structuring, or debugging Rust applications. It covers ownership and borrowing, structs and enums, pattern matching, error handling with Result/Option, traits, generics, async programming with Tokio, HTTP servers with Actix-web/Axum, Cargo workspaces, testing, and common crates such as serde, clap, and anyhow.
---
# Rust Development

Guidance for building Rust applications covering core language concepts, async programming, web services, testing, and essential crates.

## Project Setup and Cargo Workspace
```bash
cargo new my-app && cargo new my-lib --lib
```
Common `Cargo.toml` dependencies:
```toml
[dependencies]
tokio = { version = "1", features = ["full"] }
axum = "0.7"
actix-web = "4"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
clap = { version = "4", features = ["derive"] }
anyhow = "1"
thiserror = "1"
```
Multi-crate workspace:
```toml
[workspace]
members = ["crates/api", "crates/core", "crates/db"]
resolver = "2"
[workspace.dependencies]
serde = { version = "1", features = ["derive"] }
```
Build/test: `cargo build -p api`, `cargo test --workspace`.

## Ownership and Borrowing
```rust
fn demo() {
    let s1 = String::from("hello");
    let s2 = s1;                     // s1 moved, no longer valid
    let s3 = s2.clone();             // explicit deep copy
    println!("{s2} {s3}");
    let mut v = vec![1, 2, 3];
    let total: i32 = v.iter().sum(); // shared borrow (&T)
    v.push(4);                       // mutable borrow (&mut T), exclusive
    println!("{total}, {v:?}");
}
fn sum(v: &[i32]) -> i32 { v.iter().sum() }
fn push(v: &mut Vec<i32>, x: i32) { v.push(x); }
```
## Structs, Enums, and Pattern Matching
```rust
use serde::{Deserialize, Serialize};
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct User { pub name: String, pub role: Role }
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Role { Viewer, Editor, Admin }
#[derive(Debug)]
pub enum Command { Quit, Echo(String), Move { x: i32, y: i32 } }

fn handle(cmd: Command) -> String {
    match cmd {
        Command::Quit => "Goodbye".into(),
        Command::Echo(msg) => msg,
        Command::Move { x, y } => format!("({x},{y})"),
    }
}
fn patterns() {
    if let Some(v) = Some(42) { println!("{v}"); }          // if-let
    let Some(env) = Some("prod") else { return; };          // let-else
}
```

## Error Handling (Result, Option, anyhow, thiserror)
```rust
use anyhow::{Context, Result};
use thiserror::Error;
#[derive(Error, Debug)]
pub enum AppError {
    #[error("not found: {0}")]   NotFound(String),
    #[error("validation: {0}")]  Validation(String),
    #[error(transparent)]        Internal(#[from] anyhow::Error),
}
fn read_config(path: &str, key: &str) -> Result<String> {
    let text = std::fs::read_to_string(path).context("read failed")?;
    let line = text.lines().find(|l| l.starts_with(key))
        .ok_or_else(|| anyhow::anyhow!("key '{key}' missing"))?;
    Ok(line.split('=').nth(1).unwrap_or("").trim().into())
}
```

## Traits and Generics
```rust
pub trait Summary {
    fn summarize(&self) -> String;
    fn preview(&self) -> String { // default implementation
        let s = self.summarize();
        if s.len() > 50 { format!("{}...", &s[..50]) } else { s }
    }
}
fn print_all<T: Summary + std::fmt::Debug>(items: &[T]) {
    for item in items { println!("{}: {:?}", item.summarize(), item); }
}
fn first_or(a: &impl Summary, b: &impl Summary) -> String {
    let s = a.summarize(); if s.is_empty() { b.summarize() } else { s }
}
pub trait Notifier: Send + Sync { fn send(&self, msg: &str); }
struct Broadcaster { channels: Vec<Box<dyn Notifier>> }
impl Broadcaster {
    fn broadcast(&self, msg: &str) { for ch in &self.channels { ch.send(msg); } }
}
```

## Async with Tokio
```rust
use tokio::{sync::mpsc, time::{self, Duration}};
#[tokio::main]
async fn main() {
    let h = tokio::spawn(async { time::sleep(Duration::from_millis(50)).await; 42 });
    println!("{}", h.await.unwrap());
}
async fn event_loop(mut rx: mpsc::Receiver<String>) {
    let mut tick = time::interval(Duration::from_secs(5));
    loop {
        tokio::select! {
            Some(msg) = rx.recv() => println!("{msg}"),
            _ = tick.tick() => println!("heartbeat"),
            _ = tokio::signal::ctrl_c() => break,
        }
    }
}
```

## HTTP Servers (Axum and Actix-web)
```rust
// --- Axum ---
use axum::{extract::{Json, State}, routing::{get, post}, Router};
use std::sync::Arc; use tokio::sync::RwLock;
type AppState = Arc<RwLock<Vec<User>>>;
async fn list(State(s): State<AppState>) -> Json<Vec<User>> { Json(s.read().await.clone()) }
async fn create(State(s): State<AppState>, Json(u): Json<User>) -> Json<User> {
    s.write().await.push(u.clone()); Json(u)
}
fn router(state: AppState) -> Router {
    Router::new().route("/users", get(list).post(create)).with_state(state)
}
// --- Actix-web ---
use actix_web::{web, App, HttpServer, HttpResponse};
async fn health() -> HttpResponse { HttpResponse::Ok().json("ok") }
#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| App::new().route("/health", web::get().to(health)))
        .bind("0.0.0.0:8080")?.run().await
}
```

## CLI with clap
```rust
use clap::Parser;
#[derive(Parser)]
#[command(name = "mycli", about = "Sample CLI")]
struct Cli {
    #[arg(short, long, default_value_t = 8080)] port: u16,
    #[command(subcommand)] cmd: Cmd,
}
#[derive(clap::Subcommand)]
enum Cmd { Serve, Migrate { #[arg(long)] dry_run: bool } }
fn main() {
    let cli = Cli::parse();
    match cli.cmd {
        Cmd::Serve => println!("port {}", cli.port),
        Cmd::Migrate { dry_run } => println!("migrate dry={dry_run}"),
    }
}
```

## Testing
```rust
pub fn slugify(s: &str) -> String {
    s.to_lowercase().chars().map(|c| if c.is_alphanumeric() { c } else { '-' })
        .collect::<String>().split('-').filter(|p| !p.is_empty())
        .collect::<Vec<_>>().join("-")
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn test_slugify() { assert_eq!(slugify("Hello World!"), "hello-world"); }
    #[tokio::test]
    async fn test_handler() {
        let state: AppState = Arc::new(RwLock::new(vec![]));
        let _app = router(state); // use tower::ServiceExt::oneshot to test
    }
}
```
Commands: `cargo test`, `cargo test --lib`, `cargo fmt -- --check`, `cargo clippy -- -D warnings`.
## Additional Resources

- [The Rust Book](https://doc.rust-lang.org/book/) | [Rust by Example](https://doc.rust-lang.org/rust-by-example/)
- [Tokio](https://tokio.rs/tokio/tutorial) | [Axum](https://docs.rs/axum/latest/axum/) | [Actix-web](https://actix.rs/docs/)
- [Serde](https://serde.rs/) | [Clap](https://docs.rs/clap/latest/clap/) | [Anyhow](https://docs.rs/anyhow/latest/anyhow/)
