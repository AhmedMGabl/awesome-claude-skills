---
name: million-js
description: Million.js optimization patterns covering the block virtual DOM, compiler integration, automatic mode, manual block() wrapping, for-loop optimization, React component optimization, and performance profiling for faster React rendering.
---

# Million.js

This skill should be used when optimizing React rendering performance with Million.js. It covers the block virtual DOM, compiler setup, automatic mode, and component optimization.

## When to Use This Skill

Use this skill when you need to:

- Speed up React rendering with block virtual DOM
- Optimize list rendering with Million's For component
- Configure the Million.js compiler for Next.js or Vite
- Profile and identify components to optimize
- Reduce virtual DOM diffing overhead

## Installation and Setup

```typescript
// Next.js - next.config.mjs
import million from "million/compiler";

const nextConfig = {
  reactStrictMode: true,
};

export default million.next(nextConfig, {
  auto: true, // Automatically optimize components
});

// Vite - vite.config.ts
import million from "million/compiler";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [million.vite({ auto: true }), react()],
});
```

## Automatic Mode

```tsx
// With auto: true in compiler config, Million.js
// automatically wraps eligible components with block()

// This component is automatically optimized:
function UserCard({ name, email, avatar }: UserCardProps) {
  return (
    <div className="card">
      <img src={avatar} alt={name} />
      <h3>{name}</h3>
      <p>{email}</p>
    </div>
  );
}

// Components with these patterns are skipped:
// - Components using refs
// - Components with spread props on DOM elements
// - Components using context consumers
// - Components with non-deterministic rendering
```

## Manual Block Wrapping

```tsx
import { block } from "million/react";

// Wrap performance-critical components manually
const ProductCard = block(function ProductCard({
  title,
  price,
  image,
  onAddToCart,
}: ProductCardProps) {
  return (
    <div className="product-card">
      <img src={image} alt={title} />
      <h3>{title}</h3>
      <span className="price">${price.toFixed(2)}</span>
      <button onClick={onAddToCart}>Add to Cart</button>
    </div>
  );
});
```

## Optimized List Rendering

```tsx
import { For } from "million/react";

interface Todo {
  id: string;
  text: string;
  done: boolean;
}

function TodoList({ todos }: { todos: Todo[] }) {
  return (
    <ul>
      <For each={todos}>
        {(todo) => (
          <li key={todo.id} className={todo.done ? "done" : ""}>
            <span>{todo.text}</span>
          </li>
        )}
      </For>
    </ul>
  );
}

// For large datasets with virtualization hint
function LargeList({ items }: { items: Item[] }) {
  return (
    <div className="list-container">
      <For each={items} memo>
        {(item) => <ItemRow key={item.id} {...item} />}
      </For>
    </div>
  );
}
```

## Compiler Ignore Directives

```tsx
// Skip specific components from auto-optimization
// @million-ignore
function ComplexComponent({ data }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  // Complex logic that doesn't work with block()
  return <div ref={ref}>...</div>;
}
```

## Performance Profiling

```tsx
// Use React DevTools Profiler to identify slow components
// then wrap them with block()

// Before: Regular React component (slow with many re-renders)
function DataTable({ rows, columns }: DataTableProps) {
  return (
    <table>
      <tbody>
        {rows.map((row) => (
          <tr key={row.id}>
            {columns.map((col) => (
              <td key={col.key}>{row[col.key]}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// After: Optimized with Million.js
const OptimizedRow = block(function Row({ row, columns }: RowProps) {
  return (
    <tr>
      {columns.map((col) => (
        <td key={col.key}>{row[col.key]}</td>
      ))}
    </tr>
  );
});

function DataTable({ rows, columns }: DataTableProps) {
  return (
    <table>
      <tbody>
        <For each={rows}>
          {(row) => <OptimizedRow key={row.id} row={row} columns={columns} />}
        </For>
      </tbody>
    </table>
  );
}
```

## Additional Resources

- Million.js docs: https://million.dev/docs
- Automatic mode: https://million.dev/docs/automatic
- Block rules: https://million.dev/docs/rules-of-blocks
