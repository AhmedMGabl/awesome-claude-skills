---
name: python-asyncio
description: Python asyncio patterns covering coroutines, tasks, gather, semaphores, queues, streams, event loops, async context managers, and concurrent programming.
---

# Python asyncio

This skill should be used when writing async Python code with asyncio. It covers coroutines, tasks, gather, semaphores, queues, streams, and concurrency patterns.

## When to Use This Skill

Use this skill when you need to:

- Write concurrent code with async/await
- Run multiple coroutines concurrently
- Use async queues and semaphores
- Implement TCP/UDP servers with streams
- Manage async context managers and generators

## Basic Coroutines

```python
import asyncio

async def fetch_data(url: str) -> str:
    await asyncio.sleep(1)  # simulate I/O
    return f"data from {url}"

async def main():
    result = await fetch_data("https://api.example.com")
    print(result)

asyncio.run(main())
```

## Concurrent Execution

```python
# gather: run multiple coroutines concurrently
async def fetch_all():
    results = await asyncio.gather(
        fetch_data("https://api.example.com/users"),
        fetch_data("https://api.example.com/posts"),
        fetch_data("https://api.example.com/comments"),
    )
    users, posts, comments = results
    return users, posts, comments

# TaskGroup (Python 3.11+)
async def fetch_with_taskgroup():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch_data("url1"))
        task2 = tg.create_task(fetch_data("url2"))
    return task1.result(), task2.result()
```

## Semaphore for Rate Limiting

```python
async def fetch_with_limit(urls: list[str], max_concurrent: int = 5):
    semaphore = asyncio.Semaphore(max_concurrent)
    results = []

    async def bounded_fetch(url: str):
        async with semaphore:
            return await fetch_data(url)

    tasks = [bounded_fetch(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results
```

## Async Queues

```python
async def producer(queue: asyncio.Queue):
    for i in range(20):
        item = f"item-{i}"
        await queue.put(item)
        print(f"Produced: {item}")
    await queue.put(None)  # sentinel

async def consumer(queue: asyncio.Queue, name: str):
    while True:
        item = await queue.get()
        if item is None:
            await queue.put(None)  # pass sentinel to next consumer
            break
        print(f"{name} processing: {item}")
        await asyncio.sleep(0.1)
        queue.task_done()

async def main():
    queue = asyncio.Queue(maxsize=10)
    await asyncio.gather(
        producer(queue),
        consumer(queue, "worker-1"),
        consumer(queue, "worker-2"),
    )
```

## Timeouts

```python
async def with_timeout():
    try:
        result = await asyncio.wait_for(slow_operation(), timeout=5.0)
        return result
    except asyncio.TimeoutError:
        print("Operation timed out")
        return None

# Deadline-based timeout (Python 3.11+)
async def with_deadline():
    async with asyncio.timeout(5.0):
        result = await slow_operation()
        return result
```

## Async Streams (TCP Server)

```python
async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info("peername")
    print(f"Connected: {addr}")

    while True:
        data = await reader.read(1024)
        if not data:
            break
        message = data.decode()
        print(f"Received from {addr}: {message}")
        writer.write(data)  # echo back
        await writer.drain()

    writer.close()
    await writer.wait_closed()

async def start_server():
    server = await asyncio.start_server(handle_client, "127.0.0.1", 8888)
    async with server:
        await server.serve_forever()
```

## Async Context Managers

```python
class AsyncDatabasePool:
    async def __aenter__(self):
        self.pool = await create_pool("postgres://localhost/db")
        return self.pool

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.pool.close()

async def main():
    async with AsyncDatabasePool() as pool:
        async with pool.acquire() as conn:
            result = await conn.fetch("SELECT * FROM users")
```

## Async Generators

```python
async def paginate(url: str, page_size: int = 10):
    page = 1
    while True:
        data = await fetch_page(url, page=page, size=page_size)
        if not data:
            break
        for item in data:
            yield item
        page += 1

async def process_all():
    async for item in paginate("https://api.example.com/items"):
        await process_item(item)
```

## Additional Resources

- asyncio: https://docs.python.org/3/library/asyncio.html
- Guide: https://docs.python.org/3/library/asyncio-task.html
- Patterns: https://realpython.com/async-io-python/
