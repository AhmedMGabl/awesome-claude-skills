---
name: trpc-patterns
description: tRPC patterns covering router definitions, procedures, input validation with Zod, middleware, context, subscriptions, React Query integration, error handling, and Next.js App Router setup for end-to-end type-safe APIs.
---

# tRPC Patterns

This skill should be used when building end-to-end type-safe APIs with tRPC. It covers routers, procedures, middleware, subscriptions, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Build type-safe APIs without code generation
- Define routers with input validation
- Add authentication and authorization middleware
- Integrate tRPC with React Query and Next.js
- Handle real-time data with subscriptions

## Router and Procedures

```typescript
// server/trpc.ts
import { initTRPC, TRPCError } from "@trpc/server";
import { z } from "zod";

type Context = {
  userId: string | null;
  db: PrismaClient;
};

const t = initTRPC.context<Context>().create();

export const router = t.router;
export const publicProcedure = t.procedure;
export const middleware = t.middleware;

// Auth middleware
const isAuthed = middleware(async ({ ctx, next }) => {
  if (!ctx.userId) {
    throw new TRPCError({ code: "UNAUTHORIZED" });
  }
  return next({ ctx: { ...ctx, userId: ctx.userId } });
});

export const protectedProcedure = publicProcedure.use(isAuthed);

// server/routers/user.ts
export const userRouter = router({
  getById: publicProcedure
    .input(z.object({ id: z.string().uuid() }))
    .query(async ({ ctx, input }) => {
      const user = await ctx.db.user.findUnique({ where: { id: input.id } });
      if (!user) throw new TRPCError({ code: "NOT_FOUND" });
      return user;
    }),

  list: publicProcedure
    .input(
      z.object({
        cursor: z.string().optional(),
        limit: z.number().min(1).max(100).default(20),
      }),
    )
    .query(async ({ ctx, input }) => {
      const items = await ctx.db.user.findMany({
        take: input.limit + 1,
        cursor: input.cursor ? { id: input.cursor } : undefined,
        orderBy: { createdAt: "desc" },
      });
      let nextCursor: string | undefined;
      if (items.length > input.limit) {
        nextCursor = items.pop()!.id;
      }
      return { items, nextCursor };
    }),

  create: protectedProcedure
    .input(z.object({ name: z.string().min(1), email: z.string().email() }))
    .mutation(async ({ ctx, input }) => {
      return ctx.db.user.create({ data: input });
    }),

  update: protectedProcedure
    .input(z.object({ id: z.string().uuid(), name: z.string().min(1).optional() }))
    .mutation(async ({ ctx, input }) => {
      return ctx.db.user.update({ where: { id: input.id }, data: input });
    }),

  delete: protectedProcedure
    .input(z.object({ id: z.string().uuid() }))
    .mutation(async ({ ctx, input }) => {
      await ctx.db.user.delete({ where: { id: input.id } });
      return { success: true };
    }),
});
```

## App Router (Root Router)

```typescript
// server/routers/_app.ts
import { router } from "../trpc";
import { userRouter } from "./user";
import { postRouter } from "./post";

export const appRouter = router({
  user: userRouter,
  post: postRouter,
});

export type AppRouter = typeof appRouter;
```

## Next.js App Router Integration

```typescript
// app/api/trpc/[trpc]/route.ts
import { fetchRequestHandler } from "@trpc/server/adapters/fetch";
import { appRouter } from "@/server/routers/_app";

const handler = (req: Request) =>
  fetchRequestHandler({
    endpoint: "/api/trpc",
    req,
    router: appRouter,
    createContext: async () => {
      // Extract auth from headers
      return { userId: null, db: prisma };
    },
  });

export { handler as GET, handler as POST };

// lib/trpc.ts (client setup)
import { createTRPCReact } from "@trpc/react-query";
import type { AppRouter } from "@/server/routers/_app";

export const trpc = createTRPCReact<AppRouter>();

// app/providers.tsx
"use client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { httpBatchLink } from "@trpc/client";
import { trpc } from "@/lib/trpc";
import { useState } from "react";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient());
  const [trpcClient] = useState(() =>
    trpc.createClient({
      links: [httpBatchLink({ url: "/api/trpc" })],
    }),
  );

  return (
    <trpc.Provider client={trpcClient} queryClient={queryClient}>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </trpc.Provider>
  );
}
```

## React Query Usage

```tsx
"use client";
import { trpc } from "@/lib/trpc";

function UserList() {
  // Infinite query with cursor pagination
  const { data, fetchNextPage, hasNextPage, isLoading } =
    trpc.user.list.useInfiniteQuery(
      { limit: 20 },
      { getNextPageParam: (lastPage) => lastPage.nextCursor },
    );

  // Mutation with optimistic update
  const utils = trpc.useUtils();
  const createUser = trpc.user.create.useMutation({
    onSuccess: () => {
      utils.user.list.invalidate();
    },
  });

  const deleteUser = trpc.user.delete.useMutation({
    onMutate: async ({ id }) => {
      await utils.user.list.cancel();
      const prev = utils.user.list.getInfiniteData({ limit: 20 });
      utils.user.list.setInfiniteData({ limit: 20 }, (old) => {
        if (!old) return old;
        return {
          ...old,
          pages: old.pages.map((page) => ({
            ...page,
            items: page.items.filter((u) => u.id !== id),
          })),
        };
      });
      return { prev };
    },
    onError: (_err, _vars, context) => {
      if (context?.prev) {
        utils.user.list.setInfiniteData({ limit: 20 }, context.prev);
      }
    },
  });

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      {data?.pages.flatMap((page) =>
        page.items.map((user) => (
          <div key={user.id}>
            {user.name}
            <button onClick={() => deleteUser.mutate({ id: user.id })}>Delete</button>
          </div>
        )),
      )}
      {hasNextPage && <button onClick={() => fetchNextPage()}>Load more</button>}
    </div>
  );
}
```

## Error Handling

```typescript
import { TRPCError } from "@trpc/server";

// In procedures
throw new TRPCError({
  code: "BAD_REQUEST",
  message: "Invalid input",
  cause: originalError,
});

// Error codes: PARSE_ERROR, BAD_REQUEST, UNAUTHORIZED,
// FORBIDDEN, NOT_FOUND, CONFLICT, TOO_MANY_REQUESTS,
// INTERNAL_SERVER_ERROR

// Client-side error handling
const mutation = trpc.user.create.useMutation({
  onError: (error) => {
    if (error.data?.code === "CONFLICT") {
      toast.error("User already exists");
    }
  },
});
```

## Additional Resources

- tRPC docs: https://trpc.io/docs
- React Query integration: https://trpc.io/docs/client/react
- Next.js setup: https://trpc.io/docs/client/nextjs/setup
