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
