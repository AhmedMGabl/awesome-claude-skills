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