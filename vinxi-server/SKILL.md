---
name: vinxi-server
description: Vinxi meta-framework patterns covering app configuration, routers, server functions, middleware, API routes, static asset handling, and integration with React, Solid, and other UI frameworks for full-stack JavaScript applications.
---

# Vinxi Server

This skill should be used when building full-stack applications with Vinxi. It covers app configuration, routers, server functions, middleware, and multi-framework integration.

## When to Use This Skill

Use this skill when you need to:

- Configure a Vinxi full-stack application
- Define custom routers for different concerns
- Use server functions for RPC-style calls
- Add middleware and API routes
- Build framework-agnostic server infrastructure

## App Configuration

```typescript
// app.config.ts
import { createApp } from "vinxi";

export default createApp({
  routers: [
    {
      name: "public",
      type: "static",
      dir: "./public",
    },
    {
      name: "client",
      type: "client",
      handler: "./app/client.tsx",
      target: "browser",
      plugins: () => [],
      base: "/_build",
    },
    {
      name: "ssr",
      type: "http",
      handler: "./app/server.tsx",
      target: "server",
      plugins: () => [],
    },
    {
      name: "api",
      type: "http",
      handler: "./app/api.ts",
      target: "server",
      base: "/api",
    },
  ],
});
```

## Server Functions

```typescript
// app/server/db.ts
"use server";

import { db } from "./database";

export async function getUsers() {
  return db.select().from(users).all();
}

export async function createUser(data: { name: string; email: string }) {
  return db.insert(users).values(data).returning().get();
}

export async function deleteUser(id: string) {
  return db.delete(users).where(eq(users.id, id)).returning().get();
}

// Client-side usage
// app/components/UserList.tsx
import { getUsers, deleteUser } from "../server/db";

function UserList() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    getUsers().then(setUsers);
  }, []);

  const handleDelete = async (id: string) => {
    await deleteUser(id);
    setUsers((prev) => prev.filter((u) => u.id !== id));
  };

  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>
          {user.name}
          <button onClick={() => handleDelete(user.id)}>Delete</button>
        </li>
      ))}
    </ul>
  );
}
```

## API Routes

```typescript
// app/api.ts
import { eventHandler, createRouter, getQuery, readBody } from "vinxi/http";

const router = createRouter();

router.get(
  "/api/health",
  eventHandler(() => ({ status: "ok", timestamp: Date.now() })),
);

router.get(
  "/api/users",
  eventHandler(async (event) => {
    const { page = "1", limit = "20" } = getQuery(event);
    const users = await fetchUsers(Number(page), Number(limit));
    return users;
  }),
);

router.post(
  "/api/users",
  eventHandler(async (event) => {
    const body = await readBody(event);
    const user = await createUser(body);
    return user;
  }),
);

export default router.handler;
```

## Middleware

```typescript
// app/middleware/auth.ts
import { eventHandler, getHeader, createError } from "vinxi/http";

export const authMiddleware = eventHandler(async (event) => {
  const token = getHeader(event, "authorization")?.replace("Bearer ", "");

  if (!token) {
    throw createError({ statusCode: 401, message: "Unauthorized" });
  }

  const user = await verifyToken(token);
  event.context.user = user;
});

// Using middleware in router config
// app.config.ts
import { createApp } from "vinxi";

export default createApp({
  routers: [
    {
      name: "api",
      type: "http",
      handler: "./app/api.ts",
      target: "server",
      base: "/api",
      middleware: "./app/middleware/auth.ts",
    },
  ],
});
```

## SSR Handler

```typescript
// app/server.tsx
import { eventHandler, setHeader } from "vinxi/http";
import { renderToString } from "react-dom/server";
import { App } from "./App";

export default eventHandler(async (event) => {
  const html = renderToString(<App url={event.path} />);

  setHeader(event, "Content-Type", "text/html");

  return `<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>My App</title>
  </head>
  <body>
    <div id="root">${html}</div>
    <script type="module" src="/_build/client.tsx"></script>
  </body>
</html>`;
});
```

## File System Routing

```typescript
// app.config.ts
import { createApp } from "vinxi";
import { fileSystemRouter } from "vinxi/file-system-router";

export default createApp({
  routers: [
    {
      name: "api",
      type: "http",
      base: "/api",
      handler: "./app/api/index.ts",
      target: "server",
      routes: fileSystemRouter({
        dir: "./app/api",
        style: "nextjs",
      }),
    },
  ],
});
```

## Additional Resources

- Vinxi docs: https://vinxi.vercel.app/
- GitHub: https://github.com/nksaraf/vinxi
- Nitro (underlying engine): https://nitro.build/
