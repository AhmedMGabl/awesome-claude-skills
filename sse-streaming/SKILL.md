---
name: sse-streaming
description: Server-Sent Events (SSE) covering event stream protocol, Node.js/Express/Hono implementations, reconnection handling, event types, React hooks for consuming streams, and comparison with WebSockets and polling.
---

# Server-Sent Events (SSE)

This skill should be used when implementing server-to-client streaming with SSE. It covers the EventSource API, server implementations, reconnection, and React integration.

## When to Use This Skill

Use this skill when you need to:

- Stream real-time updates from server to client
- Implement live notifications or activity feeds
- Stream AI/LLM responses token by token
- Send progress updates for long-running tasks
- Choose between SSE, WebSockets, and polling

## SSE vs WebSockets vs Polling

```
SSE                    WebSockets             Long Polling
────────────────────────────────────────────────────────────
Server → Client only   Bidirectional          Client → Server
HTTP/1.1 or HTTP/2     Custom protocol        HTTP
Auto-reconnect         Manual reconnect       Manual retry
Text/event-stream      Binary + text          Any format
Simple implementation  Complex setup          Simple but wasteful
Good for: feeds,       Good for: chat,        Good for: legacy
notifications, AI      gaming, collaboration  browser support
```

## Express Server

```typescript
import express from "express";

const app = express();

app.get("/api/events", (req, res) => {
  res.writeHead(200, {
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache",
    Connection: "keep-alive",
  });

  // Send initial data
  res.write(`data: ${JSON.stringify({ type: "connected" })}\n\n`);

  // Send periodic updates
  const interval = setInterval(() => {
    res.write(`data: ${JSON.stringify({ time: new Date().toISOString() })}\n\n`);
  }, 1000);

  // Named events
  res.write(`event: notification\ndata: ${JSON.stringify({ message: "Hello" })}\n\n`);

  // Set event ID for reconnection
  res.write(`id: 42\ndata: ${JSON.stringify({ seq: 42 })}\n\n`);

  req.on("close", () => {
    clearInterval(interval);
  });
});
```

## AI Token Streaming

```typescript
app.post("/api/chat", async (req, res) => {
  res.writeHead(200, {
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache",
    Connection: "keep-alive",
  });

  const stream = await openai.chat.completions.create({
    model: "gpt-4",
    messages: req.body.messages,
    stream: true,
  });

  for await (const chunk of stream) {
    const content = chunk.choices[0]?.delta?.content;
    if (content) {
      res.write(`data: ${JSON.stringify({ content })}\n\n`);
    }
  }

  res.write(`data: [DONE]\n\n`);
  res.end();
});
```

## Client (EventSource)

```typescript
const eventSource = new EventSource("/api/events");

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Message:", data);
};

// Named events
eventSource.addEventListener("notification", (event) => {
  const data = JSON.parse(event.data);
  console.log("Notification:", data);
});

eventSource.onerror = () => {
  console.log("Connection lost, reconnecting...");
};

// Cleanup
eventSource.close();
```

## React Hook

```typescript
function useSSE<T>(url: string) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const es = new EventSource(url);

    es.onopen = () => setConnected(true);
    es.onmessage = (event) => setData(JSON.parse(event.data));
    es.onerror = () => {
      setConnected(false);
      setError(new Error("SSE connection failed"));
    };

    return () => es.close();
  }, [url]);

  return { data, error, connected };
}

// Usage
function LiveFeed() {
  const { data, connected } = useSSE<Activity>("/api/events");
  return (
    <div>
      <span>{connected ? "Connected" : "Reconnecting..."}</span>
      {data && <ActivityCard activity={data} />}
    </div>
  );
}
```

## Additional Resources

- MDN EventSource: https://developer.mozilla.org/en-US/docs/Web/API/EventSource
- SSE Spec: https://html.spec.whatwg.org/multipage/server-sent-events.html
