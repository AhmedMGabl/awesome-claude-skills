---
name: sveltekit-development
description: SvelteKit development covering Svelte 5 runes, reactivity, components, server-side rendering, load functions, form actions, API routes, authentication, deployment, and full-stack TypeScript patterns.
---

# SvelteKit Development

This skill provides comprehensive guidance for building full-stack applications with SvelteKit and Svelte 5. Apply these patterns when scaffolding new projects, creating components with runes-based reactivity, implementing server-side data loading, handling forms with progressive enhancement, building API routes, adding authentication, and deploying to production.

---

## 1. Project Setup

### Scaffolding a New Project

```bash
# Create a new SvelteKit project
npx sv create my-app
cd my-app
npm install
npm run dev
```

### Project Structure

```
my-app/
├── src/
│   ├── lib/
│   │   ├── components/    # Reusable Svelte components
│   │   ├── server/        # Server-only modules (DB, auth)
│   │   ├── stores/        # Shared stores
│   │   ├── types/         # TypeScript type definitions
│   │   └── utils/         # Shared utility functions
│   ├── routes/
│   │   ├── +layout.svelte       # Root layout
│   │   ├── +layout.server.ts    # Root layout server load
│   │   ├── +page.svelte         # Home page
│   │   ├── +page.server.ts      # Home page server load + actions
│   │   ├── +error.svelte        # Error page
│   │   ├── api/                  # API routes
│   │   │   └── posts/
│   │   │       └── +server.ts
│   │   ├── dashboard/
│   │   │   ├── +page.svelte
│   │   │   └── +page.server.ts
│   │   └── auth/
│   │       ├── login/
│   │       │   └── +page.svelte
│   │       └── logout/
│   │           └── +server.ts
│   ├── app.html           # HTML template
│   ├── app.css            # Global styles
│   ├── app.d.ts           # Type declarations
│   └── hooks.server.ts    # Server hooks (auth, logging)
├── static/                # Static assets (favicon, images)
├── svelte.config.js       # SvelteKit configuration
├── vite.config.ts         # Vite configuration
├── tsconfig.json          # TypeScript configuration
└── package.json
```

### svelte.config.js

```js
import adapter from '@sveltejs/adapter-node';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter({
      out: 'build',
      precompress: true
    }),
    alias: {
      $components: 'src/lib/components',
      $server: 'src/lib/server',
      $stores: 'src/lib/stores',
      $types: 'src/lib/types'
    },
    csrf: {
      checkOrigin: true
    }
  }
};

export default config;
```

### Type Declarations (app.d.ts)

```ts
declare global {
  namespace App {
    interface Error {
      message: string;
      code?: string;
    }
    interface Locals {
      user: {
        id: string;
        email: string;
        role: 'admin' | 'user';
      } | null;
    }
    interface PageData {
      flash?: { type: 'success' | 'error'; message: string };
    }
  }
}

export {};
```

---

## 2. Svelte 5 Runes

Svelte 5 replaces the implicit reactivity model with explicit **runes** -- compiler hints prefixed with `$`.

### $state -- Reactive State

```svelte
<script lang="ts">
  // Primitive reactive state
  let count = $state(0);

  // Object reactive state (deeply reactive)
  let user = $state({
    name: 'Alice',
    preferences: { theme: 'dark', lang: 'en' }
  });

  // Array reactive state
  let items = $state<string[]>(['svelte', 'kit', 'runes']);

  function increment() {
    count++;
  }

  function addItem(item: string) {
    items.push(item);  // Mutations are tracked automatically
  }

  function updateTheme(theme: string) {
    user.preferences.theme = theme;  // Deep mutation tracked
  }
</script>

<button onclick={increment}>Count: {count}</button>
<p>Theme: {user.preferences.theme}</p>
<ul>
  {#each items as item}
    <li>{item}</li>
  {/each}
</ul>
```

### $derived -- Computed Values

```svelte
<script lang="ts">
  let items = $state([
    { name: 'Apples', price: 2.5, quantity: 3 },
    { name: 'Bread', price: 3.0, quantity: 1 }
  ]);

  let searchQuery = $state('');

  // Simple derived value
  let totalCost = $derived(
    items.reduce((sum, item) => sum + item.price * item.quantity, 0)
  );

  // Complex derived with block syntax
  let filteredItems = $derived.by(() => {
    const query = searchQuery.toLowerCase().trim();
    if (!query) return items;
    return items.filter((item) =>
      item.name.toLowerCase().includes(query)
    );
  });

  let itemCount = $derived(filteredItems.length);
</script>

<input bind:value={searchQuery} placeholder="Search items..." />
<p>Showing {itemCount} items -- Total: ${totalCost.toFixed(2)}</p>
```

### $effect -- Side Effects

```svelte
<script lang="ts">
  let query = $state('');
  let results = $state<string[]>([]);

  // Runs when any referenced $state changes
  $effect(() => {
    if (query.length < 2) {
      results = [];
      return;
    }

    const controller = new AbortController();

    fetch(`/api/search?q=${encodeURIComponent(query)}`, {
      signal: controller.signal
    })
      .then((r) => r.json())
      .then((data) => { results = data; })
      .catch(() => {});

    // Cleanup function runs before re-execution and on destroy
    return () => controller.abort();
  });

  // Pre-effect: runs before DOM updates
  $effect.pre(() => {
    console.log('About to update DOM, query is:', query);
  });
</script>

<input bind:value={query} placeholder="Search..." />
<ul>
  {#each results as result}
    <li>{result}</li>
  {/each}
</ul>
```

### $props -- Component Props

```svelte
<!-- Button.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import type { HTMLButtonAttributes } from 'svelte/elements';

  interface Props extends HTMLButtonAttributes {
    variant?: 'primary' | 'secondary' | 'danger';
    loading?: boolean;
    children: Snippet;
  }

  let {
    variant = 'primary',
    loading = false,
    children,
    ...restProps
  }: Props = $props();
</script>

<button
  class="btn btn-{variant}"
  disabled={loading}
  {...restProps}
>
  {#if loading}
    <span class="spinner"></span>
  {/if}
  {@render children()}
</button>
```

### $bindable -- Two-Way Binding Props

```svelte
<!-- TextInput.svelte -->
<script lang="ts">
  interface Props {
    value: string;
    label: string;
    error?: string;
  }

  let { value = $bindable(), label, error }: Props = $props();
</script>

<label>
  {label}
  <input
    type="text"
    bind:value
    class:error={!!error}
  />
  {#if error}
    <span class="error-text">{error}</span>
  {/if}
</label>

<!-- Usage in parent -->
<!-- <TextInput bind:value={username} label="Username" /> -->
```

---

## 3. Components

### Component Composition with Snippets

Svelte 5 replaces slots with **snippets** for content projection.

```svelte
<!-- Card.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    title: string;
    header?: Snippet;
    children: Snippet;
    footer?: Snippet<[{ close: () => void }]>;
  }

  let { title, header, children, footer }: Props = $props();
  let visible = $state(true);

  function close() {
    visible = false;
  }
</script>

{#if visible}
  <div class="card">
    <div class="card-header">
      {#if header}
        {@render header()}
      {:else}
        <h2>{title}</h2>
      {/if}
    </div>

    <div class="card-body">
      {@render children()}
    </div>

    {#if footer}
      <div class="card-footer">
        {@render footer({ close })}
      </div>
    {/if}
  </div>
{/if}
```

```svelte
<!-- Usage -->
<Card title="User Profile">
  <p>Main content goes here.</p>

  {#snippet footer({ close })}
    <button onclick={close}>Dismiss</button>
  {/snippet}
</Card>
```

### Event Handling with Callback Props

```svelte
<!-- DataTable.svelte -->
<script lang="ts">
  interface Column<T> {
    key: keyof T;
    label: string;
    sortable?: boolean;
  }

  interface Props<T> {
    data: T[];
    columns: Column<T>[];
    onRowClick?: (row: T) => void;
    onSort?: (key: string, direction: 'asc' | 'desc') => void;
  }

  let { data, columns, onRowClick, onSort }: Props<Record<string, any>> = $props();

  let sortKey = $state('');
  let sortDir = $state<'asc' | 'desc'>('asc');

  function handleSort(key: string) {
    if (sortKey === key) {
      sortDir = sortDir === 'asc' ? 'desc' : 'asc';
    } else {
      sortKey = key;
      sortDir = 'asc';
    }
    onSort?.(sortKey, sortDir);
  }
</script>

<table>
  <thead>
    <tr>
      {#each columns as col}
        <th>
          {#if col.sortable}
            <button onclick={() => handleSort(String(col.key))}>
              {col.label} {sortKey === col.key ? (sortDir === 'asc' ? '↑' : '↓') : ''}
            </button>
          {:else}
            {col.label}
          {/if}
        </th>
      {/each}
    </tr>
  </thead>
  <tbody>
    {#each data as row}
      <tr onclick={() => onRowClick?.(row)} class:clickable={!!onRowClick}>
        {#each columns as col}
          <td>{row[col.key]}</td>
        {/each}
      </tr>
    {/each}
  </tbody>
</table>
```

### Context API for Dependency Injection

```svelte
<!-- ThemeProvider.svelte -->
<script lang="ts" module>
  import { setContext, getContext } from 'svelte';

  const THEME_KEY = Symbol('theme');

  export interface ThemeContext {
    current: string;
    toggle: () => void;
  }

  export function getTheme(): ThemeContext {
    return getContext(THEME_KEY);
  }
</script>

<script lang="ts">
  import type { Snippet } from 'svelte';

  let { children }: { children: Snippet } = $props();

  let theme = $state<'light' | 'dark'>('light');

  setContext(THEME_KEY, {
    get current() { return theme; },
    toggle() { theme = theme === 'light' ? 'dark' : 'light'; }
  });
</script>

<div class="theme-{theme}">
  {@render children()}
</div>
```

---

## 4. Reactivity and Stores

Svelte stores remain useful for sharing state across non-component modules and for interoperability.

### Writable and Derived Stores

```ts
// src/lib/stores/cart.ts
import { writable, derived } from 'svelte/store';

export interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
}

export const cart = writable<CartItem[]>([]);

export const cartTotal = derived(cart, ($cart) =>
  $cart.reduce((sum, item) => sum + item.price * item.quantity, 0)
);

export const cartCount = derived(cart, ($cart) =>
  $cart.reduce((sum, item) => sum + item.quantity, 0)
);

export function addToCart(item: Omit<CartItem, 'quantity'>) {
  cart.update((items) => {
    const existing = items.find((i) => i.id === item.id);
    if (existing) {
      existing.quantity++;
      return [...items];
    }
    return [...items, { ...item, quantity: 1 }];
  });
}

export function removeFromCart(id: string) {
  cart.update((items) => items.filter((i) => i.id !== id));
}
```

### Readable Store with External Source

```ts
// src/lib/stores/online.ts
import { readable } from 'svelte/store';

export const isOnline = readable(true, (set) => {
  const handleOnline = () => set(true);
  const handleOffline = () => set(false);

  if (typeof window !== 'undefined') {
    set(navigator.onLine);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }
});
```

### Using Stores in Svelte 5 Components

```svelte
<script lang="ts">
  import { cart, cartTotal, addToCart, removeFromCart } from '$stores/cart';

  // Access store value with the $ prefix in the template,
  // or subscribe manually in script for runes compatibility
  let items = $derived($cart);
  let total = $derived($cartTotal);
</script>

<h2>Cart ({items.length} items)</h2>
<ul>
  {#each items as item (item.id)}
    <li>
      {item.name} x{item.quantity} -- ${(item.price * item.quantity).toFixed(2)}
      <button onclick={() => removeFromCart(item.id)}>Remove</button>
    </li>
  {/each}
</ul>
<p><strong>Total: ${total.toFixed(2)}</strong></p>
```

---

## 5. Routing

### Basic Pages and Layouts

```svelte
<!-- src/routes/+layout.svelte (root layout) -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import '../app.css';

  let { children }: { children: Snippet } = $props();
</script>

<nav>
  <a href="/">Home</a>
  <a href="/about">About</a>
  <a href="/blog">Blog</a>
  <a href="/dashboard">Dashboard</a>
</nav>

<main>
  {@render children()}
</main>

<footer>
  <p>&copy; 2026 My SvelteKit App</p>
</footer>
```

### Dynamic Routes

```
src/routes/
├── blog/
│   ├── +page.svelte              # /blog
│   ├── +page.server.ts
│   ├── [slug]/
│   │   ├── +page.svelte          # /blog/my-post
│   │   └── +page.server.ts
│   └── category/
│       └── [category]/
│           ├── +page.svelte      # /blog/category/tech
│           └── +page.server.ts
├── users/
│   └── [id=integer]/             # Param matcher: /users/42
│       ├── +page.svelte
│       └── +page.server.ts
└── [[lang]]/                     # Optional param: / or /en or /fr
    └── +page.svelte
```

```ts
// src/params/integer.ts -- Parameter matcher
import type { ParamMatcher } from '@sveltejs/kit';

export const match: ParamMatcher = (param) => {
  return /^\d+$/.test(param);
};
```

### Route Groups and Layouts

```
src/routes/
├── (marketing)/           # Group: shared layout, no URL segment
│   ├── +layout.svelte     # Marketing layout (full-width, no sidebar)
│   ├── pricing/
│   │   └── +page.svelte   # /pricing
│   └── features/
│       └── +page.svelte   # /features
├── (app)/                 # Group: app layout with sidebar
│   ├── +layout.svelte     # App layout
│   ├── +layout.server.ts  # Auth check for all app routes
│   ├── dashboard/
│   │   └── +page.svelte   # /dashboard
│   └── settings/
│       └── +page.svelte   # /settings
└── +layout.svelte         # Root layout (wraps everything)
```

```svelte
<!-- src/routes/(app)/+layout.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import Sidebar from '$components/Sidebar.svelte';

  let { data, children }: { data: any; children: Snippet } = $props();
</script>

<div class="app-layout">
  <Sidebar user={data.user} />
  <div class="content">
    {@render children()}
  </div>
</div>
```

### Error and Loading Pages

```svelte
<!-- src/routes/+error.svelte -->
<script lang="ts">
  import { page } from '$app/stores';
</script>

<div class="error-page">
  <h1>{$page.status}</h1>
  <p>{$page.error?.message ?? 'Something went wrong'}</p>
  <a href="/">Return home</a>
</div>
```

---

## 6. Load Functions

### Page Server Load (+page.server.ts)

```ts
// src/routes/blog/+page.server.ts
import type { PageServerLoad } from './$types';
import { db } from '$server/database';

export const load: PageServerLoad = async ({ url, locals }) => {
  const page = Number(url.searchParams.get('page')) || 1;
  const limit = 10;
  const offset = (page - 1) * limit;

  const [posts, total] = await Promise.all([
    db.post.findMany({
      take: limit,
      skip: offset,
      orderBy: { createdAt: 'desc' },
      select: { id: true, title: true, slug: true, excerpt: true, createdAt: true }
    }),
    db.post.count()
  ]);

  return {
    posts,
    pagination: {
      page,
      totalPages: Math.ceil(total / limit),
      total
    }
  };
};
```

### Dynamic Route Load with Error Handling

```ts
// src/routes/blog/[slug]/+page.server.ts
import type { PageServerLoad } from './$types';
import { error } from '@sveltejs/kit';
import { db } from '$server/database';

export const load: PageServerLoad = async ({ params, locals }) => {
  const post = await db.post.findUnique({
    where: { slug: params.slug },
    include: {
      author: { select: { name: true, avatar: true } },
      comments: {
        orderBy: { createdAt: 'desc' },
        take: 20
      }
    }
  });

  if (!post) {
    error(404, { message: 'Post not found' });
  }

  if (!post.published && locals.user?.role !== 'admin') {
    error(403, { message: 'This post is not published' });
  }

  return { post };
};
```

### Universal Load (+page.ts) for Client-Side Data

```ts
// src/routes/search/+page.ts
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url, fetch }) => {
  const query = url.searchParams.get('q') ?? '';

  if (!query) {
    return { results: [], query };
  }

  // This fetch is isomorphic: runs on server during SSR, client on navigation
  const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
  const results = await response.json();

  return { results, query };
};
```

### Layout Server Load (Shared Data)

```ts
// src/routes/(app)/+layout.server.ts
import type { LayoutServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';

export const load: LayoutServerLoad = async ({ locals, url }) => {
  if (!locals.user) {
    redirect(303, `/auth/login?redirect=${encodeURIComponent(url.pathname)}`);
  }

  return {
    user: locals.user
  };
};
```

### Consuming Load Data in Components

```svelte
<!-- src/routes/blog/+page.svelte -->
<script lang="ts">
  import type { PageData } from './$types';
  import PostCard from '$components/PostCard.svelte';
  import Pagination from '$components/Pagination.svelte';

  let { data }: { data: PageData } = $props();
</script>

<svelte:head>
  <title>Blog | My App</title>
</svelte:head>

<h1>Blog</h1>

{#if data.posts.length === 0}
  <p>No posts found.</p>
{:else}
  <div class="posts-grid">
    {#each data.posts as post (post.id)}
      <PostCard {post} />
    {/each}
  </div>

  <Pagination
    currentPage={data.pagination.page}
    totalPages={data.pagination.totalPages}
  />
{/if}
```

---

## 7. Form Actions

### Server-Side Form Actions

```ts
// src/routes/blog/create/+page.server.ts
import type { Actions, PageServerLoad } from './$types';
import { fail, redirect } from '@sveltejs/kit';
import { db } from '$server/database';
import { z } from 'zod';

const PostSchema = z.object({
  title: z.string().min(3, 'Title must be at least 3 characters').max(200),
  content: z.string().min(10, 'Content must be at least 10 characters'),
  slug: z
    .string()
    .regex(/^[a-z0-9-]+$/, 'Slug must be lowercase alphanumeric with hyphens'),
  published: z.coerce.boolean().default(false)
});

export const load: PageServerLoad = async ({ locals }) => {
  if (!locals.user) {
    redirect(303, '/auth/login');
  }
  return {};
};

export const actions: Actions = {
  default: async ({ request, locals }) => {
    if (!locals.user) {
      return fail(401, { error: 'Unauthorized' });
    }

    const formData = await request.formData();
    const rawData = Object.fromEntries(formData);

    const parsed = PostSchema.safeParse(rawData);

    if (!parsed.success) {
      const fieldErrors = parsed.error.flatten().fieldErrors;
      return fail(400, {
        data: rawData,
        errors: fieldErrors
      });
    }

    const existingSlug = await db.post.findUnique({
      where: { slug: parsed.data.slug }
    });

    if (existingSlug) {
      return fail(400, {
        data: rawData,
        errors: { slug: ['This slug is already in use'] }
      });
    }

    const post = await db.post.create({
      data: {
        ...parsed.data,
        authorId: locals.user.id
      }
    });

    redirect(303, `/blog/${post.slug}`);
  }
};
```

### Progressive Enhancement Form Component

```svelte
<!-- src/routes/blog/create/+page.svelte -->
<script lang="ts">
  import { enhance } from '$app/forms';
  import type { ActionData } from './$types';

  let { form }: { form: ActionData } = $props();
  let submitting = $state(false);
</script>

<svelte:head>
  <title>Create Post</title>
</svelte:head>

<h1>Create New Post</h1>

<form
  method="POST"
  use:enhance={() => {
    submitting = true;
    return async ({ update }) => {
      submitting = false;
      await update();
    };
  }}
>
  <div class="field">
    <label for="title">Title</label>
    <input
      id="title"
      name="title"
      type="text"
      value={form?.data?.title ?? ''}
      required
    />
    {#if form?.errors?.title}
      <span class="error">{form.errors.title[0]}</span>
    {/if}
  </div>

  <div class="field">
    <label for="slug">Slug</label>
    <input
      id="slug"
      name="slug"
      type="text"
      value={form?.data?.slug ?? ''}
      required
    />
    {#if form?.errors?.slug}
      <span class="error">{form.errors.slug[0]}</span>
    {/if}
  </div>

  <div class="field">
    <label for="content">Content</label>
    <textarea
      id="content"
      name="content"
      rows="12"
      required
    >{form?.data?.content ?? ''}</textarea>
    {#if form?.errors?.content}
      <span class="error">{form.errors.content[0]}</span>
    {/if}
  </div>

  <div class="field">
    <label>
      <input name="published" type="checkbox" value="true" />
      Publish immediately
    </label>
  </div>

  <button type="submit" disabled={submitting}>
    {submitting ? 'Creating...' : 'Create Post'}
  </button>
</form>
```

### Named Actions (Multiple Actions per Page)

```ts
// src/routes/dashboard/settings/+page.server.ts
import type { Actions } from './$types';
import { fail, redirect } from '@sveltejs/kit';

export const actions: Actions = {
  updateProfile: async ({ request, locals }) => {
    const data = await request.formData();
    const name = data.get('name') as string;
    const bio = data.get('bio') as string;

    if (!name || name.length < 2) {
      return fail(400, { profileError: 'Name must be at least 2 characters' });
    }

    await db.user.update({
      where: { id: locals.user!.id },
      data: { name, bio }
    });

    return { profileSuccess: true };
  },

  changePassword: async ({ request, locals }) => {
    const data = await request.formData();
    const current = data.get('currentPassword') as string;
    const newPass = data.get('newPassword') as string;
    const confirm = data.get('confirmPassword') as string;

    if (newPass !== confirm) {
      return fail(400, { passwordError: 'Passwords do not match' });
    }

    if (newPass.length < 8) {
      return fail(400, { passwordError: 'Password must be at least 8 characters' });
    }

    // Verify current password and update...

    return { passwordSuccess: true };
  },

  deleteAccount: async ({ locals }) => {
    await db.user.delete({ where: { id: locals.user!.id } });
    redirect(303, '/');
  }
};
```

```svelte
<!-- Named actions are targeted via ?/ syntax -->
<form method="POST" action="?/updateProfile" use:enhance>
  <!-- profile fields -->
</form>

<form method="POST" action="?/changePassword" use:enhance>
  <!-- password fields -->
</form>

<form method="POST" action="?/deleteAccount" use:enhance>
  <button type="submit">Delete My Account</button>
</form>
```

---

## 8. API Routes

### RESTful Resource Endpoints

```ts
// src/routes/api/posts/+server.ts
import type { RequestHandler } from './$types';
import { json, error } from '@sveltejs/kit';
import { db } from '$server/database';
import { z } from 'zod';

// GET /api/posts?page=1&limit=10
export const GET: RequestHandler = async ({ url, locals }) => {
  const page = Number(url.searchParams.get('page')) || 1;
  const limit = Math.min(Number(url.searchParams.get('limit')) || 10, 100);

  const posts = await db.post.findMany({
    skip: (page - 1) * limit,
    take: limit,
    orderBy: { createdAt: 'desc' },
    where: { published: true }
  });

  return json({ data: posts, page, limit });
};

const CreatePostSchema = z.object({
  title: z.string().min(3).max(200),
  content: z.string().min(10),
  slug: z.string().regex(/^[a-z0-9-]+$/),
  published: z.boolean().default(false)
});

// POST /api/posts
export const POST: RequestHandler = async ({ request, locals }) => {
  if (!locals.user) {
    error(401, { message: 'Authentication required' });
  }

  const body = await request.json();
  const parsed = CreatePostSchema.safeParse(body);

  if (!parsed.success) {
    return json(
      { errors: parsed.error.flatten().fieldErrors },
      { status: 400 }
    );
  }

  const post = await db.post.create({
    data: { ...parsed.data, authorId: locals.user.id }
  });

  return json({ data: post }, { status: 201 });
};
```

```ts
// src/routes/api/posts/[id]/+server.ts
import type { RequestHandler } from './$types';
import { json, error } from '@sveltejs/kit';
import { db } from '$server/database';

// GET /api/posts/:id
export const GET: RequestHandler = async ({ params }) => {
  const post = await db.post.findUnique({ where: { id: params.id } });

  if (!post) {
    error(404, { message: 'Post not found' });
  }

  return json({ data: post });
};

// PUT /api/posts/:id
export const PUT: RequestHandler = async ({ params, request, locals }) => {
  if (!locals.user) {
    error(401, { message: 'Authentication required' });
  }

  const post = await db.post.findUnique({ where: { id: params.id } });

  if (!post) {
    error(404, { message: 'Post not found' });
  }

  if (post.authorId !== locals.user.id && locals.user.role !== 'admin') {
    error(403, { message: 'Not authorized to edit this post' });
  }

  const body = await request.json();
  const updated = await db.post.update({
    where: { id: params.id },
    data: body
  });

  return json({ data: updated });
};

// DELETE /api/posts/:id
export const DELETE: RequestHandler = async ({ params, locals }) => {
  if (!locals.user) {
    error(401, { message: 'Authentication required' });
  }

  const post = await db.post.findUnique({ where: { id: params.id } });

  if (!post) {
    error(404, { message: 'Post not found' });
  }

  if (post.authorId !== locals.user.id && locals.user.role !== 'admin') {
    error(403, { message: 'Forbidden' });
  }

  await db.post.delete({ where: { id: params.id } });

  return new Response(null, { status: 204 });
};
```

### Streaming and Server-Sent Events

```ts
// src/routes/api/events/+server.ts
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ locals }) => {
  if (!locals.user) {
    return new Response('Unauthorized', { status: 401 });
  }

  const stream = new ReadableStream({
    start(controller) {
      const encoder = new TextEncoder();

      const interval = setInterval(() => {
        const data = JSON.stringify({
          time: new Date().toISOString(),
          message: 'heartbeat'
        });
        controller.enqueue(encoder.encode(`data: ${data}\n\n`));
      }, 5000);

      // Clean up on close
      return () => clearInterval(interval);
    }
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      Connection: 'keep-alive'
    }
  });
};
```

---

## 9. Authentication Patterns

### Server Hooks for Session Management

```ts
// src/hooks.server.ts
import type { Handle } from '@sveltejs/kit';
import { db } from '$lib/server/database';

export const handle: Handle = async ({ event, resolve }) => {
  // Read session token from cookie
  const sessionToken = event.cookies.get('session');

  if (sessionToken) {
    const session = await db.session.findUnique({
      where: { token: sessionToken },
      include: { user: { select: { id: true, email: true, role: true } } }
    });

    if (session && session.expiresAt > new Date()) {
      event.locals.user = session.user;
    } else {
      // Expired session: clear the cookie
      event.cookies.delete('session', { path: '/' });
      event.locals.user = null;
    }
  } else {
    event.locals.user = null;
  }

  const response = await resolve(event);
  return response;
};
```

### Login and Logout

```ts
// src/routes/auth/login/+page.server.ts
import type { Actions } from './$types';
import { fail, redirect } from '@sveltejs/kit';
import { db } from '$server/database';
import { verifyPassword } from '$server/auth';
import { randomUUID } from 'crypto';

export const actions: Actions = {
  default: async ({ request, cookies, url }) => {
    const data = await request.formData();
    const email = (data.get('email') as string)?.trim().toLowerCase();
    const password = data.get('password') as string;

    if (!email || !password) {
      return fail(400, { error: 'Email and password are required', email });
    }

    const user = await db.user.findUnique({ where: { email } });

    if (!user || !(await verifyPassword(password, user.passwordHash))) {
      return fail(400, { error: 'Invalid email or password', email });
    }

    // Create session
    const token = randomUUID();
    const expiresAt = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000); // 30 days

    await db.session.create({
      data: { token, userId: user.id, expiresAt }
    });

    cookies.set('session', token, {
      path: '/',
      httpOnly: true,
      secure: true,
      sameSite: 'lax',
      maxAge: 30 * 24 * 60 * 60
    });

    const redirectTo = url.searchParams.get('redirect') ?? '/dashboard';
    redirect(303, redirectTo);
  }
};
```

```ts
// src/routes/auth/logout/+server.ts
import type { RequestHandler } from './$types';
import { redirect } from '@sveltejs/kit';
import { db } from '$server/database';

export const POST: RequestHandler = async ({ cookies, locals }) => {
  const sessionToken = cookies.get('session');

  if (sessionToken) {
    await db.session.delete({ where: { token: sessionToken } }).catch(() => {});
    cookies.delete('session', { path: '/' });
  }

  redirect(303, '/');
};
```

### Route Guards via Layout Load

```ts
// src/routes/(app)/+layout.server.ts
import type { LayoutServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';

export const load: LayoutServerLoad = async ({ locals, url }) => {
  if (!locals.user) {
    redirect(303, `/auth/login?redirect=${encodeURIComponent(url.pathname)}`);
  }

  return { user: locals.user };
};
```

### Role-Based Access Control

```ts
// src/routes/(app)/admin/+layout.server.ts
import type { LayoutServerLoad } from './$types';
import { error } from '@sveltejs/kit';

export const load: LayoutServerLoad = async ({ parent }) => {
  const { user } = await parent();

  if (user.role !== 'admin') {
    error(403, { message: 'Admin access required' });
  }

  return {};
};
```

### CSRF and Security Headers via Hooks

```ts
// src/hooks.server.ts (extended)
import type { Handle } from '@sveltejs/kit';
import { sequence } from '@sveltejs/kit/hooks';

const securityHeaders: Handle = async ({ event, resolve }) => {
  const response = await resolve(event);

  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set(
    'Permissions-Policy',
    'camera=(), microphone=(), geolocation=()'
  );

  return response;
};

const authHandle: Handle = async ({ event, resolve }) => {
  // ... session logic from above ...
  return resolve(event);
};

// Compose multiple hooks
export const handle = sequence(authHandle, securityHeaders);
```

---

## 10. Deployment

### adapter-node (Self-Hosted / Docker)

```js
// svelte.config.js
import adapter from '@sveltejs/adapter-node';

export default {
  kit: {
    adapter: adapter({
      out: 'build',
      precompress: true,       // Generate .gz and .br files
      envPrefix: 'APP_'        // Only expose APP_* env vars
    })
  }
};
```

```dockerfile
# Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
RUN npm prune --production

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/build ./build
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

ENV NODE_ENV=production
ENV PORT=3000
ENV ORIGIN=https://myapp.example.com
EXPOSE 3000
CMD ["node", "build"]
```

```bash
# Build and run
npm run build
PORT=3000 ORIGIN=https://myapp.example.com node build
```

### adapter-vercel (Serverless)

```js
// svelte.config.js
import adapter from '@sveltejs/adapter-vercel';

export default {
  kit: {
    adapter: adapter({
      runtime: 'nodejs20.x',
      regions: ['iad1'],
      split: false          // Single function for all routes
    })
  }
};
```

To configure specific routes for edge or serverless runtime:

```ts
// src/routes/api/fast-endpoint/+server.ts
export const config = {
  runtime: 'edge'       // This specific route runs on edge
};
```

### adapter-static (Static Site Generation)

```js
// svelte.config.js
import adapter from '@sveltejs/adapter-static';

export default {
  kit: {
    adapter: adapter({
      pages: 'build',
      assets: 'build',
      fallback: '404.html',  // SPA fallback page
      precompress: true
    }),
    prerender: {
      entries: ['*'],              // Prerender all discoverable routes
      handleHttpError: 'warn'      // Warn on broken links during prerender
    }
  }
};
```

For full static generation, disable SSR across the app:

```ts
// src/routes/+layout.ts
export const prerender = true;
export const ssr = false;    // Optional: disable SSR for pure SPA mode
```

### Environment Variables

```ts
// Access public env vars (available client and server)
import { PUBLIC_API_URL } from '$env/static/public';

// Access private env vars (server only)
import { DATABASE_URL, JWT_SECRET } from '$env/static/private';

// Dynamic env vars (read at runtime, not build time)
import { env } from '$env/dynamic/private';
const dbUrl = env.DATABASE_URL;
```

---

## Quick Reference

| Task                     | File                        | Key Exports / Patterns                     |
| ------------------------ | --------------------------- | ------------------------------------------ |
| Page UI                  | `+page.svelte`              | Component with `data` prop                 |
| Server data loading      | `+page.server.ts`           | `load` function                            |
| Client data loading      | `+page.ts`                  | `load` function (isomorphic fetch)         |
| Form mutations           | `+page.server.ts`           | `actions` object                           |
| API endpoints            | `+server.ts`                | `GET`, `POST`, `PUT`, `DELETE` handlers    |
| Shared layout data       | `+layout.server.ts`         | `load` function (inherited by children)    |
| Layout UI                | `+layout.svelte`            | Component with `children` snippet          |
| Middleware / auth        | `hooks.server.ts`           | `handle` function                          |
| Error page               | `+error.svelte`             | Access `$page.status` and `$page.error`    |
| Reactive state           | Component `<script>`        | `$state`, `$derived`, `$effect`            |
| Component props          | Component `<script>`        | `$props()`, `$bindable()`                  |
