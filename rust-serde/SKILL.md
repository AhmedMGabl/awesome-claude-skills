---
name: rust-serde
description: Rust Serde patterns covering JSON/TOML/YAML serialization, custom derive attributes, field renaming, default values, enums, custom serializers, and zero-copy deserialization.
---

# Rust Serde

This skill should be used when serializing and deserializing data in Rust with Serde. It covers derive macros, attributes, custom serializers, and format support.

## When to Use This Skill

Use this skill when you need to:

- Serialize/deserialize JSON, TOML, YAML, or other formats
- Customize field names, defaults, and skip rules
- Handle enums with tagged/untagged representations
- Write custom serializers and deserializers
- Work with zero-copy deserialization

## Setup

```toml
# Cargo.toml
[dependencies]
serde = { version = "1", features = ["derive"] }
serde_json = "1"
toml = "0.8"
```

## Basic Derive

```rust
use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize, Debug)]
struct User {
    id: i64,
    name: String,
    email: String,
    #[serde(default)]
    active: bool,
}

fn main() {
    let user = User {
        id: 1,
        name: "Alice".into(),
        email: "alice@example.com".into(),
        active: true,
    };

    // Serialize to JSON
    let json = serde_json::to_string_pretty(&user).unwrap();
    println!("{}", json);

    // Deserialize from JSON
    let parsed: User = serde_json::from_str(&json).unwrap();
    println!("{:?}", parsed);
}
```

## Field Attributes

```rust
#[derive(Serialize, Deserialize)]
struct Config {
    #[serde(rename = "serverName")]
    server_name: String,

    #[serde(default = "default_port")]
    port: u16,

    #[serde(skip_serializing_if = "Option::is_none")]
    description: Option<String>,

    #[serde(skip)]
    internal_state: String,

    #[serde(alias = "db_url", alias = "database_url")]
    database_url: String,

    #[serde(flatten)]
    extra: std::collections::HashMap<String, serde_json::Value>,
}

fn default_port() -> u16 { 8080 }
```

## Enum Representations

```rust
// Externally tagged (default): {"type": "Circle", "radius": 5}
#[derive(Serialize, Deserialize)]
enum Shape {
    Circle { radius: f64 },
    Rectangle { width: f64, height: f64 },
}

// Internally tagged
#[derive(Serialize, Deserialize)]
#[serde(tag = "type")]
enum Event {
    Click { x: i32, y: i32 },
    KeyPress { key: String },
}

// Adjacently tagged
#[derive(Serialize, Deserialize)]
#[serde(tag = "t", content = "c")]
enum Message {
    Text(String),
    Image { url: String, width: u32 },
}

// Untagged
#[derive(Serialize, Deserialize)]
#[serde(untagged)]
enum Value {
    Integer(i64),
    Float(f64),
    Text(String),
}
```

## Container Attributes

```rust
#[derive(Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct ApiResponse {
    status_code: u16,        // -> "statusCode"
    error_message: String,   // -> "errorMessage"
    is_success: bool,        // -> "isSuccess"
}

#[derive(Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct StrictConfig {
    host: String,
    port: u16,
}
```

## Custom Serialization

```rust
use serde::{Serializer, Deserializer};
use chrono::{DateTime, Utc};

#[derive(Serialize, Deserialize)]
struct Record {
    name: String,
    #[serde(serialize_with = "serialize_dt", deserialize_with = "deserialize_dt")]
    created_at: DateTime<Utc>,
}

fn serialize_dt<S>(dt: &DateTime<Utc>, serializer: S) -> Result<S::Ok, S::Error>
where S: Serializer {
    serializer.serialize_str(&dt.format("%Y-%m-%d %H:%M:%S").to_string())
}

fn deserialize_dt<'de, D>(deserializer: D) -> Result<DateTime<Utc>, D::Error>
where D: Deserializer<'de> {
    let s = String::deserialize(deserializer)?;
    DateTime::parse_from_str(&s, "%Y-%m-%d %H:%M:%S %z")
        .map(|dt| dt.with_timezone(&Utc))
        .map_err(serde::de::Error::custom)
}
```

## Multiple Formats

```rust
// JSON
let json_str = serde_json::to_string(&config)?;
let config: Config = serde_json::from_str(&json_str)?;

// TOML
let toml_str = toml::to_string(&config)?;
let config: Config = toml::from_str(&toml_str)?;

// Read from file
let content = std::fs::read_to_string("config.toml")?;
let config: Config = toml::from_str(&content)?;
```

## Additional Resources

- Serde: https://serde.rs/
- Attributes: https://serde.rs/attributes.html
- Examples: https://serde.rs/examples.html
