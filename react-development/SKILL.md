---
name: react-development
description: React development with hooks, component patterns, state management (Zustand/Context), performance optimization, testing with React Testing Library, and modern React 18+ best practices.
---

# React Development

This skill should be used when the user needs to build, organize, or optimize React applications. It covers component architecture, hooks, state management, performance patterns, testing, and modern React 18+ features.

## When to Use This Skill

Use this skill when you need to:

- Build React components with TypeScript
- Implement custom hooks for shared logic
- Choose and use state management (Zustand, Context, Jotai)
- Optimize React performance (memoization, lazy loading)
- Test components with React Testing Library
- Set up React with Vite or Next.js
- Implement data fetching patterns (React Query, SWR)
- Apply accessibility best practices

## Project Setup

### Vite + React + TypeScript

```bash
npm create vite@latest my-app -- --template react-ts
cd my-app
npm install

# Essential dependencies
npm install react-router-dom zustand @tanstack/react-query axios
npm install -D @testing-library/react @testing-library/user-event vitest jsdom
```

### Next.js App Router

```bash
npx create-next-app@latest my-app --typescript --tailwind --eslint --app
cd my-app
npm install zustand @tanstack/react-query
```

## Component Patterns

### Functional Components with TypeScript

```tsx
// components/UserCard.tsx
interface User {
  id: number;
  name: string;
  email: string;
  avatar?: string;
  role: "admin" | "user" | "moderator";
}

interface UserCardProps {
  user: User;
  onEdit?: (user: User) => void;
  onDelete?: (id: number) => void;
  className?: string;
}

export function UserCard({ user, onEdit, onDelete, className }: UserCardProps) {
  const handleDelete = () => {
    if (window.confirm(`Delete ${user.name}?`)) {
      onDelete?.(user.id);
    }
  };

  return (
    <article className={`user-card ${className ?? ""}`} aria-label={user.name}>
      <img
        src={user.avatar ?? "/default-avatar.png"}
        alt={`${user.name}'s avatar`}
        width={48}
        height={48}
      />
      <div className="user-info">
        <h3>{user.name}</h3>
        <p>{user.email}</p>
        <span className={`badge badge-${user.role}`}>{user.role}</span>
      </div>
      <div className="actions">
        {onEdit && (
          <button onClick={() => onEdit(user)} aria-label="Edit user">
            Edit
          </button>
        )}
        {onDelete && (
          <button onClick={handleDelete} aria-label="Delete user">
            Delete
          </button>
        )}
      </div>
    </article>
  );
}
```

### Compound Components

```tsx
// components/Tabs/index.tsx
import { createContext, useContext, useState, ReactNode } from "react";

interface TabsContextValue {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const TabsContext = createContext<TabsContextValue | null>(null);

function useTabs() {
  const ctx = useContext(TabsContext);
  if (!ctx) throw new Error("useTabs must be used within Tabs");
  return ctx;
}

interface TabsProps {
  defaultTab: string;
  children: ReactNode;
  onChange?: (tab: string) => void;
}

function Tabs({ defaultTab, children, onChange }: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultTab);

  const handleChange = (tab: string) => {
    setActiveTab(tab);
    onChange?.(tab);
  };

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab: handleChange }}>
      <div className="tabs">{children}</div>
    </TabsContext.Provider>
  );
}

function TabList({ children }: { children: ReactNode }) {
  return <div role="tablist" className="tab-list">{children}</div>;
}

function Tab({ id, children }: { id: string; children: ReactNode }) {
  const { activeTab, setActiveTab } = useTabs();
  const isActive = activeTab === id;

  return (
    <button
      role="tab"
      aria-selected={isActive}
      aria-controls={`panel-${id}`}
      onClick={() => setActiveTab(id)}
      className={isActive ? "tab active" : "tab"}
    >
      {children}
    </button>
  );
}

function TabPanel({ id, children }: { id: string; children: ReactNode }) {
  const { activeTab } = useTabs();
  if (activeTab !== id) return null;

  return (
    <div role="tabpanel" id={`panel-${id}`} className="tab-panel">
      {children}
    </div>
  );
}

Tabs.List = TabList;
Tabs.Tab = Tab;
Tabs.Panel = TabPanel;

// Usage
function App() {
  return (
    <Tabs defaultTab="overview" onChange={(tab) => console.log(tab)}>
      <Tabs.List>
        <Tabs.Tab id="overview">Overview</Tabs.Tab>
        <Tabs.Tab id="settings">Settings</Tabs.Tab>
      </Tabs.List>
      <Tabs.Panel id="overview"><Overview /></Tabs.Panel>
      <Tabs.Panel id="settings"><Settings /></Tabs.Panel>
    </Tabs>
  );
}
```

## Custom Hooks

### Data Fetching Hook

```tsx
// hooks/useUsers.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import type { User } from "../types";

const API_URL = "/api/users";

async function fetchUsers(): Promise<User[]> {
  const res = await fetch(API_URL);
  if (!res.ok) throw new Error("Failed to fetch users");
  return res.json();
}

async function createUser(data: Omit<User, "id">): Promise<User> {
  const res = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create user");
  return res.json();
}

async function deleteUser(id: number): Promise<void> {
  const res = await fetch(`${API_URL}/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete user");
}

export function useUsers() {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: ["users"],
    queryFn: fetchUsers,
    staleTime: 5 * 60 * 1000,  // 5 minutes
  });

  const create = useMutation({
    mutationFn: createUser,
    onSuccess: (newUser) => {
      // Optimistic update
      queryClient.setQueryData<User[]>(["users"], (old = []) => [
        ...old,
        newUser,
      ]);
    },
  });

  const remove = useMutation({
    mutationFn: deleteUser,
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: ["users"] });
      const previous = queryClient.getQueryData<User[]>(["users"]);
      queryClient.setQueryData<User[]>(["users"], (old = []) =>
        old.filter((u) => u.id !== id)
      );
      return { previous };
    },
    onError: (_err, _id, context) => {
      queryClient.setQueryData(["users"], context?.previous);
    },
  });

  return {
    users: query.data ?? [],
    isLoading: query.isLoading,
    error: query.error,
    createUser: create.mutate,
    deleteUser: remove.mutate,
    isCreating: create.isPending,
    isDeleting: remove.isPending,
  };
}
```

### Local State Hooks

```tsx
// hooks/useLocalStorage.ts
import { useState, useEffect } from "react";

export function useLocalStorage<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? (JSON.parse(item) as T) : initialValue;
    } catch {
      return initialValue;
    }
  });

  useEffect(() => {
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch {
      console.warn(`Failed to save ${key} to localStorage`);
    }
  }, [key, value]);

  return [value, setValue] as const;
}

// hooks/useDebounce.ts
import { useState, useEffect } from "react";

export function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debounced;
}

// hooks/useIntersectionObserver.ts
import { useEffect, useRef, useState } from "react";

export function useIntersectionObserver(options?: IntersectionObserverInit) {
  const ref = useRef<HTMLElement>(null);
  const [isIntersecting, setIsIntersecting] = useState(false);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(([entry]) => {
      setIsIntersecting(entry.isIntersecting);
    }, options);

    observer.observe(element);
    return () => observer.disconnect();
  }, [options]);

  return { ref, isIntersecting };
}
```

## State Management with Zustand

```tsx
// store/useAuthStore.ts
import { create } from "zustand";
import { persist, devtools } from "zustand/middleware";

interface User {
  id: number;
  name: string;
  email: string;
  role: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  updateUser: (updates: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>()(
  devtools(
    persist(
      (set, get) => ({
        user: null,
        token: null,
        isAuthenticated: false,

        login: async (email, password) => {
          const response = await fetch("/api/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
          });

          if (!response.ok) {
            throw new Error("Invalid credentials");
          }

          const { user, token } = await response.json();
          set({ user, token, isAuthenticated: true });
        },

        logout: () => {
          set({ user: null, token: null, isAuthenticated: false });
        },

        updateUser: (updates) => {
          const current = get().user;
          if (current) {
            set({ user: { ...current, ...updates } });
          }
        },
      }),
      {
        name: "auth-storage",
        partialize: (state) => ({ user: state.user, token: state.token }),
      }
    )
  )
);

// Usage in components
function ProfileButton() {
  const { user, logout } = useAuthStore();

  if (!user) return <a href="/login">Sign in</a>;

  return (
    <div>
      <span>{user.name}</span>
      <button onClick={logout}>Sign out</button>
    </div>
  );
}

// Selectors for performance (prevents unnecessary re-renders)
const selectUser = (state: AuthState) => state.user;
const selectIsAuthenticated = (state: AuthState) => state.isAuthenticated;

function Header() {
  const isAuthenticated = useAuthStore(selectIsAuthenticated);
  // Only re-renders when isAuthenticated changes
  return <nav>{isAuthenticated ? <ProfileButton /> : <a href="/login">Login</a>}</nav>;
}
```

## Performance Optimization

### Memoization

```tsx
import { memo, useMemo, useCallback } from "react";

// Memoize expensive child components
const UserList = memo(function UserList({
  users,
  onDelete,
}: {
  users: User[];
  onDelete: (id: number) => void;
}) {
  return (
    <ul>
      {users.map((user) => (
        <UserCard key={user.id} user={user} onDelete={onDelete} />
      ))}
    </ul>
  );
});

function Dashboard() {
  const [users, setUsers] = useState<User[]>([]);
  const [filter, setFilter] = useState("");

  // Memoize derived data
  const filteredUsers = useMemo(
    () => users.filter((u) => u.name.toLowerCase().includes(filter.toLowerCase())),
    [users, filter]
  );

  // Memoize callbacks passed to children
  const handleDelete = useCallback((id: number) => {
    setUsers((prev) => prev.filter((u) => u.id !== id));
  }, []); // stable reference — no deps

  return (
    <>
      <input value={filter} onChange={(e) => setFilter(e.target.value)} />
      <UserList users={filteredUsers} onDelete={handleDelete} />
    </>
  );
}
```

### Lazy Loading

```tsx
import { lazy, Suspense } from "react";

// Lazy load heavy components/pages
const AdminPanel = lazy(() => import("./pages/AdminPanel"));
const Charts = lazy(() => import("./components/Charts"));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route path="/admin" element={<AdminPanel />} />
      </Routes>
    </Suspense>
  );
}

// Virtualize long lists
import { useVirtualizer } from "@tanstack/react-virtual";

function VirtualList({ items }: { items: string[] }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
  });

  return (
    <div ref={parentRef} style={{ height: 400, overflow: "auto" }}>
      <div style={{ height: virtualizer.getTotalSize(), position: "relative" }}>
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: "absolute",
              top: virtualItem.start,
              height: virtualItem.size,
            }}
          >
            {items[virtualItem.index]}
          </div>
        ))}
      </div>
    </div>
  );
}
```

## Testing with React Testing Library

```tsx
// components/__tests__/UserCard.test.tsx
import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { UserCard } from "../UserCard";

const mockUser = {
  id: 1,
  name: "Alice Smith",
  email: "alice@example.com",
  role: "admin" as const,
};

describe("UserCard", () => {
  it("renders user information", () => {
    render(<UserCard user={mockUser} />);

    expect(screen.getByText("Alice Smith")).toBeInTheDocument();
    expect(screen.getByText("alice@example.com")).toBeInTheDocument();
    expect(screen.getByText("admin")).toBeInTheDocument();
  });

  it("calls onEdit when edit button clicked", async () => {
    const user = userEvent.setup();
    const onEdit = vi.fn();

    render(<UserCard user={mockUser} onEdit={onEdit} />);

    await user.click(screen.getByRole("button", { name: /edit/i }));
    expect(onEdit).toHaveBeenCalledWith(mockUser);
  });

  it("calls onDelete after confirmation", async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();
    vi.spyOn(window, "confirm").mockReturnValue(true);

    render(<UserCard user={mockUser} onDelete={onDelete} />);

    await user.click(screen.getByRole("button", { name: /delete/i }));
    expect(onDelete).toHaveBeenCalledWith(1);
  });

  it("does not call onDelete when confirmation cancelled", async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();
    vi.spyOn(window, "confirm").mockReturnValue(false);

    render(<UserCard user={mockUser} onDelete={onDelete} />);
    await user.click(screen.getByRole("button", { name: /delete/i }));
    expect(onDelete).not.toHaveBeenCalled();
  });
});

// Testing hooks
import { renderHook, act } from "@testing-library/react";
import { useUsers } from "../../hooks/useUsers";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

describe("useUsers", () => {
  it("fetches users on mount", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [mockUser],
    }));

    const { result } = renderHook(() => useUsers(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.users).toHaveLength(1);
    });

    expect(result.current.users[0].name).toBe("Alice Smith");
  });
});
```

## React 18+ Features

```tsx
// useTransition — non-urgent state updates
import { useTransition, useState } from "react";

function SearchResults() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<string[]>([]);
  const [isPending, startTransition] = useTransition();

  function handleSearch(e: React.ChangeEvent<HTMLInputElement>) {
    setQuery(e.target.value);

    // Mark as non-urgent — won't block input
    startTransition(() => {
      setResults(expensiveSearch(e.target.value));
    });
  }

  return (
    <>
      <input value={query} onChange={handleSearch} />
      {isPending ? <Spinner /> : <ResultList results={results} />}
    </>
  );
}

// useDeferredValue — defer re-render of slow components
import { useDeferredValue } from "react";

function ParentComponent() {
  const [query, setQuery] = useState("");
  const deferredQuery = useDeferredValue(query);

  return (
    <>
      <input value={query} onChange={(e) => setQuery(e.target.value)} />
      {/* SlowComponent re-renders with deferred value */}
      <SlowComponent query={deferredQuery} />
    </>
  );
}

// Server Components (Next.js App Router)
// app/users/page.tsx — Server Component (no "use client")
async function UsersPage() {
  // Direct DB access — runs on server
  const users = await db.users.findAll();

  return (
    <main>
      <h1>Users</h1>
      {/* Interactive client component */}
      <UserFilters />
      <ul>
        {users.map((user) => (
          <li key={user.id}>{user.name}</li>
        ))}
      </ul>
    </main>
  );
}
```

## File Organization

```
src/
├── components/           # Reusable UI components
│   ├── ui/               # Primitives (Button, Input, Modal)
│   ├── layout/           # Layout components (Header, Sidebar)
│   └── features/         # Feature-specific components
├── hooks/                # Custom React hooks
├── pages/ (or app/)      # Route components
├── store/                # Zustand stores
├── lib/                  # API clients, utilities
├── types/                # TypeScript types/interfaces
└── __tests__/            # Co-located tests
```

## Additional Resources

- React docs: https://react.dev/
- React Query: https://tanstack.com/query/latest
- Zustand: https://zustand-demo.pmnd.rs/
- React Testing Library: https://testing-library.com/docs/react-testing-library/intro/
- Vite: https://vitejs.dev/
