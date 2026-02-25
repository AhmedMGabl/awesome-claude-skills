---
name: swr-data-fetching
description: SWR data fetching library covering stale-while-revalidate pattern, global configuration, mutation and optimistic updates, pagination with useSWRInfinite, conditional fetching, middleware, prefetching, error handling, and comparison with TanStack Query.
---

# SWR Data Fetching

This skill should be used when implementing data fetching with the SWR library. It covers caching strategies, mutations, pagination, prefetching, and middleware.

## When to Use This Skill

Use this skill when you need to:

- Fetch and cache remote data in React
- Implement stale-while-revalidate caching
- Handle mutations with optimistic updates
- Build paginated or infinite scroll lists
- Share data across components without prop drilling

## Basic Usage

```tsx
import useSWR from "swr";

const fetcher = (url: string) => fetch(url).then((r) => r.json());

function UserProfile({ userId }: { userId: string }) {
  const { data, error, isLoading } = useSWR<User>(`/api/users/${userId}`, fetcher);

  if (isLoading) return <Spinner />;
  if (error) return <Error message="Failed to load user" />;

  return <div>{data.name} — {data.email}</div>;
}
```

## Global Configuration

```tsx
import { SWRConfig } from "swr";

function App({ children }: { children: React.ReactNode }) {
  return (
    <SWRConfig
      value={{
        fetcher: (url: string) => fetch(url).then((r) => {
          if (!r.ok) throw new Error("Request failed");
          return r.json();
        }),
        revalidateOnFocus: true,
        revalidateOnReconnect: true,
        dedupingInterval: 2000,
        errorRetryCount: 3,
      }}
    >
      {children}
    </SWRConfig>
  );
}
```

## Mutation with Optimistic Update

```tsx
import useSWR, { useSWRConfig } from "swr";

function TodoList() {
  const { data: todos, mutate } = useSWR<Todo[]>("/api/todos", fetcher);

  async function addTodo(text: string) {
    const newTodo = { id: Date.now().toString(), text, done: false };

    // Optimistic update — update UI immediately
    await mutate(
      async () => {
        const created = await fetch("/api/todos", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text }),
        }).then((r) => r.json());
        return [...(todos ?? []), created];
      },
      {
        optimisticData: [...(todos ?? []), newTodo],
        rollbackOnError: true,
        revalidate: false,
      },
    );
  }

  async function toggleTodo(id: string) {
    const updated = todos?.map((t) =>
      t.id === id ? { ...t, done: !t.done } : t,
    );

    await mutate(
      fetch(`/api/todos/${id}`, { method: "PATCH" }).then(() => updated),
      { optimisticData: updated, rollbackOnError: true },
    );
  }

  return (
    <ul>
      {todos?.map((todo) => (
        <li key={todo.id} onClick={() => toggleTodo(todo.id)}>
          {todo.done ? "✓" : "○"} {todo.text}
        </li>
      ))}
    </ul>
  );
}
```

## Infinite Scroll

```tsx
import useSWRInfinite from "swr/infinite";

function PostFeed() {
  const getKey = (pageIndex: number, previousPageData: Post[] | null) => {
    if (previousPageData && previousPageData.length === 0) return null;
    return `/api/posts?page=${pageIndex + 1}&limit=10`;
  };

  const { data, size, setSize, isValidating } = useSWRInfinite<Post[]>(getKey, fetcher);

  const posts = data ? data.flat() : [];
  const isEnd = data && data[data.length - 1]?.length < 10;

  return (
    <div>
      {posts.map((post) => (
        <PostCard key={post.id} post={post} />
      ))}
      {!isEnd && (
        <button onClick={() => setSize(size + 1)} disabled={isValidating}>
          {isValidating ? "Loading..." : "Load More"}
        </button>
      )}
    </div>
  );
}
```

## Conditional Fetching

```tsx
// Only fetch when userId is available
const { data } = useSWR(userId ? `/api/users/${userId}` : null, fetcher);

// Dependent fetching — fetch user, then fetch their orders
function UserOrders({ userId }: { userId: string }) {
  const { data: user } = useSWR(`/api/users/${userId}`, fetcher);
  const { data: orders } = useSWR(
    user ? `/api/users/${user.id}/orders` : null,
    fetcher,
  );

  return <div>{orders?.length} orders</div>;
}
```

## Prefetching

```tsx
import { preload } from "swr";

// Prefetch before navigation
function UserLink({ userId }: { userId: string }) {
  return (
    <Link
      href={`/users/${userId}`}
      onMouseEnter={() => preload(`/api/users/${userId}`, fetcher)}
    >
      View User
    </Link>
  );
}
```

## SWR vs TanStack Query

```
FEATURE              SWR                  TANSTACK QUERY
──────────────────────────────────────────────────────
Bundle size          ~4KB                 ~13KB
API complexity       Minimal              Feature-rich
Mutations            Manual mutate()      useMutation hook
Devtools             Community            Built-in
Infinite queries     useSWRInfinite       useInfiniteQuery
Parallel queries     Multiple useSWR      useQueries
```

## Additional Resources

- SWR docs: https://swr.vercel.app/
- SWR examples: https://swr.vercel.app/examples
- SWR API: https://swr.vercel.app/docs/api
