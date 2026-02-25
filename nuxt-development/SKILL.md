---
name: nuxt-development
description: Nuxt 3 full-stack development covering auto-imports, file-based routing, server routes, composables, useFetch and useAsyncData, Nitro server engine, middleware, plugins, SEO with useHead, Pinia state, and deployment to various platforms.
---

# Nuxt Development

This skill should be used when building full-stack applications with Nuxt 3. It covers auto-imports, server routes, composables, data fetching, SEO, and deployment.

## When to Use This Skill

Use this skill when you need to:

- Build Vue.js applications with SSR/SSG
- Create API routes with Nitro server engine
- Implement data fetching with useFetch/useAsyncData
- Set up authentication and middleware
- Deploy to Vercel, Netlify, or Cloudflare

## File-Based Routing

```
pages/
├── index.vue           # /
├── about.vue           # /about
├── blog/
│   ├── index.vue       # /blog
│   └── [slug].vue      # /blog/:slug
├── users/
│   ├── [id].vue        # /users/:id
│   └── [...slug].vue   # /users/* (catch-all)
└── [[optional]].vue    # /optional or /
```

## Page Component

```vue
<!-- pages/blog/[slug].vue -->
<script setup lang="ts">
const route = useRoute();
const { data: post, error } = await useFetch(`/api/posts/${route.params.slug}`);

if (error.value) {
  throw createError({ statusCode: 404, message: "Post not found" });
}

useHead({
  title: post.value?.title,
  meta: [{ name: "description", content: post.value?.excerpt }],
});

useSeoMeta({
  ogTitle: post.value?.title,
  ogImage: post.value?.coverImage,
  twitterCard: "summary_large_image",
});
</script>

<template>
  <article v-if="post">
    <h1>{{ post.title }}</h1>
    <div v-html="post.content" />
  </article>
</template>
```

## Server Routes (Nitro)

```typescript
// server/api/posts/index.get.ts
export default defineEventHandler(async (event) => {
  const query = getQuery(event);
  const page = Number(query.page) || 1;
  const limit = Number(query.limit) || 10;

  const posts = await db.post.findMany({
    skip: (page - 1) * limit,
    take: limit,
    orderBy: { createdAt: "desc" },
  });

  return { posts, page, total: await db.post.count() };
});

// server/api/posts/index.post.ts
export default defineEventHandler(async (event) => {
  const body = await readBody(event);
  const session = await requireAuth(event);

  const post = await db.post.create({
    data: { ...body, authorId: session.userId },
  });

  return post;
});

// server/api/posts/[slug].get.ts
export default defineEventHandler(async (event) => {
  const slug = getRouterParam(event, "slug");
  const post = await db.post.findUnique({ where: { slug } });
  if (!post) throw createError({ statusCode: 404, message: "Not found" });
  return post;
});
```

## Composables

```typescript
// composables/useAuth.ts
export function useAuth() {
  const user = useState<User | null>("auth-user", () => null);
  const isAuthenticated = computed(() => !!user.value);

  async function login(email: string, password: string) {
    const data = await $fetch("/api/auth/login", {
      method: "POST",
      body: { email, password },
    });
    user.value = data.user;
    navigateTo("/dashboard");
  }

  async function logout() {
    await $fetch("/api/auth/logout", { method: "POST" });
    user.value = null;
    navigateTo("/login");
  }

  return { user, isAuthenticated, login, logout };
}
```

## Middleware

```typescript
// middleware/auth.ts
export default defineNuxtRouteMiddleware((to) => {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated.value) {
    return navigateTo(`/login?redirect=${to.fullPath}`);
  }
});
```

```vue
<!-- Usage in page -->
<script setup lang="ts">
definePageMeta({ middleware: "auth" });
</script>
```

## Pinia State Management

```typescript
// stores/cart.ts
export const useCartStore = defineStore("cart", () => {
  const items = ref<CartItem[]>([]);
  const total = computed(() => items.value.reduce((sum, item) => sum + item.price * item.qty, 0));

  function addItem(product: Product) {
    const existing = items.value.find((i) => i.id === product.id);
    if (existing) {
      existing.qty++;
    } else {
      items.value.push({ ...product, qty: 1 });
    }
  }

  function removeItem(id: string) {
    items.value = items.value.filter((i) => i.id !== id);
  }

  return { items, total, addItem, removeItem };
});
```

## Configuration

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  devtools: { enabled: true },
  modules: ["@pinia/nuxt", "@nuxt/image", "@nuxtjs/i18n"],
  runtimeConfig: {
    databaseUrl: "",  // NUXT_DATABASE_URL
    public: {
      apiBase: "/api",  // NUXT_PUBLIC_API_BASE
    },
  },
  app: {
    head: {
      title: "My App",
      meta: [{ name: "description", content: "My Nuxt app" }],
    },
  },
  nitro: {
    prerender: { routes: ["/", "/about"] },
  },
});
```

## CLI Commands

```bash
npx nuxi init my-app              # Create new project
npx nuxi dev                      # Start dev server
npx nuxi build                    # Production build
npx nuxi generate                 # Static generation
npx nuxi add page blog/[slug]     # Scaffold page
npx nuxi add composable useAuth   # Scaffold composable
npx nuxi add api posts            # Scaffold server route
```

## Additional Resources

- Nuxt 3 docs: https://nuxt.com/docs
- Nuxt modules: https://nuxt.com/modules
- Nitro: https://nitro.build/
