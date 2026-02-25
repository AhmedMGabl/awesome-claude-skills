---
name: graphql-subscriptions
description: GraphQL subscriptions for real-time data covering WebSocket transport with graphql-ws, subscription resolvers, pub/sub with Redis, filtering subscriptions, authentication in WebSocket connections, client-side subscription hooks, and scaling subscriptions in production.
---

# GraphQL Subscriptions

This skill should be used when implementing real-time features with GraphQL subscriptions. It covers WebSocket setup, pub/sub patterns, filtering, authentication, and production scaling.

## When to Use This Skill

Use this skill when you need to:

- Add real-time updates to a GraphQL API
- Implement chat, notifications, or live feeds
- Set up WebSocket transport with graphql-ws
- Scale subscriptions with Redis pub/sub
- Authenticate WebSocket connections

## Server Setup

```typescript
import { createServer } from "http";
import { WebSocketServer } from "ws";
import { useServer } from "graphql-ws/lib/use/ws";
import { makeExecutableSchema } from "@graphql-tools/schema";
import express from "express";

const app = express();
const httpServer = createServer(app);

const schema = makeExecutableSchema({ typeDefs, resolvers });

const wsServer = new WebSocketServer({
  server: httpServer,
  path: "/graphql",
});

useServer(
  {
    schema,
    context: async (ctx) => {
      // Authenticate WebSocket connection
      const token = ctx.connectionParams?.authorization as string;
      if (!token) throw new Error("Missing auth token");
      const user = await verifyToken(token);
      return { user };
    },
    onConnect: async (ctx) => {
      console.log("Client connected");
    },
    onDisconnect: (ctx) => {
      console.log("Client disconnected");
    },
  },
  wsServer,
);

httpServer.listen(4000);
```

## Schema and Resolvers

```typescript
const typeDefs = `#graphql
  type Message {
    id: ID!
    content: String!
    sender: User!
    roomId: String!
    createdAt: String!
  }

  type Notification {
    id: ID!
    type: String!
    message: String!
    read: Boolean!
  }

  type Subscription {
    messageAdded(roomId: String!): Message!
    notificationReceived: Notification!
    typingIndicator(roomId: String!): TypingEvent!
  }

  type Mutation {
    sendMessage(roomId: String!, content: String!): Message!
  }
`;

import { PubSub, withFilter } from "graphql-subscriptions";

const pubsub = new PubSub();

const resolvers = {
  Subscription: {
    messageAdded: {
      subscribe: withFilter(
        () => pubsub.asyncIterableIterator(["MESSAGE_ADDED"]),
        (payload, variables) => {
          return payload.messageAdded.roomId === variables.roomId;
        },
      ),
    },
    notificationReceived: {
      subscribe: withFilter(
        () => pubsub.asyncIterableIterator(["NOTIFICATION"]),
        (payload, _variables, context) => {
          return payload.notificationReceived.userId === context.user.id;
        },
      ),
    },
  },
  Mutation: {
    sendMessage: async (_: any, { roomId, content }: any, { user }: any) => {
      const message = await db.messages.create({
        data: { roomId, content, senderId: user.id },
      });

      await pubsub.publish("MESSAGE_ADDED", {
        messageAdded: { ...message, sender: user },
      });

      return message;
    },
  },
};
```

## Redis Pub/Sub for Scaling

```typescript
import { RedisPubSub } from "graphql-redis-subscriptions";
import { Redis } from "ioredis";

const pubsub = new RedisPubSub({
  publisher: new Redis(process.env.REDIS_URL),
  subscriber: new Redis(process.env.REDIS_URL),
});

// Use exactly the same way as in-memory PubSub
// Now works across multiple server instances
```

## Client-Side (React + Apollo)

```typescript
import { useSubscription, gql } from "@apollo/client";

const MESSAGE_SUBSCRIPTION = gql`
  subscription OnMessageAdded($roomId: String!) {
    messageAdded(roomId: $roomId) {
      id
      content
      sender { id name avatar }
      createdAt
    }
  }
`;

function ChatRoom({ roomId }: { roomId: string }) {
  const { data, loading, error } = useSubscription(MESSAGE_SUBSCRIPTION, {
    variables: { roomId },
    onData: ({ data }) => {
      // Handle new message (play sound, scroll, etc.)
    },
  });

  if (loading) return <p>Connecting...</p>;
  if (error) return <p>Subscription error: {error.message}</p>;

  return <MessageBubble message={data?.messageAdded} />;
}
```

## Apollo Client WebSocket Setup

```typescript
import { ApolloClient, InMemoryCache, split, HttpLink } from "@apollo/client";
import { GraphQLWsLink } from "@apollo/client/link/subscriptions";
import { createClient } from "graphql-ws";
import { getMainDefinition } from "@apollo/client/utilities";

const httpLink = new HttpLink({ uri: "/graphql" });

const wsLink = new GraphQLWsLink(
  createClient({
    url: "ws://localhost:4000/graphql",
    connectionParams: { authorization: getToken() },
    shouldRetry: () => true,
    retryAttempts: 5,
  }),
);

const splitLink = split(
  ({ query }) => {
    const definition = getMainDefinition(query);
    return (
      definition.kind === "OperationDefinition" &&
      definition.operation === "subscription"
    );
  },
  wsLink,
  httpLink,
);

const client = new ApolloClient({
  link: splitLink,
  cache: new InMemoryCache(),
});
```

## Subscription Patterns

```
PATTERN              USE CASE                      EXAMPLE
────────────────────────────────────────────────────────────
Live query           Data sync                     Order status updates
Event stream         Activity feeds                New comments, likes
Presence             Online/typing indicators      Chat typing status
Fan-out              Broadcast to group            Room messages
Filtered             Per-user events               User notifications
```

## Additional Resources

- graphql-ws: https://github.com/enisdenjo/graphql-ws
- Apollo Subscriptions: https://www.apollographql.com/docs/react/data/subscriptions
- graphql-redis-subscriptions: https://github.com/davidyaha/graphql-redis-subscriptions
