---
name: websocket-realtime
description: WebSocket and real-time communication patterns covering Socket.IO, native WebSocket API, Server-Sent Events, pub/sub messaging, presence tracking, room management, reconnection strategies, and scalable real-time architecture.
---

# WebSocket & Real-time

This skill should be used when building real-time features in applications. It covers WebSocket servers, Socket.IO, Server-Sent Events, pub/sub patterns, and production-ready real-time architecture.

## When to Use This Skill

Use this skill when you need to:

- Build real-time chat, notifications, or live updates
- Implement WebSocket servers and clients
- Use Socket.IO for real-time communication
- Build presence systems (who's online)
- Implement Server-Sent Events (SSE) for one-way streaming
- Scale real-time systems with Redis pub/sub
- Handle reconnection and error recovery

## Socket.IO Server

```typescript
import { Server } from "socket.io";
import { createServer } from "http";
import { createAdapter } from "@socket.io/redis-adapter";
import { createClient } from "redis";

const httpServer = createServer();
const io = new Server(httpServer, {
  cors: { origin: process.env.CLIENT_URL, methods: ["GET", "POST"] },
  pingTimeout: 60000,
  pingInterval: 25000,
});

// Redis adapter for horizontal scaling
const pubClient = createClient({ url: process.env.REDIS_URL });
const subClient = pubClient.duplicate();
await Promise.all([pubClient.connect(), subClient.connect()]);
io.adapter(createAdapter(pubClient, subClient));

// Authentication middleware
io.use(async (socket, next) => {
  const token = socket.handshake.auth.token;
  try {
    const user = await verifyToken(token);
    socket.data.user = user;
    next();
  } catch {
    next(new Error("Authentication failed"));
  }
});

// Connection handling
io.on("connection", (socket) => {
  const user = socket.data.user;
  console.log(`User connected: ${user.id}`);

  // Join user's personal room
  socket.join(`user:${user.id}`);

  // Chat room management
  socket.on("join-room", async (roomId: string) => {
    socket.join(`room:${roomId}`);
    socket.to(`room:${roomId}`).emit("user-joined", {
      userId: user.id,
      username: user.name,
    });
  });

  socket.on("leave-room", (roomId: string) => {
    socket.leave(`room:${roomId}`);
    socket.to(`room:${roomId}`).emit("user-left", { userId: user.id });
  });

  // Messages
  socket.on("message", async (data: { roomId: string; content: string }) => {
    const message = {
      id: crypto.randomUUID(),
      userId: user.id,
      username: user.name,
      content: data.content,
      timestamp: new Date().toISOString(),
    };

    // Save to database
    await saveMessage(data.roomId, message);

    // Broadcast to room
    io.to(`room:${data.roomId}`).emit("message", message);
  });

  // Typing indicators
  socket.on("typing-start", (roomId: string) => {
    socket.to(`room:${roomId}`).emit("typing", { userId: user.id, username: user.name });
  });

  socket.on("typing-stop", (roomId: string) => {
    socket.to(`room:${roomId}`).emit("typing-stopped", { userId: user.id });
  });

  // Disconnect
  socket.on("disconnect", (reason) => {
    console.log(`User disconnected: ${user.id}, reason: ${reason}`);
  });
});

httpServer.listen(3001);
```

## Socket.IO Client (React)

```typescript
import { useEffect, useRef, useState, useCallback } from "react";
import { io, Socket } from "socket.io-client";

function useSocket(url: string, token: string) {
  const socketRef = useRef<Socket | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const socket = io(url, {
      auth: { token },
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 10,
    });

    socket.on("connect", () => setConnected(true));
    socket.on("disconnect", () => setConnected(false));
    socket.on("connect_error", (err) => console.error("Connection error:", err.message));

    socketRef.current = socket;
    return () => { socket.disconnect(); };
  }, [url, token]);

  const emit = useCallback((event: string, data?: unknown) => {
    socketRef.current?.emit(event, data);
  }, []);

  const on = useCallback((event: string, handler: (...args: unknown[]) => void) => {
    socketRef.current?.on(event, handler);
    return () => { socketRef.current?.off(event, handler); };
  }, []);

  return { socket: socketRef.current, connected, emit, on };
}

// Chat component
function ChatRoom({ roomId, token }: { roomId: string; token: string }) {
  const { connected, emit, on } = useSocket("http://localhost:3001", token);
  const [messages, setMessages] = useState<Message[]>([]);
  const [typingUsers, setTypingUsers] = useState<string[]>([]);

  useEffect(() => {
    emit("join-room", roomId);

    const offMessage = on("message", (msg: Message) => {
      setMessages((prev) => [...prev, msg]);
    });

    const offTyping = on("typing", (data: { username: string }) => {
      setTypingUsers((prev) => [...new Set([...prev, data.username])]);
    });

    const offTypingStopped = on("typing-stopped", (data: { userId: string }) => {
      setTypingUsers((prev) => prev.filter((u) => u !== data.userId));
    });

    return () => {
      emit("leave-room", roomId);
      offMessage();
      offTyping();
      offTypingStopped();
    };
  }, [roomId, emit, on]);

  const sendMessage = (content: string) => {
    emit("message", { roomId, content });
  };

  return (
    <div>
      <div>{connected ? "Connected" : "Disconnected"}</div>
      <MessageList messages={messages} />
      {typingUsers.length > 0 && <div>{typingUsers.join(", ")} typing...</div>}
      <MessageInput onSend={sendMessage} onTyping={() => emit("typing-start", roomId)} />
    </div>
  );
}
```

## Presence System

```typescript
// Server-side presence tracking
const presence = new Map<string, { socketId: string; status: string; lastSeen: Date }>();

io.on("connection", (socket) => {
  const userId = socket.data.user.id;

  // Track presence
  presence.set(userId, {
    socketId: socket.id,
    status: "online",
    lastSeen: new Date(),
  });

  // Broadcast presence to all
  io.emit("presence-update", {
    userId,
    status: "online",
  });

  // Status changes
  socket.on("set-status", (status: "online" | "away" | "busy") => {
    const entry = presence.get(userId);
    if (entry) {
      entry.status = status;
      io.emit("presence-update", { userId, status });
    }
  });

  socket.on("disconnect", () => {
    presence.delete(userId);
    io.emit("presence-update", { userId, status: "offline" });
  });
});

// Get online users for a room
function getRoomPresence(roomId: string): string[] {
  const room = io.sockets.adapter.rooms.get(`room:${roomId}`);
  if (!room) return [];
  return [...room]
    .map((socketId) => io.sockets.sockets.get(socketId)?.data.user.id)
    .filter(Boolean);
}
```

## Server-Sent Events (SSE)

```typescript
// Express SSE endpoint
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

  // Heartbeat
  const heartbeat = setInterval(() => res.write(": heartbeat\n\n"), 30000);

  // Event listener
  const onEvent = (data: unknown) => {
    res.write(`event: update\ndata: ${JSON.stringify(data)}\n\n`);
  };
  eventEmitter.on("update", onEvent);

  // Cleanup
  req.on("close", () => {
    clearInterval(heartbeat);
    eventEmitter.off("update", onEvent);
  });
});

// Client-side EventSource
const eventSource = new EventSource("/api/events");

eventSource.addEventListener("update", (event) => {
  const data = JSON.parse(event.data);
  handleUpdate(data);
});

eventSource.onerror = () => {
  // Browser auto-reconnects with EventSource
  console.log("SSE connection lost, reconnecting...");
};
```

## Native WebSocket Server

```typescript
import { WebSocketServer, WebSocket } from "ws";

const wss = new WebSocketServer({ port: 8080 });
const clients = new Map<string, WebSocket>();

wss.on("connection", (ws, req) => {
  const clientId = crypto.randomUUID();
  clients.set(clientId, ws);

  ws.on("message", (raw) => {
    const message = JSON.parse(raw.toString());

    switch (message.type) {
      case "broadcast":
        // Send to all except sender
        clients.forEach((client, id) => {
          if (id !== clientId && client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify(message.payload));
          }
        });
        break;
      case "direct":
        const target = clients.get(message.targetId);
        if (target?.readyState === WebSocket.OPEN) {
          target.send(JSON.stringify(message.payload));
        }
        break;
    }
  });

  ws.on("close", () => clients.delete(clientId));
  ws.on("error", (err) => console.error(`Client ${clientId} error:`, err));

  // Ping/pong keepalive
  const interval = setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) ws.ping();
  }, 30000);
  ws.on("close", () => clearInterval(interval));
});
```

## Production Scaling

```typescript
// Redis pub/sub for multi-server broadcasting
import { createClient } from "redis";

const publisher = createClient({ url: process.env.REDIS_URL });
const subscriber = publisher.duplicate();
await Promise.all([publisher.connect(), subscriber.connect()]);

// Publish events from any server
async function broadcastEvent(channel: string, data: unknown) {
  await publisher.publish(channel, JSON.stringify(data));
}

// Each server subscribes to channels
await subscriber.subscribe("notifications", (message) => {
  const data = JSON.parse(message);
  // Send to connected clients on this server
  io.to(`user:${data.userId}`).emit("notification", data);
});
```

## Additional Resources

- Socket.IO: https://socket.io/docs/v4/
- ws (WebSocket library): https://github.com/websockets/ws
- MDN WebSocket API: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
- MDN Server-Sent Events: https://developer.mozilla.org/en-US/docs/Web/API/EventSource
