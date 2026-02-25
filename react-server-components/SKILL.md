---
name: react-server-components
description: React Server Components covering server vs client component patterns, data fetching in server components, streaming with Suspense, server actions, use server and use client directives, composition patterns, caching, and migration strategies.
---

# React Server Components

This skill should be used when building applications with React Server Components (RSC). It covers server/client boundaries, data fetching, streaming, server actions, and composition patterns.

## When to Use This Skill

Use this skill when you need to:

- Decide between server and client components
- Fetch data directly in server components
- Implement server actions for mutations
- Stream content with Suspense boundaries
- Compose server and client components effectively

## Server vs Client Components

```
SERVER COMPONENTS (default)          CLIENT COMPONENTS ("use client")
────────────────────────────────────────────────────────────────────
Render on the server                 Render on client (hydrated)
Direct database/API access           No direct backend access
Zero bundle size                     Added to JS bundle
No hooks (useState, useEffect)       Full hooks API
No browser APIs                      Access to window, document
No event handlers                    onClick, onChange, etc.
Can import client components         Cannot import server components
```

## Data Fetching in Server Components

```tsx
// app/posts/page.tsx — Server Component (default)
import { db } from "@/lib/db";

export default async function PostsPage() {
  // Direct database access — no API needed
  const posts = await db.post.findMany({
    where: { published: true },
    orderBy: { createdAt: "desc" },
    include: { author: { select: { name: true } } },
  });

  return (
    <div>
      <h1>Blog Posts</h1>
      {posts.map((post) => (
        <article key={post.id}>
          <h2>{post.title}</h2>
          <p>By {post.author.name}</p>
        </article>
      ))}
    </div>
  );
}
```

## Server Actions

```tsx
// app/posts/new/page.tsx
import { redirect } from "next/navigation";
import { revalidatePath } from "next/cache";
import { db } from "@/lib/db";

export default function NewPostPage() {
  async function createPost(formData: FormData) {
    "use server";

    const title = formData.get("title") as string;
    const content = formData.get("content") as string;

    await db.post.create({ data: { title, content, published: true } });

    revalidatePath("/posts");
    redirect("/posts");
  }

  return (
    <form action={createPost}>
      <input name="title" placeholder="Title" required />
      <textarea name="content" placeholder="Content" required />
      <button type="submit">Create Post</button>
    </form>
  );
}
```

## Server Actions with Client Components

```tsx
// lib/actions.ts
"use server";

import { db } from "@/lib/db";
import { revalidatePath } from "next/cache";

export async function toggleLike(postId: string, userId: string) {
  const existing = await db.like.findUnique({
    where: { postId_userId: { postId, userId } },
  });

  if (existing) {
    await db.like.delete({ where: { id: existing.id } });
  } else {
    await db.like.create({ data: { postId, userId } });
  }

  revalidatePath(`/posts/${postId}`);
}
```

```tsx
// components/LikeButton.tsx
"use client";

import { useTransition } from "react";
import { toggleLike } from "@/lib/actions";

export function LikeButton({ postId, userId, liked }: Props) {
  const [isPending, startTransition] = useTransition();

  return (
    <button
      onClick={() => startTransition(() => toggleLike(postId, userId))}
      disabled={isPending}
    >
      {liked ? "Unlike" : "Like"} {isPending && "..."}
    </button>
  );
}
```

## Streaming with Suspense

```tsx
// app/dashboard/page.tsx
import { Suspense } from "react";

export default function DashboardPage() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Suspense fallback={<StatsSkeleton />}>
        <Stats />
      </Suspense>
      <Suspense fallback={<TableSkeleton />}>
        <RecentOrders />
      </Suspense>
    </div>
  );
}

// These components can be slow — they stream in independently
async function Stats() {
  const stats = await db.getStats(); // Slow query
  return <StatsGrid data={stats} />;
}

async function RecentOrders() {
  const orders = await db.order.findMany({ take: 10 }); // Another slow query
  return <OrderTable orders={orders} />;
}
```

## Composition Patterns

```tsx
// Server component wrapping client component
// Pass server data as props to client components
async function PostPage({ params }: { params: { id: string } }) {
  const post = await db.post.findUnique({ where: { id: params.id } });

  return (
    <article>
      <h1>{post.title}</h1>
      <div>{post.content}</div>
      {/* Server data passed to client component */}
      <LikeButton postId={post.id} liked={post.likedByUser} />
      <CommentSection postId={post.id} />
    </article>
  );
}

// Pattern: Server component as children of client component
// ClientWrapper.tsx — "use client"
function ClientWrapper({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  return (
    <div>
      <button onClick={() => setOpen(!open)}>Toggle</button>
      {open && children}  {/* Server components passed as children */}
    </div>
  );
}
```

## Decision Guide

```
NEED                              USE
──────────────────────────────────────────────────
Fetch data, DB queries            Server Component
Interactive UI (click, input)     Client Component
Use hooks (useState, etc.)        Client Component
Access environment variables      Server Component
Reduce bundle size                Server Component
Browser APIs (localStorage)       Client Component
Form submissions                  Server Action
Third-party interactive libs      Client Component
```

## Additional Resources

- React Server Components: https://react.dev/reference/rsc/server-components
- Server Actions: https://react.dev/reference/rsc/server-actions
- Next.js App Router: https://nextjs.org/docs/app
