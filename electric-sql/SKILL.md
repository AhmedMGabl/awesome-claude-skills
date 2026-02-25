---
name: electric-sql
description: ElectricSQL local-first sync covering Shape streams, real-time Postgres replication, offline support, optimistic mutations, conflict resolution, React hooks, and integration with PGlite and existing databases.
---

# ElectricSQL

This skill should be used when building local-first applications with ElectricSQL. It covers shape streams, real-time sync, offline support, and React integration.

## When to Use This Skill

Use this skill when you need to:

- Sync Postgres data to the client in real-time
- Build offline-capable applications
- Implement optimistic UI with automatic sync
- Use local-first architecture patterns
- Stream partial database views (shapes) to clients

## Shape Streams

```typescript
import { ShapeStream, Shape } from "@electric-sql/client";

// Stream a subset of your Postgres table
const stream = new ShapeStream({
  url: "http://localhost:3000/v1/shape",
  params: {
    table: "todos",
    where: `user_id = '${userId}'`,
    columns: ["id", "title", "completed", "created_at"],
  },
});

const shape = new Shape(stream);

// Subscribe to changes
shape.subscribe((data) => {
  const todos = [...data.values()]; // Map of rows
  console.log("Todos:", todos);
});
```

## React Hooks

```tsx
import { useShape } from "@electric-sql/react";

function TodoList({ userId }: { userId: string }) {
  const { data: todos, isLoading } = useShape<Todo>({
    url: "http://localhost:3000/v1/shape",
    params: {
      table: "todos",
      where: `user_id = '${userId}'`,
    },
  });

  if (isLoading) return <div>Loading...</div>;

  return (
    <ul>
      {todos.map((todo) => (
        <li key={todo.id}>
          <input
            type="checkbox"
            checked={todo.completed}
            onChange={() => toggleTodo(todo.id)}
          />
          {todo.title}
        </li>
      ))}
    </ul>
  );
}
```

## Optimistic Mutations

```typescript
async function createTodo(title: string, userId: string) {
  const id = crypto.randomUUID();

  // Write to server (Postgres)
  await fetch("/api/todos", {
    method: "POST",
    body: JSON.stringify({ id, title, userId, completed: false }),
  });

  // ElectricSQL automatically syncs the change back via shapes
}

async function toggleTodo(id: string) {
  await fetch(`/api/todos/${id}/toggle`, { method: "PATCH" });
}
```

## With PGlite (Local Database)

```typescript
import { PGlite } from "@electric-sql/pglite";

// In-memory Postgres in the browser
const db = new PGlite();

await db.query(`
  CREATE TABLE IF NOT EXISTS todos (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    completed BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT now()
  )
`);

// Query with full SQL support
const result = await db.query("SELECT * FROM todos WHERE completed = $1", [false]);
console.log(result.rows);

// Live queries
const unsubscribe = await db.live.query(
  "SELECT * FROM todos ORDER BY created_at DESC",
  [],
  (result) => {
    console.log("Todos changed:", result.rows);
  },
);
```

## Additional Resources

- ElectricSQL docs: https://electric-sql.com/docs
- Shape API: https://electric-sql.com/docs/api/http
- PGlite: https://electric-sql.com/docs/api/clients/pglite
