---
name: performance-optimization
description: This skill should be used when analyzing, diagnosing, or improving application performance, including Core Web Vitals (LCP, INP, CLS), bundle optimization, code splitting, lazy loading, image and font optimization, caching strategies, database query tuning, API performance, memory profiling, React/Next.js rendering optimizations, and Node.js runtime performance.
---

# Performance Optimization

This skill should be used when identifying bottlenecks and applying targeted optimizations across frontend, backend, and infrastructure layers of web applications.

## When to Use This Skill

- Diagnosing slow page loads or poor Core Web Vitals
- Reducing bundle size and implementing code splitting
- Optimizing images, fonts, and static assets
- Designing caching layers (browser, CDN, service worker)
- Fixing slow database queries (N+1, missing indexes)
- Improving API throughput (pagination, compression, pooling)
- Profiling memory leaks in browser or Node.js
- Optimizing React/Next.js rendering performance
- Scaling Node.js with worker threads and clustering

---

## 1. Core Web Vitals

### LCP (Largest Contentful Paint) -- Target: < 2.5s

**Before:**
```html
<link rel="stylesheet" href="/styles/animations.css">
<script src="/js/analytics.js"></script>
<img src="/hero.jpg" alt="Hero">
```

**After:**
```html
<link rel="preload" as="image" href="/hero.webp" fetchpriority="high">
<link rel="stylesheet" href="/styles/animations.css" media="print" onload="this.media='all'">
<script src="/js/analytics.js" defer></script>
<img src="/hero.webp" alt="Hero" fetchpriority="high" width="1200" height="600">
```

Key fixes: preload LCP element, defer non-critical CSS/JS, use `fetchpriority="high"`.

### INP (Interaction to Next Paint) -- Target: < 200ms

Break long tasks and yield to the main thread so the browser can paint between chunks:

```typescript
// Before: 500ms blocking click handler
button.addEventListener("click", () => { renderTable(hugeDataset.filter(complexFilter).sort(expensiveCompare)); });

// After: yield between phases
button.addEventListener("click", async () => {
  showSpinner();
  await scheduler.yield();
  const results = hugeDataset.filter(complexFilter);
  await scheduler.yield();
  renderTable(results.sort(expensiveCompare));
});
```

### CLS (Cumulative Layout Shift) -- Target: < 0.1

Set explicit dimensions on images, ads, embeds, and dynamic content to prevent layout shifts:

```html
<img src="/photo.jpg" alt="Photo" width="800" height="600">
<div class="ad-slot" style="min-height: 250px; aspect-ratio: 300/250;"></div>
```

---

## 2. Bundle Optimization

### Analysis Commands

```bash
npx webpack-bundle-analyzer dist/stats.json   # Webpack
npx vite-bundle-visualizer                     # Vite
ANALYZE=true next build                        # Next.js (@next/bundle-analyzer)
```

### Tree Shaking

```typescript
// Before: imports entire lodash (~70KB gzipped)
import _ from "lodash";
// After: imports only what is needed (~1KB)
import get from "lodash/get";
```

### Heavy Dependency Replacements

| Heavy | Lighter Alternative | Savings |
|-------|-------------------|---------|
| `moment` (67KB) | `dayjs` (2KB) | ~95% |
| `lodash` (70KB) | `lodash-es` + tree shaking | ~80% |
| `axios` (13KB) | Native `fetch` | 100% |
| `uuid` (3KB) | `crypto.randomUUID()` | 100% |

---

## 3. Code Splitting and Lazy Loading

### Route-Level Splitting

```tsx
import { lazy, Suspense } from "react";
const Dashboard = lazy(() => import("./pages/Dashboard"));
const Settings = lazy(() => import("./pages/Settings"));

function App() {
  return (
    <Suspense fallback={<PageSkeleton />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>);
}
```

### Conditional Component Splitting

Load heavy components only on user interaction:

```tsx
const HeavyChart = lazy(() => import("./components/AnalyticsChart"));
function Dashboard() {
  const [show, setShow] = useState(false);
  return (<>
    <button onClick={() => setShow(true)}>Show Analytics</button>
    {show && <Suspense fallback={<Skeleton />}><HeavyChart /></Suspense>}
  </>);
}
```

---

## 4. Image Optimization

Serve modern formats (AVIF > WebP > JPEG) with responsive `srcset` and explicit dimensions:

```html
<picture>
  <source srcset="/img-400.avif 400w, /img-800.avif 800w" type="image/avif" sizes="(max-width: 768px) 100vw, 50vw">
  <source srcset="/img-400.webp 400w, /img-800.webp 800w" type="image/webp" sizes="(max-width: 768px) 100vw, 50vw">
  <img src="/img-800.jpg" alt="Description" width="800" height="600" loading="lazy">
</picture>
```

Next.js `<Image>` automates format, resizing, and lazy loading:
```tsx
<Image src={url} alt={alt} width={400} height={300} sizes="(max-width: 768px) 100vw, 33vw" placeholder="blur" />
```

---

## 5. Font Optimization

Preload critical fonts, use `font-display: swap` to avoid invisible text, and subset to reduce size:

```html
<link rel="preload" href="/fonts/custom-latin.woff2" as="font" type="font/woff2" crossorigin>
```
```css
@font-face {
  font-family: "Custom";
  src: url("/fonts/custom-latin.woff2") format("woff2");
  font-display: swap;       /* Show fallback immediately, swap when loaded */
  unicode-range: U+0000-00FF; /* Latin subset only */
}
```
```bash
pyftsubset Custom.ttf --output-file=custom-latin.woff2 --flavor=woff2 --unicodes="U+0000-00FF"
```

---

## 6. Caching Strategies

### Browser and CDN Cache Headers (nginx)

```nginx
location /assets/ { expires 1y; add_header Cache-Control "public, immutable"; }
location /api/    { add_header Cache-Control "no-cache, must-revalidate"; }
location /        { add_header Cache-Control "public, max-age=300, stale-while-revalidate=86400"; }
```

### Service Worker

Cache-first for static assets, network-first with cache fallback for API:

```typescript
self.addEventListener("fetch", (event: FetchEvent) => {
  const isApi = event.request.url.includes("/api/");
  event.respondWith(isApi
    ? fetch(event.request).then(r => { caches.open("api").then(c => c.put(event.request, r.clone())); return r; }).catch(() => caches.match(event.request))
    : caches.match(event.request).then(c => c || fetch(event.request))
  );
});
```

---

## 7. Database Query Optimization

### Fixing N+1 Queries

**Before (1 + N queries):**
```typescript
const orders = await db.query("SELECT * FROM orders WHERE status = 'active'");
for (const order of orders) {
  order.customer = await db.query("SELECT * FROM customers WHERE id = $1", [order.customer_id]);
}
```

**After -- JOIN (single query):**
```sql
SELECT o.*, c.name AS customer_name, c.email AS customer_email
FROM orders o JOIN customers c ON c.id = o.customer_id WHERE o.status = 'active';
```

**After -- batch loading (for ORM/GraphQL DataLoader patterns):**
```typescript
const ids = [...new Set(orders.map(o => o.customer_id))];
const customers = await db.query("SELECT * FROM customers WHERE id = ANY($1)", [ids]);
const map = new Map(customers.map(c => [c.id, c]));
orders.forEach(o => { o.customer = map.get(o.customer_id); });
```

### Indexing

```sql
-- Find tables with excessive sequential scans (missing indexes)
SELECT relname, seq_scan - idx_scan AS excess FROM pg_stat_user_tables WHERE seq_scan > idx_scan ORDER BY 2 DESC;
-- Partial index for filtered queries
CREATE INDEX CONCURRENTLY idx_orders_active ON orders (created_at DESC) WHERE status = 'active';
-- Covering index to avoid table lookups
CREATE INDEX CONCURRENTLY idx_products_cat ON products (category_id, price) INCLUDE (name);
```

---

## 8. API Performance

### Cursor Pagination

Offset pagination degrades at scale. Cursor pagination runs in constant time:

```typescript
// Before: OFFSET 100000 still scans 100K rows
await db.query("SELECT * FROM products ORDER BY id LIMIT 20 OFFSET $1", [(page - 1) * 20]);
// After: cursor-based -- constant performance regardless of depth
const cursor = req.query.cursor as string | undefined;
const q = "SELECT * FROM products" + (cursor ? " WHERE id > $1" : "") + " ORDER BY id LIMIT 21";
const rows = await db.query(q, cursor ? [cursor] : []);
const hasNext = rows.length > 20;
if (hasNext) rows.pop();
res.json({ data: rows, nextCursor: hasNext ? rows.at(-1).id : null });
```

### Compression and Connection Pooling

```typescript
import compression from "compression";
app.use(compression({ threshold: 1024, level: 6 }));

import { Pool } from "pg";
const pool = new Pool({ max: 20, idleTimeoutMillis: 30000, connectionTimeoutMillis: 5000 });
```

---

## 9. Memory Profiling

### Browser -- Clean Up Event Listeners

```typescript
// Before: listeners leak on SPA navigation
window.addEventListener("resize", handleResize);
// After: AbortController cleans up all listeners at once
const controller = new AbortController();
window.addEventListener("resize", handleResize, { signal: controller.signal });
document.addEventListener("scroll", handleScroll, { signal: controller.signal });
// Cleanup: controller.abort();
```

### Node.js -- Bounded Caches

Unbounded `Map` or object caches cause memory leaks. Use an LRU eviction policy:

```typescript
// Before: grows forever
const cache = new Map<string, object>();

// After: evict oldest entries when max size is reached
class LRUCache<K, V> {
  private map = new Map<K, V>();
  constructor(private maxSize: number) {}
  get(key: K) { const v = this.map.get(key); if (v !== undefined) { this.map.delete(key); this.map.set(key, v); } return v; }
  set(key: K, value: V) { this.map.delete(key); this.map.set(key, value); if (this.map.size > this.maxSize) this.map.delete(this.map.keys().next().value); }
}
```

---

## 10. React / Next.js Optimizations

### memo, useMemo, useCallback

Inline objects and arrow functions create new references every render, defeating `memo`:

```tsx
// Before: new style object and onAdd function on every render cause child re-renders
<ProductCard style={{ border: "1px solid gray" }} onAdd={() => addToCart(p.id)} />

// After: stable references with memo + useCallback + useMemo
const ProductCard = memo(function ProductCard({ product, onAdd }: Props) {
  return <div><h3>{product.name}</h3><button onClick={() => onAdd(product.id)}>Add</button></div>;
});
function ProductList({ products }: { products: Product[] }) {
  const handleAdd = useCallback((id: string) => addToCart(id), []);
  const stats = useMemo(() => computeExpensiveStats(products), [products]);
  return products.map(p => <ProductCard key={p.id} product={p} onAdd={handleAdd} />);
}
```

### Next.js Server Components

Keep data-fetching in Server Components (zero client JS). Only interactive parts need `"use client"`:

```tsx
// app/products/page.tsx -- Server Component: no JS shipped to browser
async function ProductsPage() {
  const products = await db.products.findMany({ take: 50 });
  return <ul>{products.map(p => <li key={p.id}>{p.name} <AddToCartButton id={p.id} /></li>)}</ul>;
}

// components/AddToCartButton.tsx -- Client Component: only this ships JS
"use client";
export function AddToCartButton({ id }: { id: string }) {
  const [isPending, start] = useTransition();
  return <button disabled={isPending} onClick={() => start(() => addToCart(id))}>{isPending ? "..." : "Add"}</button>;
}
```

---

## 11. Node.js Performance

### Worker Threads for CPU-Intensive Work

Offload CPU-bound operations to avoid blocking the event loop:

```typescript
// Before: 2s of CPU work blocks all concurrent requests
app.post("/api/reports", async (req, res) => { res.send(generatePDF(await fetchData(req.body))); });

// After: run in a worker thread
import { Worker } from "worker_threads";
function runWorker(path: string, data: unknown): Promise<Buffer> {
  return new Promise((resolve, reject) => {
    const w = new Worker(path, { workerData: data });
    w.on("message", resolve); w.on("error", reject);
  });
}
app.post("/api/reports", async (req, res) => { res.send(await runWorker("./pdf-worker.js", await fetchData(req.body))); });
```

### Clustering

```typescript
import cluster from "cluster";
import { cpus } from "os";
if (cluster.isPrimary) {
  for (let i = 0; i < Math.min(cpus().length, 4); i++) cluster.fork();
  cluster.on("exit", () => cluster.fork()); // Auto-replace crashed workers
} else { createApp().listen(3000); }
```

---

## Performance Checklist

**Frontend:**
- LCP < 2.5s: preload hero image, inline critical CSS, defer scripts
- INP < 200ms: break long tasks, yield to main thread
- CLS < 0.1: explicit dimensions on all images/embeds/ads
- Bundle analyzed; heavy deps replaced; route-level code splitting
- Images in WebP/AVIF with responsive srcset; fonts subsetted and preloaded

**Backend:**
- N+1 queries eliminated (JOINs or batch loading)
- Indexes cover frequent query patterns; slow queries profiled
- Cursor pagination for large datasets; compression enabled
- Connection pooling configured; bounded caches prevent memory leaks

**Infrastructure:** CDN with stale-while-revalidate; service worker for static; Node.js clustered; CPU work in worker threads
