---
name: remix-development
description: Remix framework development covering nested routes, loaders, actions, form handling, error boundaries, deferred data, resource routes, authentication patterns, streaming SSR, and progressive enhancement.
---

# Remix Development

This skill should be used when building web applications with Remix. It covers loaders, actions, nested routing, forms, error handling, and progressive enhancement.

## When to Use This Skill

Use this skill when you need to:

- Build full-stack Remix applications
- Implement server-side data loading with loaders
- Handle form submissions with actions
- Set up nested routing and error boundaries
- Leverage progressive enhancement

## Loaders and Actions

```typescript
// app/routes/posts._index.tsx
import type { LoaderFunctionArgs, ActionFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import { useLoaderData, Form, useNavigation } from "@remix-run/react";
import { getPosts, createPost } from "~/models/post.server";
import { requireUserId } from "~/session.server";

export async function loader({ request }: LoaderFunctionArgs) {
  const url = new URL(request.url);
  const page = Number(url.searchParams.get("page") ?? "1");
  const posts = await getPosts({ page, limit: 20 });
  return json({ posts, page });
}

export async function action({ request }: ActionFunctionArgs) {
  const userId = await requireUserId(request);
  const formData = await request.formData();
  const title = formData.get("title");
  const content = formData.get("content");

  if (typeof title !== "string" || title.length < 3) {
    return json({ error: "Title must be at least 3 characters" }, { status: 400 });
  }

  const post = await createPost({ title, content: content as string, authorId: userId });
  return redirect(`/posts/${post.id}`);
}

export default function PostsIndex() {
  const { posts, page } = useLoaderData<typeof loader>();
  const navigation = useNavigation();
  const isSubmitting = navigation.state === "submitting";

  return (
    <div>
      <h1>Posts</h1>

      <Form method="post">
        <input name="title" placeholder="Post title" required minLength={3} />
        <textarea name="content" placeholder="Write something..." />
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Creating..." : "Create Post"}
        </button>
      </Form>

      <ul>
        {posts.map((post) => (
          <li key={post.id}>
            <a href={`/posts/${post.id}`}>{post.title}</a>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

## Nested Routes and Error Boundaries

```typescript
// app/routes/dashboard.tsx — Parent layout
import { Outlet, NavLink } from "@remix-run/react";

export default function DashboardLayout() {
  return (
    <div className="flex">
      <nav>
        <NavLink to="overview" className={({ isActive }) => (isActive ? "font-bold" : "")}>
          Overview
        </NavLink>
        <NavLink to="settings">Settings</NavLink>
      </nav>
      <main>
        <Outlet />
      </main>
    </div>
  );
}

export function ErrorBoundary() {
  return (
    <div className="error-container">
      <h1>Something went wrong in the dashboard</h1>
      <p>Please try refreshing the page.</p>
    </div>
  );
}
```

## Authentication

```typescript
// app/session.server.ts
import { createCookieSessionStorage, redirect } from "@remix-run/node";

const sessionStorage = createCookieSessionStorage({
  cookie: {
    name: "__session",
    httpOnly: true,
    maxAge: 60 * 60 * 24 * 7, // 7 days
    path: "/",
    sameSite: "lax",
    secrets: [process.env.SESSION_SECRET!],
    secure: process.env.NODE_ENV === "production",
  },
});

export async function requireUserId(request: Request): Promise<string> {
  const session = await sessionStorage.getSession(request.headers.get("Cookie"));
  const userId = session.get("userId");

  if (!userId) {
    throw redirect("/login");
  }

  return userId;
}

export async function createUserSession(userId: string, redirectTo: string) {
  const session = await sessionStorage.getSession();
  session.set("userId", userId);

  return redirect(redirectTo, {
    headers: {
      "Set-Cookie": await sessionStorage.commitSession(session),
    },
  });
}
```

## Resource Routes

```typescript
// app/routes/api.posts.ts — JSON API endpoint
import { json, type LoaderFunctionArgs } from "@remix-run/node";
import { getPosts } from "~/models/post.server";

export async function loader({ request }: LoaderFunctionArgs) {
  const url = new URL(request.url);
  const query = url.searchParams.get("q") ?? "";
  const posts = await getPosts({ search: query });
  return json(posts);
}
```

## Additional Resources

- Remix docs: https://remix.run/docs
- Remix tutorials: https://remix.run/docs/en/main/start/tutorial
- Remix Stacks: https://remix.run/stacks
