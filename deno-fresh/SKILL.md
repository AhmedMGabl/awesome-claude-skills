---
name: deno-fresh
description: Deno Fresh patterns covering islands architecture, route handlers, middleware, Preact components, server-side rendering, form handling, and edge deployment.
---

# Deno Fresh

This skill should be used when building web applications with Deno Fresh. It covers islands, routes, middleware, Preact components, SSR, forms, and deployment.

## When to Use This Skill

Use this skill when you need to:

- Build server-rendered apps with islands architecture
- Create API routes and middleware in Fresh
- Use Preact components with selective hydration
- Handle forms and file uploads
- Deploy to Deno Deploy edge network

## Route Handlers

```typescript
// routes/api/users.ts
import { Handlers } from "$fresh/server.ts";

interface User {
  id: string;
  name: string;
  email: string;
}

export const handler: Handlers = {
  async GET(_req, ctx) {
    const users = await db.query<User>("SELECT * FROM users ORDER BY name");
    return new Response(JSON.stringify(users), {
      headers: { "Content-Type": "application/json" },
    });
  },

  async POST(req, _ctx) {
    const body = await req.json();
    const user = await db.query(
      "INSERT INTO users (name, email) VALUES ($1, $2) RETURNING *",
      [body.name, body.email],
    );
    return new Response(JSON.stringify(user[0]), { status: 201 });
  },
};
```

## Page Routes with Data

```typescript
// routes/users/[id].tsx
import { Handlers, PageProps } from "$fresh/server.ts";

interface Data {
  user: User;
  posts: Post[];
}

export const handler: Handlers<Data> = {
  async GET(_req, ctx) {
    const user = await getUser(ctx.params.id);
    if (!user) return ctx.renderNotFound();
    const posts = await getUserPosts(ctx.params.id);
    return ctx.render({ user, posts });
  },
};

export default function UserPage({ data }: PageProps<Data>) {
  const { user, posts } = data;
  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
      <h2>Posts</h2>
      <ul>
        {posts.map((post) => (
          <li key={post.id}>{post.title}</li>
        ))}
      </ul>
    </div>
  );
}
```

## Islands (Interactive Components)

```typescript
// islands/Counter.tsx
import { useSignal } from "@preact/signals";

export default function Counter({ initial = 0 }: { initial?: number }) {
  const count = useSignal(initial);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => count.value++}>+</button>
      <button onClick={() => count.value--}>-</button>
    </div>
  );
}

// islands/SearchBox.tsx
import { useSignal } from "@preact/signals";

export default function SearchBox() {
  const query = useSignal("");
  const results = useSignal<string[]>([]);

  const search = async () => {
    const res = await fetch(`/api/search?q=${query.value}`);
    results.value = await res.json();
  };

  return (
    <div>
      <input
        value={query}
        onInput={(e) => { query.value = e.currentTarget.value; }}
        onKeyUp={(e) => { if (e.key === "Enter") search(); }}
        placeholder="Search..."
      />
      <ul>
        {results.value.map((r) => <li key={r}>{r}</li>)}
      </ul>
    </div>
  );
}
```

## Middleware

```typescript
// routes/_middleware.ts
import { FreshContext } from "$fresh/server.ts";

export async function handler(req: Request, ctx: FreshContext) {
  const start = performance.now();
  const resp = await ctx.next();
  const duration = performance.now() - start;
  resp.headers.set("X-Response-Time", `${duration.toFixed(2)}ms`);
  return resp;
}

// routes/api/_middleware.ts (auth)
export async function handler(req: Request, ctx: FreshContext) {
  const token = req.headers.get("Authorization")?.replace("Bearer ", "");
  if (!token) {
    return new Response("Unauthorized", { status: 401 });
  }
  ctx.state.user = await verifyToken(token);
  return ctx.next();
}
```

## Layouts

```typescript
// routes/_layout.tsx
import { PageProps } from "$fresh/server.ts";

export default function Layout({ Component }: PageProps) {
  return (
    <html>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <link rel="stylesheet" href="/styles.css" />
      </head>
      <body>
        <nav><a href="/">Home</a> | <a href="/about">About</a></nav>
        <main><Component /></main>
        <footer>Built with Fresh</footer>
      </body>
    </html>
  );
}
```

## Additional Resources

- Fresh: https://fresh.deno.dev/docs/
- Deno: https://docs.deno.com/
- Preact Signals: https://preactjs.com/guide/v10/signals/
