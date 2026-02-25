---
name: nanostores
description: Nanostores lightweight state management covering atoms, computed stores, maps, deep maps, lifecycle events, and framework-agnostic integration with React, Vue, Svelte, and Solid.
---

# Nanostores

This skill should be used when managing state with Nanostores. It covers atoms, computed stores, maps, lifecycle events, and multi-framework integration.

## When to Use This Skill

Use this skill when you need to:

- Share state across framework-agnostic components
- Use lightweight state management (< 1KB)
- Build stores that work with React, Vue, Svelte, and Solid
- Create computed derived state
- Manage complex nested state with maps

## Atoms

```typescript
// stores/counter.ts
import { atom } from "nanostores";

export const $count = atom(0);

export function increment() {
  $count.set($count.get() + 1);
}

export function decrement() {
  $count.set($count.get() - 1);
}

export function reset() {
  $count.set(0);
}
```

## Maps (Object State)

```typescript
import { map } from "nanostores";

interface User {
  name: string;
  email: string;
  plan: "free" | "pro";
}

export const $user = map<User>({
  name: "",
  email: "",
  plan: "free",
});

// Update single key
$user.setKey("name", "Alice");
$user.setKey("plan", "pro");

// Update multiple keys
$user.set({ ...$user.get(), name: "Alice", email: "alice@example.com" });
```

## Computed Stores

```typescript
import { atom, computed } from "nanostores";

const $items = atom<{ id: string; price: number; quantity: number }[]>([]);
const $taxRate = atom(0.1);

// Derived from single store
const $itemCount = computed($items, (items) =>
  items.reduce((sum, item) => sum + item.quantity, 0),
);

// Derived from multiple stores
const $total = computed([$items, $taxRate], (items, taxRate) => {
  const subtotal = items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  return subtotal * (1 + taxRate);
});

// Chained computed
const $formattedTotal = computed($total, (total) =>
  new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(total),
);
```

## React Integration

```tsx
import { useStore } from "@nanostores/react";
import { $count, increment, decrement } from "../stores/counter";
import { $user } from "../stores/user";

function Counter() {
  const count = useStore($count);
  return (
    <div>
      <span>{count}</span>
      <button onClick={decrement}>-</button>
      <button onClick={increment}>+</button>
    </div>
  );
}

function UserProfile() {
  const user = useStore($user);
  return (
    <div>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
      <span>{user.plan}</span>
    </div>
  );
}
```

## Vue Integration

```vue
<script setup>
import { useStore } from "@nanostores/vue";
import { $count, increment, decrement } from "../stores/counter";

const count = useStore($count);
</script>

<template>
  <div>
    <span>{{ count }}</span>
    <button @click="decrement">-</button>
    <button @click="increment">+</button>
  </div>
</template>
```

## Lifecycle and Async

```typescript
import { atom, onMount } from "nanostores";

export const $posts = atom<Post[]>([]);
export const $loading = atom(false);

// Fetch on first subscribe
onMount($posts, () => {
  $loading.set(true);
  fetch("/api/posts")
    .then((r) => r.json())
    .then((data) => {
      $posts.set(data);
      $loading.set(false);
    });

  // Cleanup on last unsubscribe
  return () => {
    $posts.set([]);
  };
});
```

## Persistent Store

```typescript
import { persistentAtom, persistentMap } from "@nanostores/persistent";

export const $theme = persistentAtom<"light" | "dark">("theme", "light");

export const $settings = persistentMap<{
  language: string;
  notifications: boolean;
}>("settings:", {
  language: "en",
  notifications: true,
});
```

## Additional Resources

- Nanostores docs: https://github.com/nanostores/nanostores
- React integration: https://github.com/nanostores/react
- Persistent: https://github.com/nanostores/persistent
