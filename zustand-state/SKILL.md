---
name: zustand-state
description: Zustand state management covering store creation, selectors, middleware (persist, devtools, immer), async actions, computed values, store composition, TypeScript patterns, testing stores, and migration from Redux.
---

# Zustand State Management

This skill should be used when managing client-side state with Zustand. It covers store creation, middleware, selectors, async actions, and testing.

## When to Use This Skill

Use this skill when you need to:

- Manage global client state in React
- Persist state to localStorage
- Implement async actions in stores
- Compose multiple stores
- Test Zustand stores

## Basic Store

```typescript
import { create } from "zustand";

interface TodoStore {
  todos: Todo[];
  addTodo: (title: string) => void;
  toggleTodo: (id: string) => void;
  removeTodo: (id: string) => void;
}

export const useTodoStore = create<TodoStore>((set) => ({
  todos: [],

  addTodo: (title) =>
    set((state) => ({
      todos: [...state.todos, { id: crypto.randomUUID(), title, completed: false }],
    })),

  toggleTodo: (id) =>
    set((state) => ({
      todos: state.todos.map((t) => (t.id === id ? { ...t, completed: !t.completed } : t)),
    })),

  removeTodo: (id) =>
    set((state) => ({
      todos: state.todos.filter((t) => t.id !== id),
    })),
}));
```

## Middleware Stack

```typescript
import { create } from "zustand";
import { devtools, persist } from "zustand/middleware";
import { immer } from "zustand/middleware/immer";

interface AuthStore {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthStore>()(
  devtools(
    persist(
      immer((set) => ({
        user: null,
        token: null,

        login: async (email, password) => {
          const res = await fetch("/api/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
          });
          const { user, token } = await res.json();

          set((state) => {
            state.user = user;
            state.token = token;
          });
        },

        logout: () => {
          set((state) => {
            state.user = null;
            state.token = null;
          });
        },
      })),
      { name: "auth-storage" },
    ),
    { name: "AuthStore" },
  ),
);
```

## Selectors (Avoid Re-renders)

```tsx
// BAD — re-renders on any store change
const { todos, addTodo } = useTodoStore();

// GOOD — only re-renders when selected value changes
const todos = useTodoStore((state) => state.todos);
const addTodo = useTodoStore((state) => state.addTodo);

// Derived/computed values with shallow comparison
import { useShallow } from "zustand/react/shallow";

const { completedCount, totalCount } = useTodoStore(
  useShallow((state) => ({
    completedCount: state.todos.filter((t) => t.completed).length,
    totalCount: state.todos.length,
  })),
);
```

## Async Actions

```typescript
interface ProductStore {
  products: Product[];
  loading: boolean;
  error: string | null;
  fetchProducts: () => Promise<void>;
}

export const useProductStore = create<ProductStore>((set, get) => ({
  products: [],
  loading: false,
  error: null,

  fetchProducts: async () => {
    if (get().loading) return; // Prevent duplicate fetches

    set({ loading: true, error: null });
    try {
      const res = await fetch("/api/products");
      const products = await res.json();
      set({ products, loading: false });
    } catch (err) {
      set({ error: (err as Error).message, loading: false });
    }
  },
}));
```

## Store Slices Pattern

```typescript
// Split large stores into slices
interface UserSlice {
  user: User | null;
  setUser: (user: User | null) => void;
}

interface SettingsSlice {
  theme: "light" | "dark";
  toggleTheme: () => void;
}

type AppStore = UserSlice & SettingsSlice;

const createUserSlice = (set: any): UserSlice => ({
  user: null,
  setUser: (user) => set({ user }),
});

const createSettingsSlice = (set: any): SettingsSlice => ({
  theme: "light",
  toggleTheme: () =>
    set((state: SettingsSlice) => ({
      theme: state.theme === "light" ? "dark" : "light",
    })),
});

export const useAppStore = create<AppStore>()((...args) => ({
  ...createUserSlice(...args),
  ...createSettingsSlice(...args),
}));
```

## Testing

```typescript
import { describe, it, expect, beforeEach } from "vitest";
import { useTodoStore } from "./todo-store";

describe("TodoStore", () => {
  beforeEach(() => {
    // Reset store between tests
    useTodoStore.setState({ todos: [] });
  });

  it("adds a todo", () => {
    useTodoStore.getState().addTodo("Test task");

    const { todos } = useTodoStore.getState();
    expect(todos).toHaveLength(1);
    expect(todos[0].title).toBe("Test task");
    expect(todos[0].completed).toBe(false);
  });

  it("toggles a todo", () => {
    useTodoStore.getState().addTodo("Test");
    const id = useTodoStore.getState().todos[0].id;

    useTodoStore.getState().toggleTodo(id);
    expect(useTodoStore.getState().todos[0].completed).toBe(true);
  });
});
```

## Additional Resources

- Zustand docs: https://zustand.docs.pmnd.rs/
- Zustand recipes: https://zustand.docs.pmnd.rs/guides/how-to-reset-state
- Comparison with Redux: https://zustand.docs.pmnd.rs/getting-started/comparison
