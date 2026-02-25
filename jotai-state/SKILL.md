---
name: jotai-state
description: Jotai atomic state management covering primitive atoms, derived atoms, async atoms, atom families, persistence, DevTools, and integration patterns for React applications.
---

# Jotai State Management

This skill should be used when managing state with Jotai in React applications. It covers atoms, derived state, async patterns, persistence, and DevTools.

## When to Use This Skill

Use this skill when you need to:

- Manage global state with atomic primitives
- Create derived and computed state
- Handle async data fetching in atoms
- Persist state to localStorage or URL params
- Build state management without boilerplate

## Primitive Atoms

```typescript
import { atom, useAtom, useAtomValue, useSetAtom } from "jotai";

// Primitive atoms
const countAtom = atom(0);
const nameAtom = atom("World");
const darkModeAtom = atom(false);

function Counter() {
  const [count, setCount] = useAtom(countAtom);
  return (
    <div>
      <span>{count}</span>
      <button onClick={() => setCount((c) => c + 1)}>+</button>
    </div>
  );
}

// Read-only hook (no setter)
function DisplayName() {
  const name = useAtomValue(nameAtom);
  return <h1>Hello, {name}!</h1>;
}

// Write-only hook (no value)
function ToggleDarkMode() {
  const setDarkMode = useSetAtom(darkModeAtom);
  return <button onClick={() => setDarkMode((d) => !d)}>Toggle</button>;
}
```

## Derived Atoms

```typescript
// Read-only derived atom
const doubleCountAtom = atom((get) => get(countAtom) * 2);

// Derived from multiple atoms
const greetingAtom = atom((get) => {
  const name = get(nameAtom);
  const isDark = get(darkModeAtom);
  return `${isDark ? "Good evening" : "Hello"}, ${name}!`;
});

// Read-write derived atom
const uppercaseNameAtom = atom(
  (get) => get(nameAtom).toUpperCase(),
  (get, set, newName: string) => {
    set(nameAtom, newName);
  },
);

// Write-only atom (action)
const resetAllAtom = atom(null, (get, set) => {
  set(countAtom, 0);
  set(nameAtom, "World");
  set(darkModeAtom, false);
});
```

## Async Atoms

```typescript
// Async read atom
const userAtom = atom(async () => {
  const res = await fetch("/api/user");
  return res.json();
});

// Async derived atom
const userPostsAtom = atom(async (get) => {
  const user = await get(userAtom);
  const res = await fetch(`/api/users/${user.id}/posts`);
  return res.json();
});

// Usage with Suspense
function UserProfile() {
  const user = useAtomValue(userAtom);
  return <div>{user.name}</div>;
}

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <UserProfile />
    </Suspense>
  );
}

// Refreshable async atom
const refreshCountAtom = atom(0);
const dataAtom = atom(async (get) => {
  get(refreshCountAtom); // dependency trigger
  const res = await fetch("/api/data");
  return res.json();
});

const refreshDataAtom = atom(null, (get, set) => {
  set(refreshCountAtom, (c) => c + 1);
});
```

## Atom Families

```typescript
import { atomFamily } from "jotai/utils";

// Create atoms dynamically by key
const todoAtomFamily = atomFamily((id: string) =>
  atom({ id, text: "", done: false }),
);

const todoIdsAtom = atom<string[]>([]);

function TodoItem({ id }: { id: string }) {
  const [todo, setTodo] = useAtom(todoAtomFamily(id));
  return (
    <div>
      <input
        type="checkbox"
        checked={todo.done}
        onChange={() => setTodo((t) => ({ ...t, done: !t.done }))}
      />
      <span>{todo.text}</span>
    </div>
  );
}
```

## Persistence

```typescript
import { atomWithStorage } from "jotai/utils";

// Persist to localStorage
const themeAtom = atomWithStorage("theme", "light");
const settingsAtom = atomWithStorage("settings", {
  notifications: true,
  language: "en",
});

// Persist to sessionStorage
const sessionAtom = atomWithStorage("session", null, sessionStorage);
```

## DevTools

```typescript
import { useAtomsDebugValue } from "jotai-devtools";
import { DevTools } from "jotai-devtools";

function App() {
  useAtomsDebugValue(); // Shows atoms in React DevTools
  return (
    <>
      <DevTools />
      <Router />
    </>
  );
}
```

## Additional Resources

- Jotai docs: https://jotai.org/docs/introduction
- Utils: https://jotai.org/docs/utilities
- Recipes: https://jotai.org/docs/recipes/atom-creators
