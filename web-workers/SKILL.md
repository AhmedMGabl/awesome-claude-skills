---
name: web-workers
description: Web Workers for parallel processing covering dedicated workers, shared workers, worker pools, Comlink RPC, transferable objects, OffscreenCanvas, and integration with React, Vite, and webpack bundlers.
---

# Web Workers

This skill should be used when implementing parallel processing in web applications using Web Workers. It covers dedicated workers, shared workers, worker pools, Comlink, and bundler integration.

## When to Use This Skill

Use this skill when you need to:

- Offload CPU-intensive tasks from the main thread
- Process large datasets without blocking the UI
- Implement worker pools for parallel computation
- Use Comlink for ergonomic worker communication
- Integrate workers with React and bundlers

## Basic Dedicated Worker

```typescript
// worker.ts
self.addEventListener("message", (event: MessageEvent) => {
  const { type, data } = event.data;

  switch (type) {
    case "sort": {
      const sorted = [...data].sort((a, b) => a - b);
      self.postMessage({ type: "sorted", result: sorted });
      break;
    }
    case "filter": {
      const filtered = data.filter((item: any) => item.active);
      self.postMessage({ type: "filtered", result: filtered });
      break;
    }
  }
});

// main.ts
const worker = new Worker(new URL("./worker.ts", import.meta.url), {
  type: "module",
});

worker.addEventListener("message", (event) => {
  console.log("Result:", event.data.result);
});

worker.postMessage({ type: "sort", data: [3, 1, 4, 1, 5, 9] });

// Cleanup
worker.terminate();
```

## Transferable Objects

```typescript
// Transfer ArrayBuffer — zero-copy, original becomes detached
const buffer = new ArrayBuffer(1024 * 1024);
const data = new Float32Array(buffer);
// Fill data...

// Transfer ownership (not copy)
worker.postMessage({ type: "process", buffer }, [buffer]);
// buffer.byteLength === 0 after transfer

// Worker side
self.addEventListener("message", (event) => {
  const { buffer } = event.data;
  const data = new Float32Array(buffer);
  // Process data...
  // Transfer back
  self.postMessage({ result: buffer }, [buffer]);
});
```

## Comlink (RPC Pattern)

```typescript
// worker.ts
import * as Comlink from "comlink";

const api = {
  async processImage(imageData: ImageData): Promise<ImageData> {
    // CPU-intensive image processing
    const data = new Uint8ClampedArray(imageData.data);
    for (let i = 0; i < data.length; i += 4) {
      const avg = (data[i] + data[i + 1] + data[i + 2]) / 3;
      data[i] = data[i + 1] = data[i + 2] = avg; // Grayscale
    }
    return new ImageData(data, imageData.width, imageData.height);
  },

  async heavyComputation(input: number[]): Promise<number> {
    return input.reduce((sum, n) => sum + Math.sqrt(n), 0);
  },
};

Comlink.expose(api);

// main.ts
import * as Comlink from "comlink";

const worker = new Worker(new URL("./worker.ts", import.meta.url), {
  type: "module",
});

const api = Comlink.wrap<typeof import("./worker").api>(worker);

// Call as if it were a local async function
const result = await api.heavyComputation([1, 2, 3, 4, 5]);
console.log(result);
```

## Worker Pool

```typescript
class WorkerPool {
  private workers: Worker[] = [];
  private queue: Array<{
    data: any;
    resolve: (value: any) => void;
    reject: (reason: any) => void;
  }> = [];
  private available: Worker[] = [];

  constructor(workerUrl: URL, poolSize: number) {
    for (let i = 0; i < poolSize; i++) {
      const worker = new Worker(workerUrl, { type: "module" });
      this.workers.push(worker);
      this.available.push(worker);
    }
  }

  async execute<T>(data: any): Promise<T> {
    return new Promise((resolve, reject) => {
      const worker = this.available.pop();
      if (worker) {
        this.runTask(worker, data, resolve, reject);
      } else {
        this.queue.push({ data, resolve, reject });
      }
    });
  }

  private runTask(worker: Worker, data: any, resolve: Function, reject: Function) {
    const handler = (event: MessageEvent) => {
      worker.removeEventListener("message", handler);
      worker.removeEventListener("error", errorHandler);
      this.available.push(worker);
      this.processQueue();
      resolve(event.data);
    };
    const errorHandler = (error: ErrorEvent) => {
      worker.removeEventListener("message", handler);
      worker.removeEventListener("error", errorHandler);
      this.available.push(worker);
      this.processQueue();
      reject(error);
    };
    worker.addEventListener("message", handler);
    worker.addEventListener("error", errorHandler);
    worker.postMessage(data);
  }

  private processQueue() {
    if (this.queue.length > 0 && this.available.length > 0) {
      const { data, resolve, reject } = this.queue.shift()!;
      const worker = this.available.pop()!;
      this.runTask(worker, data, resolve, reject);
    }
  }

  terminate() {
    this.workers.forEach((w) => w.terminate());
  }
}

// Usage
const pool = new WorkerPool(
  new URL("./worker.ts", import.meta.url),
  navigator.hardwareConcurrency || 4,
);

const results = await Promise.all(
  chunks.map((chunk) => pool.execute<number[]>({ type: "sort", data: chunk })),
);
```

## React Hook

```tsx
import { useEffect, useRef, useState, useCallback } from "react";

function useWorker<TInput, TOutput>(workerUrl: URL) {
  const workerRef = useRef<Worker | null>(null);
  const [result, setResult] = useState<TOutput | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    workerRef.current = new Worker(workerUrl, { type: "module" });
    workerRef.current.onmessage = (e) => {
      setResult(e.data);
      setLoading(false);
    };
    workerRef.current.onerror = (e) => {
      setError(new Error(e.message));
      setLoading(false);
    };
    return () => workerRef.current?.terminate();
  }, [workerUrl]);

  const postMessage = useCallback((data: TInput) => {
    setLoading(true);
    setError(null);
    workerRef.current?.postMessage(data);
  }, []);

  return { result, loading, error, postMessage };
}

// Usage
function ImageProcessor() {
  const { result, loading, postMessage } = useWorker<ImageData, ImageData>(
    new URL("./image-worker.ts", import.meta.url),
  );

  return (
    <div>
      <button onClick={() => postMessage(imageData)} disabled={loading}>
        {loading ? "Processing..." : "Process Image"}
      </button>
    </div>
  );
}
```

## OffscreenCanvas

```typescript
// worker.ts
self.addEventListener("message", (event) => {
  const canvas = event.data.canvas as OffscreenCanvas;
  const ctx = canvas.getContext("2d")!;

  // Render-intensive animation in worker
  function render() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // Draw complex scene...
    requestAnimationFrame(render);
  }
  render();
});

// main.ts
const canvas = document.getElementById("canvas") as HTMLCanvasElement;
const offscreen = canvas.transferControlToOffscreen();
worker.postMessage({ canvas: offscreen }, [offscreen]);
```

## Additional Resources

- Web Workers API: https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API
- Comlink: https://github.com/GoogleChromeLabs/comlink
