---
name: nuxt-server
description: Nuxt server patterns covering API routes with defineEventHandler, middleware, server utilities, database integration with Nitro, server plugins, caching with defineCachedFunction, WebSocket support, and server-side auth patterns.
---

# Nuxt Server

This skill should be used when building server-side features with Nuxt 3. It covers API routes, middleware, server utilities, caching, and Nitro server engine features.

## When to Use This Skill

Use this skill when you need to:

- Create API routes in Nuxt 3
- Add server middleware for auth or logging
- Cache server responses for performance
- Integrate databases with Nitro utilities
- Build WebSocket endpoints in Nuxt

## API Routes

```typescript
// server/api/users/index.get.ts
export default defineEventHandler(async (event) => {
  const query = getQuery(event);
  const page = Number(query.page ?? 1);
  const limit = Number(query.limit ?? 20);

  // Access database, external API, etc.
  const users = await $fetch("https://api.example.com/users", {
    query: { page, limit },
  });

  return users;
});

// server/api/users/index.post.ts
export default defineEventHandler(async (event) => {
  const body = await readBody(event);

  if (!body.name || !body.email) {
    throw createError({
      statusCode: 400,
      statusMessage: "Name and email are required",
    });
  }

  const user = await createUser(body);
  setResponseStatus(event, 201);
  return user;
});

// server/api/users/[id].get.ts
export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, "id");
  const user = await getUserById(id);

  if (!user) {
    throw createError({ statusCode: 404, statusMessage: "User not found" });
  }

  return user;
});

// server/api/users/[id].put.ts
export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, "id");
  const body = await readBody(event);
  return await updateUser(id, body);
});

// server/api/users/[id].delete.ts
export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, "id");
  await deleteUser(id);
  setResponseStatus(event, 204);
  return null;
});
```

## Server Middleware

```typescript
// server/middleware/auth.ts
export default defineEventHandler(async (event) => {
  const protectedRoutes = ["/api/admin", "/api/users"];
  const isProtected = protectedRoutes.some((route) =>
    event.path.startsWith(route),
  );

  if (!isProtected) return;

  const token = getHeader(event, "authorization")?.replace("Bearer ", "");
  if (!token) {
    throw createError({ statusCode: 401, statusMessage: "Unauthorized" });
  }

  try {
    const user = await verifyToken(token);
    event.context.user = user;
  } catch {
    throw createError({ statusCode: 401, statusMessage: "Invalid token" });
  }
});

// server/middleware/log.ts
export default defineEventHandler((event) => {
  console.log(`${event.method} ${event.path}`);
});
```

## Server Utilities

```typescript
// server/utils/db.ts
import { drizzle } from "drizzle-orm/better-sqlite3";
import Database from "better-sqlite3";

let _db: ReturnType<typeof drizzle>;

export function useDb() {
  if (!_db) {
    const sqlite = new Database("./data/db.sqlite");
    _db = drizzle(sqlite);
  }
  return _db;
}

// server/utils/auth.ts
import jwt from "jsonwebtoken";

const config = useRuntimeConfig();

export function signToken(payload: Record<string, unknown>) {
  return jwt.sign(payload, config.jwtSecret, { expiresIn: "7d" });
}

export function verifyToken(token: string) {
  return jwt.verify(token, config.jwtSecret);
}

// Usage in API route
// server/api/posts.get.ts
export default defineEventHandler(async () => {
  const db = useDb();
  return db.select().from(posts).all();
});
```

## Caching

```typescript
// server/api/stats.get.ts
export default defineCachedEventHandler(
  async () => {
    const stats = await computeExpensiveStats();
    return stats;
  },
  {
    maxAge: 60 * 60, // Cache for 1 hour
    name: "stats",
    getKey: () => "global-stats",
  },
);

// Cached function (reusable)
// server/utils/cached.ts
export const getPopularPosts = defineCachedFunction(
  async (limit: number) => {
    return await fetchPopularPosts(limit);
  },
  {
    maxAge: 60 * 10, // 10 minutes
    name: "popular-posts",
    getKey: (limit) => `popular-${limit}`,
  },
);
```

## Server Plugins

```typescript
// server/plugins/db.ts
export default defineNitroPlugin((nitro) => {
  // Run on server start
  console.log("Server starting, initializing database...");

  nitro.hooks.hook("close", () => {
    // Cleanup on server shutdown
    console.log("Closing database connections...");
  });

  nitro.hooks.hook("request", (event) => {
    // Run on every request
    event.context.requestId = crypto.randomUUID();
  });
});
```

## Session and Cookies

```typescript
// server/api/auth/login.post.ts
export default defineEventHandler(async (event) => {
  const { email, password } = await readBody(event);
  const user = await authenticate(email, password);

  if (!user) {
    throw createError({ statusCode: 401, statusMessage: "Invalid credentials" });
  }

  // Set session cookie
  const token = signToken({ userId: user.id });
  setCookie(event, "auth-token", token, {
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    maxAge: 60 * 60 * 24 * 7, // 7 days
  });

  return { user: { id: user.id, name: user.name } };
});

// server/api/auth/me.get.ts
export default defineEventHandler(async (event) => {
  const token = getCookie(event, "auth-token");
  if (!token) throw createError({ statusCode: 401 });

  const payload = verifyToken(token);
  return await getUserById(payload.userId);
});
```

## Additional Resources

- Nuxt server docs: https://nuxt.com/docs/guide/directory-structure/server
- Nitro docs: https://nitro.build/
- Server utilities: https://nuxt.com/docs/api/utils/define-event-handler
