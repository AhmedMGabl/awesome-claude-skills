---
name: trpc-api
description: tRPC type-safe API development covering router definition, procedures, input validation with Zod, middleware, context creation, React Query integration, subscriptions, error handling, and full-stack TypeScript type safety between server and client.
---

# tRPC API

This skill should be used when building type-safe APIs with tRPC. It covers routers, procedures, middleware, React integration, and end-to-end type safety.

## When to Use This Skill

Use this skill when you need to:

- Build type-safe APIs without code generation
- Share types between server and client
- Integrate tRPC with React Query
- Add authentication middleware
- Handle real-time subscriptions

## Server Setup

```typescript
// server/trpc.ts
import { initTRPC, TRPCError } from "@trpc/server";
import { z } from "zod";
import type { Context } from "./context";

const t = initTRPC.context<Context>().create();

export const router = t.router;
export const publicProcedure = t.procedure;

// Auth middleware
const isAuthenticated = t.middleware(({ ctx, next }) => {
  if (!ctx.user) {
    throw new TRPCError({ code: "UNAUTHORIZED" });
  }
  return next({ ctx: { ...ctx, user: ctx.user } });
});

export const protectedProcedure = t.procedure.use(isAuthenticated);
```

```typescript
// server/context.ts
import type { CreateNextContextOptions } from "@trpc/server/adapters/next";
import { getSession } from "./auth";

export async function createContext({ req }: CreateNextContextOptions) {
  const session = await getSession(req);
  return { user: session?.user ?? null, db: prisma };
}

export type Context = Awaited<ReturnType<typeof createContext>>;
```

## Router Definition

```typescript
// server/routers/post.ts
import { z } from "zod";
import { router, publicProcedure, protectedProcedure } from "../trpc";

export const postRouter = router({
  list: publicProcedure
    .input(
      z.object({
        page: z.number().min(1).default(1),
        limit: z.number().min(1).max(100).default(20),
      }),
    )
    .query(async ({ input, ctx }) => {
      const posts = await ctx.db.post.findMany({
        take: input.limit,
        skip: (input.page - 1) * input.limit,
        orderBy: { createdAt: "desc" },
        include: { author: { select: { name: true } } },
      });
      const total = await ctx.db.post.count();
      return { posts, total, page: input.page };
    }),

  byId: publicProcedure
    .input(z.object({ id: z.string().uuid() }))
    .query(async ({ input, ctx }) => {
      const post = await ctx.db.post.findUnique({
        where: { id: input.id },
        include: { author: true, comments: true },
      });
      if (!post) throw new TRPCError({ code: "NOT_FOUND" });
      return post;
    }),

  create: protectedProcedure
    .input(
      z.object({
        title: z.string().min(1).max(200),
        content: z.string().min(1),
      }),
    )
    .mutation(async ({ input, ctx }) => {
      return ctx.db.post.create({
        data: { ...input, authorId: ctx.user.id },
      });
    }),

  delete: protectedProcedure
    .input(z.object({ id: z.string().uuid() }))
    .mutation(async ({ input, ctx }) => {
      const post = await ctx.db.post.findUnique({ where: { id: input.id } });
      if (!post || post.authorId !== ctx.user.id) {
        throw new TRPCError({ code: "FORBIDDEN" });
      }
      return ctx.db.post.delete({ where: { id: input.id } });
    }),
});
```

```typescript
// server/routers/_app.ts
import { router } from "../trpc";
import { postRouter } from "./post";
import { userRouter } from "./user";

export const appRouter = router({
  post: postRouter,
  user: userRouter,
});

export type AppRouter = typeof appRouter;
```

## React Client

```typescript
// utils/trpc.ts
import { createTRPCReact } from "@trpc/react-query";
import type { AppRouter } from "~/server/routers/_app";

export const trpc = createTRPCReact<AppRouter>();
```

```tsx
// components/PostList.tsx
import { trpc } from "~/utils/trpc";

export function PostList() {
  const { data, isLoading } = trpc.post.list.useQuery({ page: 1 });
  const utils = trpc.useUtils();

  const createPost = trpc.post.create.useMutation({
    onSuccess: () => {
      utils.post.list.invalidate();
    },
  });

  if (isLoading) return <p>Loading...</p>;

  return (
    <div>
      <button onClick={() => createPost.mutate({ title: "New Post", content: "Hello!" })}>
        Create Post
      </button>
      {data?.posts.map((post) => (
        <article key={post.id}>
          <h2>{post.title}</h2>
          <p>by {post.author.name}</p>
        </article>
      ))}
    </div>
  );
}
```

## Prefetching (SSR)

```typescript
// app/posts/page.tsx (Next.js App Router)
import { createServerSideHelpers } from "@trpc/react-query/server";
import { appRouter } from "~/server/routers/_app";

export default async function PostsPage() {
  const helpers = createServerSideHelpers({ router: appRouter, ctx: await createContext() });

  // Prefetch on server
  await helpers.post.list.prefetch({ page: 1 });

  return (
    <HydrationBoundary state={helpers.dehydrate()}>
      <PostList />
    </HydrationBoundary>
  );
}
```

## Additional Resources

- tRPC docs: https://trpc.io/docs
- tRPC + Next.js: https://trpc.io/docs/client/nextjs
- T3 Stack: https://create.t3.gg/
