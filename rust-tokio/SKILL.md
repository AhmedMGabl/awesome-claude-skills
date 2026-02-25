---
name: rust-tokio
description: Rust Tokio async runtime patterns covering task spawning, channels, synchronization, TCP/UDP networking, timers, graceful shutdown, and concurrent programming.
---

# Rust Tokio

This skill should be used when building async applications with Rust Tokio. It covers task spawning, channels, synchronization, networking, timers, and graceful shutdown.

## When to Use This Skill

Use this skill when you need to:

- Build async applications with Tokio runtime
- Spawn and manage concurrent tasks
- Use channels for inter-task communication
- Implement TCP/UDP servers and clients
- Handle timeouts and graceful shutdown

## Setup

```toml
# Cargo.toml
[dependencies]
tokio = { version = "1", features = ["full"] }
```

## Basic Async Tasks

```rust
use tokio::task;

#[tokio::main]
async fn main() {
    // Spawn a task
    let handle = task::spawn(async {
        println!("Running in background");
        42
    });

    let result = handle.await.unwrap();
    println!("Result: {}", result);

    // Spawn blocking work
    let result = task::spawn_blocking(|| {
        std::thread::sleep(std::time::Duration::from_secs(1));
        "computed"
    }).await.unwrap();
}
```

## Channels

```rust
use tokio::sync::{mpsc, oneshot, broadcast};

// mpsc: multiple producer, single consumer
async fn mpsc_example() {
    let (tx, mut rx) = mpsc::channel::<String>(100);

    let tx2 = tx.clone();
    tokio::spawn(async move {
        tx.send("from task 1".into()).await.unwrap();
    });
    tokio::spawn(async move {
        tx2.send("from task 2".into()).await.unwrap();
    });

    while let Some(msg) = rx.recv().await {
        println!("Received: {}", msg);
    }
}

// oneshot: single value response
async fn oneshot_example() {
    let (tx, rx) = oneshot::channel::<String>();
    tokio::spawn(async move {
        tx.send("response".into()).unwrap();
    });
    let result = rx.await.unwrap();
    println!("Got: {}", result);
}

// broadcast: multiple consumers
async fn broadcast_example() {
    let (tx, _) = broadcast::channel::<String>(16);
    let mut rx1 = tx.subscribe();
    let mut rx2 = tx.subscribe();

    tx.send("hello".into()).unwrap();

    println!("rx1: {}", rx1.recv().await.unwrap());
    println!("rx2: {}", rx2.recv().await.unwrap());
}
```

## Synchronization

```rust
use tokio::sync::{Mutex, RwLock, Semaphore};
use std::sync::Arc;

// Async mutex
async fn mutex_example() {
    let data = Arc::new(Mutex::new(vec![]));

    let mut handles = vec![];
    for i in 0..10 {
        let data = data.clone();
        handles.push(tokio::spawn(async move {
            let mut lock = data.lock().await;
            lock.push(i);
        }));
    }

    for h in handles { h.await.unwrap(); }
    println!("Data: {:?}", data.lock().await);
}

// Semaphore for limiting concurrency
async fn semaphore_example() {
    let sem = Arc::new(Semaphore::new(3)); // max 3 concurrent

    let mut handles = vec![];
    for i in 0..10 {
        let permit = sem.clone().acquire_owned().await.unwrap();
        handles.push(tokio::spawn(async move {
            println!("Task {} running", i);
            tokio::time::sleep(std::time::Duration::from_secs(1)).await;
            drop(permit);
        }));
    }

    for h in handles { h.await.unwrap(); }
}
```

## TCP Server

```rust
use tokio::net::TcpListener;
use tokio::io::{AsyncReadExt, AsyncWriteExt};

async fn tcp_server() -> std::io::Result<()> {
    let listener = TcpListener::bind("127.0.0.1:8080").await?;

    loop {
        let (mut socket, addr) = listener.accept().await?;
        println!("Connection from: {}", addr);

        tokio::spawn(async move {
            let mut buf = [0u8; 1024];
            loop {
                let n = match socket.read(&mut buf).await {
                    Ok(0) => return,
                    Ok(n) => n,
                    Err(_) => return,
                };
                if socket.write_all(&buf[..n]).await.is_err() {
                    return;
                }
            }
        });
    }
}
```

## Timeouts and Select

```rust
use tokio::time::{timeout, Duration, interval};
use tokio::select;

async fn with_timeout() {
    match timeout(Duration::from_secs(5), long_operation()).await {
        Ok(result) => println!("Completed: {:?}", result),
        Err(_) => println!("Timed out"),
    }
}

async fn select_example(mut rx: mpsc::Receiver<String>) {
    let mut tick = interval(Duration::from_secs(1));

    loop {
        select! {
            Some(msg) = rx.recv() => {
                println!("Message: {}", msg);
            }
            _ = tick.tick() => {
                println!("Tick");
            }
        }
    }
}
```

## Graceful Shutdown

```rust
use tokio::signal;
use tokio::sync::watch;

async fn run_server() {
    let (shutdown_tx, mut shutdown_rx) = watch::channel(false);

    let server = tokio::spawn(async move {
        loop {
            tokio::select! {
                _ = shutdown_rx.changed() => {
                    println!("Shutting down...");
                    break;
                }
                _ = do_work() => {}
            }
        }
    });

    signal::ctrl_c().await.unwrap();
    println!("Received Ctrl+C");
    shutdown_tx.send(true).unwrap();
    server.await.unwrap();
}
```

## Additional Resources

- Tokio: https://tokio.rs/
- Tutorial: https://tokio.rs/tokio/tutorial
- API: https://docs.rs/tokio/
