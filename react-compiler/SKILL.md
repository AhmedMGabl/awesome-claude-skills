---
name: react-compiler
description: React Compiler patterns covering automatic memoization, compiler directives, opt-in/opt-out configuration, ESLint plugin, Babel integration, migration from manual useMemo/useCallback, and debugging compiler optimizations.
---

# React Compiler

This skill should be used when working with the React Compiler (React Forget). It covers automatic memoization, configuration, migration from manual memoization, and debugging.

## When to Use This Skill

Use this skill when you need to:

- Enable automatic memoization in React applications
- Configure the React Compiler with Babel or Next.js
- Migrate from manual useMemo/useCallback patterns
- Debug compiler optimization decisions
- Use compiler directives for opt-in/opt-out

## Next.js Configuration

```javascript
// next.config.js
const nextConfig = {
  experimental: {
    reactCompiler: true,
  },
};

module.exports = nextConfig;

// Opt-in mode (gradual adoption)
const nextConfig = {
  experimental: {
    reactCompiler: {
      compilationMode: "annotation",
    },
  },
};
```

## Babel Configuration

```javascript
// babel.config.js
module.exports = {
  plugins: [
    ["babel-plugin-react-compiler", {
      // Options
      compilationMode: "all", // "all" | "annotation"
    }],
  ],
};
```

## Compiler Directives

```tsx
// Opt into compilation (when using annotation mode)
"use memo";
function ExpensiveComponent({ data }: { data: Item[] }) {
  const sorted = data.toSorted((a, b) => a.name.localeCompare(b.name));
  const filtered = sorted.filter((item) => item.active);
  return (
    <ul>
      {filtered.map((item) => (
        <li key={item.id}>{item.name}</li>
      ))}
    </ul>
  );
}

// Opt out of compilation for specific component
"use no memo";
function ComponentWithSideEffects() {
  // This component won't be optimized by the compiler
  // Useful for components that rely on referential identity
  return <div>...</div>;
}
```

## Migration from Manual Memoization

```tsx
// Before: Manual memoization
import { useMemo, useCallback, memo } from "react";

const UserList = memo(function UserList({ users, onSelect }: Props) {
  const sorted = useMemo(
    () => users.toSorted((a, b) => a.name.localeCompare(b.name)),
    [users],
  );

  const handleSelect = useCallback(
    (id: string) => {
      onSelect(id);
    },
    [onSelect],
  );

  return (
    <ul>
      {sorted.map((user) => (
        <li key={user.id} onClick={() => handleSelect(user.id)}>
          {user.name}
        </li>
      ))}
    </ul>
  );
});

// After: React Compiler handles memoization automatically
function UserList({ users, onSelect }: Props) {
  const sorted = users.toSorted((a, b) => a.name.localeCompare(b.name));

  const handleSelect = (id: string) => {
    onSelect(id);
  };

  return (
    <ul>
      {sorted.map((user) => (
        <li key={user.id} onClick={() => handleSelect(user.id)}>
          {user.name}
        </li>
      ))}
    </ul>
  );
}
```

## ESLint Plugin

```javascript
// eslint.config.js
import reactCompiler from "eslint-plugin-react-compiler";

export default [
  {
    plugins: { "react-compiler": reactCompiler },
    rules: {
      "react-compiler/react-compiler": "error",
    },
  },
];

// Common violations the linter catches:
// - Mutating objects/arrays that are used in render
// - Breaking the rules of React (hooks, etc.)
// - Patterns that prevent compilation
```

## Rules of React (Required for Compiler)

```tsx
// The compiler requires following React's rules strictly:

// 1. Components must be pure functions of their props
function Good({ items }: { items: Item[] }) {
  // Create new arrays instead of mutating
  const sorted = items.toSorted((a, b) => a.name.localeCompare(b.name));
  return <List items={sorted} />;
}

// 2. Don't mutate props or state during render
function Bad({ items }: { items: Item[] }) {
  items.sort(); // Mutates input — breaks compilation
  return <List items={items} />;
}

// 3. Return values from hooks must be treated as immutable
function Good2() {
  const [items, setItems] = useState<Item[]>([]);
  // Use setter function, don't mutate directly
  const addItem = (item: Item) => setItems((prev) => [...prev, item]);
  return <button onClick={() => addItem(newItem)}>Add</button>;
}
```

## Additional Resources

- React Compiler docs: https://react.dev/learn/react-compiler
- ESLint plugin: https://www.npmjs.com/package/eslint-plugin-react-compiler
