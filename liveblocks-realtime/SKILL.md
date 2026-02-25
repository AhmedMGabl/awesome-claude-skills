---
name: liveblocks-realtime
description: Liveblocks real-time collaboration patterns covering presence, live cursors, storage with conflict-free data types, Yjs text editing, comments, notifications, and React hooks for multiplayer experiences.
---

# Liveblocks Real-time

This skill should be used when building real-time collaborative features with Liveblocks. It covers presence, cursors, storage, text editing, comments, and notifications.

## When to Use This Skill

Use this skill when you need to:

- Add multiplayer presence and cursors
- Build collaborative document editing
- Use conflict-free replicated data types
- Add comments and notifications to apps
- Implement real-time state synchronization

## Setup

```bash
npm install @liveblocks/client @liveblocks/react @liveblocks/node
```

```typescript
// liveblocks.config.ts
import { createClient } from "@liveblocks/client";
import { createRoomContext } from "@liveblocks/react";

const client = createClient({
  publicApiKey: process.env.NEXT_PUBLIC_LIVEBLOCKS_PUBLIC_KEY!,
});

type Presence = {
  cursor: { x: number; y: number } | null;
  name: string;
  color: string;
};

type Storage = {
  items: LiveList<Item>;
  document: LiveObject<DocumentData>;
};

export const {
  RoomProvider,
  useOthers,
  useMyPresence,
  useSelf,
  useStorage,
  useMutation,
  useStatus,
} = createRoomContext<Presence, Storage>(client);
```

## Presence and Cursors

```tsx
import { RoomProvider, useOthers, useMyPresence } from "./liveblocks.config";

function Room({ roomId }: { roomId: string }) {
  return (
    <RoomProvider
      id={roomId}
      initialPresence={{ cursor: null, name: "User", color: "#ff0000" }}
      initialStorage={{ items: new LiveList([]) }}
    >
      <Canvas />
    </RoomProvider>
  );
}

function Canvas() {
  const [myPresence, updateMyPresence] = useMyPresence();
  const others = useOthers();

  return (
    <div
      style={{ width: "100vw", height: "100vh", position: "relative" }}
      onPointerMove={(e) => {
        updateMyPresence({ cursor: { x: e.clientX, y: e.clientY } });
      }}
      onPointerLeave={() => {
        updateMyPresence({ cursor: null });
      }}
    >
      {/* Render other users' cursors */}
      {others.map(({ connectionId, presence }) => {
        if (!presence.cursor) return null;
        return (
          <div
            key={connectionId}
            style={{
              position: "absolute",
              left: presence.cursor.x,
              top: presence.cursor.y,
              transform: "translate(-50%, -50%)",
              pointerEvents: "none",
            }}
          >
            <svg width="24" height="24" viewBox="0 0 24 24">
              <path d="M5 3l14 8-7 2-3 7z" fill={presence.color} />
            </svg>
            <span style={{ color: presence.color }}>{presence.name}</span>
          </div>
        );
      })}
    </div>
  );
}
```

## Storage (Conflict-free Data)

```tsx
import { useStorage, useMutation } from "./liveblocks.config";
import { LiveList, LiveObject } from "@liveblocks/client";

function TodoList() {
  const items = useStorage((root) => root.items);

  const addItem = useMutation(({ storage }, text: string) => {
    const items = storage.get("items");
    items.push(
      new LiveObject({
        id: crypto.randomUUID(),
        text,
        done: false,
        createdAt: Date.now(),
      })
    );
  }, []);

  const toggleItem = useMutation(({ storage }, id: string) => {
    const items = storage.get("items");
    const item = items.find((i) => i.get("id") === id);
    if (item) {
      item.set("done", !item.get("done"));
    }
  }, []);

  const deleteItem = useMutation(({ storage }, id: string) => {
    const items = storage.get("items");
    const index = items.findIndex((i) => i.get("id") === id);
    if (index !== -1) {
      items.delete(index);
    }
  }, []);

  if (!items) return <div>Loading...</div>;

  return (
    <div>
      <form onSubmit={(e) => {
        e.preventDefault();
        const input = e.currentTarget.elements.namedItem("text") as HTMLInputElement;
        addItem(input.value);
        input.value = "";
      }}>
        <input name="text" placeholder="Add item..." />
        <button type="submit">Add</button>
      </form>
      {items.map((item) => (
        <div key={item.id}>
          <input
            type="checkbox"
            checked={item.done}
            onChange={() => toggleItem(item.id)}
          />
          <span>{item.text}</span>
          <button onClick={() => deleteItem(item.id)}>Delete</button>
        </div>
      ))}
    </div>
  );
}
```

## Who's Online

```tsx
function WhoIsOnline() {
  const others = useOthers();
  const self = useSelf();

  return (
    <div style={{ display: "flex", gap: 4 }}>
      {self && (
        <div
          style={{
            width: 32,
            height: 32,
            borderRadius: "50%",
            background: self.presence.color,
            border: "2px solid white",
          }}
          title={`${self.presence.name} (You)`}
        />
      )}
      {others.map(({ connectionId, presence }) => (
        <div
          key={connectionId}
          style={{
            width: 32,
            height: 32,
            borderRadius: "50%",
            background: presence.color,
          }}
          title={presence.name}
        />
      ))}
    </div>
  );
}
```

## Authentication

```typescript
// app/api/liveblocks-auth/route.ts
import { Liveblocks } from "@liveblocks/node";

const liveblocks = new Liveblocks({ secret: process.env.LIVEBLOCKS_SECRET_KEY! });

export async function POST(request: Request) {
  const user = await getAuthenticatedUser(request);

  const session = liveblocks.prepareSession(user.id, {
    userInfo: {
      name: user.name,
      avatar: user.avatar,
      color: user.color,
    },
  });

  session.allow(`room:${user.teamId}:*`, session.FULL_ACCESS);

  const { body, status } = await session.authorize();
  return new Response(body, { status });
}
```

## Additional Resources

- Liveblocks: https://liveblocks.io/
- React docs: https://liveblocks.io/docs/get-started/react
- Storage: https://liveblocks.io/docs/products/storage
