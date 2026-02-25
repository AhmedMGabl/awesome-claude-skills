---
name: svelte-v5
description: Svelte 5 runes patterns covering $state, $derived, $effect, $props, $bindable, snippet blocks, event handling, component composition, migration from Svelte 4, and SvelteKit integration.
---

# Svelte v5

This skill should be used when building applications with Svelte 5 and its runes system. It covers $state, $derived, $effect, $props, snippets, and migration from Svelte 4.

## When to Use This Skill

Use this skill when you need to:

- Use Svelte 5 runes for reactive state management
- Define component props with $props rune
- Create derived state and side effects
- Use snippet blocks for reusable template fragments
- Migrate from Svelte 4 to Svelte 5

## State Rune

```svelte
<script lang="ts">
  let count = $state(0);
  let name = $state("World");
  let items = $state<string[]>([]);

  function increment() {
    count++;
  }

  function addItem(item: string) {
    items.push(item); // Direct mutation works with $state
  }
</script>

<button onclick={increment}>Count: {count}</button>
<input bind:value={name} />
<p>Hello, {name}!</p>
<ul>
  {#each items as item}
    <li>{item}</li>
  {/each}
</ul>
```

## Derived Rune

```svelte
<script lang="ts">
  let items = $state([
    { name: "Apple", price: 1.5, quantity: 3 },
    { name: "Banana", price: 0.5, quantity: 6 },
  ]);

  let total = $derived(
    items.reduce((sum, item) => sum + item.price * item.quantity, 0)
  );

  let itemCount = $derived(items.length);

  // Derived with complex logic using $derived.by
  let summary = $derived.by(() => {
    const subtotal = items.reduce((s, i) => s + i.price * i.quantity, 0);
    const tax = subtotal * 0.1;
    return { subtotal, tax, total: subtotal + tax };
  });
</script>

<p>Items: {itemCount}, Total: ${total.toFixed(2)}</p>
<p>Tax: ${summary.tax.toFixed(2)}, Grand Total: ${summary.total.toFixed(2)}</p>
```

## Effect Rune

```svelte
<script lang="ts">
  let query = $state("");
  let results = $state<string[]>([]);

  // Runs when dependencies change
  $effect(() => {
    if (query.length < 2) {
      results = [];
      return;
    }

    const controller = new AbortController();
    fetch(`/api/search?q=${query}`, { signal: controller.signal })
      .then((r) => r.json())
      .then((data) => { results = data; });

    // Cleanup function
    return () => controller.abort();
  });

  // Pre-effect (runs before DOM update)
  $effect.pre(() => {
    console.log("About to update DOM with:", results.length, "results");
  });
</script>
```

## Props Rune

```svelte
<!-- Button.svelte -->
<script lang="ts">
  interface Props {
    variant?: "primary" | "secondary";
    size?: "sm" | "md" | "lg";
    disabled?: boolean;
    onclick?: () => void;
    children: import("svelte").Snippet;
  }

  let {
    variant = "primary",
    size = "md",
    disabled = false,
    onclick,
    children,
  }: Props = $props();
</script>

<button
  class="{variant} {size}"
  {disabled}
  {onclick}
>
  {@render children()}
</button>

<!-- Usage -->
<Button variant="primary" onclick={() => save()}>
  Save Changes
</Button>
```

## Bindable Props

```svelte
<!-- TextInput.svelte -->
<script lang="ts">
  let { value = $bindable(""), placeholder = "" }: {
    value?: string;
    placeholder?: string;
  } = $props();
</script>

<input bind:value {placeholder} />

<!-- Parent -->
<script lang="ts">
  let name = $state("");
</script>

<TextInput bind:value={name} placeholder="Enter name" />
<p>You typed: {name}</p>
```

## Snippets

```svelte
<script lang="ts">
  interface User {
    id: string;
    name: string;
    email: string;
  }

  let { users }: { users: User[] } = $props();
</script>

{#snippet userRow(user: User)}
  <tr>
    <td>{user.name}</td>
    <td>{user.email}</td>
  </tr>
{/snippet}

{#snippet emptyState()}
  <tr>
    <td colspan="2" class="text-center text-gray-500">No users found</td>
  </tr>
{/snippet}

<table>
  <thead>
    <tr><th>Name</th><th>Email</th></tr>
  </thead>
  <tbody>
    {#if users.length > 0}
      {#each users as user}
        {@render userRow(user)}
      {/each}
    {:else}
      {@render emptyState()}
    {/if}
  </tbody>
</table>
```

## Migration from Svelte 4

```svelte
<!-- Svelte 4 -->
<script>
  export let name;
  export let count = 0;
  $: doubled = count * 2;
  $: console.log(count);
</script>

<!-- Svelte 5 -->
<script>
  let { name, count = $bindable(0) } = $props();
  let doubled = $derived(count * 2);
  $effect(() => { console.log(count); });
</script>
```

## Additional Resources

- Svelte 5 docs: https://svelte.dev/docs/svelte
- Runes: https://svelte.dev/docs/svelte/$state
- Migration guide: https://svelte.dev/docs/svelte/v5-migration-guide
