---
name: vuejs-development
description: Vue.js development covering Composition API, reactive state, Pinia store, Vue Router, TypeScript integration, component patterns, composables, testing with Vitest, and production-ready patterns with Nuxt.js.
---

# Vue.js Development

Apply this skill for all Vue.js development tasks: building components, managing state, routing,
writing tests, and deploying Nuxt.js applications. Use TypeScript throughout unless the project
explicitly opts out.

---

## 1. Project Setup

### Scaffold with create-vue

```bash
npm create vue@latest my-app
# Select: TypeScript, JSX, Vue Router, Pinia, Vitest, ESLint, Prettier
cd my-app && npm install && npm run dev
```

### vite.config.ts

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': { target: 'http://localhost:8080', changeOrigin: true },
    },
  },
  build: {
    target: 'esnext',
    rollupOptions: {
      output: { manualChunks: { vendor: ['vue', 'vue-router', 'pinia'] } },
    },
  },
})
```

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ESNext",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "jsx": "preserve",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "lib": ["ESNext", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "noEmit": true,
    "baseUrl": ".",
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### src/main.ts

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from '@/router'
import App from '@/App.vue'
import '@/assets/main.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
```

---

## 2. Composition API

### ref, reactive, computed, watch, watchEffect

```vue
<script setup lang="ts">
import { ref, reactive, computed, watch, watchEffect, onMounted, onUnmounted } from 'vue'

// ref: primitives and objects
const count = ref(0)
const message = ref<string>("")

// reactive: plain objects (no .value in template)
const form = reactive({ username: "", email: "", age: 0 })

// computed: derived, cached, lazy
const doubled = computed(() => count.value * 2)
const isValid = computed(() => form.username.length >= 3 && form.email.includes('@'))

// writable computed
const fullName = computed({
  get: () => form.username,
  set: (val: string) => { form.username = val },
})

// watch: explicit source, callback after each change
watch(count, (newVal, oldVal) => {
  console.log("count changed:", oldVal, "->", newVal)
})

// watch multiple sources
watch([() => form.username, () => form.email], ([username, email]) => {
  console.log("form changed", username, email)
}, { deep: false, immediate: false })

// deep watch for nested objects
const config = ref({ theme: 'dark', locale: 'en' })
watch(config, (newConfig) => {
  localStorage.setItem('config', JSON.stringify(newConfig))
}, { deep: true })

// watchEffect: auto-tracks deps, runs immediately
watchEffect(() => {
  document.title = "Count: " + count.value
})

onMounted(() => console.log("mounted"))
onUnmounted(() => console.log("unmounted -- clean up here"))

function increment() { count.value++ }
</script>

<template>
  <div>
    <p>Count: {{ count }} | Doubled: {{ doubled }}</p>
    <button @click="increment">+1</button>
    <input v-model="form.username" placeholder="Username" />
    <p v-if="isValid" class="text-green-600">Form is valid</p>
  </div>
</template>
```

### toRef, toRefs, readonly

```typescript
import { reactive, toRef, toRefs, readonly } from 'vue'

const state = reactive({ x: 0, y: 0, label: 'origin' })

// toRef: single reactive ref linked to a reactive property
const x = toRef(state, 'x')
x.value = 10  // mutates state.x

// toRefs: destructure without losing reactivity
const { y, label } = toRefs(state)
y.value = 5   // mutates state.y

// readonly: immutable view -- mutations throw at runtime
const immutable = readonly(state)
// immutable.x = 1  // TypeError
```

---

## 3. Component Patterns

### defineProps, defineEmits, defineExpose

```vue
<!-- src/components/UserCard.vue -->
<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  userId: number
  name: string
  email: string
  role?: 'admin' | 'user' | 'moderator'
  avatarUrl?: string
}

const props = withDefaults(defineProps<Props>(), {
  role: 'user',
  avatarUrl: '/default-avatar.png',
})

const emit = defineEmits<{
  select: [userId: number]
  delete: [userId: number, confirm: boolean]
  'update:name': [value: string]
}>()

const isExpanded = ref(false)
const displayName = computed(() => props.name.trim() || 'Anonymous')

function handleSelect() { emit("select", props.userId) }
function handleDelete() {
  if (confirm("Delete " + props.name + "?")) emit("delete", props.userId, true)
}

// Expose public surface to parent via template ref
defineExpose({ isExpanded, displayName })
</script>

<template>
  <div class="user-card" @click="handleSelect">
    <img :src="avatarUrl" :alt="displayName" />
    <h3>{{ displayName }}</h3>
    <span class="badge">{{ role }}</span>
    <button @click.stop="isExpanded = !isExpanded">Details</button>
    <div v-if="isExpanded" class="details">
      <p>{{ email }}</p>
      <button @click.stop="handleDelete">Delete</button>
    </div>
  </div>
</template>
```

### Slots: default, named, scoped

```vue
<!-- src/components/DataTable.vue -->
<script setup lang="ts">
interface Column { key: string; label: string; sortable?: boolean }
interface Props { rows: Record<string, unknown>[]; columns: Column[]; loading?: boolean }
defineProps<Props>()
</script>

<template>
  <div class="data-table">
    <!-- Named slot: toolbar -->
    <div class="toolbar"><slot name="toolbar" /></div>

    <table v-if="!loading">
      <thead>
        <tr>
          <th v-for="col in columns" :key="col.key">
            <!-- Scoped slot: exposes column to parent -->
            <slot name="header" :column="col">{{ col.label }}</slot>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, i) in rows" :key="i">
          <td v-for="col in columns" :key="col.key">
            <!-- Scoped slot: exposes row, column, and cell value -->
            <slot name="cell" :row="row" :column="col" :value="row[col.key]">
              {{ row[col.key] }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="loading"><slot name="loading"><span>Loading...</span></slot></div>
    <slot />
  </div>
</template>
```

```vue
<!-- DataTable usage with scoped slots -->
<DataTable :rows="users" :columns="cols">
  <template #toolbar>
    <input v-model="search" placeholder="Search..." />
  </template>
  <template #cell="{ column, value }">
    <span v-if="column.key === 'status'" :class="value === 'active' ? 'green' : 'red'">
      {{ value }}
    </span>
    <span v-else>{{ value }}</span>
  </template>
</DataTable>
```

### Teleport and Suspense

```vue
<!-- Teleport: render at body level to escape stacking context -->
<script setup lang="ts">
import { ref } from 'vue'
const showModal = ref(false)
</script>
<template>
  <button @click="showModal = true">Open Modal</button>
  <Teleport to="body">
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <slot />
        <button @click="showModal = false">Close</button>
      </div>
    </div>
  </Teleport>
</template>
```

```vue
<!-- AsyncProfile.vue: async setup works inside Suspense -->
<script setup lang="ts">
const user = await fetch('/api/user/1').then(r => r.json())
</script>
<template><div>{{ user.name }}</div></template>
```

```vue
<!-- Parent wraps async component with Suspense -->
<Suspense>
  <template #default><AsyncProfile /></template>
  <template #fallback><div class="skeleton">Loading profile...</div></template>
</Suspense>
```

---

## 4. Composables

### useLocalStorage

```typescript
// src/composables/useLocalStorage.ts
import { ref, watch } from 'vue'

export function useLocalStorage<T>(key: string, defaultValue: T) {
  const stored = localStorage.getItem(key)
  const initial: T = stored ? (JSON.parse(stored) as T) : defaultValue
  const value = ref<T>(initial)

  watch(value, (newVal) => {
    if (newVal === null || newVal === undefined) localStorage.removeItem(key)
    else localStorage.setItem(key, JSON.stringify(newVal))
  }, { deep: true })

  function reset() { value.value = defaultValue }
  return { value, reset }
}

// const { value: theme, reset: resetTheme } = useLocalStorage('theme', 'light')
```

### useFetch

```typescript
// src/composables/useFetch.ts
import { ref, shallowRef, toValue, watchEffect, type MaybeRefOrGetter } from 'vue'

interface UseFetchOptions { immediate?: boolean; headers?: Record<string, string> }

export function useFetch<T = unknown>(
  url: MaybeRefOrGetter<string>,
  options: UseFetchOptions = {},
) {
  const { immediate = true, headers = {} } = options
  const data = shallowRef<T | null>(null)
  const error = ref<Error | null>(null)
  const loading = ref(false)
  let controller: AbortController | null = null

  async function execute() {
    controller?.abort()
    controller = new AbortController()
    loading.value = true
    error.value = null
    try {
      const response = await fetch(toValue(url), {
        signal: controller.signal,
        headers: { 'Content-Type': 'application/json', ...headers },
      })
      if (!response.ok)
        throw new Error("HTTP " + response.status + ": " + response.statusText)
      data.value = (await response.json()) as T
    } catch (err) {
      if ((err as Error).name !== 'AbortError')
        error.value = err instanceof Error ? err : new Error(String(err))
    } finally { loading.value = false }
  }

  if (immediate) watchEffect(() => { void execute() })
  return { data, error, loading, execute }
}

// const { data: users, loading, error } = useFetch<User[]>('/api/users')
// const { data, execute: refresh } = useFetch<Post>(() => '/api/posts/' + postId.value)
```

### useEventListener

```typescript
// src/composables/useEventListener.ts
import { onMounted, onUnmounted, toValue, type MaybeRefOrGetter } from 'vue'

export function useEventListener(
  target: MaybeRefOrGetter<EventTarget | null>,
  event: string,
  handler: EventListener,
  options?: AddEventListenerOptions,
) {
  onMounted(() => { toValue(target)?.addEventListener(event, handler, options) })
  onUnmounted(() => { toValue(target)?.removeEventListener(event, handler, options) })
}

// useEventListener(window, 'resize', () => { width.value = window.innerWidth })
// useEventListener(document, 'keydown', (e) => {
//   if ((e as KeyboardEvent).key === 'Escape') closeModal()
// })
```

### useDebounce

```typescript
// src/composables/useDebounce.ts
import { ref, watch, type Ref } from 'vue'

export function useDebounce<T>(source: Ref<T>, delay = 300): Ref<T> {
  const debounced = ref<T>(source.value) as Ref<T>
  let timer: ReturnType<typeof setTimeout>
  watch(source, (value) => {
    clearTimeout(timer)
    timer = setTimeout(() => { debounced.value = value }, delay)
  })
  return debounced
}

// const search = ref('')
// const debouncedSearch = useDebounce(search, 400)
// watch(debouncedSearch, (q) => fetchResults(q))
```

---

## 5. Pinia Store

### Setup store (recommended)

```typescript
// src/stores/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface User { id: number; name: string; email: string; roles: string[] }

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters (computed properties)
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.roles.includes('admin') ?? false)
  const displayName = computed(() => user.value?.name ?? 'Guest')

  async function login(payload: { email: string; password: string }) {
    loading.value = true
    error.value = null
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!res.ok) throw new Error('Invalid credentials')
      const data = await res.json() as { user: User; token: string }
      user.value = data.user
      token.value = data.token
      localStorage.setItem('token', data.token)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Login failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchProfile() {
    if (!token.value) return
    try {
      const res = await fetch('/api/auth/me', {
        headers: { Authorization: "Bearer " + token.value },
      })
      if (!res.ok) throw new Error('Unauthorized')
      user.value = await res.json() as User
    } catch { logout() }
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  return {
    user, token, loading, error,
    isAuthenticated, isAdmin, displayName,
    login, fetchProfile, logout,
  }
})
```

### Options store style

```typescript
// src/stores/cart.ts
import { defineStore } from 'pinia'

interface CartItem { id: number; name: string; price: number; quantity: number }

export const useCartStore = defineStore('cart', {
  state: () => ({ items: [] as CartItem[], couponCode: null as string | null }),

  getters: {
    itemCount: (state) => state.items.reduce((acc, i) => acc + i.quantity, 0),
    subtotal: (state) => state.items.reduce((acc, i) => acc + i.price * i.quantity, 0),
    total(): number {
      const discount = this.couponCode === 'SAVE10' ? 0.1 : 0
      return this.subtotal * (1 - discount)
    },
  },

  actions: {
    addItem(item: Omit<CartItem, "quantity">) {
      const existing = this.items.find((i) => i.id === item.id)
      if (existing) existing.quantity++
      else this.items.push({ ...item, quantity: 1 })
    },
    removeItem(id: number) {
      this.items = this.items.filter((i) => i.id !== id)
    },
    updateQuantity(id: number, quantity: number) {
      const item = this.items.find((i) => i.id === id)
      if (item) { if (quantity <= 0) this.removeItem(id); else item.quantity = quantity }
    },
    clearCart() { this.$reset() },
  },
})
```

### Pinia plugin for persistence

```typescript
// src/plugins/piniaPersist.ts
import type { PiniaPluginContext } from 'pinia'

interface PersistOptions { persist?: boolean | { key?: string; pick?: string[] } }

export function persistPlugin({ store, options }: PiniaPluginContext) {
  const persist = (options as PersistOptions).persist
  if (!persist) return
  const config = typeof persist === "object" ? persist : {}
  const storageKey = config.key ?? "pinia-" + store.$id
  const saved = localStorage.getItem(storageKey)
  if (saved) store.$patch(JSON.parse(saved) as Record<string, unknown>)
  store.$subscribe((_mutation, state) => {
    const toSave = config.pick
      ? Object.fromEntries(config.pick.map((k) => [k, (state as Record<string, unknown>)[k]]))
      : state
    localStorage.setItem(storageKey, JSON.stringify(toSave))
  })
}

// Register in main.ts:
// const pinia = createPinia()
// pinia.use(persistPlugin)
```

---

## 6. Vue Router

### createRouter, guards, lazy routes, route meta

```typescript
// src/router/index.ts
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    requiresAdmin?: boolean
    title?: string
    layout?: 'default' | 'auth' | 'dashboard'
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
    meta: { title: 'Home', layout: 'default' },
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { title: 'Login', layout: 'auth' },
    beforeEnter: (_to, _from, next) => {
      const auth = useAuthStore()
      if (auth.isAuthenticated) next({ name: 'dashboard' })
      else next()
    },
  },
  {
    path: '/dashboard',
    component: () => import('@/layouts/DashboardLayout.vue'),
    meta: { requiresAuth: true, layout: 'dashboard' },
    children: [
      {
        path: '',
        name: 'dashboard',
        component: () => import('@/views/DashboardView.vue'),
        meta: { title: 'Dashboard' },
      },
      {
        path: 'users',
        name: 'users',
        component: () => import('@/views/UsersView.vue'),
        meta: { title: 'Users', requiresAdmin: true },
      },
      {
        path: 'users/:id',
        name: 'user-detail',
        component: () => import('@/views/UserDetailView.vue'),
        props: true,
        meta: { title: 'User Detail' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { title: '404 Not Found' },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, _from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.hash) return { el: to.hash, behavior: 'smooth' }
    return { top: 0 }
  },
})

// Global navigation guard
router.beforeEach(async (to, _from, next) => {
  const auth = useAuthStore()
  document.title = to.meta.title ? to.meta.title + ' | MyApp' : 'MyApp'
  if (to.meta.requiresAuth && !auth.isAuthenticated)
    return next({ name: 'login', query: { redirect: to.fullPath } })
  if (to.meta.requiresAdmin && !auth.isAdmin)
    return next({ name: 'dashboard' })
  next()
})

// After-hook: analytics page tracking
router.afterEach((to) => {
  window.analytics?.page(to.name as string)
})

export default router
```

### Programmatic navigation

```typescript
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// Read params and query string
const userId = route.params.id as string
const page = Number(route.query.page ?? 1)

// Navigate declaratively
await router.push({ name: 'user-detail', params: { id: 42 } })
router.replace({ name: 'home' })
router.back()

// Redirect to intended page after login
const redirect = route.query.redirect as string | undefined
await router.push(redirect ?? { name: 'dashboard' })
```

---

## 7. TypeScript Integration

### Typed provide/inject with InjectionKey

```typescript
// src/composables/useTheme.ts
import { provide, inject, ref, type InjectionKey, type Ref } from 'vue'

type Theme = 'light' | 'dark'
interface ThemeContext { theme: Ref<Theme>; toggle: () => void }
const ThemeKey: InjectionKey<ThemeContext> = Symbol("theme")

export function provideTheme() {
  const theme = ref<Theme>((localStorage.getItem('theme') as Theme) ?? 'light')
  function toggle() {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    localStorage.setItem('theme', theme.value)
    document.documentElement.classList.toggle('dark', theme.value === 'dark')
  }
  provide(ThemeKey, { theme, toggle })
  return { theme, toggle }
}

export function useTheme(): ThemeContext {
  const ctx = inject(ThemeKey)
  if (!ctx) throw new Error("useTheme must be inside a component that called provideTheme()")
  return ctx
}
```

### Typed component instance via template ref

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import UserCard from '@/components/UserCard.vue'

// Ref typed to match the component defineExpose surface
const cardRef = ref<InstanceType<typeof UserCard> | null>(null)

onMounted(() => {
  console.log(cardRef.value?.displayName)  // string
  console.log(cardRef.value?.isExpanded)   // boolean
})
</script>

<template>
  <UserCard ref="cardRef" :user-id="1" name="Alice" email="alice@example.com" />
</template>
```

### Generic components

```vue
<!-- src/components/SelectInput.vue -->
<script setup lang="ts" generic="T extends { id: number; label: string }">
interface Props { options: T[]; modelValue: T | null }
const props = defineProps<Props>()
const emit = defineEmits<{ 'update:modelValue': [value: T] }>()
function select(option: T) { emit("update:modelValue", option) }
</script>

<template>
  <select
    @change="select(options.find(o => o.id === Number(($event.target as HTMLSelectElement).value))!)"
  >
    <option
      v-for="opt in options"
      :key="opt.id"
      :value="opt.id"
      :selected="modelValue?.id === opt.id"
    >
      {{ opt.label }}
    </option>
  </select>
</template>
```

### v-model with custom components

```vue
<!-- BaseInput.vue -->
<script setup lang="ts">
defineProps<{ modelValue: string; label?: string }>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()
</script>
<template>
  <div>
    <label v-if="label">{{ label }}</label>
    <input
      :value="modelValue"
      @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
  </div>
</template>
```

```vue
<!-- Multiple v-model bindings -->
<script setup lang="ts">
defineProps<{ firstName: string; lastName: string }>()
defineEmits<{ 'update:firstName': [string]; 'update:lastName': [string] }>()
</script>

<!-- Parent usage: -->
<!-- <NameInput v-model:first-name="user.first" v-model:last-name="user.last" /> -->
```

---

## 8. Testing with Vitest + Vue Test Utils

### vitest.config.ts

```typescript
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      exclude: ['src/test/**'],
    },
  },
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
})
```

### src/test/setup.ts

```typescript
import { config } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach } from 'vitest'

beforeEach(() => { setActivePinia(createPinia()) })

config.global.stubs = {
  RouterLink: { template: '<a><slot /></a>' },
  RouterView: { template: '<div />' },
}
```

### Component unit test

```typescript
// src/components/__tests__/UserCard.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import UserCard from '@/components/UserCard.vue'

describe('UserCard', () => {
  const props = { userId: 1, name: "Alice Smith", email: "alice@example.com", role: "admin" as const }
  it('renders name and role badge', () => {
    const w = mount(UserCard, { props })
    expect(w.text()).toContain("Alice Smith")
    expect(w.find(".badge").text()).toBe("admin")
  })
  it('emits select with userId on card click', async () => {
    const w = mount(UserCard, { props })
    await w.trigger('click')
    expect(w.emitted("select")).toEqual([[1]])
  })
  it('toggles expanded on Details click', async () => {
    const w = mount(UserCard, { props })
    expect(w.find(".details").exists()).toBe(false)
    await w.find('button').trigger('click')
    expect(w.find(".details").exists()).toBe(true)
  })
  it('exposes isExpanded and displayName', () => {
    const w = mount(UserCard, { props })
    expect(w.vm.isExpanded).toBe(false)
    expect(w.vm.displayName).toBe("Alice Smith")
  })
  it('uses default avatarUrl when not provided', () => {
    const w = mount(UserCard, { props })
    expect(w.find("img").attributes("src")).toBe("/default-avatar.png")
  })
})
```

### Pinia store test

```typescript
// src/stores/__tests__/auth.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'

describe('useAuthStore', () => {
  beforeEach(() => { setActivePinia(createPinia()); localStorage.clear() })
  it('starts unauthenticated', () => {
    const auth = useAuthStore()
    expect(auth.isAuthenticated).toBe(false)
    expect(auth.user).toBeNull()
  })
  it('login sets user and token', async () => {
    const mockUser = { id: 1, name: 'Alice', email: 'alice@example.com', roles: ['user'] }
    global.fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ user: mockUser, token: "abc123" }) } as Response)
    const auth = useAuthStore()
    await auth.login({ email: 'alice@example.com', password: 'pass' })
    expect(auth.isAuthenticated).toBe(true)
    expect(localStorage.getItem('token')).toBe('abc123')
  })
  it('isAdmin returns true for admin role', () => {
    const auth = useAuthStore()
    auth.$patch({ user: { id: 1, name: 'A', email: 'a@b.com', roles: ['admin'] }, token: 't' })
    expect(auth.isAdmin).toBe(true)
  })
  it('logout clears state and storage', () => {
    const auth = useAuthStore()
    auth.$patch({ token: 'abc', user: { id: 1, name: 'A', email: 'a@b.com', roles: [] } })
    auth.logout()
    expect(auth.isAuthenticated).toBe(false)
    expect(localStorage.getItem('token')).toBeNull()
  })
  it('login throws and sets error on failure', async () => {
    global.fetch = vi.fn().mockResolvedValue({ ok: false } as Response)
    const auth = useAuthStore()
    await expect(auth.login({ email: 'x', password: 'x' })).rejects.toThrow()
    expect(auth.error).toBeTruthy()
    expect(auth.loading).toBe(false)
  })
})
```

### Composable test

```typescript
// src/composables/__tests__/useFetch.test.ts
import { describe, it, expect, vi, afterEach } from 'vitest'
import { useFetch } from '@/composables/useFetch'

describe('useFetch', () => {
  afterEach(() => vi.restoreAllMocks())
  it('fetches data and clears loading', async () => {
    const mockData = { id: 1, name: "Alice" }
    global.fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => mockData } as Response)
    const { data, loading, error } = useFetch('/api/user/1')
    expect(loading.value).toBe(true)
    await vi.waitFor(() => expect(loading.value).toBe(false))
    expect(data.value).toEqual(mockData)
    expect(error.value).toBeNull()
  })
  it('sets error on non-ok response', async () => {
    global.fetch = vi.fn().mockResolvedValue({ ok: false, status: 404, statusText: "Not Found" } as Response)
    const { error } = useFetch('/api/missing')
    await vi.waitFor(() => expect(error.value).toBeInstanceOf(Error))
    expect(error.value?.message).toContain("404")
  })
})
```

---

## 9. Performance

### v-memo: skip re-renders for stable list items

```vue
<template>
  <!-- Only re-renders when item.id or item.selected changes -->
  <div v-for="item in list" :key="item.id" v-memo="[item.id, item.selected]">
    <ExpensiveItemComponent :item="item" />
  </div>
</template>
```

### shallowRef and shallowReactive

```typescript
import { shallowRef, shallowReactive, triggerRef } from 'vue'

// Large datasets: track only the reference, not deep properties
const rows = shallowRef<Record<string, unknown>[]>([])

function updateRows(newData: Record<string, unknown>[]) {
  rows.value = newData  // reference change triggers reactivity
}

// Mutate in-place then manually signal update
function appendRow(row: Record<string, unknown>) {
  rows.value.push(row)
  triggerRef(rows)
}

// shallowReactive: only first-level properties are reactive
const state = shallowReactive({ config: { deep: { value: 42 } }, count: 0 })
state.count++         // reactive
state.config = {}     // reactive (top-level reassign)
// state.config.deep is NOT reactive -- intentional for performance
```

### defineAsyncComponent with loading/error states

```typescript
import { defineAsyncComponent } from 'vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ErrorDisplay from '@/components/ErrorDisplay.vue'

const HeavyChart = defineAsyncComponent({
  loader: () => import('@/components/HeavyChart.vue'),
  loadingComponent: LoadingSpinner,
  errorComponent: ErrorDisplay,
  delay: 200,       // ms before loading component appears
  timeout: 10_000,  // ms before error component appears
  onError(error, retry, fail, attempts) {
    if (attempts <= 3) retry()
    else fail()
  },
})
```

### Virtual scrolling: windowed rendering

```vue
<!-- src/components/VirtualList.vue -->
<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props { items: unknown[]; itemHeight: number; containerHeight: number }
const props = defineProps<Props>()
const scrollTop = ref(0)

const visibleCount = computed(() => Math.ceil(props.containerHeight / props.itemHeight) + 2)
const startIndex = computed(() => Math.max(0, Math.floor(scrollTop.value / props.itemHeight) - 1))
const endIndex = computed(() => Math.min(props.items.length, startIndex.value + visibleCount.value))
const visibleItems = computed(() =>
  props.items.slice(startIndex.value, endIndex.value).map((item, i) => ({
    item, index: startIndex.value + i,
  }))
)
const totalHeight = computed(() => props.items.length * props.itemHeight)
const offsetY = computed(() => startIndex.value * props.itemHeight)
function onScroll(e: Event) { scrollTop.value = (e.target as HTMLElement).scrollTop }
</script>

<template>
  <div :style="{ height: containerHeight + 'px', overflow: 'auto' }" @scroll="onScroll">
    <div :style="{ height: totalHeight + 'px', position: 'relative' }">
      <div :style="{ transform: 'translateY(' + offsetY + 'px)' }">
        <div
          v-for="{ item, index } in visibleItems"
          :key="index"
          :style="{ height: itemHeight + 'px' }"
        >
          <slot :item="item" :index="index" />
        </div>
      </div>
    </div>
  </div>
</template>
```

### markRaw: opt out of reactivity for third-party instances

```typescript
import { ref, markRaw } from 'vue'

// Map, chart, and WebGL instances must not be deeply proxied by Vue
const mapInstance = ref(markRaw(new google.maps.Map(el, options)))
const chartInstance = markRaw(new Chart(canvas, config))

// Use markRaw for any non-plain-object stored in reactive state
const store = reactive({
  worker: markRaw(new Worker("./worker.js")),
  socket: markRaw(new WebSocket("wss://api.example.com")),
})
```

---

## 10. Nuxt.js Basics

### Project setup

```bash
npx nuxi@latest init my-nuxt-app
cd my-nuxt-app && npm install && npm run dev
```

### nuxt.config.ts

```typescript
export default defineNuxtConfig({
  devtools: { enabled: true },
  typescript: { strict: true },
  modules: ['@pinia/nuxt', '@nuxt/image', '@nuxtjs/tailwindcss'],
  runtimeConfig: {
    databaseUrl: process.env.DATABASE_URL,
    jwtSecret: process.env.JWT_SECRET,
    public: { apiBase: process.env.NUXT_PUBLIC_API_BASE ?? '/api' },
  },
  routeRules: {
    '/': { prerender: true },
    '/dashboard/**': { ssr: false },
    '/api/**': { cors: true, headers: { 'cache-control': 'no-store' } },
  },
})
```

### pages/ directory: file-based routing

```
pages/
  index.vue              ->  /
  about.vue              ->  /about
  blog/[slug].vue        ->  /blog/:slug
  dashboard/index.vue    ->  /dashboard
  dashboard/[...path].vue ->  /dashboard/* (catch-all)
```

```vue
<!-- pages/blog/[slug].vue -->
<script setup lang="ts">
const route = useRoute()
const { data: post, error } = await useFetch('/api/posts/' + route.params.slug)

if (error.value) throw createError({ statusCode: 404, message: 'Post not found' })

useSeoMeta({
  title: post.value?.title,
  description: post.value?.excerpt,
  ogImage: post.value?.coverImage,
})
</script>

<template>
  <article v-if="post">
    <h1>{{ post.title }}</h1>
    <p>{{ post.content }}</p>
  </article>
</template>
```

### layouts/ directory: page wrappers

```vue
<!-- layouts/default.vue -->
<template>
  <div class="min-h-screen flex flex-col">
    <AppHeader />
    <main class="flex-1 container mx-auto px-4 py-8"><slot /></main>
    <AppFooter />
  </div>
</template>
```

```vue
<!-- pages/dashboard/index.vue: opt into named layout -->
<script setup lang="ts">
definePageMeta({ layout: 'dashboard', middleware: 'auth' })
</script>
```

### middleware/ directory: navigation guards

```typescript
// middleware/auth.ts
export default defineNuxtRouteMiddleware((to) => {
  const auth = useAuthStore()
  if (!auth.isAuthenticated) {
    return navigateTo({ path: '/login', query: { redirect: to.fullPath } })
  }
})
```

### server/api/ directory: HTTP handlers

```typescript
// server/api/posts/[id].get.ts
export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  if (!id || isNaN(Number(id)))
    throw createError({ statusCode: 400, message: 'Invalid post ID' })

  const db = useDatabase()
  const post = await db.query.posts.findFirst({
    where: eq(posts.id, Number(id)),
    with: { author: true, tags: true },
  })

  if (!post) throw createError({ statusCode: 404, message: 'Post not found' })
  return post
})
```

```typescript
// server/api/posts/index.post.ts
export default defineEventHandler(async (event) => {
  const session = await requireUserSession(event)
  const body = await readBody<{ title: string; content: string }>(event)

  if (!body.title || body.title.length < 3)
    throw createError({ statusCode: 422, message: 'Title must be at least 3 characters' })

  const db = useDatabase()
  const [newPost] = await db.insert(posts)
    .values({ title: body.title, content: body.content, authorId: session.user.id })
    .returning()

  setResponseStatus(event, 201)
  return newPost
})
```

### useFetch and useAsyncData in Nuxt pages

```vue
<script setup lang="ts">
// useFetch: SSR-aware, auto-deduplicates request keys, hydrates on client
const { data: users, refresh, status } = await useFetch('/api/users', {
  query: { page: 1, limit: 20 },
  transform: (res: { users: User[]; total: number }) => res.users,
  watch: false,
})

// useAsyncData: compose multiple fetches with custom logic
const { data: stats } = await useAsyncData('dashboard-stats', async () => {
  const [users, orders, revenue] = await Promise.all([
    ('/api/stats/users'),
    ('/api/stats/orders'),
    ('/api/stats/revenue'),
  ])
  return { users, orders, revenue }
}, { server: true, lazy: false, default: () => ({ users: 0, orders: 0, revenue: 0 }) })

// Client-only fetch: skip SSR entirely
const { data: livePrice } = await useFetch('/api/price/live', { server: false })
</script>
```

### Nuxt composables: auto-imported

```typescript
// composables/useApi.ts -- available in all pages/components without import
export const useApi = () => {
  const config = useRuntimeConfig()
  const base = config.public.apiBase
  async function get<T>(path: string, query?: Record<string, unknown>): Promise<T> {
    return <T>(base + path, { query })
  }
  async function post<T>(path: string, body: unknown): Promise<T> {
    return <T>(base + path, { method: 'POST', body })
  }
  async function put<T>(path: string, body: unknown): Promise<T> {
    return <T>(base + path, { method: 'PUT', body })
  }
  async function del<T>(path: string): Promise<T> {
    return <T>(base + path, { method: 'DELETE' })
  }
  return { get, post, put, del }
}
```

---

## Common Patterns Quick Reference

| Task | Pattern |
|---|---|
| Two-way binding on custom component | v-model + modelValue prop + update:modelValue emit |
| Multiple v-model bindings | v-model:title + title prop + update:title emit |
| Global state | Pinia defineStore (setup style preferred) |
| Share logic across components | Composable prefixed with use in composables/ |
| Code-split heavy component | defineAsyncComponent(() => import(...)) |
| Avoid deep reactivity overhead | shallowRef + triggerRef for large datasets |
| Skip re-render for stable items | v-memo=[dep1, dep2] |
| Opt objects out of Vue proxy | markRaw(instance) |
| CSS scoping in SFC | style scoped |
| Animate list additions/removals | TransitionGroup with name attribute |
| Animate single element | Transition with name attribute |
| Render outside component subtree | Teleport to=body |
| Handle async component loading states | Suspense with fallback slot |
| Debounce reactive input | useDebounce(ref, ms) composable |
| Persist state to localStorage | useLocalStorage(key, default) composable |

## File Naming Conventions

- Components: PascalCase.vue (UserCard.vue, DataTable.vue)
- Composables: camelCase.ts prefixed with use (useAuth.ts, useFetch.ts)
- Stores: camelCase.ts; exported function prefixed with use (auth.ts exports useAuthStore)
- Nuxt pages: kebab-case.vue or [param].vue ([slug].vue, [...path].vue)
- Nuxt API routes: endpoint.method.ts (users.get.ts, [id].delete.ts)

## Dependency Versions (as of 2026)

```json
{
  "vue": "^3.5",
  "vue-router": "^4.4",
  "pinia": "^2.3",
  "@vitejs/plugin-vue": "^5",
  "vite": "^6",
  "vitest": "^2",
  "@vue/test-utils": "^2.4",
  "nuxt": "^3.15",
  "@pinia/nuxt": "^0.10"
}
```
