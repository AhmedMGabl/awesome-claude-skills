---
name: socket-io
description: Socket.IO real-time communication covering server setup with Express and standalone modes, client connection with auto-reconnection, rooms and namespaces, broadcasting patterns, authentication middleware, TypeScript typed events, React integration hooks, horizontal scaling with Redis adapter, error handling, disconnect recovery, and testing strategies.
---

# Socket.IO Real-Time Communication

This skill should be used when building real-time features with Socket.IO. It covers server configuration, client integration, typed events, room management, authentication, scaling, and production-ready patterns for bidirectional event-based communication.

## When to Use This Skill

- Set up a Socket.IO server with Express or as a standalone service
- Connect clients with automatic reconnection and fallback transports
- Organize connections with rooms and namespaces
- Broadcast events to specific audiences (room, all, all except sender)
- Authenticate socket connections with middleware
- Define strongly typed events in TypeScript
- Integrate Socket.IO into React applications with custom hooks
- Scale horizontally across multiple server instances with the Redis adapter
- Handle errors, disconnects, and connection lifecycle
- Test Socket.IO servers and client interactions

## Server Setup

### With Express

```typescript
import express from "express";
import { createServer } from "http";
import { Server } from "socket.io";

const app = express();
const httpServer = createServer(app);

const io = new Server(httpServer, {
  cors: {
    origin: process.env.CLIENT_URL ?? "http://localhost:3000",
    methods: ["GET", "POST"],
    credentials: true,
  },
  pingTimeout: 60_000,
  pingInterval: 25_000,
  maxHttpBufferSize: 1e6, // 1 MB max payload
  connectionStateRecovery: {
    maxDisconnectionDuration: 2 * 60_000, // 2 minutes
    skipMiddlewares: true,
  },
});

app.get("/health", (_req, res) => {
  res.json({ status: "ok", connections: io.engine.clientsCount });
});

httpServer.listen(3001, () => {
  console.log("Socket.IO server listening on port 3001");
});
```

### Standalone (No Express)

```typescript
import { Server } from "socket.io";

const io = new Server(3001, {
  cors: {
    origin: process.env.CLIENT_URL ?? "http://localhost:3000",
  },
  transports: ["websocket", "polling"],
});

io.on("connection", (socket) => {
  console.log(`Connected: ${socket.id}`);
});
```

## TypeScript Typed Events

Define event maps for full type safety across server and client.

```typescript
// shared/events.ts -- shared between server and client packages
export interface ServerToClientEvents {
  "chat:message": (message: ChatMessage) => void;
  "chat:typing": (data: { userId: string; username: string }) => void;
  "chat:typing-stopped": (data: { userId: string }) => void;
  "user:joined": (data: { userId: string; username: string }) => void;
  "user:left": (data: { userId: string }) => void;
  "presence:update": (data: { userId: string; status: PresenceStatus }) => void;
  "error:custom": (data: { code: string; message: string }) => void;
}

export interface ClientToServerEvents {
  "chat:send": (
    data: { roomId: string; content: string },
    ack: (response: { messageId: string }) => void
  ) => void;
  "chat:typing-start": (roomId: string) => void;
  "chat:typing-stop": (roomId: string) => void;
  "room:join": (
    roomId: string,
    ack: (response: { success: boolean; error?: string }) => void
  ) => void;
  "room:leave": (roomId: string) => void;
}

export interface InterServerEvents {
  ping: () => void;
}

export interface SocketData {
  user: {
    id: string;
    name: string;
    email: string;
    roles: string[];
  };
  joinedRooms: Set<string>;
}

export interface ChatMessage {
  id: string;
  userId: string;
  username: string;
  content: string;
  roomId: string;
  timestamp: string;
}

export type PresenceStatus = "online" | "away" | "busy" | "offline";
```

### Applying Types to the Server

```typescript
import { Server } from "socket.io";
import type {
  ServerToClientEvents,
  ClientToServerEvents,
  InterServerEvents,
  SocketData,
} from "../shared/events.js";

const io = new Server<
  ClientToServerEvents,
  ServerToClientEvents,
  InterServerEvents,
  SocketData
>(httpServer, {
  cors: { origin: process.env.CLIENT_URL },
});

// All event handlers are now fully typed
io.on("connection", (socket) => {
  // socket.data.user is typed as SocketData["user"]
  const user = socket.data.user;

  socket.on("chat:send", async (data, ack) => {
    // data is typed as { roomId: string; content: string }
    // ack is typed as (response: { messageId: string }) => void
    const message = {
      id: crypto.randomUUID(),
      userId: user.id,
      username: user.name,
      content: data.content,
      roomId: data.roomId,
      timestamp: new Date().toISOString(),
    };

    io.to(`room:${data.roomId}`).emit("chat:message", message);
    ack({ messageId: message.id });
  });
});
```

## Client Connection and Auto-Reconnection

```typescript
import { io, Socket } from "socket.io-client";
import type {
  ServerToClientEvents,
  ClientToServerEvents,
} from "../shared/events.js";

type TypedSocket = Socket<ServerToClientEvents, ClientToServerEvents>;

function createSocket(token: string): TypedSocket {
  const socket: TypedSocket = io(
    process.env.NEXT_PUBLIC_SOCKET_URL ?? "http://localhost:3001",
    {
      auth: { token },
      reconnection: true,
      reconnectionDelay: 1_000,
      reconnectionDelayMax: 10_000,
      reconnectionAttempts: 20,
      transports: ["websocket", "polling"],
      timeout: 10_000,
      autoConnect: false, // connect manually after setting up listeners
    }
  );

  socket.on("connect", () => {
    console.log(`Connected: ${socket.id}`);
  });

  socket.on("disconnect", (reason) => {
    console.log(`Disconnected: ${reason}`);
    if (reason === "io server disconnect") {
      // Server forced disconnect; must reconnect manually
      socket.connect();
    }
    // Otherwise the client will auto-reconnect
  });

  socket.on("connect_error", (err) => {
    console.error("Connection error:", err.message);
    if (err.message === "Authentication failed") {
      // Stop reconnecting on auth failure; refresh token instead
      socket.disconnect();
    }
  });

  socket.io.on("reconnect", (attempt) => {
    console.log(`Reconnected after ${attempt} attempts`);
  });

  socket.io.on("reconnect_attempt", (attempt) => {
    console.log(`Reconnection attempt ${attempt}`);
  });

  socket.connect();
  return socket;
}
```

## Rooms and Namespaces

### Rooms

Rooms are server-side groupings of sockets. Clients cannot join rooms on their own; the server must add them.

```typescript
io.on("connection", (socket) => {
  const user = socket.data.user;
  socket.data.joinedRooms = new Set<string>();

  // Join the user's personal room for direct messages
  socket.join(`user:${user.id}`);

  socket.on("room:join", async (roomId, ack) => {
    // Authorize room access before joining
    const hasAccess = await checkRoomAccess(user.id, roomId);
    if (!hasAccess) {
      ack({ success: false, error: "Access denied" });
      return;
    }

    socket.join(`room:${roomId}`);
    socket.data.joinedRooms.add(roomId);

    // Notify others in the room
    socket.to(`room:${roomId}`).emit("user:joined", {
      userId: user.id,
      username: user.name,
    });

    ack({ success: true });
  });

  socket.on("room:leave", (roomId) => {
    socket.leave(`room:${roomId}`);
    socket.data.joinedRooms.delete(roomId);

    socket.to(`room:${roomId}`).emit("user:left", { userId: user.id });
  });

  // Clean up all rooms on disconnect
  socket.on("disconnecting", () => {
    for (const roomId of socket.data.joinedRooms) {
      socket.to(`room:${roomId}`).emit("user:left", { userId: user.id });
    }
  });
});
```

### Listing Room Members

```typescript
async function getRoomMembers(
  io: Server,
  roomId: string
): Promise<string[]> {
  const sockets = await io.in(`room:${roomId}`).fetchSockets();
  return sockets.map((s) => s.data.user.id);
}
```

### Namespaces

Namespaces provide separate communication channels on a single connection.

```typescript
// Admin namespace with its own auth
const adminNamespace = io.of("/admin");

adminNamespace.use(async (socket, next) => {
  const token = socket.handshake.auth.token;
  try {
    const user = await verifyToken(token);
    if (!user.roles.includes("admin")) {
      return next(new Error("Admin access required"));
    }
    socket.data.user = user;
    next();
  } catch {
    next(new Error("Authentication failed"));
  }
});

adminNamespace.on("connection", (socket) => {
  console.log(`Admin connected: ${socket.data.user.name}`);
});

// Chat namespace
const chatNamespace = io.of("/chat");

chatNamespace.on("connection", (socket) => {
  // Chat-specific logic here
});

// Dynamic namespaces using regex
const workspaceNamespace = io.of(/^\/workspace\/\w+$/);

workspaceNamespace.on("connection", (socket) => {
  const workspace = socket.nsp.name; // e.g. "/workspace/abc123"
  console.log(`User joined workspace: ${workspace}`);
});
```

## Broadcasting Patterns

```typescript
io.on("connection", (socket) => {
  const user = socket.data.user;

  socket.on("chat:send", async (data, ack) => {
    const message = {
      id: crypto.randomUUID(),
      userId: user.id,
      username: user.name,
      content: data.content,
      roomId: data.roomId,
      timestamp: new Date().toISOString(),
    };

    await saveMessage(message);

    // --- Broadcasting variants ---

    // 1. To all clients in a room (including sender)
    io.to(`room:${data.roomId}`).emit("chat:message", message);

    // 2. To all clients in a room EXCEPT the sender
    socket.to(`room:${data.roomId}`).emit("chat:message", message);

    // 3. To all connected clients everywhere
    io.emit("chat:message", message);

    // 4. To all connected clients EXCEPT the sender
    socket.broadcast.emit("chat:message", message);

    // 5. To multiple rooms at once
    io.to("room:general").to("room:announcements").emit("chat:message", message);

    // 6. To a specific user via their personal room
    io.to(`user:${targetUserId}`).emit("chat:message", message);

    // 7. To all clients except those in a specific room
    io.except("room:muted").emit("chat:message", message);

    ack({ messageId: message.id });
  });
});

// Broadcasting from outside connection handlers (e.g. HTTP routes, job workers)
app.post("/api/notifications", async (req, res) => {
  const { userId, payload } = req.body;
  io.to(`user:${userId}`).emit("chat:message", payload);
  res.json({ sent: true });
});
```

## Authentication Middleware

### JWT Token Authentication

```typescript
import jwt from "jsonwebtoken";

io.use(async (socket, next) => {
  const token = socket.handshake.auth.token;

  if (!token) {
    return next(new Error("Authentication required"));
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as {
      userId: string;
      email: string;
    };

    const user = await getUserById(decoded.userId);
    if (!user) {
      return next(new Error("User not found"));
    }

    socket.data.user = {
      id: user.id,
      name: user.name,
      email: user.email,
      roles: user.roles,
    };

    next();
  } catch (err) {
    if (err instanceof jwt.TokenExpiredError) {
      return next(new Error("Token expired"));
    }
    next(new Error("Authentication failed"));
  }
});
```

### Chaining Multiple Middleware

```typescript
// 1. Rate-limit connections per IP
io.use((socket, next) => {
  const ip =
    socket.handshake.headers["x-forwarded-for"] ?? socket.handshake.address;
  const connections = getConnectionCount(ip as string);

  if (connections >= 10) {
    return next(new Error("Too many connections from this IP"));
  }

  next();
});

// 2. Authenticate
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

// 3. Authorize (e.g. check account is active)
io.use(async (socket, next) => {
  const user = socket.data.user;
  const account = await getAccount(user.id);

  if (account.suspended) {
    return next(new Error("Account suspended"));
  }

  next();
});
```

### Refreshing Tokens on Reconnection

```typescript
// Client-side: supply a fresh token on each reconnect attempt
const socket = io("http://localhost:3001", {
  auth: (cb) => {
    cb({ token: getLatestAccessToken() });
  },
  reconnection: true,
});
```

## React Integration Hooks

### Core Socket Provider and Hook

```typescript
// context/SocketContext.tsx
import {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  useCallback,
  type ReactNode,
} from "react";
import { io, Socket } from "socket.io-client";
import type {
  ServerToClientEvents,
  ClientToServerEvents,
} from "../../shared/events.js";

type TypedSocket = Socket<ServerToClientEvents, ClientToServerEvents>;

interface SocketContextValue {
  socket: TypedSocket | null;
  connected: boolean;
}

const SocketContext = createContext<SocketContextValue>({
  socket: null,
  connected: false,
});

export function SocketProvider({
  url,
  token,
  children,
}: {
  url: string;
  token: string;
  children: ReactNode;
}) {
  const socketRef = useRef<TypedSocket | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const socket: TypedSocket = io(url, {
      auth: { token },
      reconnection: true,
      reconnectionDelay: 1_000,
      reconnectionDelayMax: 10_000,
      reconnectionAttempts: 20,
      transports: ["websocket", "polling"],
    });

    socket.on("connect", () => setConnected(true));
    socket.on("disconnect", () => setConnected(false));

    socketRef.current = socket;

    return () => {
      socket.disconnect();
      socketRef.current = null;
    };
  }, [url, token]);

  return (
    <SocketContext.Provider value={{ socket: socketRef.current, connected }}>
      {children}
    </SocketContext.Provider>
  );
}

export function useSocket(): SocketContextValue {
  return useContext(SocketContext);
}
```

### Event Listener Hook

```typescript
// hooks/useSocketEvent.ts
import { useEffect, useRef } from "react";
import { useSocket } from "../context/SocketContext.js";
import type { ServerToClientEvents } from "../../shared/events.js";

export function useSocketEvent<K extends keyof ServerToClientEvents>(
  event: K,
  handler: ServerToClientEvents[K]
): void {
  const { socket } = useSocket();
  const handlerRef = useRef(handler);
  handlerRef.current = handler;

  useEffect(() => {
    if (!socket) return;

    const listener = (...args: unknown[]) => {
      (handlerRef.current as (...a: unknown[]) => void)(...args);
    };

    socket.on(event as string, listener);
    return () => {
      socket.off(event as string, listener);
    };
  }, [socket, event]);
}
```

### Emit Hook with Acknowledgement Support

```typescript
// hooks/useSocketEmit.ts
import { useCallback } from "react";
import { useSocket } from "../context/SocketContext.js";
import type { ClientToServerEvents } from "../../shared/events.js";

export function useSocketEmit() {
  const { socket } = useSocket();

  const emit = useCallback(
    <K extends keyof ClientToServerEvents>(
      event: K,
      ...args: Parameters<ClientToServerEvents[K]>
    ) => {
      if (!socket?.connected) {
        console.warn(`Cannot emit "${String(event)}": socket not connected`);
        return;
      }
      socket.emit(event, ...args);
    },
    [socket]
  );

  return emit;
}
```

### Example Chat Component

```tsx
// components/ChatRoom.tsx
import { useState, useEffect } from "react";
import { useSocket } from "../context/SocketContext.js";
import { useSocketEvent } from "../hooks/useSocketEvent.js";
import { useSocketEmit } from "../hooks/useSocketEmit.js";
import type { ChatMessage } from "../../shared/events.js";

export function ChatRoom({ roomId }: { roomId: string }) {
  const { connected } = useSocket();
  const emit = useSocketEmit();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");

  // Join room on mount
  useEffect(() => {
    if (!connected) return;

    emit("room:join", roomId, (res) => {
      if (!res.success) {
        console.error("Failed to join room:", res.error);
      }
    });

    return () => {
      emit("room:leave", roomId);
    };
  }, [roomId, connected, emit]);

  // Listen for incoming messages
  useSocketEvent("chat:message", (message) => {
    if (message.roomId === roomId) {
      setMessages((prev) => [...prev, message]);
    }
  });

  const sendMessage = () => {
    if (!input.trim()) return;

    emit("chat:send", { roomId, content: input }, (res) => {
      console.log("Message sent:", res.messageId);
    });
    setInput("");
  };

  return (
    <div>
      <div>{connected ? "Connected" : "Reconnecting..."}</div>
      <ul>
        {messages.map((msg) => (
          <li key={msg.id}>
            <strong>{msg.username}:</strong> {msg.content}
          </li>
        ))}
      </ul>
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        placeholder="Type a message..."
      />
      <button onClick={sendMessage} disabled={!connected}>
        Send
      </button>
    </div>
  );
}
```

### App-Level Setup

```tsx
// App.tsx
import { SocketProvider } from "./context/SocketContext.js";
import { ChatRoom } from "./components/ChatRoom.js";

export function App() {
  const token = useAuthToken(); // your auth hook

  return (
    <SocketProvider
      url={process.env.NEXT_PUBLIC_SOCKET_URL ?? "http://localhost:3001"}
      token={token}
    >
      <ChatRoom roomId="general" />
    </SocketProvider>
  );
}
```

## Scaling with Redis Adapter

When running multiple Socket.IO server instances behind a load balancer, use the Redis adapter so events reach all connected clients regardless of which instance they are connected to.

### Setup

```typescript
import { Server } from "socket.io";
import { createAdapter } from "@socket.io/redis-adapter";
import { createClient } from "redis";

const io = new Server(httpServer, {
  cors: { origin: process.env.CLIENT_URL },
});

const pubClient = createClient({ url: process.env.REDIS_URL });
const subClient = pubClient.duplicate();

await Promise.all([pubClient.connect(), subClient.connect()]);

io.adapter(createAdapter(pubClient, subClient));
```

### Sticky Sessions

Socket.IO requires sticky sessions when using multiple server processes with HTTP long-polling. Configure the load balancer to route requests from the same client to the same server instance. With Nginx:

```nginx
upstream socketio_nodes {
    ip_hash;  # sticky sessions
    server 127.0.0.1:3001;
    server 127.0.0.1:3002;
    server 127.0.0.1:3003;
}

server {
    listen 80;

    location /socket.io/ {
        proxy_pass http://socketio_nodes;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Alternatively, force the WebSocket transport only and skip sticky sessions:

```typescript
// Server
const io = new Server(httpServer, {
  transports: ["websocket"],
});

// Client
const socket = io("http://localhost:3001", {
  transports: ["websocket"],
});
```

### Emitting Across Instances

With the Redis adapter in place, standard emit calls automatically propagate:

```typescript
// This reaches all clients in the room across all server instances
io.to("room:general").emit("chat:message", message);

// Fetch sockets across all instances
const sockets = await io.in("room:general").fetchSockets();
console.log(`${sockets.length} users in general room (across all instances)`);
```

### Redis Streams Adapter (Higher Reliability)

For environments where messages must not be lost (e.g. during Redis reconnections), use the Redis Streams adapter:

```typescript
import { createAdapter } from "@socket.io/redis-streams-adapter";
import { createClient } from "redis";

const redisClient = createClient({ url: process.env.REDIS_URL });
await redisClient.connect();

io.adapter(createAdapter(redisClient));
```

## Error Handling and Disconnect Patterns

### Server-Side Error Handling

```typescript
io.on("connection", (socket) => {
  // Catch-all listener for debugging
  socket.onAny((event, ...args) => {
    console.log(`[${socket.id}] ${event}`, args);
  });

  // Wrap handlers to catch async errors
  const safeHandler = <T extends unknown[]>(
    handler: (...args: T) => Promise<void>
  ) => {
    return async (...args: T) => {
      try {
        await handler(...args);
      } catch (err) {
        console.error(`Error in handler [${socket.id}]:`, err);
        socket.emit("error:custom", {
          code: "INTERNAL_ERROR",
          message: "An unexpected error occurred",
        });
      }
    };
  };

  socket.on(
    "chat:send",
    safeHandler(async (data, ack) => {
      // Validate input
      if (!data.content || data.content.length > 5000) {
        socket.emit("error:custom", {
          code: "VALIDATION_ERROR",
          message: "Message content is required and must be under 5000 characters",
        });
        return;
      }

      const message = await createAndBroadcastMessage(io, socket, data);
      ack({ messageId: message.id });
    })
  );

  // Disconnect reasons and cleanup
  socket.on("disconnect", (reason) => {
    console.log(`Disconnected [${socket.id}]: ${reason}`);

    switch (reason) {
      case "server namespace disconnect":
        // Server called socket.disconnect()
        break;
      case "client namespace disconnect":
        // Client called socket.disconnect()
        break;
      case "ping timeout":
        // Client stopped responding to pings
        break;
      case "transport close":
        // Connection was closed (browser tab, network loss)
        break;
      case "transport error":
        // Connection encountered an error
        break;
    }

    // Clean up presence, room state, etc.
    removePresence(socket.data.user.id);
  });

  // Fired before the socket leaves all rooms (useful for "user left" notifications)
  socket.on("disconnecting", (reason) => {
    for (const room of socket.rooms) {
      if (room !== socket.id) {
        socket.to(room).emit("user:left", { userId: socket.data.user.id });
      }
    }
  });
});
```

### Graceful Server Shutdown

```typescript
async function shutdown() {
  console.log("Shutting down Socket.IO server...");

  // Notify all clients
  io.emit("error:custom", {
    code: "SERVER_SHUTDOWN",
    message: "Server is restarting. You will be reconnected automatically.",
  });

  // Close all connections
  io.close(() => {
    console.log("All connections closed");
    process.exit(0);
  });

  // Force exit after timeout
  setTimeout(() => {
    console.error("Forced shutdown after timeout");
    process.exit(1);
  }, 10_000);
}

process.on("SIGTERM", shutdown);
process.on("SIGINT", shutdown);
```

### Client-Side Connection State Machine

```typescript
import { io, type Socket } from "socket.io-client";

type ConnectionState = "connecting" | "connected" | "disconnected" | "error";

function createSocketWithState(url: string, token: string) {
  let state: ConnectionState = "connecting";
  const listeners = new Set<(s: ConnectionState) => void>();

  const socket = io(url, {
    auth: { token },
    reconnection: true,
    reconnectionAttempts: 20,
  });

  function setState(newState: ConnectionState) {
    state = newState;
    listeners.forEach((fn) => fn(state));
  }

  socket.on("connect", () => setState("connected"));
  socket.on("disconnect", () => setState("disconnected"));
  socket.on("connect_error", () => setState("error"));
  socket.io.on("reconnect", () => setState("connected"));

  return {
    socket,
    getState: () => state,
    onStateChange: (fn: (s: ConnectionState) => void) => {
      listeners.add(fn);
      return () => listeners.delete(fn);
    },
  };
}
```

## Testing Socket.IO Connections

### Server Integration Tests with Vitest

```typescript
import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { Server } from "socket.io";
import { io as clientIo, type Socket as ClientSocket } from "socket.io-client";
import { createServer, type Server as HttpServer } from "http";
import jwt from "jsonwebtoken";

describe("Socket.IO Server", () => {
  let httpServer: HttpServer;
  let io: Server;
  let clientSocket: ClientSocket;
  const PORT = 0; // random available port

  function createAuthToken(userId: string): string {
    return jwt.sign({ userId, email: "test@example.com" }, "test-secret");
  }

  beforeAll(
    () =>
      new Promise<void>((resolve) => {
        httpServer = createServer();
        io = new Server(httpServer);

        // Register the same middleware and handlers as production
        registerMiddleware(io);
        registerHandlers(io);

        httpServer.listen(PORT, () => {
          const port = (httpServer.address() as { port: number }).port;
          clientSocket = clientIo(`http://localhost:${port}`, {
            auth: { token: createAuthToken("user-1") },
            transports: ["websocket"],
          });
          clientSocket.on("connect", resolve);
        });
      })
  );

  afterAll(() =>
    new Promise<void>((resolve) => {
      clientSocket.disconnect();
      io.close(() => {
        httpServer.close(() => resolve());
      });
    })
  );

  it("should join a room and receive messages", () =>
    new Promise<void>((resolve) => {
      clientSocket.emit("room:join", "test-room", (res) => {
        expect(res.success).toBe(true);

        clientSocket.on("chat:message", (message) => {
          expect(message.content).toBe("Hello, room!");
          expect(message.roomId).toBe("test-room");
          resolve();
        });

        clientSocket.emit(
          "chat:send",
          { roomId: "test-room", content: "Hello, room!" },
          (ackRes) => {
            expect(ackRes.messageId).toBeDefined();
          }
        );
      });
    }));

  it("should reject unauthenticated connections", () =>
    new Promise<void>((resolve) => {
      const port = (httpServer.address() as { port: number }).port;
      const badSocket = clientIo(`http://localhost:${port}`, {
        auth: { token: "invalid-token" },
        transports: ["websocket"],
      });

      badSocket.on("connect_error", (err) => {
        expect(err.message).toBe("Authentication failed");
        badSocket.disconnect();
        resolve();
      });
    }));

  it("should handle acknowledgements", () =>
    new Promise<void>((resolve) => {
      clientSocket.emit(
        "chat:send",
        { roomId: "test-room", content: "ack test" },
        (res) => {
          expect(res.messageId).toBeDefined();
          expect(typeof res.messageId).toBe("string");
          resolve();
        }
      );
    }));
});
```

### Testing Multiple Clients

```typescript
describe("Multi-client interactions", () => {
  let httpServer: HttpServer;
  let io: Server;
  let client1: ClientSocket;
  let client2: ClientSocket;

  beforeAll(
    () =>
      new Promise<void>((resolve) => {
        httpServer = createServer();
        io = new Server(httpServer);
        registerMiddleware(io);
        registerHandlers(io);

        httpServer.listen(0, () => {
          const port = (httpServer.address() as { port: number }).port;
          const url = `http://localhost:${port}`;

          let connectedCount = 0;
          const onConnect = () => {
            connectedCount++;
            if (connectedCount === 2) resolve();
          };

          client1 = clientIo(url, {
            auth: { token: createAuthToken("user-1") },
            transports: ["websocket"],
          });
          client2 = clientIo(url, {
            auth: { token: createAuthToken("user-2") },
            transports: ["websocket"],
          });

          client1.on("connect", onConnect);
          client2.on("connect", onConnect);
        });
      })
  );

  afterAll(() =>
    new Promise<void>((resolve) => {
      client1.disconnect();
      client2.disconnect();
      io.close(() => httpServer.close(() => resolve()));
    })
  );

  it("should broadcast messages to other room members", () =>
    new Promise<void>((resolve) => {
      // Both clients join the same room
      client1.emit("room:join", "shared-room", () => {
        client2.emit("room:join", "shared-room", () => {
          // Client 2 listens for messages
          client2.on("chat:message", (message) => {
            expect(message.content).toBe("Hello from client 1");
            resolve();
          });

          // Client 1 sends a message
          client1.emit(
            "chat:send",
            { roomId: "shared-room", content: "Hello from client 1" },
            () => {}
          );
        });
      });
    }));

  it("should notify when a user leaves a room", () =>
    new Promise<void>((resolve) => {
      client1.emit("room:join", "leave-test", () => {
        client2.emit("room:join", "leave-test", () => {
          client1.on("user:left", (data) => {
            expect(data.userId).toBe("user-2");
            resolve();
          });

          client2.emit("room:leave", "leave-test");
        });
      });
    }));
});
```

### Testing with Supertest for HTTP + Socket.IO

```typescript
import request from "supertest";

describe("HTTP + Socket.IO", () => {
  it("should report connection count on health endpoint", async () => {
    // clientSocket is already connected from beforeAll
    const res = await request(httpServer).get("/health").expect(200);

    expect(res.body.status).toBe("ok");
    expect(res.body.connections).toBeGreaterThanOrEqual(1);
  });
});
```

## Additional Resources

- Socket.IO documentation: https://socket.io/docs/v4/
- Socket.IO Redis adapter: https://socket.io/docs/v4/redis-adapter/
- Socket.IO Redis Streams adapter: https://socket.io/docs/v4/redis-streams-adapter/
- Socket.IO with TypeScript: https://socket.io/docs/v4/typescript/
- Connection state recovery: https://socket.io/docs/v4/connection-state-recovery
