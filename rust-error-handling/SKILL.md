---
name: rust-error-handling
description: Rust error handling patterns covering thiserror, anyhow, custom error types, error conversion, Result chaining, context propagation, and error reporting.
---

# Rust Error Handling

This skill should be used when implementing error handling in Rust applications. It covers thiserror, anyhow, custom types, conversions, and error reporting.

## When to Use This Skill

Use this skill when you need to:

- Define custom error types with thiserror
- Use anyhow for application-level errors
- Convert between error types
- Propagate errors with context
- Implement error reporting and display

## Setup

```toml
# Cargo.toml
[dependencies]
thiserror = "1"
anyhow = "1"
```

## Custom Errors with thiserror

```rust
use thiserror::Error;

#[derive(Error, Debug)]
enum AppError {
    #[error("user not found: {0}")]
    UserNotFound(String),

    #[error("validation failed: {field} - {message}")]
    Validation { field: String, message: String },

    #[error("database error")]
    Database(#[from] sqlx::Error),

    #[error("authentication failed")]
    Unauthorized,

    #[error("permission denied for {resource}")]
    Forbidden { resource: String },

    #[error(transparent)]
    Other(#[from] anyhow::Error),
}
```

## Using thiserror in Libraries

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ParseError {
    #[error("invalid format at position {position}: {message}")]
    InvalidFormat { position: usize, message: String },

    #[error("unexpected end of input")]
    UnexpectedEof,

    #[error("unknown token: {0}")]
    UnknownToken(String),
}

pub fn parse(input: &str) -> Result<Document, ParseError> {
    if input.is_empty() {
        return Err(ParseError::UnexpectedEof);
    }
    // parsing logic...
    Ok(Document::new())
}
```

## anyhow for Applications

```rust
use anyhow::{Context, Result, bail, ensure};

fn load_config(path: &str) -> Result<Config> {
    let content = std::fs::read_to_string(path)
        .context("failed to read config file")?;

    let config: Config = toml::from_str(&content)
        .context("failed to parse config")?;

    ensure!(config.port > 0, "port must be positive");

    if config.host.is_empty() {
        bail!("host cannot be empty");
    }

    Ok(config)
}

fn main() -> Result<()> {
    let config = load_config("config.toml")
        .context("unable to initialize application")?;

    run_server(config)?;
    Ok(())
}
```

## Error Conversion

```rust
use thiserror::Error;

#[derive(Error, Debug)]
enum ServiceError {
    #[error("not found: {0}")]
    NotFound(String),
    #[error("internal error: {0}")]
    Internal(String),
}

// Convert from repository errors
impl From<RepoError> for ServiceError {
    fn from(err: RepoError) -> Self {
        match err {
            RepoError::NotFound(id) => ServiceError::NotFound(id),
            RepoError::Connection(e) => ServiceError::Internal(e.to_string()),
        }
    }
}

// Convert to HTTP responses (for web frameworks)
impl ServiceError {
    fn status_code(&self) -> u16 {
        match self {
            ServiceError::NotFound(_) => 404,
            ServiceError::Internal(_) => 500,
        }
    }
}
```

## Result Extensions

```rust
use anyhow::{Context, Result};

// Chain operations with context
fn process_user(id: &str) -> Result<Output> {
    let user = fetch_user(id)
        .with_context(|| format!("failed to fetch user {}", id))?;

    let profile = load_profile(&user)
        .context("failed to load profile")?;

    let result = transform(profile)
        .context("transformation failed")?;

    Ok(result)
}

// Map and handle specific errors
fn try_operation() -> Result<Data> {
    let result = risky_operation()
        .map_err(|e| anyhow::anyhow!("operation failed: {}", e))?;
    Ok(result)
}
```

## Multiple Error Types

```rust
#[derive(Error, Debug)]
enum AppError {
    #[error(transparent)]
    Io(#[from] std::io::Error),

    #[error(transparent)]
    Parse(#[from] serde_json::Error),

    #[error(transparent)]
    Database(#[from] sqlx::Error),

    #[error(transparent)]
    Http(#[from] reqwest::Error),
}

fn complex_operation() -> Result<Data, AppError> {
    let content = std::fs::read_to_string("data.json")?;  // io::Error -> AppError
    let parsed: RawData = serde_json::from_str(&content)?; // serde -> AppError
    let saved = db_save(&parsed)?;                         // sqlx -> AppError
    Ok(saved)
}
```

## Pattern: Layered Errors

```rust
// Repository layer
#[derive(Error, Debug)]
pub enum RepoError {
    #[error("record not found")]
    NotFound,
    #[error("duplicate key: {0}")]
    Duplicate(String),
    #[error("connection error: {0}")]
    Connection(#[source] sqlx::Error),
}

// Service layer
#[derive(Error, Debug)]
pub enum ServiceError {
    #[error("user not found: {0}")]
    UserNotFound(String),
    #[error("email already taken")]
    EmailTaken,
    #[error("internal error")]
    Internal(#[source] Box<dyn std::error::Error + Send + Sync>),
}

// HTTP layer
#[derive(Error, Debug)]
pub enum ApiError {
    #[error("{message}")]
    Client { status: u16, message: String },
    #[error("internal server error")]
    Server(#[source] Box<dyn std::error::Error + Send + Sync>),
}
```

## Additional Resources

- thiserror: https://docs.rs/thiserror/
- anyhow: https://docs.rs/anyhow/
- Error Handling: https://doc.rust-lang.org/book/ch09-00-error-handling.html
