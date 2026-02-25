---
name: concurrency-patterns
description: Concurrency and parallelism patterns covering Promise.all/allSettled/race, Web Workers, worker threads, async iterators, mutex and semaphore patterns, producer-consumer queues, Go goroutines and channels, Python asyncio, and thread-safe data structures.
---

# Concurrency Patterns

This skill should be used when implementing concurrent or parallel processing. It covers Promise patterns, workers, async iterators, mutexes, and language-specific concurrency.

## When to Use This Skill

Use this skill when you need to:

- Run multiple async operations in parallel
- Use Web Workers or worker threads
- Implement mutex/semaphore patterns
- Process data with async iterators
- Write concurrent Go or Python code

## Promise Patterns (JavaScript/TypeScript)

```typescript
// Promise.all — all must succeed
const [users, posts, stats] = await Promise.all([
  fetchUsers(),
  fetchPosts(),
  fetchStats(),
]);

// Promise.allSettled — handle mixed results
const results = await Promise.allSettled([
  fetchUsers(),
  fetchPosts(),
  fetchStats(),
]);

for (const result of results) {
  if (result.status === "fulfilled") {
    console.log("Data:", result.value);
  } else {
    console.error("Failed:", result.reason);
  }
}

// Promise.race — first to resolve
const data = await Promise.race([
  fetchFromPrimary(),
  fetchFromFallback(),
]);

// Timeout pattern
async function withTimeout<T>(promise: Promise<T>, ms: number): Promise<T> {
  const timeout = new Promise<never>((_, reject) =>
    setTimeout(() => reject(new Error(`Timeout after ${ms}ms`)), ms),
  );
  return Promise.race([promise, timeout]);
}

const data = await withTimeout(fetchData(), 5000);
```

## Concurrency Limiter

```typescript
// Process items with limited concurrency
async function mapWithConcurrency<T, R>(
  items: T[],
  fn: (item: T) => Promise<R>,
  concurrency: number,
): Promise<R[]> {
  const results: R[] = [];
  const executing = new Set<Promise<void>>();

  for (const [index, item] of items.entries()) {
    const p = fn(item).then((result) => {
      results[index] = result;
    });

    executing.add(p);
    const cleanup = p.finally(() => executing.delete(p));

    if (executing.size >= concurrency) {
      await Promise.race(executing);
    }
  }

  await Promise.all(executing);
  return results;
}

// Process 100 URLs, max 5 at a time
const responses = await mapWithConcurrency(urls, fetch, 5);
```

## Worker Threads (Node.js)

```typescript
// main.ts
import { Worker } from "worker_threads";

function runWorker(data: unknown): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const worker = new Worker("./worker.js", { workerData: data });
    worker.on("message", resolve);
    worker.on("error", reject);
  });
}

// Process heavy computation in parallel
const results = await Promise.all(
  chunks.map((chunk) => runWorker({ type: "process", data: chunk })),
);
```

```typescript
// worker.ts
import { parentPort, workerData } from "worker_threads";

function heavyComputation(data: number[]): number {
  return data.reduce((sum, n) => sum + Math.sqrt(n), 0);
}

const result = heavyComputation(workerData.data);
parentPort?.postMessage(result);
```

## Async Iterators

```typescript
// Process a stream of data
async function* paginate<T>(fetchPage: (page: number) => Promise<{ data: T[]; hasMore: boolean }>) {
  let page = 1;
  while (true) {
    const result = await fetchPage(page);
    yield* result.data;
    if (!result.hasMore) break;
    page++;
  }
}

// Usage
for await (const user of paginate(fetchUsersPage)) {
  await processUser(user);
}
```

## Python asyncio

```python
import asyncio
import aiohttp

async def fetch_url(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        return await response.text()

async def fetch_all(urls: list[str]) -> list[str]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)

# With semaphore for concurrency limiting
async def fetch_with_limit(urls: list[str], max_concurrent: int = 10):
    semaphore = asyncio.Semaphore(max_concurrent)

    async def limited_fetch(session: aiohttp.ClientSession, url: str):
        async with semaphore:
            return await fetch_url(session, url)

    async with aiohttp.ClientSession() as session:
        return await asyncio.gather(*[limited_fetch(session, u) for u in urls])
```

## Go Goroutines and Channels

```go
// Fan-out, fan-in pattern
func processItems(items []string) []Result {
    results := make(chan Result, len(items))
    var wg sync.WaitGroup

    // Fan-out: launch goroutine per item
    for _, item := range items {
        wg.Add(1)
        go func(item string) {
            defer wg.Done()
            results <- process(item)
        }(item)
    }

    // Close channel when all done
    go func() {
        wg.Wait()
        close(results)
    }()

    // Fan-in: collect results
    var out []Result
    for r := range results {
        out = append(out, r)
    }
    return out
}

// Worker pool with bounded concurrency
func workerPool(jobs <-chan Job, results chan<- Result, workers int) {
    var wg sync.WaitGroup
    for i := 0; i < workers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for job := range jobs {
                results <- processJob(job)
            }
        }()
    }
    wg.Wait()
    close(results)
}
```

## Additional Resources

- MDN Async iteration: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/for-await...of
- Node.js worker threads: https://nodejs.org/api/worker_threads.html
- Python asyncio: https://docs.python.org/3/library/asyncio.html
- Go concurrency: https://go.dev/doc/effective_go#concurrency
