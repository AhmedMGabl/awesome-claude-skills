---
name: supabase-realtime
description: Supabase Realtime covering Postgres changes, broadcast channels, presence tracking, database triggers, row-level security filters, and React/Next.js subscription patterns.
---

# Supabase Realtime

This skill should be used when building real-time features with Supabase Realtime. It covers database changes, broadcast, presence, and subscription patterns.

## When to Use This Skill

Use this skill when you need to:

- Listen to Postgres database changes in real-time
- Build collaborative features with presence
- Broadcast messages to connected clients
- Filter real-time events with RLS policies
- Build chat, notifications, or live dashboards

## Database Changes

```typescript
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
);

// Listen to all changes on a table
const channel = supabase
  .channel("messages-changes")
  .on(
    "postgres_changes",
    { event: "*", schema: "public", table: "messages" },
    (payload) => {
      console.log("Change:", payload.eventType, payload.new);
    },
  )
  .subscribe();

// Listen to specific events
supabase
  .channel("new-orders")
  .on(
    "postgres_changes",
    { event: "INSERT", schema: "public", table: "orders" },
    (payload) => {
      console.log("New order:", payload.new);
    },
  )
  .subscribe();

// Filter by column value
supabase
  .channel("my-messages")
  .on(
    "postgres_changes",
    {
      event: "INSERT",
      schema: "public",
      table: "messages",
      filter: `room_id=eq.${roomId}`,
    },
    (payload) => {
      addMessage(payload.new);
    },
  )
  .subscribe();
```

## Broadcast

```typescript
// Send messages to all connected clients (no database involved)
const channel = supabase.channel("room-1");

// Subscribe and listen
channel
  .on("broadcast", { event: "cursor" }, (payload) => {
    updateCursor(payload.payload);
  })
  .on("broadcast", { event: "typing" }, (payload) => {
    showTypingIndicator(payload.payload.userId);
  })
  .subscribe();

// Send broadcast
channel.send({
  type: "broadcast",
  event: "cursor",
  payload: { x: 100, y: 200, userId: "user-1" },
});
```

## Presence

```typescript
const channel = supabase.channel("room-1");

// Track presence
channel
  .on("presence", { event: "sync" }, () => {
    const state = channel.presenceState();
    const users = Object.values(state).flat();
    setOnlineUsers(users);
  })
  .on("presence", { event: "join" }, ({ newPresences }) => {
    console.log("Joined:", newPresences);
  })
  .on("presence", { event: "leave" }, ({ leftPresences }) => {
    console.log("Left:", leftPresences);
  })
  .subscribe(async (status) => {
    if (status === "SUBSCRIBED") {
      await channel.track({
        userId: user.id,
        name: user.name,
        online_at: new Date().toISOString(),
      });
    }
  });

// Untrack on leave
await channel.untrack();
```

## React Hook

```tsx
import { useEffect, useState } from "react";
import { createClient, RealtimePostgresChangesPayload } from "@supabase/supabase-js";

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

function useRealtimeMessages(roomId: string) {
  const [messages, setMessages] = useState<Message[]>([]);

  useEffect(() => {
    // Fetch initial messages
    supabase
      .from("messages")
      .select("*, user:users(name, avatar)")
      .eq("room_id", roomId)
      .order("created_at", { ascending: true })
      .then(({ data }) => setMessages(data ?? []));

    // Subscribe to new messages
    const channel = supabase
      .channel(`room-${roomId}`)
      .on(
        "postgres_changes",
        {
          event: "INSERT",
          schema: "public",
          table: "messages",
          filter: `room_id=eq.${roomId}`,
        },
        (payload) => {
          setMessages((prev) => [...prev, payload.new as Message]);
        },
      )
      .subscribe();

    return () => { supabase.removeChannel(channel); };
  }, [roomId]);

  const sendMessage = async (text: string) => {
    await supabase.from("messages").insert({ room_id: roomId, text, user_id: user.id });
  };

  return { messages, sendMessage };
}
```

## Row-Level Security for Realtime

```sql
-- Enable RLS on messages table
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Users can only see messages in rooms they belong to
CREATE POLICY "Users see room messages" ON messages
  FOR SELECT USING (
    room_id IN (
      SELECT room_id FROM room_members WHERE user_id = auth.uid()
    )
  );

-- Enable realtime for the table
ALTER PUBLICATION supabase_realtime ADD TABLE messages;
```

## Additional Resources

- Supabase Realtime docs: https://supabase.com/docs/guides/realtime
- Broadcast: https://supabase.com/docs/guides/realtime/broadcast
- Presence: https://supabase.com/docs/guides/realtime/presence
