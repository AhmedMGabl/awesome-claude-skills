---
name: sveltekit-development
description: This skill should be used when building full-stack web applications with SvelteKit and Svelte 5. It covers runes-based reactivity, component patterns, routing, load functions, form actions, server routes, layouts, error handling, stores, SSR/CSR, and deployment.
---

# SvelteKit Development

## Reactive Declarations (Svelte 5 Runes)

```svelte
<script lang="ts">
  let count = $state(0);                                // reactive primitive
  let items = $state<string[]>([]);                     // deep reactive array
  let total = $derived(items.length);                   // computed value
  let label = $derived.by(() => `${total} items`);      // computed with block body
  $effect(() => {                                       // side effect + auto cleanup
    const ctrl = new AbortController();
    fetch(`/api/data?q=${count}`, { signal: ctrl.signal })
      .then((r) => r.json()).then((d) => { items = d; });
    return () => ctrl.abort();
  });
</script>
<button onclick={() => count++}>{count} - {label}</button>
```

## Components
```svelte
<!-- Button.svelte: typed props, snippets, rest spreading -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import type { HTMLButtonAttributes } from 'svelte/elements';
  interface Props extends HTMLButtonAttributes { variant?: 'primary' | 'secondary'; children: Snippet; }
  let { variant = 'primary', children, ...rest }: Props = $props();
</script>
<button class="btn-{variant}" {...rest}>{@render children()}</button>

<!-- Two-way binding with $bindable and callback props -->
<script lang="ts">
  let { value = $bindable(''), onsubmit }: { value?: string; onsubmit?: (v: string) => void } = $props();
</script>
<input bind:value />
<button onclick={() => onsubmit?.(value)}>Go</button>
```

## Load Functions
```typescript
// +page.server.ts: server-only (access DB, secrets, locals)
import { error, redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
export const load: PageServerLoad = async ({ locals, url, depends }) => {
  if (!locals.user) redirect(303, '/login');
  depends('app:dashboard');
  const [stats, orders] = await Promise.all([
    db.getStats(locals.user.id), db.getOrders(locals.user.id, { page: +(url.searchParams.get('page') ?? 1) })
  ]);
  return { stats, orders };
};
// +page.ts: universal load (runs on server during SSR, on client during navigation)
import type { PageLoad } from './$types';
export const load: PageLoad = async ({ params, fetch }) => {
  const res = await fetch(`/api/posts/${params.slug}`);
  if (!res.ok) error(404, { message: 'Not found' });
  return { post: await res.json() };
};
```

## Form Actions
```typescript
// src/routes/todos/+page.server.ts
import { fail } from '@sveltejs/kit';
import type { Actions } from './$types';
export const actions: Actions = {
  create: async ({ request, locals }) => {
    if (!locals.user) return fail(401, { error: 'Unauthorized' });
    const title = ((await request.formData()).get('title') as string)?.trim();
    if (!title) return fail(400, { error: 'Title required', title });
    await db.createTodo({ title, userId: locals.user.id });
  },
  delete: async ({ request, locals }) => {
    await db.deleteTodo((await request.formData()).get('id') as string, locals.user!.id);
  }
};
```

```svelte
<!-- +page.svelte: progressive enhancement with use:enhance -->
<script lang="ts">
  import { enhance } from '$app/forms';
  let { data, form }: { data: PageData; form: ActionData } = $props();
</script>
<form method="POST" action="?/create" use:enhance>
  <input name="title" value={form?.title ?? ''} required />
  {#if form?.error}<p class="error">{form.error}</p>{/if}
  <button>Add</button>
</form>
```

## Server Routes (+server.ts)
```typescript
import { json, error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
export const GET: RequestHandler = async ({ url, locals }) => {
  if (!locals.user) error(401, { message: 'Unauthorized' });
  return json(await db.getUsers({ page: +(url.searchParams.get('page') ?? 1) }));
};
export const POST: RequestHandler = async ({ request, locals }) => {
  if (!locals.user) error(401, { message: 'Unauthorized' });
  return json(await db.createUser(await request.json()), { status: 201 });
};
export const DELETE: RequestHandler = async ({ params }) => {
  await db.deleteUser(params.id);
  return new Response(null, { status: 204 });
};
```

## Layouts and Error Handling

```svelte
<!-- src/routes/+layout.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import { page } from '$app/state';
  let { data, children }: { data: LayoutData; children: Snippet } = $props();
</script>
<nav>
  <a href="/" class:active={page.url.pathname === '/'}>Home</a>
  {#if data.user}<span>{data.user.email}</span>{/if}
</nav>
<main>{@render children()}</main>

<!-- src/routes/+error.svelte -->
<script lang="ts">
  import { page } from '$app/state';
</script>
<h1>{page.status}</h1>
<p>{page.error?.message ?? 'Something went wrong'}</p>
```

## Hooks
```typescript
// src/hooks.server.ts
import type { Handle, HandleServerError } from '@sveltejs/kit';
import { sequence } from '@sveltejs/kit/hooks';
const auth: Handle = async ({ event, resolve }) => {
  const sid = event.cookies.get('session');
  event.locals.user = sid ? await db.getUserBySession(sid) : null;
  return resolve(event);
};
const security: Handle = async ({ event, resolve }) => {
  const res = await resolve(event);
  res.headers.set('X-Frame-Options', 'DENY');
  return res;
};
export const handle = sequence(auth, security);
export const handleError: HandleServerError = async ({ error, event }) => {
  console.error(`${event.request.method} ${event.url.pathname}:`, error);
  return { message: 'An unexpected error occurred' };
};
```

## Stores and Shared State
```typescript
// src/lib/stores/cart.svelte.ts (rune-based shared reactive module)
interface CartItem { id: string; name: string; price: number; qty: number; }
function createCart() {
  let items = $state<CartItem[]>([]);
  const total = $derived(items.reduce((s, i) => s + i.price * i.qty, 0));
  return {
    get items() { return items; }, get total() { return total; },
    add(p: Omit<CartItem, 'qty'>) {
      const e = items.find((i) => i.id === p.id);
      e ? e.qty++ : items.push({ ...p, qty: 1 });
    },
    clear() { items.length = 0; }
  };
}
export const cart = createCart();
```

## SSR/CSR and Deployment

```typescript
// Per-route rendering in +page.ts: export const prerender = true; export const ssr = false;
// svelte.config.js
import adapter from '@sveltejs/adapter-auto'; // auto-detects Vercel, Netlify, Cloudflare
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
export default { preprocess: vitePreprocess(), kit: { adapter: adapter() } };
// Node/Docker: @sveltejs/adapter-node  -> adapter({ out: 'build', precompress: true })
// Vercel:      @sveltejs/adapter-vercel -> adapter({ runtime: 'nodejs22.x' })
```

## Additional Resources

- SvelteKit Docs: https://svelte.dev/docs/kit
- Svelte 5 Runes: https://svelte.dev/docs/svelte/$state
- SvelteKit Routing: https://svelte.dev/docs/kit/routing
- SvelteKit Form Actions: https://svelte.dev/docs/kit/form-actions
- SvelteKit Hooks: https://svelte.dev/docs/kit/hooks
- Svelte Tutorial: https://svelte.dev/tutorial
