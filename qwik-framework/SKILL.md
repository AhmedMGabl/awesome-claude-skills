---
name: qwik-framework
description: Qwik framework covering resumability, component creation, useSignal/useStore state, routeLoader$ and routeAction$, server$ functions, middleware, layout routes, and Qwik City deployment.
---

# Qwik Framework

This skill should be used when building applications with Qwik and Qwik City. It covers resumability, component$ creation, state management, data loading, mutations, server$ functions, middleware, layout routes, and deployment.

## When to Use This Skill

- Build fast web apps using Qwik's resumability model (zero hydration overhead)
- Manage state with `useSignal`/`useStore`/`useComputed$`
- Load data with `routeLoader$` and handle mutations with `routeAction$`
- Run server-only logic inline with `server$`
- Add middleware for auth or request transformation
- Deploy to Node.js, Cloudflare Workers, Vercel, or Netlify

## component$ and State Management

The `$` suffix marks lazy-loadable code boundaries. Qwik serializes state on the server and resumes without re-executing server code on the client. `useSignal` holds a primitive reactive value; `useStore` tracks a reactive object; `useComputed$` derives a value that recomputes when dependencies change.

```tsx
import { component$, useSignal, useStore, useComputed$ } from "@builder.io/qwik";

export const CartWidget = component$<{ label: string }>(({ label }) => {
  const discount = useSignal(0);
  const cart = useStore({ items: [] as { name: string; price: number }[] });
  const total = useComputed$(() =>
    cart.items.reduce((s, i) => s + i.price, 0) * (1 - discount.value / 100)
  );
  return (
    <div>
      <h2>{label}</h2>
      <p>Total after {discount.value}% off: ${total.value.toFixed(2)}</p>
      <button onClick$={() => (discount.value += 5)}>Apply 5% off</button>
    </div>
  );
});
```

## Event Handlers with $

Event handler props (`onClick$`, `onInput$`, `onSubmit$`) are lazy — the handler code downloads only when the event fires.

```tsx
export const SearchBox = component$(() => {
  const query = useSignal("");
  return (
    <form onSubmit$={$((e: SubmitEvent) => { e.preventDefault(); console.log(query.value); })}>
      <input value={query.value}
        onInput$={(e) => (query.value = (e.target as HTMLInputElement).value)} />
      <button type="submit">Search</button>
    </form>
  );
});
```

## routeLoader$ — Server Data Loading

Runs on the server before the route renders. The returned value is serialized and forwarded to the component.

```tsx
// src/routes/posts/[id]/index.tsx
import { component$ } from "@builder.io/qwik";
import { routeLoader$ } from "@builder.io/qwik-city";

export const usePost = routeLoader$(async ({ params, error }) => {
  const post = await db.post.findUnique({ where: { id: params.id } });
  if (!post) throw error(404, "Post not found");
  return post;
});

export default component$(() => {
  const post = usePost();
  return <article><h1>{post.value.title}</h1><p>{post.value.body}</p></article>;
});
```

## routeAction$ — Mutations

Handles server-side form submissions progressively — works without client JavaScript.

```tsx
import { component$ } from "@builder.io/qwik";
import { routeAction$, zod$, Form, z } from "@builder.io/qwik-city";

export const useCreatePost = routeAction$(
  async (data, { redirect }) => {
    const post = await db.post.create({ data });
    throw redirect(302, `/posts/${post.id}`);
  },
  zod$({ title: z.string().min(1), body: z.string().min(1) })
);

export default component$(() => {
  const action = useCreatePost();
  return (
    <Form action={action}>
      {action.value?.failed && <p>{action.value.fieldErrors?.title}</p>}
      <input name="title" required /><textarea name="body" required />
      <button type="submit">Create</button>
    </Form>
  );
});
```

## server$ Functions

Creates ad-hoc RPC functions that run on the server, callable directly from components.

```tsx
import { component$, useSignal } from "@builder.io/qwik";
import { server$ } from "@builder.io/qwik-city";

const getStats = server$(async function () {
  return { users: await db.user.count(), posts: await db.post.count() };
});

export const Dashboard = component$(() => {
  const stats = useSignal<Awaited<ReturnType<typeof getStats>> | null>(null);
  return (
    <div>
      <button onClick$={async () => { stats.value = await getStats(); }}>Load</button>
      {stats.value && <p>Users: {stats.value.users} | Posts: {stats.value.posts}</p>}
    </div>
  );
});
```

## Layout and Routing

File-system routing: `layout.tsx` wraps all child routes and can expose loaders available across the subtree. Route groups `(auth)/` add no URL segment.

```tsx
// src/routes/layout.tsx — available at / and all children
import { component$, Slot } from "@builder.io/qwik";
import { routeLoader$ } from "@builder.io/qwik-city";

export const useSession = routeLoader$(async ({ cookie }) => {
  const token = cookie.get("session")?.value;
  return token ? validateSession(token) : null;
});

export default component$(() => {
  const session = useSession();
  return (
    <>
      <nav>
        <a href="/">Home</a>
        {session.value ? <a href="/dashboard">Dashboard</a> : <a href="/login">Login</a>}
      </nav>
      <main><Slot /></main>
    </>
  );
});
```

Route structure: `src/routes/layout.tsx`, `index.tsx`, `posts/[id]/index.tsx`, `(auth)/login/index.tsx`.

## Middleware

Runs before route handlers. Use `sharedMap` to pass data to loaders downstream.

```typescript
// src/routes/middleware.ts
import type { RequestHandler } from "@builder.io/qwik-city/middleware/request-handler";

export const onRequest: RequestHandler = async ({ cookie, redirect, next, sharedMap, url }) => {
  if (url.pathname.startsWith("/dashboard")) {
    const token = cookie.get("session")?.value;
    if (!token) throw redirect(302, `/login?from=${url.pathname}`);
    sharedMap.set("user", await validateSession(token));
  }
  await next();
};

// In any loader: sharedMap.get("user") as User
```

## Deployment

```bash
# Node.js
npm run build && node dist/server/entry.express.js

# Cloudflare Workers
npm run build && npx wrangler deploy
```

Vercel or Netlify — install the adapter and add it to `vite.config.ts` plugins: `[qwikCity(), qwikVite(), vercelEdgeAdapter()]`. Adapters: `@builder.io/qwik-city/adapters/vercel-edge/vite` or `netlify-edge/vite`.

## Resources

- Qwik docs: https://qwik.dev/docs/
- Qwik City routing: https://qwik.dev/docs/routing/
- Resumability: https://qwik.dev/docs/concepts/resumable/
