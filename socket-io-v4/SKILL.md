---
name: socket-io-v4
description: Socket.IO v4 covering namespaces, rooms, acknowledgements, middleware, binary streaming, Redis adapter for horizontal scaling, and TypeScript-first event typing.
---

# Socket.IO v4

This skill should be used when building real-time communication with Socket.IO v4. It covers typed events, namespaces, rooms, middleware, and horizontal scaling.

## When to Use This Skill

Use this skill when you need to:

- Build real-time bidirectional communication
- Manage rooms and namespaces
- Scale WebSocket servers horizontally with Redis
- Type events end-to-end with TypeScript
- Handle reconnection and offline events

## Typed Server

```typescript
import { Server } from "socket.io";
import { createServer } from "http";

// Type definitions
interface ServerToClientEvents {
  message: (data: { user: string; text: string; timestamp: number }) => void;
  userJoined: (data: { userId: string; name: string }) => void;
  userLeft: (data: { userId: string }) => void;
  roomState: (data: { users: string[]; messageCount: number }) => void;
}

interface ClientToServerEvents {
  sendMessage: (text: string, callback: (ok: boolean) => void) => void;
  joinRoom: (roomId: string) => void;
  leaveRoom: (roomId: string) => void;
  typing: (roomId: string) => void;
}

interface InterServerEvents {
  ping: () => void;
}

interface SocketData {
  userId: string;
  name: string;
}

const httpServer = createServer();
const io = new Server<ClientToServerEvents, ServerToClientEvents, InterServerEvents, SocketData>(
  httpServer,
  {
    cors: { origin: "http://localhost:3000", methods: ["GET", "POST"] },
    pingInterval: 25000,
    pingTimeout: 20000,
  },
);
```

## Event Handling

```typescript
io.on("connection", (socket) => {
  console.log(`Connected: ${socket.id}`);

  // Set socket data
  socket.data.userId = socket.handshake.auth.userId;
  socket.data.name = socket.handshake.auth.name;

  // Join room
  socket.on("joinRoom", async (roomId) => {
    await socket.join(roomId);
    socket.to(roomId).emit("userJoined", {
      userId: socket.data.userId,
      name: socket.data.name,
    });
  });

  // Send message with acknowledgement
  socket.on("sendMessage", (text, callback) => {
    const rooms = [...socket.rooms].filter((r) => r !== socket.id);
    for (const room of rooms) {
      io.to(room).emit("message", {
        user: socket.data.name,
        text,
        timestamp: Date.now(),
      });
    }
    callback(true);
  });

  // Broadcast typing indicator
  socket.on("typing", (roomId) => {
    socket.to(roomId).volatile.emit("typing" as any, {
      userId: socket.data.userId,
    });
  });

  socket.on("disconnect", () => {
    io.emit("userLeft", { userId: socket.data.userId });
  });
});
```

## Middleware

```typescript
// Authentication middleware
io.use(async (socket, next) => {
  const token = socket.handshake.auth.token;
  if (!token) return next(new Error("Authentication required"));

  try {
    const user = await verifyToken(token);
    socket.data.userId = user.id;
    socket.data.name = user.name;
    next();
  } catch {
    next(new Error("Invalid token"));
  }
});

// Namespace middleware
const adminNamespace = io.of("/admin");
adminNamespace.use(async (socket, next) => {
  const user = await getUser(socket.data.userId);
  if (user?.role !== "admin") return next(new Error("Unauthorized"));
  next();
});
```

## Rooms

```typescript
// Join/leave rooms
socket.join("room-1");
socket.leave("room-1");

// Emit to room
io.to("room-1").emit("message", data);

// Emit to multiple rooms
io.to("room-1").to("room-2").emit("announcement", data);

// Emit to room except sender
socket.to("room-1").emit("message", data);

// Get room members
const sockets = await io.in("room-1").fetchSockets();
const users = sockets.map((s) => ({ id: s.data.userId, name: s.data.name }));
```

## Typed Client

```tsx
import { io, Socket } from "socket.io-client";

const socket: Socket<ServerToClientEvents, ClientToServerEvents> = io(
  "http://localhost:3001",
  { auth: { token: "jwt-token", userId: "123", name: "Alice" } },
);

// Listen
socket.on("message", (data) => {
  console.log(`${data.user}: ${data.text}`);
});

// Send with acknowledgement
socket.emit("sendMessage", "Hello!", (ok) => {
  console.log("Delivered:", ok);
});

// Connection events
socket.on("connect", () => console.log("Connected"));
socket.on("disconnect", (reason) => console.log("Disconnected:", reason));
socket.on("connect_error", (err) => console.error("Error:", err.message));
```

## Redis Adapter (Scaling)

```typescript
import { createAdapter } from "@socket.io/redis-adapter";
import { createClient } from "redis";

const pubClient = createClient({ url: "redis://localhost:6379" });
const subClient = pubClient.duplicate();

await Promise.all([pubClient.connect(), subClient.connect()]);

io.adapter(createAdapter(pubClient, subClient));
// Now multiple Socket.IO servers share rooms and events
```

## Additional Resources

- Socket.IO docs: https://socket.io/docs/v4/
- Server API: https://socket.io/docs/v4/server-api/
- Client API: https://socket.io/docs/v4/client-api/
