---
name: tanstack-query
description: TanStack Query (React Query) patterns covering queries, mutations, query invalidation, optimistic updates, infinite scrolling, prefetching, suspense integration, cache management, and server state synchronization in React applications.
---

# TanStack Query

This skill should be used when managing server state in React applications with TanStack Query. It covers queries, mutations, caching, optimistic updates, and advanced patterns.

## When to Use This Skill

Use this skill when you need to:

- Fetch and cache server data in React
- Handle mutations with optimistic updates
- Implement infinite scrolling
- Prefetch data for navigation
- Manage complex cache invalidation

## Setup

```tsx
// app/providers.tsx
"use client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { useState } from "react";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,      // 1 minute
            gcTime: 5 * 60 * 1000,     // 5 minutes
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      }),
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

## Query Hooks

```tsx
import { useQuery, useSuspenseQuery } from "@tanstack/react-query";

// Basic query
function useUsers(page: number = 1) {
  return useQuery({
    queryKey: ["users", { page }],
    queryFn: async () => {
      const res = await fetch(`/api/users?page=${page}`);
      if (!res.ok) throw new Error("Failed to fetch users");
      return res.json() as Promise<{ users: User[]; total: number }>;
    },
  });
}

// Dependent query
function useUserPosts(userId: string | undefined) {
  return useQuery({
    queryKey: ["users", userId, "posts"],
    queryFn: () => fetch(`/api/users/${userId}/posts`).then((r) => r.json()),
    enabled: !!userId, // Only run when userId exists
  });
}

// With Suspense
function useUser(id: string) {
  return useSuspenseQuery({
    queryKey: ["users", id],
    queryFn: () => fetch(`/api/users/${id}`).then((r) => r.json()),
  });
}
```

## Mutations with Optimistic Updates

```tsx
import { useMutation, useQueryClient } from "@tanstack/react-query";

function useCreatePost() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (newPost: { title: string; content: string }) => {
      const res = await fetch("/api/posts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newPost),
      });
      return res.json();
    },

    // Optimistic update
    onMutate: async (newPost) => {
      await queryClient.cancelQueries({ queryKey: ["posts"] });
      const previous = queryClient.getQueryData(["posts"]);

      queryClient.setQueryData(["posts"], (old: Post[]) => [
        { id: "temp-id", ...newPost, createdAt: new Date().toISOString() },
        ...old,
      ]);

      return { previous };
    },

    onError: (_err, _newPost, context) => {
      // Rollback on error
      queryClient.setQueryData(["posts"], context?.previous);
    },

    onSettled: () => {
      // Refetch to sync with server
      queryClient.invalidateQueries({ queryKey: ["posts"] });
    },
  });
}

// Usage
function CreatePostForm() {
  const createPost = useCreatePost();

  const handleSubmit = (data: { title: string; content: string }) => {
    createPost.mutate(data);
  };

  return (
    <form onSubmit={handleSubmit}>
      {createPost.isPending && <p>Saving...</p>}
      {createPost.isError && <p>Error: {createPost.error.message}</p>}
    </form>
  );
}
```

## Infinite Scrolling

```tsx
import { useInfiniteQuery } from "@tanstack/react-query";
import { useInView } from "react-intersection-observer";
import { useEffect } from "react";

function useFeed() {
  return useInfiniteQuery({
    queryKey: ["feed"],
    queryFn: async ({ pageParam }) => {
      const res = await fetch(`/api/feed?cursor=${pageParam}`);
      return res.json() as Promise<{ items: Post[]; nextCursor: string | null }>;
    },
    initialPageParam: "",
    getNextPageParam: (lastPage) => lastPage.nextCursor,
  });
}

function Feed() {
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage } = useFeed();
  const { ref, inView } = useInView();

  useEffect(() => {
    if (inView && hasNextPage) fetchNextPage();
  }, [inView, hasNextPage, fetchNextPage]);

  return (
    <div>
      {data?.pages.map((page) =>
        page.items.map((post) => <PostCard key={post.id} post={post} />),
      )}
      <div ref={ref}>
        {isFetchingNextPage ? <Spinner /> : hasNextPage ? "Load more" : "End of feed"}
      </div>
    </div>
  );
}
```

## Prefetching

```tsx
// Prefetch on hover for instant navigation
function UserLink({ userId, name }: { userId: string; name: string }) {
  const queryClient = useQueryClient();

  const prefetch = () => {
    queryClient.prefetchQuery({
      queryKey: ["users", userId],
      queryFn: () => fetch(`/api/users/${userId}`).then((r) => r.json()),
      staleTime: 5 * 60 * 1000,
    });
  };

  return (
    <Link href={`/users/${userId}`} onMouseEnter={prefetch}>
      {name}
    </Link>
  );
}
```

## Query Key Factory

```typescript
// Organized query keys
export const queryKeys = {
  users: {
    all: ["users"] as const,
    lists: () => [...queryKeys.users.all, "list"] as const,
    list: (filters: UserFilters) => [...queryKeys.users.lists(), filters] as const,
    details: () => [...queryKeys.users.all, "detail"] as const,
    detail: (id: string) => [...queryKeys.users.details(), id] as const,
  },
  posts: {
    all: ["posts"] as const,
    byUser: (userId: string) => [...queryKeys.posts.all, "user", userId] as const,
  },
};

// Precise invalidation
queryClient.invalidateQueries({ queryKey: queryKeys.users.lists() }); // All user lists
queryClient.invalidateQueries({ queryKey: queryKeys.users.detail("1") }); // Specific user
```

## Additional Resources

- TanStack Query docs: https://tanstack.com/query/latest
- Query key factory: https://tkdodo.eu/blog/effective-react-query-keys
- Practical React Query: https://tkdodo.eu/blog/practical-react-query
