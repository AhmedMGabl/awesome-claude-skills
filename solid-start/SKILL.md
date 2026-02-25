---
name: solid-start
description: SolidStart full-stack framework patterns covering file-based routing, server functions, API routes, data loading with createAsync, middleware, sessions, SSR/SSG modes, and deployment configuration.
---

# SolidStart

This skill should be used when building full-stack applications with SolidStart. It covers routing, server functions, data loading, middleware, sessions, and deployment.

## When to Use This Skill

Use this skill when you need to:

- Build full-stack Solid.js applications with SolidStart
- Define file-based routes with nested layouts
- Use server functions for type-safe RPC
- Load data with createAsync and cache
- Configure SSR, SSG, or client-side rendering modes

## File-Based Routing

```typescript
// src/routes/index.tsx
export default function Home() {
  return <h1>Welcome to SolidStart</h1>;
}

// src/routes/about.tsx
export default function About() {
  return <h1>About</h1>;
}

// src/routes/users/[id].tsx
import { useParams } from "@solidjs/router";

export default function UserPage() {
  const params = useParams<{ id: string }>();
  return <h1>User {params.id}</h1>;
}

// src/routes/posts/[...slug].tsx (catch-all)
import { useParams } from "@solidjs/router";

export default function PostPage() {
  const params = useParams<{ slug: string }>();
  return <h1>Post: {params.slug}</h1>;
}
```

## Layouts

```tsx
// src/routes/(app).tsx - Layout for grouped routes
import { RouteSectionProps } from "@solidjs/router";

export default function AppLayout(props: RouteSectionProps) {
  return (
    <div class="app-layout">
      <nav>
        <a href="/">Home</a>
        <a href="/dashboard">Dashboard</a>
      </nav>
      <main>{props.children}</main>
    </div>
  );
}

// src/routes/(app)/dashboard.tsx
// Automatically wrapped by (app).tsx layout
export default function Dashboard() {
  return <h1>Dashboard</h1>;
}
```

## Server Functions

```typescript
"use server";

import { db } from "~/lib/db";

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
import { createAsync } from "@solidjs/router";
import { getUsers } from "~/server/users";

export default function UsersPage() {
  const users = createAsync(() => getUsers());

  return (
    <ul>
      <For each={users()}>{(user) => <li>{user.name}</li>}</For>
    </ul>
  );
}
```

## Data Loading with Cache

```typescript
import { cache, createAsync, useParams } from "@solidjs/router";
import { Show } from "solid-js";

// Define cached data loader
const getUser = cache(async (id: string) => {
  "use server";
  const user = await db.select().from(users).where(eq(users.id, id)).get();
  if (!user) throw new Error("User not found");
  return user;
}, "user");

// Preload data for route
export const route = {
  preload: ({ params }: { params: { id: string } }) => getUser(params.id),
};

export default function UserPage() {
  const params = useParams<{ id: string }>();
  const user = createAsync(() => getUser(params.id));

  return (
    <Show when={user()} fallback={<p>Loading...</p>}>
      {(u) => (
        <div>
          <h1>{u().name}</h1>
          <p>{u().email}</p>
        </div>
      )}
    </Show>
  );
}
```

## API Routes

```typescript
// src/routes/api/users.ts
import type { APIEvent } from "@solidjs/start/server";

export async function GET(event: APIEvent) {
  const users = await db.select().from(usersTable).all();
  return Response.json(users);
}

export async function POST(event: APIEvent) {
  const body = await event.request.json();
  const user = await db.insert(usersTable).values(body).returning().get();
  return Response.json(user, { status: 201 });
}

// src/routes/api/users/[id].ts
export async function GET(event: APIEvent) {
  const id = event.params.id;
  const user = await db.select().from(usersTable).where(eq(usersTable.id, id)).get();
  if (!user) return new Response("Not found", { status: 404 });
  return Response.json(user);
}
```

## Middleware

```typescript
// src/middleware.ts
import { createMiddleware } from "@solidjs/start/middleware";

export default createMiddleware({
  onRequest: [
    (event) => {
      // Runs on every request
      console.log(`${event.request.method} ${event.request.url}`);
    },
    async (event) => {
      // Auth check
      const token = event.request.headers.get("authorization");
      if (event.request.url.includes("/api/admin") && !token) {
        return new Response("Unauthorized", { status: 401 });
      }
    },
  ],
  onBeforeResponse: [
    (event, response) => {
      response.headers.set("X-Powered-By", "SolidStart");
    },
  ],
});
```

## App Configuration

```typescript
// app.config.ts
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  server: {
    preset: "node-server", // or "cloudflare-pages", "vercel", "netlify"
    prerender: {
      routes: ["/", "/about"],
    },
  },
  vite: {
    plugins: [],
  },
});
```

## Additional Resources

- SolidStart docs: https://start.solidjs.com/
- Solid.js docs: https://www.solidjs.com/
- Router: https://docs.solidjs.com/solid-router
