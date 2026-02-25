---
name: sveltekit-development
description: SvelteKit full-stack development covering Svelte 5 runes, component patterns, routing, load functions, form actions, server-side rendering, API endpoints, authentication, deployment adapters, and production-ready patterns.
---

# SvelteKit Development

This skill should be used when building full-stack web applications with SvelteKit. It covers Svelte 5 runes reactivity, component architecture, file-based routing, server-side data loading, form actions, API endpoints, authentication, hooks, state management, styling, deployment, and testing.

## When to Use This Skill

Use this skill when you need to:

- Scaffold and structure SvelteKit projects
- Build reactive components with Svelte 5 runes ($state, $derived, $effect, $props)
- Implement file-based routing with layouts, groups, and dynamic segments
- Write load functions for server-side and universal data fetching
- Handle forms with progressive enhancement and validation
- Create REST API endpoints with +server.ts files
- Implement authentication with cookies, sessions, and route guards
- Configure hooks for request interception, error handling, and fetch customization
- Deploy with adapter-auto, adapter-node, or adapter-vercel
- Test applications with Vitest and Playwright

---

## 1. Project Setup

### Scaffold with sv

```bash
npx sv create my-app
# Select: SvelteKit minimal, TypeScript, Tailwind CSS, Prettier, ESLint, Vitest, Playwright
cd my-app && npm install && npm run dev
```

### Directory Structure

```
my-app/
├── src/
│   ├── app.html                  # HTML shell template
│   ├── app.css                   # Global styles
│   ├── app.d.ts                  # App-level type declarations
│   ├── hooks.server.ts           # Server hooks (handle, handleError, handleFetch)
│   ├── hooks.client.ts           # Client hooks (handleError)
│   ├── lib/
│   │   ├── components/           # Reusable components
│   │   │   ├── ui/               # Primitives (Button, Input, Modal)
│   │   │   └── features/         # Feature-specific components
│   │   ├── server/               # Server-only modules ($lib/server/*)
│   │   │   ├── db.ts             # Database client
│   │   │   └── auth.ts           # Auth utilities
│   │   ├── stores/               # Shared state (Svelte stores)
│   │   ├── utils/                # Helper functions
│   │   └── types/                # Shared TypeScript types
│   │       └── index.ts
│   ├── params/                   # Param matchers for routes
│   │   └── integer.ts
│   └── routes/
│       ├── +layout.svelte        # Root layout
│       ├── +layout.server.ts     # Root layout server load
│       ├── +page.svelte          # Home page
│       ├── +page.server.ts       # Home page server load + actions
│       ├── +error.svelte         # Error page
│       ├── (auth)/               # Route group (no URL segment)
│       │   ├── login/+page.svelte
│       │   └── register/+page.svelte
│       ├── dashboard/
│       │   ├── +layout.svelte
│       │   ├── +layout.server.ts
│       │   ├── +page.svelte
│       │   └── [id]/+page.svelte # Dynamic route
│       └── api/
│           └── users/+server.ts  # API endpoint
├── static/                       # Static assets (favicon, robots.txt)
├── tests/                        # Playwright e2e tests
├── svelte.config.js
├── vite.config.ts
└── tsconfig.json
```

### svelte.config.js

```javascript
import adapter from '@sveltejs/adapter-auto';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter(),
    alias: {
      $components: 'src/lib/components',
      $stores: 'src/lib/stores',
      $utils: 'src/lib/utils'
    },
    csrf: {
      checkOrigin: true
    }
  }
};

export default config;
```

### vite.config.ts

```typescript
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [sveltekit()],
  test: {
    include: ['src/**/*.{test,spec}.{js,ts}']
  },
  server: {
    port: 5173,
    proxy: {
      '/external-api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/external-api/, '')
      }
    }
  }
});
```

### app.d.ts

```typescript
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
      user: App.Locals['user'];
    }
    interface PageState {
      showModal?: boolean;
    }
    interface Platform {}
  }
}

export {};
```

---

## 2. Svelte 5 Runes

### $state: Reactive State

```svelte
<script lang="ts">
  let count = $state(0);
  let name = $state('');

  // Object state (deeply reactive)
  let user = $state({
    name: 'Alice',
    email: 'alice@example.com',
    preferences: { theme: 'dark', locale: 'en' }
  });

  // Array state (deeply reactive -- push, splice, etc. all trigger updates)
  let items = $state<string[]>([]);

  function addItem(item: string) {
    items.push(item); // Mutating directly works with $state
  }

  function updateTheme(theme: string) {
    user.preferences.theme = theme; // Deep mutation triggers reactivity
  }
</script>

<p>Count: {count}</p>
<button onclick={() => count++}>Increment</button>

<input bind:value={name} placeholder="Name" />
<p>Hello, {name || 'stranger'}</p>

<button onclick={() => addItem('New item')}>Add Item</button>
<ul>
  {#each items as item, i}
    <li>{i + 1}. {item}</li>
  {/each}
</ul>
```

### $state.raw: Non-Deep Reactive State

```svelte
<script lang="ts">
  // Use $state.raw for large datasets where deep reactivity is unnecessary.
  // Only reassignment triggers updates, not mutation.
  let rows = $state.raw<Array<{ id: number; value: string }>>([]);

  function replaceRows(newRows: typeof rows) {
    rows = newRows; // Triggers update
  }
</script>
```

### $derived: Computed Values

```svelte
<script lang="ts">
  let items = $state([
    { name: 'Apple', price: 1.5, quantity: 3 },
    { name: 'Banana', price: 0.75, quantity: 5 }
  ]);
  let taxRate = $state(0.08);

  let totalItems = $derived(items.reduce((sum, i) => sum + i.quantity, 0));

  // Derived with complex logic using $derived.by
  let orderSummary = $derived.by(() => {
    const subtotal = items.reduce((sum, i) => sum + i.price * i.quantity, 0);
    const tax = subtotal * taxRate;
    const total = subtotal + tax;
    return { subtotal, tax, total };
  });
</script>

<p>Items in cart: {totalItems}</p>
<p>Subtotal: ${orderSummary.subtotal.toFixed(2)}</p>
<p>Tax: ${orderSummary.tax.toFixed(2)}</p>
<p>Total: ${orderSummary.total.toFixed(2)}</p>
```

### $effect: Side Effects

```svelte
<script lang="ts">
  let query = $state('');
  let results = $state<string[]>([]);

  // $effect runs after DOM update whenever tracked dependencies change.
  $effect(() => {
    if (query.length < 2) {
      results = [];
      return;
    }

    const controller = new AbortController();

    fetch(`/api/search?q=${encodeURIComponent(query)}`, { signal: controller.signal })
      .then((r) => r.json())
      .then((data) => { results = data; })
      .catch(() => {});

    // Cleanup runs before the next effect execution and on destroy
    return () => controller.abort();
  });

  // $effect.pre runs before DOM update (rare -- use for measuring DOM before paint)
  let container: HTMLDivElement;
  $effect.pre(() => {
    if (container) {
      console.log('Height before update:', container.scrollHeight);
    }
  });
</script>

<input bind:value={query} placeholder="Search..." />
<ul>
  {#each results as result}
    <li>{result}</li>
  {/each}
</ul>
<div bind:this={container}>Content</div>
```

### $props and $bindable: Component Props

```svelte
<!-- Counter.svelte -->
<script lang="ts">
  interface Props {
    initialCount?: number;
    step?: number;
    count?: number;
    onchange?: (count: number) => void;
    label: string;
  }

  let {
    initialCount = 0,
    step = 1,
    count = $bindable(initialCount),
    onchange,
    label
  }: Props = $props();

  function increment() {
    count += step;
    onchange?.(count);
  }

  function decrement() {
    count -= step;
    onchange?.(count);
  }
</script>

<div class="counter">
  <span>{label}: {count}</span>
  <button onclick={decrement}>-{step}</button>
  <button onclick={increment}>+{step}</button>
</div>
```

```svelte
<!-- Usage with bind -->
<script lang="ts">
  import Counter from '$components/Counter.svelte';
  let value = $state(10);
</script>

<Counter label="Quantity" bind:count={value} step={5} />
<p>Parent sees: {value}</p>

<Counter label="Independent" onchange={(c) => console.log('Changed:', c)} />
```

### $inspect: Debug Reactive Values

```svelte
<script lang="ts">
  let count = $state(0);
  let doubled = $derived(count * 2);

  // Development only, stripped in production
  $inspect(count, doubled);

  $inspect(count).with((type, value) => {
    if (type === 'update') console.log('Count updated to:', value);
  });
</script>
```

---

## 3. Component Patterns

### Snippets (Replacing Slots in Svelte 5)

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
  let isOpen = $state(true);

  function close() { isOpen = false; }
</script>

{#if isOpen}
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
  {#snippet header()}
    <h2 class="text-xl font-bold">Custom Header</h2>
  {/snippet}

  <p>This is the card body content.</p>

  {#snippet footer(props)}
    <button onclick={props.close}>Dismiss</button>
  {/snippet}
</Card>
```

### Events and Callback Props

```svelte
<!-- SearchInput.svelte -->
<script lang="ts">
  interface Props {
    value?: string;
    placeholder?: string;
    onsearch?: (query: string) => void;
    onclear?: () => void;
  }

  let { value = $bindable(''), placeholder = 'Search...', onsearch, onclear }: Props = $props();

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter') onsearch?.(value);
  }

  function clear() {
    value = '';
    onclear?.();
  }
</script>

<div class="search-input">
  <input type="text" bind:value {placeholder} onkeydown={handleKeydown} />
  {#if value}
    <button onclick={clear} aria-label="Clear search">x</button>
  {/if}
</div>
```

### Context API

```svelte
<!-- ThemeProvider.svelte -->
<script lang="ts" module>
  import { setContext, getContext } from 'svelte';

  const THEME_KEY = Symbol('theme');

  export interface ThemeContext {
    theme: string;
    toggleTheme: () => void;
  }

  export function setThemeContext(ctx: ThemeContext) {
    setContext(THEME_KEY, ctx);
  }

  export function getThemeContext(): ThemeContext {
    return getContext<ThemeContext>(THEME_KEY);
  }
</script>

<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    initialTheme?: 'light' | 'dark';
    children: Snippet;
  }

  let { initialTheme = 'light', children }: Props = $props();
  let theme = $state(initialTheme);

  function toggleTheme() {
    theme = theme === 'light' ? 'dark' : 'light';
  }

  setThemeContext({
    get theme() { return theme; },
    toggleTheme
  });
</script>

<div class="app" data-theme={theme}>
  {@render children()}
</div>
```

### Spreading Props and HTML Attributes

```svelte
<!-- Button.svelte -->
<script lang="ts">
  import type { HTMLButtonAttributes } from 'svelte/elements';

  interface Props extends HTMLButtonAttributes {
    variant?: 'primary' | 'secondary' | 'danger';
    loading?: boolean;
    children: import('svelte').Snippet;
  }

  let { variant = 'primary', loading = false, children, ...rest }: Props = $props();
</script>

<button class="btn btn-{variant}" disabled={loading || rest.disabled} {...rest}>
  {#if loading}
    <span class="spinner" aria-hidden="true"></span> Loading...
  {:else}
    {@render children()}
  {/if}
</button>
```

---

## 4. Routing

### Basic Routes

```
src/routes/
├── +page.svelte                    # /
├── about/+page.svelte              # /about
├── blog/
│   ├── +page.svelte                # /blog
│   └── [slug]/+page.svelte         # /blog/:slug
├── users/
│   ├── +page.svelte                # /users
│   └── [id=integer]/+page.svelte   # /users/:id (with param matcher)
└── docs/[...path]/+page.svelte     # /docs/* (catch-all)
```

### Param Matchers

```typescript
// src/params/integer.ts
import type { ParamMatcher } from '@sveltejs/kit';

export const match: ParamMatcher = (param) => {
  return /^\d+$/.test(param);
};
```

### Layouts

```svelte
<!-- src/routes/+layout.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import { page } from '$app/state';

  interface Props {
    data: import('./$types').LayoutData;
    children: Snippet;
  }

  let { data, children }: Props = $props();
</script>

<nav>
  <a href="/" class:active={page.url.pathname === '/'}>Home</a>
  <a href="/dashboard" class:active={page.url.pathname.startsWith('/dashboard')}>Dashboard</a>
  {#if data.user}
    <span>{data.user.email}</span>
    <form method="POST" action="/logout">
      <button type="submit">Sign out</button>
    </form>
  {:else}
    <a href="/login">Sign in</a>
  {/if}
</nav>

<main>{@render children()}</main>
```

### Route Groups

```
src/routes/
├── (marketing)/              # Group: no /marketing in URL
│   ├── +layout.svelte
│   ├── +page.svelte          # /
│   └── pricing/+page.svelte  # /pricing
├── (app)/                    # Group: no /app in URL
│   ├── +layout.server.ts     # Auth guard for all app pages
│   ├── dashboard/+page.svelte  # /dashboard
│   └── settings/+page.svelte   # /settings
└── (auth)/                   # Group: no /auth in URL
    ├── login/+page.svelte    # /login
    └── register/+page.svelte # /register
```

### Navigation

```svelte
<script lang="ts">
  import { goto, invalidate, invalidateAll } from '$app/navigation';

  async function navigateToDashboard() {
    await goto('/dashboard');
  }

  async function navigateWithOptions() {
    await goto('/dashboard', {
      replaceState: true,
      noScroll: true,
      invalidateAll: true
    });
  }

  async function refreshUserData() {
    await invalidate('app:user');
    await invalidate('/api/users');
  }
</script>

<a href="/dashboard" data-sveltekit-preload-data="hover">Dashboard</a>
<a href="/external" data-sveltekit-reload>Full Page Load</a>
```

### Error Pages

```svelte
<!-- src/routes/+error.svelte -->
<script lang="ts">
  import { page } from '$app/state';
</script>

<h1>{page.status}</h1>
<p>{page.error?.message ?? 'Something went wrong'}</p>
{#if page.status === 404}
  <a href="/">Go back home</a>
{:else}
  <button onclick={() => location.reload()}>Try again</button>
{/if}
```

---

## 5. Load Functions

### Server Load (+page.server.ts)

```typescript
// src/routes/dashboard/+page.server.ts
import { error, redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { db } from '$lib/server/db';

export const load: PageServerLoad = async ({ locals, depends, url }) => {
  if (!locals.user) redirect(303, '/login');

  depends('app:dashboard');

  const page = Number(url.searchParams.get('page') ?? '1');

  try {
    const [stats, recentOrders] = await Promise.all([
      db.getDashboardStats(locals.user.id),
      db.getRecentOrders(locals.user.id, { page, limit: 20 })
    ]);

    return { stats, recentOrders };
  } catch (err) {
    console.error('Dashboard load failed:', err);
    error(500, { message: 'Failed to load dashboard data' });
  }
};
```

### Universal Load (+page.ts)

```typescript
// src/routes/blog/[slug]/+page.ts
import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';

// Runs on both server (SSR) and client (navigation).
export const load: PageLoad = async ({ params, fetch }) => {
  const response = await fetch(`/api/posts/${params.slug}`);

  if (!response.ok) {
    error(response.status, { message: 'Post not found' });
  }

  return { post: await response.json() };
};
```

### Layout Server Load

```typescript
// src/routes/+layout.server.ts
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals }) => {
  return { user: locals.user };
};
```

### Streaming with Promises

```typescript
// src/routes/dashboard/+page.server.ts
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
  return {
    user: locals.user,
    quickStats: await db.getQuickStats(locals.user!.id),
    // These resolve later -- SvelteKit streams them to the client
    recentActivity: db.getRecentActivity(locals.user!.id),
    recommendations: db.getRecommendations(locals.user!.id)
  };
};
```

```svelte
<!-- Consuming streamed data -->
<script lang="ts">
  let { data }: { data: PageData } = $props();
</script>

<h1>Welcome, {data.user?.email}</h1>

{#await data.recentActivity}
  <p>Loading recent activity...</p>
{:then activity}
  <ul>
    {#each activity as item}
      <li>{item.description}</li>
    {/each}
  </ul>
{:catch error}
  <p>Failed to load: {error.message}</p>
{/await}
```

---

## 6. Form Actions

### Default and Named Actions

```typescript
// src/routes/todos/+page.server.ts
import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { db } from '$lib/server/db';
import { z } from 'zod';

const CreateTodoSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200),
  description: z.string().max(1000).optional()
});

export const load: PageServerLoad = async ({ locals }) => {
  if (!locals.user) redirect(303, '/login');
  return { todos: await db.getTodos(locals.user.id) };
};

export const actions: Actions = {
  default: async ({ request, locals }) => {
    if (!locals.user) return fail(401, { error: 'Unauthorized' });

    const formData = await request.formData();
    const data = {
      title: formData.get('title') as string,
      description: formData.get('description') as string | undefined
    };

    const result = CreateTodoSchema.safeParse(data);
    if (!result.success) {
      return fail(400, {
        error: 'Validation failed',
        fields: data,
        errors: result.error.flatten().fieldErrors
      });
    }

    await db.createTodo({ ...result.data, userId: locals.user.id });
  },

  delete: async ({ request, locals }) => {
    if (!locals.user) return fail(401, { error: 'Unauthorized' });
    const id = (await request.formData()).get('id') as string;
    if (!id) return fail(400, { error: 'Missing todo ID' });
    await db.deleteTodo(id, locals.user.id);
  },

  toggle: async ({ request, locals }) => {
    if (!locals.user) return fail(401, { error: 'Unauthorized' });
    const id = (await request.formData()).get('id') as string;
    await db.toggleTodo(id, locals.user.id);
  }
};
```

### Form with Progressive Enhancement

```svelte
<!-- src/routes/todos/+page.svelte -->
<script lang="ts">
  import { enhance } from '$app/forms';
  import type { ActionData, PageData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();
  let isSubmitting = $state(false);
</script>

<form
  method="POST"
  use:enhance={() => {
    isSubmitting = true;
    return async ({ update, result }) => {
      isSubmitting = false;
      await update({ reset: result.type === 'success' });
    };
  }}
>
  <label for="title">Title</label>
  <input id="title" name="title" required value={form?.fields?.title ?? ''} />
  {#if form?.errors?.title}
    <p class="error">{form.errors.title[0]}</p>
  {/if}

  <button type="submit" disabled={isSubmitting}>
    {isSubmitting ? 'Adding...' : 'Add Todo'}
  </button>
</form>

<ul>
  {#each data.todos as todo}
    <li>
      <form method="POST" action="?/toggle" use:enhance>
        <input type="hidden" name="id" value={todo.id} />
        <button type="submit" class:completed={todo.completed}>{todo.title}</button>
      </form>
      <form method="POST" action="?/delete" use:enhance>
        <input type="hidden" name="id" value={todo.id} />
        <button type="submit">Delete</button>
      </form>
    </li>
  {/each}
</ul>
```

---

## 7. API Endpoints (+server.ts)

### RESTful CRUD

```typescript
// src/routes/api/users/+server.ts
import { json, error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { db } from '$lib/server/db';
import { z } from 'zod';

const CreateUserSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email()
});

export const GET: RequestHandler = async ({ url, locals }) => {
  if (!locals.user) error(401, { message: 'Unauthorized' });

  const page = Number(url.searchParams.get('page') ?? '1');
  const limit = Math.min(Number(url.searchParams.get('limit') ?? '20'), 100);

  const { users, total } = await db.getUsers({ page, limit });

  return json({ users, pagination: { page, limit, total } });
};

export const POST: RequestHandler = async ({ request, locals }) => {
  if (!locals.user || locals.user.role !== 'admin') {
    error(403, { message: 'Forbidden' });
  }

  const body = await request.json();
  const result = CreateUserSchema.safeParse(body);

  if (!result.success) {
    return json(
      { error: 'Validation failed', details: result.error.flatten().fieldErrors },
      { status: 400 }
    );
  }

  const user = await db.createUser(result.data);
  return json(user, { status: 201 });
};
```

```typescript
// src/routes/api/users/[id]/+server.ts
import { json, error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ params, locals }) => {
  if (!locals.user) error(401, { message: 'Unauthorized' });
  const user = await db.getUser(params.id);
  if (!user) error(404, { message: 'User not found' });
  return json(user);
};

export const PATCH: RequestHandler = async ({ params, request, locals }) => {
  if (!locals.user || locals.user.role !== 'admin') error(403, { message: 'Forbidden' });
  const updates = await request.json();
  return json(await db.updateUser(params.id, updates));
};

export const DELETE: RequestHandler = async ({ params, locals }) => {
  if (!locals.user || locals.user.role !== 'admin') error(403, { message: 'Forbidden' });
  await db.deleteUser(params.id);
  return new Response(null, { status: 204 });
};
```

### Streaming Responses (Server-Sent Events)

```typescript
// src/routes/api/stream/+server.ts
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async () => {
  const stream = new ReadableStream({
    async start(controller) {
      const encoder = new TextEncoder();
      for (let i = 0; i < 10; i++) {
        const data = JSON.stringify({ count: i, timestamp: Date.now() });
        controller.enqueue(encoder.encode(`data: ${data}\n\n`));
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
      controller.enqueue(encoder.encode('data: [DONE]\n\n'));
      controller.close();
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

## 8. Hooks

### Server Hooks (hooks.server.ts)

```typescript
// src/hooks.server.ts
import type { Handle, HandleFetch, HandleServerError } from '@sveltejs/kit';
import { sequence } from '@sveltejs/kit/hooks';
import { db } from '$lib/server/db';

const authHandle: Handle = async ({ event, resolve }) => {
  const sessionId = event.cookies.get('session');
  if (sessionId) {
    try {
      const session = await db.getSession(sessionId);
      if (session && session.expiresAt > new Date()) {
        event.locals.user = { id: session.userId, email: session.email, role: session.role };
      } else {
        event.cookies.delete('session', { path: '/' });
      }
    } catch {
      event.locals.user = null;
    }
  } else {
    event.locals.user = null;
  }
  return resolve(event);
};

const securityHandle: Handle = async ({ event, resolve }) => {
  const response = await resolve(event);
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  return response;
};

export const handle = sequence(authHandle, securityHandle);

export const handleFetch: HandleFetch = async ({ request, fetch, event }) => {
  if (request.url.startsWith('https://api.internal.example.com')) {
    request.headers.set('Authorization', `Bearer ${event.locals.user?.id ?? ''}`);
  }
  return fetch(request);
};

export const handleError: HandleServerError = async ({ error, event, status }) => {
  const errorId = crypto.randomUUID();
  console.error(`[${errorId}] ${event.request.method} ${event.url.pathname}:`, error);
  return {
    message: status === 404 ? 'Page not found' : 'An unexpected error occurred',
    code: errorId
  };
};
```

### Client Hooks (hooks.client.ts)

```typescript
// src/hooks.client.ts
import type { HandleClientError } from '@sveltejs/kit';

export const handleError: HandleClientError = async ({ error, status }) => {
  const errorId = crypto.randomUUID();
  console.error(`[Client ${errorId}]:`, error);
  return {
    message: status === 404 ? 'Page not found' : 'Something went wrong',
    code: errorId
  };
};
```

---

## 9. Authentication Patterns

### Cookie-Based Session Authentication

```typescript
// src/lib/server/auth.ts
import { db } from '$lib/server/db';
import bcrypt from 'bcrypt';
import crypto from 'node:crypto';

const SESSION_DURATION_MS = 7 * 24 * 60 * 60 * 1000;

export async function createSession(userId: string) {
  const sessionId = crypto.randomUUID();
  const expiresAt = new Date(Date.now() + SESSION_DURATION_MS);
  await db.createSession({ id: sessionId, userId, expiresAt });
  return { sessionId, expiresAt };
}

export async function verifyCredentials(email: string, password: string) {
  const user = await db.getUserByEmail(email);
  if (!user) return null;
  const valid = await bcrypt.compare(password, user.passwordHash);
  if (!valid) return null;
  return { id: user.id, email: user.email, role: user.role };
}

export async function invalidateSession(sessionId: string) {
  await db.deleteSession(sessionId);
}
```

```typescript
// src/routes/login/+page.server.ts
import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { createSession, verifyCredentials } from '$lib/server/auth';

export const load: PageServerLoad = async ({ locals }) => {
  if (locals.user) redirect(303, '/dashboard');
};

export const actions: Actions = {
  default: async ({ request, cookies }) => {
    const formData = await request.formData();
    const email = (formData.get('email') as string)?.trim();
    const password = formData.get('password') as string;

    if (!email || !password) {
      return fail(400, { email, error: 'Email and password are required' });
    }

    const user = await verifyCredentials(email, password);
    if (!user) {
      return fail(401, { email, error: 'Invalid email or password' });
    }

    const { sessionId, expiresAt } = await createSession(user.id);

    cookies.set('session', sessionId, {
      path: '/',
      httpOnly: true,
      secure: true,
      sameSite: 'lax',
      expires: expiresAt
    });

    redirect(303, '/dashboard');
  }
};
```

### Route Guards and Role-Based Access

```typescript
// src/lib/server/guards.ts
import { error } from '@sveltejs/kit';
import type { RequestEvent } from '@sveltejs/kit';

export function requireAuth(event: RequestEvent) {
  if (!event.locals.user) error(401, { message: 'Authentication required' });
  return event.locals.user;
}

export function requireRole(event: RequestEvent, role: 'admin' | 'user') {
  const user = requireAuth(event);
  if (user.role !== role) error(403, { message: 'Insufficient permissions' });
  return user;
}
```

```typescript
// src/routes/(app)/+layout.server.ts
import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals, url }) => {
  if (!locals.user) {
    redirect(303, `/login?redirectTo=${encodeURIComponent(url.pathname)}`);
  }
  return { user: locals.user };
};
```

---

## 10. Stores and State Management

### Svelte Stores

```typescript
// src/lib/stores/theme.ts
import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

type Theme = 'light' | 'dark' | 'system';

function createThemeStore() {
  const stored = browser ? (localStorage.getItem('theme') as Theme) : null;
  const { subscribe, set, update } = writable<Theme>(stored ?? 'system');

  return {
    subscribe,
    set(value: Theme) {
      set(value);
      if (browser) localStorage.setItem('theme', value);
    },
    toggle() {
      update((current) => {
        const next = current === 'light' ? 'dark' : 'light';
        if (browser) localStorage.setItem('theme', next);
        return next;
      });
    }
  };
}

export const theme = createThemeStore();

export const resolvedTheme = derived(theme, ($theme) => {
  if ($theme !== 'system') return $theme;
  if (!browser) return 'light';
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
});
```

### Rune-Based Shared State (.svelte.ts)

```typescript
// src/lib/stores/cart.svelte.ts
interface CartItem { id: string; name: string; price: number; quantity: number; }

function createCart() {
  let items = $state<CartItem[]>([]);

  const total = $derived(items.reduce((sum, i) => sum + i.price * i.quantity, 0));
  const itemCount = $derived(items.reduce((sum, i) => sum + i.quantity, 0));

  function addItem(product: Omit<CartItem, 'quantity'>) {
    const existing = items.find((i) => i.id === product.id);
    if (existing) existing.quantity++;
    else items.push({ ...product, quantity: 1 });
  }

  function removeItem(id: string) {
    const idx = items.findIndex((i) => i.id === id);
    if (idx !== -1) items.splice(idx, 1);
  }

  function updateQuantity(id: string, qty: number) {
    if (qty <= 0) { removeItem(id); return; }
    const item = items.find((i) => i.id === id);
    if (item) item.quantity = qty;
  }

  function clear() { items.length = 0; }

  return {
    get items() { return items; },
    get total() { return total; },
    get itemCount() { return itemCount; },
    addItem, removeItem, updateQuantity, clear
  };
}

export const cart = createCart();
```

---

## 11. Styling

### Scoped Styles

```svelte
<button class="btn {variant}">
  <slot />
</button>

<style>
  .btn {
    padding: 0.5rem 1rem;
    border-radius: 0.375rem;
    font-weight: 600;
    cursor: pointer;
  }
  .btn :global(svg) { width: 1em; height: 1em; }
</style>
```

### CSS Custom Properties

```svelte
<style>
  :global(:root) {
    --color-primary: #3b82f6;
    --color-background: #ffffff;
    --color-text: #1f2937;
    --color-border: #e5e7eb;
  }
  :global([data-theme='dark']) {
    --color-background: #111827;
    --color-text: #f9fafb;
    --color-border: #374151;
  }
</style>
```

### Tailwind CSS

```bash
npx sv add tailwindcss
```

```svelte
<script lang="ts">
  import type { Snippet } from 'svelte';
  let { variant = 'primary', children }: { variant?: string; children: Snippet } = $props();

  const classes: Record<string, string> = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
    danger: 'bg-red-600 text-white hover:bg-red-700'
  };
</script>

<button class="px-4 py-2 rounded-md font-medium transition-colors {classes[variant]}">
  {@render children()}
</button>
```

### Dynamic Classes

```svelte
<script lang="ts">
  let active = $state(false);
  let size = $state<'sm' | 'md' | 'lg'>('md');
</script>

<div class="card size-{size}" class:active>Content</div>
```

---

## 12. Deployment

### adapter-auto (Recommended Default)

```javascript
import adapter from '@sveltejs/adapter-auto';
const config = { kit: { adapter: adapter() } };
export default config;
```

### adapter-node (Docker)

```bash
npm install -D @sveltejs/adapter-node
```

```javascript
import adapter from '@sveltejs/adapter-node';
const config = {
  kit: {
    adapter: adapter({ out: 'build', precompress: true, envPrefix: 'APP_' })
  }
};
export default config;
```

```dockerfile
FROM node:22-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build && npm prune --production

FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup -S sk && adduser -S sk -G sk
COPY --from=builder --chown=sk:sk /app/build ./build
COPY --from=builder --chown=sk:sk /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
USER sk
EXPOSE 3000
CMD ["node", "build"]
```

### adapter-vercel

```bash
npm install -D @sveltejs/adapter-vercel
```

```javascript
import adapter from '@sveltejs/adapter-vercel';
const config = {
  kit: { adapter: adapter({ runtime: 'nodejs22.x', regions: ['iad1'] }) }
};
export default config;
```

### Prerendering and SSR

```typescript
// src/routes/about/+page.ts
export const prerender = true;   // Static at build time

// src/routes/dashboard/+page.ts
export const ssr = false;        // Client-only rendering

// src/routes/+layout.ts (full static site)
export const prerender = true;
export const trailingSlash = 'never';
```

---

## 13. Testing

### Unit Tests with Vitest

```typescript
// src/lib/utils/format.test.ts
import { describe, it, expect } from 'vitest';
import { formatCurrency, slugify } from './format';

describe('formatCurrency', () => {
  it('formats USD', () => expect(formatCurrency(1234.56)).toBe('$1,234.56'));
  it('formats zero', () => expect(formatCurrency(0)).toBe('$0.00'));
});

describe('slugify', () => {
  it('converts to kebab-case', () => expect(slugify('Hello World')).toBe('hello-world'));
  it('removes special chars', () => expect(slugify('Hello! World?')).toBe('hello-world'));
});
```

### Component Tests with @testing-library/svelte

```typescript
// src/lib/components/Counter.test.ts
import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import Counter from './Counter.svelte';

describe('Counter', () => {
  it('renders with initial count', () => {
    render(Counter, { props: { label: 'Items', initialCount: 5 } });
    expect(screen.getByText('Items: 5')).toBeInTheDocument();
  });

  it('increments on click', async () => {
    render(Counter, { props: { label: 'Items', step: 1 } });
    await fireEvent.click(screen.getByText('+1'));
    expect(screen.getByText('Items: 1')).toBeInTheDocument();
  });
});
```

### End-to-End Tests with Playwright

```typescript
// tests/auth.test.ts
import { expect, test } from '@playwright/test';

test.describe('Authentication', () => {
  test('login page renders', async ({ page }) => {
    await page.goto('/login');
    await expect(page.getByRole('heading', { name: 'Sign In' })).toBeVisible();
  });

  test('invalid credentials show error', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel('Email').fill('bad@example.com');
    await page.getByLabel('Password').fill('wrong');
    await page.getByRole('button', { name: 'Sign In' }).click();
    await expect(page.getByText('Invalid email or password')).toBeVisible();
  });

  test('protected route redirects', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/login/);
  });
});
```

### Playwright Configuration

```typescript
// playwright.config.ts
import type { PlaywrightTestConfig } from '@playwright/test';

const config: PlaywrightTestConfig = {
  webServer: {
    command: 'npm run build && npm run preview',
    port: 4173,
    reuseExistingServer: !process.env.CI
  },
  testDir: 'tests',
  use: { baseURL: 'http://localhost:4173' }
};

export default config;
```

---

## Quick Reference

| Task | Pattern |
|---|---|
| Reactive state | `let x = $state(value)` |
| Computed value | `let y = $derived(expr)` or `$derived.by(() => {...})` |
| Side effect | `$effect(() => { ...; return cleanup })` |
| Component props | `let { a, b = default }: Props = $props()` |
| Two-way binding | `let { value = $bindable() } = $props()` |
| Children content | `children: Snippet` + `{@render children()}` |
| Named snippet | `footer?: Snippet<[{ data: T }]>` + `{@render footer({data})}` |
| Shared state (runes) | `.svelte.ts` file with `$state`, export getters |
| Shared state (stores) | `writable()` in `.ts`, `$store` in templates |
| Server load | `+page.server.ts` exports `load` |
| Universal load | `+page.ts` exports `load` |
| Form actions | `+page.server.ts` exports `actions` |
| Progressive enhance | `use:enhance` on `<form>` |
| API endpoint | `+server.ts` exports `GET`/`POST`/`PATCH`/`DELETE` |
| Auth guard | `redirect(303, '/login')` in layout server load |
| Hooks | `hooks.server.ts` exports `handle`/`handleFetch`/`handleError` |
| Combine hooks | `sequence(h1, h2)` from `@sveltejs/kit/hooks` |
| Prerender | `export const prerender = true` in `+page.ts` |
| Disable SSR | `export const ssr = false` in `+page.ts` |

## File Naming

- Components: PascalCase.svelte (UserCard.svelte)
- Rune modules: name.svelte.ts (cart.svelte.ts)
- Store modules: name.ts (theme.ts)
- Route files: +page.svelte, +page.ts, +page.server.ts, +layout.svelte, +server.ts, +error.svelte
- Param matchers: lowercase.ts in src/params/
- Hooks: hooks.server.ts, hooks.client.ts in src/

## Dependency Versions (as of 2026)

```json
{
  "@sveltejs/kit": "^2",
  "svelte": "^5",
  "@sveltejs/vite-plugin-svelte": "^4",
  "@sveltejs/adapter-auto": "^3",
  "@sveltejs/adapter-node": "^5",
  "@sveltejs/adapter-vercel": "^5",
  "vite": "^6",
  "vitest": "^2",
  "@testing-library/svelte": "^5",
  "@playwright/test": "^1.49",
  "typescript": "^5.6"
}
```

## Additional Resources

- SvelteKit Docs: https://svelte.dev/docs/kit
- Svelte 5 Runes: https://svelte.dev/docs/svelte/$state
- SvelteKit Routing: https://svelte.dev/docs/kit/routing
- SvelteKit Form Actions: https://svelte.dev/docs/kit/form-actions
- SvelteKit Hooks: https://svelte.dev/docs/kit/hooks
- Svelte Tutorial: https://svelte.dev/tutorial
