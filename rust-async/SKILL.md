---
name: rust-async
description: Rust async programming patterns covering futures, async/await, streams, pin, select, join, async traits, concurrency limits, and runtime-agnostic design.
---

# Rust Async Programming

This skill should be used when writing async Rust code. It covers futures, async/await, streams, concurrency patterns, async traits, and runtime-agnostic design.

## When to Use This Skill

Use this skill when you need to:

- Write async functions and use futures
- Work with streams and async iterators
- Run tasks concurrently with join and select
- Implement async traits
- Design runtime-agnostic async code

## Async Functions

```rust
async fn fetch_data(url: &str) -> Result<String, reqwest::Error> {
    let response = reqwest::get(url).await?;
    let body = response.text().await?;
    Ok(body)
}

async fn process_items(items: Vec<String>) -> Vec<Result<String, Error>> {
    let mut results = Vec::new();
    for item in items {
        let result = process_one(&item).await;
        results.push(result);
    }
    results
}
```

## Concurrent Execution with join

```rust
use tokio::join;
use futures::future::join_all;

// Run two futures concurrently
async fn fetch_both() -> (String, String) {
    let (user, posts) = join!(
        fetch_user("alice"),
        fetch_posts("alice"),
    );
    (user.unwrap(), posts.unwrap())
}

// Run many futures concurrently
async fn fetch_all_users(ids: Vec<i64>) -> Vec<User> {
    let futures: Vec<_> = ids.iter()
        .map(|id| fetch_user(*id))
        .collect();

    let results = join_all(futures).await;
    results.into_iter().filter_map(|r| r.ok()).collect()
}
```

## Select: First to Complete

```rust
use tokio::select;
use tokio::time::{sleep, Duration};

async fn fetch_with_timeout(url: &str) -> Result<String, String> {
    select! {
        result = fetch_data(url) => {
            result.map_err(|e| e.to_string())
        }
        _ = sleep(Duration::from_secs(5)) => {
            Err("request timed out".into())
        }
    }
}

async fn race_requests(urls: Vec<&str>) -> String {
    select! {
        result = fetch_data(urls[0]) => result.unwrap_or_default(),
        result = fetch_data(urls[1]) => result.unwrap_or_default(),
    }
}
```

## Streams

```rust
use tokio_stream::{StreamExt, Stream};
use async_stream::stream;

// Create a stream
fn number_stream() -> impl Stream<Item = i32> {
    stream! {
        for i in 0..10 {
            tokio::time::sleep(Duration::from_millis(100)).await;
            yield i;
        }
    }
}

// Consume a stream
async fn process_stream() {
    let mut stream = number_stream();
    while let Some(value) = stream.next().await {
        println!("Got: {}", value);
    }
}

// Transform streams
async fn filtered_stream() {
    let stream = number_stream()
        .filter(|x| *x % 2 == 0)
        .map(|x| x * 10)
        .take(3);

    tokio::pin!(stream);
    while let Some(value) = stream.next().await {
        println!("Value: {}", value);
    }
}
```

## Concurrency Limits

```rust
use futures::stream::{self, StreamExt};

// Process at most N items concurrently
async fn bounded_concurrent(urls: Vec<String>) -> Vec<String> {
    stream::iter(urls)
        .map(|url| async move {
            fetch_data(&url).await.unwrap_or_default()
        })
        .buffer_unordered(10) // max 10 concurrent
        .collect()
        .await
}

// Using semaphore
use tokio::sync::Semaphore;
use std::sync::Arc;

async fn limited_tasks(items: Vec<Item>) {
    let semaphore = Arc::new(Semaphore::new(5));
    let mut handles = vec![];

    for item in items {
        let permit = semaphore.clone().acquire_owned().await.unwrap();
        handles.push(tokio::spawn(async move {
            let result = process_item(item).await;
            drop(permit);
            result
        }));
    }

    for handle in handles {
        handle.await.unwrap();
    }
}
```

## Async Traits

```rust
use async_trait::async_trait;

#[async_trait]
trait Repository {
    async fn find_by_id(&self, id: i64) -> Option<Record>;
    async fn save(&self, record: &Record) -> Result<(), Error>;
}

#[async_trait]
impl Repository for PostgresRepo {
    async fn find_by_id(&self, id: i64) -> Option<Record> {
        sqlx::query_as!(Record, "SELECT * FROM records WHERE id = $1", id)
            .fetch_optional(&self.pool)
            .await
            .ok()
            .flatten()
    }

    async fn save(&self, record: &Record) -> Result<(), Error> {
        sqlx::query!("INSERT INTO records (id, data) VALUES ($1, $2)", record.id, record.data)
            .execute(&self.pool)
            .await?;
        Ok(())
    }
}
```

## Retry Pattern

```rust
use tokio::time::{sleep, Duration};

async fn retry<F, Fut, T, E>(f: F, max_retries: u32, base_delay: Duration) -> Result<T, E>
where
    F: Fn() -> Fut,
    Fut: std::future::Future<Output = Result<T, E>>,
{
    let mut attempts = 0;
    loop {
        match f().await {
            Ok(value) => return Ok(value),
            Err(err) if attempts < max_retries => {
                attempts += 1;
                let delay = base_delay * 2u32.pow(attempts - 1);
                sleep(delay).await;
            }
            Err(err) => return Err(err),
        }
    }
}

// Usage
let result = retry(
    || fetch_data("https://api.example.com/data"),
    3,
    Duration::from_millis(100),
).await;
```

## Additional Resources

- Async Book: https://rust-lang.github.io/async-book/
- Tokio Tutorial: https://tokio.rs/tokio/tutorial
- Futures crate: https://docs.rs/futures/
