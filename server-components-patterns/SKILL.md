---
name: server-components-patterns
description: React Server Components advanced patterns covering server/client component boundaries, data fetching, streaming with Suspense, server actions, composition patterns, caching strategies, and progressive enhancement in Next.js App Router.
---

# Server Components Patterns

This skill should be used when building advanced React Server Component architectures. It covers component boundaries, data fetching, streaming, server actions, and composition.

## When to Use This Skill

Use this skill when you need to:

- Design server/client component boundaries effectively
- Stream data with Suspense for progressive loading
- Compose server and client components correctly
- Implement server actions with optimistic updates
- Cache and revalidate server component data

## Component Boundaries

```tsx
// Server Component (default in App Router)
// app/users/page.tsx — runs on the server, no JavaScript sent to client
async function UsersPage() {
  const users = await db.users.findMany();
  return (
    <div>
      <h1>Users ({users.length})</h1>
      <UserSearch /> {/* Client component for interactivity */}
      <UserList users={users} /> {/* Server component for data display */}
    </div>
  );
}

// Client Component — includes "use client" directive
// components/UserSearch.tsx
"use client";
import { useState } from "react";

export function UserSearch() {
  const [query, setQuery] = useState("");
  return (
    <input
      value={query}
      onChange={(e) => setQuery(e.target.value)}
      placeholder="Search users..."
    />
  );
}

// Server Component rendering data
// components/UserList.tsx (no "use client" — server by default)
function UserList({ users }: { users: User[] }) {
  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>
          <span>{user.name}</span>
          <DeleteButton userId={user.id} /> {/* Client component */}
        </li>
      ))}
    </ul>
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
      {/* Each section streams independently */}
      <Suspense fallback={<StatsSkeleton />}>
        <Stats />
      </Suspense>
      <Suspense fallback={<RecentOrdersSkeleton />}>
        <RecentOrders />
      </Suspense>
      <Suspense fallback={<ChartSkeleton />}>
        <RevenueChart />
      </Suspense>
    </div>
  );
}

// Each async component fetches its own data
async function Stats() {
  const stats = await getStats(); // Slow API call
  return (
    <div className="grid grid-cols-3 gap-4">
      <StatCard label="Revenue" value={stats.revenue} />
      <StatCard label="Orders" value={stats.orders} />
      <StatCard label="Customers" value={stats.customers} />
    </div>
  );
}

async function RecentOrders() {
  const orders = await getRecentOrders();
  return <OrderTable orders={orders} />;
}
```

## Server Actions

```tsx
// actions.ts
"use server";
import { revalidatePath } from "next/cache";

export async function createTodo(formData: FormData) {
  const title = formData.get("title") as string;
  await db.todos.create({ data: { title } });
  revalidatePath("/todos");
}

export async function toggleTodo(id: string) {
  const todo = await db.todos.findUnique({ where: { id } });
  await db.todos.update({
    where: { id },
    data: { completed: !todo?.completed },
  });
  revalidatePath("/todos");
}

export async function deleteTodo(id: string) {
  await db.todos.delete({ where: { id } });
  revalidatePath("/todos");
}

// Usage in Server Component (form action)
// app/todos/page.tsx
import { createTodo, toggleTodo } from "./actions";

async function TodosPage() {
  const todos = await db.todos.findMany();

  return (
    <div>
      <form action={createTodo}>
        <input name="title" required />
        <button type="submit">Add</button>
      </form>
      <ul>
        {todos.map((todo) => (
          <li key={todo.id}>
            <form action={toggleTodo.bind(null, todo.id)}>
              <button type="submit">{todo.completed ? "✓" : "○"}</button>
            </form>
            <span>{todo.title}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

## Composition: Passing Server Components as Children

```tsx
// Client component that wraps server components
"use client";
function Tabs({ children }: { children: React.ReactNode }) {
  const [activeTab, setActiveTab] = useState(0);
  return (
    <div>
      <div className="tabs">
        <button onClick={() => setActiveTab(0)}>Tab 1</button>
        <button onClick={() => setActiveTab(1)}>Tab 2</button>
      </div>
      {/* Server component content passed as children */}
      <div>{children}</div>
    </div>
  );
}

// Server component page passes server-fetched data through
async function Page() {
  const data = await fetchData();
  return (
    <Tabs>
      <DataDisplay data={data} /> {/* Server component as child */}
    </Tabs>
  );
}
```

## Caching Strategies

```tsx
import { unstable_cache } from "next/cache";

// Cache database queries
const getCachedUsers = unstable_cache(
  async () => db.users.findMany(),
  ["users"],
  { revalidate: 3600, tags: ["users"] },
);

// Use in server components
async function UserList() {
  const users = await getCachedUsers();
  return <ul>{users.map((u) => <li key={u.id}>{u.name}</li>)}</ul>;
}

// Invalidate cache from server actions
"use server";
import { revalidateTag } from "next/cache";

export async function createUser(data: UserData) {
  await db.users.create({ data });
  revalidateTag("users");
}
```

## Additional Resources

- React Server Components: https://react.dev/reference/rsc/server-components
- Next.js Server Components: https://nextjs.org/docs/app/building-your-application/rendering/server-components
- Server Actions: https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations
