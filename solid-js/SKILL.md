---
name: solid-js
description: SolidJS reactive UI framework covering signals, effects, memos, stores, context, control flow components, resource fetching, routing with solid-router, and SolidStart SSR/SSG deployment.
---

# SolidJS

This skill should be used when building reactive UIs with SolidJS. It covers signals, effects, stores, control flow, resource fetching, routing, and SolidStart.

## When to Use This Skill

Use this skill when you need to:

- Build reactive UIs with fine-grained reactivity
- Create SPA or SSR apps with SolidStart
- Manage state with signals and stores
- Fetch data with resources
- Implement routing with solid-router

## Signals and Effects

```tsx
import { createSignal, createEffect, createMemo, onCleanup } from "solid-js";

function Counter() {
  const [count, setCount] = createSignal(0);
  const doubled = createMemo(() => count() * 2);

  // Effect runs when dependencies change
  createEffect(() => {
    console.log("Count:", count());
  });

  // Interval with cleanup
  const timer = setInterval(() => setCount((c) => c + 1), 1000);
  onCleanup(() => clearInterval(timer));

  return (
    <div>
      <p>Count: {count()}</p>
      <p>Doubled: {doubled()}</p>
      <button onClick={() => setCount((c) => c + 1)}>Increment</button>
    </div>
  );
}
```

## Control Flow

```tsx
import { Show, For, Switch, Match, Index, Dynamic } from "solid-js";

function UserList(props: { users: User[]; loading: boolean }) {
  return (
    <div>
      <Show when={!props.loading} fallback={<p>Loading...</p>}>
        <Show when={props.users.length > 0} fallback={<p>No users found</p>}>
          <For each={props.users}>
            {(user, index) => (
              <div>
                {index() + 1}. {user.name} — {user.email}
              </div>
            )}
          </For>
        </Show>
      </Show>

      <Switch>
        <Match when={props.users.length === 0}>Empty</Match>
        <Match when={props.users.length < 10}>Few users</Match>
        <Match when={props.users.length >= 10}>Many users</Match>
      </Switch>
    </div>
  );
}
```

## Stores

```tsx
import { createStore, produce } from "solid-js/store";

interface AppState {
  user: { name: string; email: string } | null;
  todos: { id: string; text: string; done: boolean }[];
}

const [state, setState] = createStore<AppState>({
  user: null,
  todos: [],
});

// Nested updates
setState("user", { name: "John", email: "john@example.com" });
setState("user", "name", "Jane");

// Array operations with produce (immer-style)
setState(
  produce((s) => {
    s.todos.push({ id: crypto.randomUUID(), text: "New todo", done: false });
  }),
);

// Toggle specific todo
setState("todos", (todo) => todo.id === id, "done", (done) => !done);
```

## Resources (Data Fetching)

```tsx
import { createResource, Suspense, ErrorBoundary } from "solid-js";

const fetchUser = async (id: string): Promise<User> => {
  const res = await fetch(`/api/users/${id}`);
  if (!res.ok) throw new Error("Failed to fetch user");
  return res.json();
};

function UserProfile(props: { userId: string }) {
  const [user, { refetch, mutate }] = createResource(
    () => props.userId,
    fetchUser,
  );

  return (
    <ErrorBoundary fallback={(err) => <p>Error: {err.message}</p>}>
      <Suspense fallback={<p>Loading...</p>}>
        <div>
          <h1>{user()?.name}</h1>
          <p>{user()?.email}</p>
          <button onClick={refetch}>Refresh</button>
        </div>
      </Suspense>
    </ErrorBoundary>
  );
}
```

## Context

```tsx
import { createContext, useContext, ParentComponent } from "solid-js";
import { createStore } from "solid-js/store";

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>();

export const AuthProvider: ParentComponent = (props) => {
  const [state, setState] = createStore<{ user: User | null }>({ user: null });

  const auth: AuthContextType = {
    get user() { return state.user; },
    login: async (email, password) => {
      const user = await api.login(email, password);
      setState("user", user);
    },
    logout: () => setState("user", null),
  };

  return (
    <AuthContext.Provider value={auth}>
      {props.children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
};
```

## SolidStart (SSR)

```tsx
// src/routes/posts/[id].tsx
import { RouteDefinition, useParams } from "@solidjs/router";
import { createAsync, cache } from "@solidjs/router";

const getPost = cache(async (id: string) => {
  "use server";
  return db.post.findUnique({ where: { id } });
}, "post");

export const route = {
  load: ({ params }) => getPost(params.id),
} satisfies RouteDefinition;

export default function PostPage() {
  const params = useParams();
  const post = createAsync(() => getPost(params.id));

  return (
    <article>
      <h1>{post()?.title}</h1>
      <div innerHTML={post()?.content} />
    </article>
  );
}
```

## Server Actions

```tsx
// src/lib/actions.ts
import { action, redirect } from "@solidjs/router";

export const createPost = action(async (formData: FormData) => {
  "use server";
  const title = formData.get("title") as string;
  const body = formData.get("body") as string;
  const post = await db.post.create({ data: { title, body } });
  throw redirect(`/posts/${post.id}`);
});

// Usage in component
import { createPost } from "~/lib/actions";

function NewPostForm() {
  return (
    <form action={createPost} method="post">
      <input name="title" required />
      <textarea name="body" required />
      <button type="submit">Create</button>
    </form>
  );
}
```

## Additional Resources

- SolidJS docs: https://www.solidjs.com/
- SolidStart: https://start.solidjs.com/
- Solid Router: https://docs.solidjs.com/solid-router
