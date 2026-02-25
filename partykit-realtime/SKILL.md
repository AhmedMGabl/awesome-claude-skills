---
name: partykit-realtime
description: PartyKit real-time collaboration covering party servers, WebSocket connections, room-based state, presence, broadcast, storage, scheduled tasks, and React integration for multiplayer applications.
---

# PartyKit

This skill should be used when building real-time collaborative features with PartyKit. It covers party servers, WebSocket rooms, presence, and React integration.

## When to Use This Skill

Use this skill when you need to:

- Build real-time multiplayer features
- Implement collaborative editing
- Manage shared room state with WebSockets
- Track user presence and cursors
- Build chat, polls, or live dashboards

## Party Server

```typescript
// party/index.ts
import type { Party, PartyConnection, PartyRequest } from "partykit/server";

export default class ChatRoom implements Party.Server {
  messages: { user: string; text: string; timestamp: number }[] = [];

  constructor(public room: Party.Room) {}

  onConnect(conn: PartyConnection) {
    // Send existing messages to new connection
    conn.send(JSON.stringify({ type: "history", messages: this.messages }));

    // Broadcast join
    this.room.broadcast(
      JSON.stringify({ type: "join", user: conn.id }),
      [conn.id],
    );
  }

  onMessage(message: string, sender: PartyConnection) {
    const data = JSON.parse(message);

    if (data.type === "message") {
      const msg = { user: sender.id, text: data.text, timestamp: Date.now() };
      this.messages.push(msg);

      // Broadcast to all connections
      this.room.broadcast(JSON.stringify({ type: "message", ...msg }));
    }
  }

  onClose(conn: PartyConnection) {
    this.room.broadcast(JSON.stringify({ type: "leave", user: conn.id }));
  }
}
```

## Client Connection

```typescript
import PartySocket from "partysocket";

const socket = new PartySocket({
  host: "my-project.username.partykit.dev",
  room: "chat-room-1",
});

socket.addEventListener("message", (event) => {
  const data = JSON.parse(event.data);
  switch (data.type) {
    case "history":
      setMessages(data.messages);
      break;
    case "message":
      setMessages((prev) => [...prev, data]);
      break;
    case "join":
      console.log(`${data.user} joined`);
      break;
  }
});

// Send message
socket.send(JSON.stringify({ type: "message", text: "Hello!" }));
```

## Presence

```typescript
// Server - track presence
export default class Room implements Party.Server {
  presence = new Map<string, { cursor: { x: number; y: number }; name: string }>();

  onMessage(message: string, sender: PartyConnection) {
    const data = JSON.parse(message);

    if (data.type === "presence") {
      this.presence.set(sender.id, data.value);
      this.room.broadcast(
        JSON.stringify({
          type: "presence",
          userId: sender.id,
          value: data.value,
        }),
        [sender.id],
      );
    }
  }

  onClose(conn: PartyConnection) {
    this.presence.delete(conn.id);
    this.room.broadcast(JSON.stringify({ type: "leave", userId: conn.id }));
  }
}
```

## React Hook

```tsx
import usePartySocket from "partysocket/react";

function ChatRoom({ roomId }: { roomId: string }) {
  const [messages, setMessages] = useState<Message[]>([]);

  const socket = usePartySocket({
    host: "my-project.username.partykit.dev",
    room: roomId,
    onMessage: (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "message") {
        setMessages((prev) => [...prev, data]);
      }
    },
  });

  const sendMessage = (text: string) => {
    socket.send(JSON.stringify({ type: "message", text }));
  };

  return (
    <div>
      {messages.map((msg, i) => (
        <div key={i}>{msg.user}: {msg.text}</div>
      ))}
      <input onKeyDown={(e) => {
        if (e.key === "Enter") {
          sendMessage(e.currentTarget.value);
          e.currentTarget.value = "";
        }
      }} />
    </div>
  );
}
```

## Storage (Durable)

```typescript
export default class Room implements Party.Server {
  async onMessage(message: string, sender: PartyConnection) {
    const data = JSON.parse(message);

    if (data.type === "save") {
      await this.room.storage.put("state", data.value);
    }

    if (data.type === "load") {
      const state = await this.room.storage.get("state");
      sender.send(JSON.stringify({ type: "state", value: state }));
    }
  }
}
```

## Additional Resources

- PartyKit docs: https://docs.partykit.io/
- Guides: https://docs.partykit.io/guides/
- Examples: https://docs.partykit.io/examples/
