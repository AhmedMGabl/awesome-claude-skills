---
name: rust-clap-cli
description: Rust Clap CLI patterns covering derive-based argument parsing, subcommands, value enums, custom validation, shell completions, and colored output.
---

# Rust Clap CLI

This skill should be used when building command-line tools with Rust Clap. It covers derive-based parsing, subcommands, value validation, shell completions, and output formatting.

## When to Use This Skill

Use this skill when you need to:

- Parse command-line arguments with Clap derive
- Build multi-command CLI tools
- Validate arguments and provide defaults
- Generate shell completion scripts
- Format CLI output with colors and tables

## Setup

```toml
# Cargo.toml
[dependencies]
clap = { version = "4", features = ["derive", "env"] }
```

## Basic CLI

```rust
use clap::Parser;

#[derive(Parser, Debug)]
#[command(name = "myctl", about = "A CLI tool for managing resources")]
struct Cli {
    /// Name of the resource
    #[arg(short, long)]
    name: String,

    /// Enable verbose output
    #[arg(short, long, default_value_t = false)]
    verbose: bool,

    /// Number of retries
    #[arg(short, long, default_value_t = 3)]
    retries: u32,

    /// Output format
    #[arg(short, long, default_value = "text")]
    format: String,
}

fn main() {
    let cli = Cli::parse();
    println!("Name: {}, Verbose: {}", cli.name, cli.verbose);
}
```

## Subcommands

```rust
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "myctl", version, about)]
struct Cli {
    #[command(subcommand)]
    command: Commands,

    /// Config file path
    #[arg(short, long, global = true)]
    config: Option<String>,
}

#[derive(Subcommand)]
enum Commands {
    /// Create a new resource
    Create {
        /// Resource name
        name: String,
        /// Resource type
        #[arg(short = 't', long, default_value = "default")]
        kind: String,
    },
    /// List all resources
    List {
        /// Output format
        #[arg(short, long, default_value = "table")]
        format: OutputFormat,
        /// Maximum number of results
        #[arg(short, long)]
        limit: Option<u32>,
    },
    /// Delete a resource
    Delete {
        /// Resource ID
        id: String,
        /// Skip confirmation
        #[arg(short, long)]
        force: bool,
    },
    /// Manage users
    User {
        #[command(subcommand)]
        action: UserCommands,
    },
}

#[derive(Subcommand)]
enum UserCommands {
    Add { name: String, email: String },
    Remove { id: String },
    List,
}

fn main() {
    let cli = Cli::parse();
    match cli.command {
        Commands::Create { name, kind } => {
            println!("Creating {} of type {}", name, kind);
        }
        Commands::List { format, limit } => {
            println!("Listing (format: {:?}, limit: {:?})", format, limit);
        }
        Commands::Delete { id, force } => {
            if !force {
                println!("Are you sure you want to delete {}?", id);
            }
        }
        Commands::User { action } => match action {
            UserCommands::Add { name, email } => println!("Adding {} ({})", name, email),
            UserCommands::Remove { id } => println!("Removing {}", id),
            UserCommands::List => println!("Listing users"),
        },
    }
}
```

## Value Enums

```rust
use clap::ValueEnum;

#[derive(Clone, Debug, ValueEnum)]
enum OutputFormat {
    Table,
    Json,
    Yaml,
    Csv,
}

#[derive(Parser)]
struct Cli {
    #[arg(short, long, value_enum, default_value_t = OutputFormat::Table)]
    format: OutputFormat,
}
```

## Environment Variables and Validation

```rust
#[derive(Parser)]
struct Cli {
    /// API key (can also use MYCTL_API_KEY env var)
    #[arg(long, env = "MYCTL_API_KEY")]
    api_key: String,

    /// Server port
    #[arg(short, long, value_parser = clap::value_parser!(u16).range(1024..65535))]
    port: u16,

    /// Log level
    #[arg(long, default_value = "info", value_parser = ["trace", "debug", "info", "warn", "error"])]
    log_level: String,

    /// Input files
    #[arg(required = true, num_args = 1..)]
    files: Vec<String>,
}
```

## Colored Output

```toml
# Cargo.toml
[dependencies]
colored = "2"
```

```rust
use colored::*;

fn print_success(msg: &str) {
    println!("{} {}", "SUCCESS".green().bold(), msg);
}

fn print_error(msg: &str) {
    eprintln!("{} {}", "ERROR".red().bold(), msg);
}

fn print_warning(msg: &str) {
    println!("{} {}", "WARNING".yellow().bold(), msg);
}
```

## Shell Completions

```rust
use clap::CommandFactory;
use clap_complete::{generate, Shell};
use std::io;

#[derive(Subcommand)]
enum Commands {
    // ... other commands
    /// Generate shell completions
    Completions {
        #[arg(value_enum)]
        shell: Shell,
    },
}

// In main:
Commands::Completions { shell } => {
    let mut cmd = Cli::command();
    generate(shell, &mut cmd, "myctl", &mut io::stdout());
}
```

## Additional Resources

- Clap: https://docs.rs/clap/
- Derive tutorial: https://docs.rs/clap/latest/clap/_derive/_tutorial/index.html
- Cookbook: https://docs.rs/clap/latest/clap/_cookbook/index.html
