---
name: astro-framework
description: Comprehensive Astro framework development skill covering component syntax, content collections, island architecture with partial hydration directives, MDX integration, SSG/SSR/hybrid rendering modes, dynamic routing, API endpoints, View Transitions API, image optimization with astro:assets, framework integration for React/Vue/Svelte, and deployment to Vercel, Netlify, and Cloudflare Pages.
---

# Astro Framework

This skill should be used when building content-driven websites with Astro. It covers the full spectrum of Astro development: component syntax, content collections, island architecture with partial hydration, framework integration, rendering strategies, routing, API endpoints, View Transitions, image optimization, and multi-platform deployment.

## When to Use This Skill

- Build content-heavy websites (blogs, documentation sites, marketing pages, portfolios)
- Use island architecture for partial hydration of interactive components
- Create MDX-powered documentation or blog sites
- Implement View Transitions for SPA-like navigation without a full SPA
- Mix static and server-rendered pages in a single project
- Integrate React, Vue, or Svelte components within an Astro site
- Optimize images and assets for production delivery
- Deploy static or server-rendered Astro sites to modern hosting platforms

## Project Structure

```
my-astro-site/
├── astro.config.mjs        # Astro configuration
├── tsconfig.json            # TypeScript configuration
├── package.json
├── public/                  # Static assets (served as-is)
│   ├── favicon.svg
│   └── robots.txt
├── src/
│   ├── assets/              # Build-processed assets (images, fonts)
│   │   └── images/
│   ├── components/          # .astro, .tsx, .vue, .svelte components
│   │   ├── Header.astro
│   │   ├── Footer.astro
│   │   ├── Counter.tsx       # React island
│   │   ├── SearchBar.vue     # Vue island
│   │   └── Accordion.svelte  # Svelte island
│   ├── content/
│   │   ├── config.ts         # Content collection schemas
│   │   ├── blog/             # Blog posts (MD/MDX)
│   │   │   ├── first-post.mdx
│   │   │   └── second-post.md
│   │   ├── docs/             # Documentation pages
│   │   │   ├── getting-started.md
│   │   │   └── api-reference.mdx
│   │   └── authors/          # Data collection (JSON/YAML)
│   │       ├── alice.json
│   │       └── bob.json
│   ├── layouts/
│   │   ├── BaseLayout.astro
│   │   ├── BlogLayout.astro
│   │   └── DocsLayout.astro
│   ├── pages/
│   │   ├── index.astro
│   │   ├── about.astro
│   │   ├── blog/
│   │   │   ├── index.astro
│   │   │   └── [...slug].astro
│   │   ├── docs/
│   │   │   └── [...slug].astro
│   │   ├── tags/
│   │   │   └── [tag].astro
│   │   └── api/
│   │       ├── search.ts
│   │       └── newsletter.ts
│   ├── styles/
│   │   └── global.css
│   └── utils/
│       ├── helpers.ts
│       └── constants.ts
└── .env                     # Environment variables
```

## Astro Component Syntax (.astro Files)

Astro components use a single-file format with a frontmatter fence (`---`) separating server-side logic from the template.

### Basic Component

```astro
---
// src/components/Card.astro
// Everything above the --- fence runs at BUILD TIME on the server.
// No JavaScript is shipped to the client from this block.

interface Props {
  title: string;
  description: string;
  href?: string;
  tags?: string[];
}

const { title, description, href = "#", tags = [] } = Astro.props;
const formattedTitle = title.toUpperCase();
---

<!-- Template: standard HTML with JSX-like expressions -->
<article class="card">
  <h2>
    <a href={href}>{formattedTitle}</a>
  </h2>
  <p>{description}</p>
  {tags.length > 0 && (
    <ul class="tags">
      {tags.map((tag) => (
        <li class="tag">{tag}</li>
      ))}
    </ul>
  )}
  <!-- Named slots for composition -->
  <footer>
    <slot name="footer" />
  </footer>
</article>

<!-- Scoped styles: only apply to this component -->
<style>
  .card {
    padding: 1.5rem;
    border: 1px solid #e2e8f0;
    border-radius: 0.5rem;
    transition: box-shadow 0.2s;
  }
  .card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  .tags {
    display: flex;
    gap: 0.5rem;
    list-style: none;
    padding: 0;
  }
  .tag {
    background: #edf2f7;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.875rem;
  }
</style>
```

### Slots and Composition

```astro
---
// src/components/Modal.astro
interface Props {
  title: string;
  size?: "sm" | "md" | "lg";
}

const { title, size = "md" } = Astro.props;
const widths = { sm: "400px", md: "600px", lg: "800px" };
---

<div class="modal-overlay">
  <div class="modal" style={`max-width: ${widths[size]}`}>
    <header class="modal-header">
      <h2>{title}</h2>
      <slot name="header-actions" />
    </header>
    <div class="modal-body">
      <!-- Default slot captures all unnamed children -->
      <slot />
    </div>
    <footer class="modal-footer">
      <slot name="footer">
        <!-- Fallback content when no footer slot is provided -->
        <button class="btn-close">Close</button>
      </slot>
    </footer>
  </div>
</div>
```

Usage:

```astro
---
import Modal from "../components/Modal.astro";
---

<Modal title="Confirm Action" size="sm">
  <p>Are you sure you want to proceed?</p>
  <div slot="footer">
    <button class="btn-cancel">Cancel</button>
    <button class="btn-confirm">Confirm</button>
  </div>
</Modal>
```

### Global vs Scoped Styles

```astro
---
// Styles in Astro components
---

<!-- Scoped by default: auto-generates unique class selectors -->
<style>
  h1 { color: navy; }     /* Only this component's h1 */
</style>

<!-- Global styles: use is:global directive -->
<style is:global>
  .prose h1 { color: navy; }   /* Applies globally */
</style>

<!-- Inline styles with CSS variables -->
<div style={`--accent: ${accentColor};`}>
  <slot />
</div>

<!-- Import external stylesheet -->
<style>
  @import "../styles/typography.css";
</style>
```

### Accessing Request Data in Components

```astro
---
// Available in .astro pages and components
const currentUrl = Astro.url;             // Full URL object
const pathname = Astro.url.pathname;      // /blog/my-post
const searchParams = Astro.url.searchParams; // URLSearchParams
const cookies = Astro.cookies;            // Cookie access
const headers = Astro.request.headers;    // Request headers
const isLoggedIn = cookies.has("session");

// Redirect programmatically (SSR only)
if (!isLoggedIn && pathname.startsWith("/dashboard")) {
  return Astro.redirect("/login", 302);
}
---
```

## Content Collections

### Defining Schemas

```typescript
// src/content/config.ts
import { defineCollection, z, reference } from "astro:content";

const blog = defineCollection({
  type: "content",   // Markdown/MDX content
  schema: ({ image }) => z.object({
    title: z.string().max(100),
    description: z.string().max(200),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    // Image schema validates and processes local images
    heroImage: image().optional(),
    heroImageAlt: z.string().optional(),
    tags: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
    // Reference another collection
    author: reference("authors"),
    // Related posts
    relatedPosts: z.array(reference("blog")).default([]),
    // Custom enums
    category: z.enum(["tutorial", "guide", "opinion", "news"]),
  }),
});

const docs = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string(),
    description: z.string(),
    order: z.number().default(0),
    section: z.string(),
    badge: z.enum(["new", "updated", "deprecated"]).optional(),
  }),
});

const authors = defineCollection({
  type: "data",      // JSON/YAML data (no body content)
  schema: ({ image }) => z.object({
    name: z.string(),
    bio: z.string(),
    avatar: image(),
    website: z.string().url().optional(),
    social: z.object({
      twitter: z.string().optional(),
      github: z.string().optional(),
    }).optional(),
  }),
});

const changelog = defineCollection({
  type: "content",
  schema: z.object({
    version: z.string(),
    date: z.coerce.date(),
    breaking: z.boolean().default(false),
  }),
});

export const collections = { blog, docs, authors, changelog };
```

### Querying Collections

```astro
---
// src/pages/blog/index.astro
import { getCollection, getEntry } from "astro:content";
import BlogLayout from "../../layouts/BlogLayout.astro";
import PostCard from "../../components/PostCard.astro";

// Fetch all non-draft blog posts, sorted by date
const posts = (await getCollection("blog", ({ data }) => {
  return import.meta.env.PROD ? !data.draft : true;  // Show drafts in dev
})).sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());

// Get unique tags across all posts
const allTags = [...new Set(posts.flatMap((post) => post.data.tags))];

// Fetch a single entry by slug
const featuredPost = await getEntry("blog", "welcome-to-astro");

// Fetch a referenced author from a post
const authorEntry = await getEntry(posts[0].data.author);
---

<BlogLayout title="Blog">
  <section class="featured" >
    {featuredPost && (
      <PostCard post={featuredPost} featured />
    )}
  </section>

  <nav class="tags">
    {allTags.map((tag) => (
      <a href={`/tags/${tag}`}>{tag}</a>
    ))}
  </nav>

  <section class="posts">
    {posts.map((post) => (
      <PostCard post={post} />
    ))}
  </section>
</BlogLayout>
```

### Rendering Content Pages

```astro
---
// src/pages/blog/[...slug].astro
import { getCollection } from "astro:content";
import BlogLayout from "../../layouts/BlogLayout.astro";
import AuthorCard from "../../components/AuthorCard.astro";
import TableOfContents from "../../components/TableOfContents.astro";

export async function getStaticPaths() {
  const posts = await getCollection("blog", ({ data }) => !data.draft);
  return posts.map((post) => ({
    params: { slug: post.slug },
    props: { post },
  }));
}

const { post } = Astro.props;
const { Content, headings } = await post.render();
const author = await getEntry(post.data.author);
---

<BlogLayout title={post.data.title} description={post.data.description}>
  <article class="blog-post">
    {post.data.heroImage && (
      <img
        src={post.data.heroImage.src}
        alt={post.data.heroImageAlt ?? ""}
        width={post.data.heroImage.width}
        height={post.data.heroImage.height}
        transition:name={`hero-${post.slug}`}
      />
    )}

    <h1>{post.data.title}</h1>

    <div class="meta">
      <time datetime={post.data.pubDate.toISOString()}>
        {post.data.pubDate.toLocaleDateString("en-US", {
          year: "numeric", month: "long", day: "numeric"
        })}
      </time>
      {post.data.updatedDate && (
        <span class="updated">
          Updated: {post.data.updatedDate.toLocaleDateString()}
        </span>
      )}
    </div>

    <div class="tags">
      {post.data.tags.map((tag) => (
        <a href={`/tags/${tag}`} class="tag">{tag}</a>
      ))}
    </div>

    <aside class="toc">
      <TableOfContents headings={headings} />
    </aside>

    <div class="prose">
      <Content />
    </div>

    <AuthorCard author={author} />
  </article>
</BlogLayout>
```

### MDX Content with Components

```mdx
---
# src/content/blog/interactive-guide.mdx
title: "Building Interactive Charts"
description: "Learn to add interactive charts to your Astro blog"
pubDate: 2025-06-15
author: alice
category: tutorial
tags: ["charts", "interactive", "d3"]
---

import Chart from "../../components/Chart.tsx";
import CodeBlock from "../../components/CodeBlock.astro";
import Callout from "../../components/Callout.astro";

# Building Interactive Charts

<Callout type="info">
  This tutorial requires familiarity with D3.js basics.
</Callout>

Here is a live chart that hydrates when visible:

<Chart
  client:visible
  data={[
    { label: "Jan", value: 30 },
    { label: "Feb", value: 45 },
    { label: "Mar", value: 62 },
  ]}
  type="bar"
/>

## The Code

<CodeBlock lang="typescript">
{`const chart = d3.select("#chart")
  .append("svg")
  .attr("width", 400)
  .attr("height", 300);`}
</CodeBlock>

Static content below the chart ships zero JavaScript.
```

## Island Architecture (Partial Hydration)

Astro ships zero JavaScript by default. Interactive components become "islands" of interactivity in a sea of static HTML. Each island hydrates independently based on its directive.

### Hydration Directives

```astro
---
import Counter from "../components/Counter.tsx";
import Newsletter from "../components/Newsletter.tsx";
import Carousel from "../components/Carousel.svelte";
import MobileMenu from "../components/MobileMenu.vue";
import ThreeScene from "../components/ThreeScene.tsx";
import SearchDialog from "../components/SearchDialog.tsx";
---

<!-- NO DIRECTIVE: renders static HTML only. Zero JS. -->
<Counter initialCount={5} />

<!-- client:load - Hydrate immediately on page load.
     Use for: above-the-fold interactive elements, critical UI. -->
<Counter client:load initialCount={0} />

<!-- client:idle - Hydrate when the browser is idle (requestIdleCallback).
     Use for: non-critical interactivity, below-fold components. -->
<Carousel client:idle images={images} />

<!-- client:visible - Hydrate when the element scrolls into view (IntersectionObserver).
     Use for: lazy-loaded content, comments, footers. -->
<Newsletter client:visible />

<!-- client:media - Hydrate only when a CSS media query matches.
     Use for: mobile-only or desktop-only interactive components. -->
<MobileMenu client:media="(max-width: 768px)" />

<!-- client:only="react" - Skip SSR entirely. Render only on client.
     Use for: components that depend on browser APIs (canvas, WebGL, window).
     Must specify the framework: "react", "vue", "svelte", "solid", etc. -->
<ThreeScene client:only="react" />
```

### Practical Island Pattern: Interactive Search

```astro
---
// src/pages/docs/index.astro
import { getCollection } from "astro:content";
import DocsLayout from "../../layouts/DocsLayout.astro";
import SearchBar from "../../components/SearchBar.tsx";

const docs = await getCollection("docs");
const searchIndex = docs.map((doc) => ({
  slug: doc.slug,
  title: doc.data.title,
  description: doc.data.description,
  section: doc.data.section,
}));
---

<DocsLayout title="Documentation">
  <!-- Search is an island: hydrates immediately for good UX -->
  <SearchBar client:load entries={searchIndex} />

  <!-- Everything else is static HTML -->
  <nav class="docs-nav">
    {docs.sort((a, b) => a.data.order - b.data.order).map((doc) => (
      <a href={`/docs/${doc.slug}`}>{doc.data.title}</a>
    ))}
  </nav>
</DocsLayout>
```

### React Island Component

```tsx
// src/components/SearchBar.tsx
import { useState, useMemo } from "react";

interface Entry {
  slug: string;
  title: string;
  description: string;
  section: string;
}

export default function SearchBar({ entries }: { entries: Entry[] }) {
  const [query, setQuery] = useState("");

  const results = useMemo(() => {
    if (!query.trim()) return [];
    const lower = query.toLowerCase();
    return entries.filter(
      (e) =>
        e.title.toLowerCase().includes(lower) ||
        e.description.toLowerCase().includes(lower)
    );
  }, [query, entries]);

  return (
    <div className="search">
      <input
        type="search"
        placeholder="Search docs..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        aria-label="Search documentation"
      />
      {results.length > 0 && (
        <ul className="search-results" role="listbox">
          {results.map((entry) => (
            <li key={entry.slug} role="option">
              <a href={`/docs/${entry.slug}`}>
                <strong>{entry.title}</strong>
                <span>{entry.description}</span>
              </a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

## Framework Integration (React, Vue, Svelte)

### Configuration

```javascript
// astro.config.mjs
import { defineConfig } from "astro/config";
import react from "@astrojs/react";
import vue from "@astrojs/vue";
import svelte from "@astrojs/svelte";

export default defineConfig({
  integrations: [
    react(),
    vue(),
    svelte(),
  ],
});
```

### Mixing Frameworks in a Single Page

```astro
---
// src/pages/dashboard.astro
// Each framework component can coexist on the same page.
// They hydrate independently as separate islands.
import ReactChart from "../components/Chart.tsx";
import VueForm from "../components/ContactForm.vue";
import SvelteAccordion from "../components/Accordion.svelte";
import AstroHeader from "../components/Header.astro";
---

<AstroHeader />

<main>
  <section>
    <h2>Analytics</h2>
    <ReactChart client:visible data={chartData} />
  </section>

  <section>
    <h2>Contact Us</h2>
    <VueForm client:idle />
  </section>

  <section>
    <h2>FAQ</h2>
    <SvelteAccordion client:visible items={faqItems} />
  </section>
</main>
```

### Sharing State Between Islands

Islands do not share state by default. Use nanostores for cross-island communication:

```typescript
// src/stores/cart.ts
import { atom, computed } from "nanostores";

export interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
}

export const cartItems = atom<CartItem[]>([]);

export const cartTotal = computed(cartItems, (items) =>
  items.reduce((sum, item) => sum + item.price * item.quantity, 0)
);

export function addToCart(item: Omit<CartItem, "quantity">) {
  const current = cartItems.get();
  const existing = current.find((i) => i.id === item.id);
  if (existing) {
    cartItems.set(
      current.map((i) =>
        i.id === item.id ? { ...i, quantity: i.quantity + 1 } : i
      )
    );
  } else {
    cartItems.set([...current, { ...item, quantity: 1 }]);
  }
}
```

```tsx
// src/components/CartButton.tsx (React island)
import { useStore } from "@nanostores/react";
import { cartItems, cartTotal } from "../stores/cart";

export default function CartButton() {
  const items = useStore(cartItems);
  const total = useStore(cartTotal);

  return (
    <button className="cart-btn">
      Cart ({items.length}) - ${total.toFixed(2)}
    </button>
  );
}
```

```svelte
<!-- src/components/AddToCart.svelte (Svelte island) -->
<script>
  import { addToCart } from "../stores/cart";

  export let product;
</script>

<button on:click={() => addToCart(product)}>
  Add {product.name} to Cart
</button>
```

## SSG, SSR, and Hybrid Rendering

### Static Site Generation (SSG) -- Default

All pages are pre-rendered at build time. Best for content sites.

```javascript
// astro.config.mjs
export default defineConfig({
  output: "static",  // Default: every page pre-rendered at build
});
```

### Server-Side Rendering (SSR)

All pages rendered on each request. Requires an adapter.

```javascript
// astro.config.mjs
import node from "@astrojs/node";

export default defineConfig({
  output: "server",  // Every page rendered per-request
  adapter: node({ mode: "standalone" }),
});
```

### Hybrid Rendering (Recommended for Most Projects)

Default to static, opt individual pages into SSR. Best of both worlds.

```javascript
// astro.config.mjs
import vercel from "@astrojs/vercel";

export default defineConfig({
  output: "hybrid",   // Default static, opt-in to server per page
  adapter: vercel(),
});
```

Opt specific pages into server rendering:

```astro
---
// src/pages/dashboard.astro
// This page will be server-rendered on each request
export const prerender = false;

const session = Astro.cookies.get("session")?.value;
if (!session) {
  return Astro.redirect("/login");
}

const user = await getUser(session);
---

<h1>Welcome, {user.name}</h1>
```

Opt a page into static rendering in server mode:

```astro
---
// src/pages/about.astro
// Force this page to be pre-rendered even in "server" mode
export const prerender = true;
---

<h1>About Us</h1>
<p>This page is static and pre-rendered at build time.</p>
```

## Routing and Dynamic Routes

### File-Based Routing

```
src/pages/
├── index.astro          -> /
├── about.astro          -> /about
├── blog/
│   ├── index.astro      -> /blog
│   └── [...slug].astro  -> /blog/any/nested/path
├── products/
│   └── [id].astro       -> /products/123
├── tags/
│   └── [tag].astro      -> /tags/javascript
├── [lang]/
│   └── [...slug].astro  -> /en/any/path, /fr/any/path
└── 404.astro            -> Custom 404 page
```

### Static Dynamic Routes (SSG)

```astro
---
// src/pages/tags/[tag].astro
import { getCollection } from "astro:content";

export async function getStaticPaths() {
  const posts = await getCollection("blog");
  const allTags = [...new Set(posts.flatMap((post) => post.data.tags))];

  return allTags.map((tag) => ({
    params: { tag },
    props: {
      posts: posts.filter((post) => post.data.tags.includes(tag)),
    },
  }));
}

const { tag } = Astro.params;
const { posts } = Astro.props;
---

<h1>Posts tagged: {tag}</h1>
<ul>
  {posts.map((post) => (
    <li><a href={`/blog/${post.slug}`}>{post.data.title}</a></li>
  ))}
</ul>
```

### Paginated Routes

```astro
---
// src/pages/blog/[...page].astro
import { getCollection } from "astro:content";
import type { GetStaticPaths } from "astro";

export const getStaticPaths = (async ({ paginate }) => {
  const posts = (await getCollection("blog", ({ data }) => !data.draft))
    .sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());

  // 10 posts per page: /blog, /blog/2, /blog/3, etc.
  return paginate(posts, { pageSize: 10 });
}) satisfies GetStaticPaths;

const { page } = Astro.props;
---

<h1>Blog (Page {page.currentPage})</h1>

{page.data.map((post) => (
  <article>
    <a href={`/blog/${post.slug}`}>{post.data.title}</a>
  </article>
))}

<nav class="pagination">
  {page.url.prev && <a href={page.url.prev}>Previous</a>}
  <span>Page {page.currentPage} of {page.lastPage}</span>
  {page.url.next && <a href={page.url.next}>Next</a>}
</nav>
```

### Server-Side Dynamic Routes (SSR)

```astro
---
// src/pages/products/[id].astro
// In SSR mode, no getStaticPaths needed
export const prerender = false;

const { id } = Astro.params;
const product = await fetch(`https://api.example.com/products/${id}`).then(
  (res) => {
    if (!res.ok) return null;
    return res.json();
  }
);

if (!product) {
  return Astro.redirect("/404");
}
---

<h1>{product.name}</h1>
<p>{product.description}</p>
<span>${product.price}</span>
```

### Internationalized Routes

```astro
---
// src/pages/[lang]/[...slug].astro
import { getCollection } from "astro:content";

const supportedLangs = ["en", "es", "fr", "de"];

export async function getStaticPaths() {
  const pages = await getCollection("docs");

  return supportedLangs.flatMap((lang) =>
    pages.map((page) => ({
      params: { lang, slug: page.slug },
      props: { page, lang },
    }))
  );
}

const { page, lang } = Astro.props;
const { Content } = await page.render();
---

<html lang={lang}>
  <body>
    <Content />
  </body>
</html>
```

## API Endpoints

### REST API Endpoints

```typescript
// src/pages/api/posts.ts
import type { APIRoute } from "astro";
import { getCollection } from "astro:content";

export const GET: APIRoute = async ({ url }) => {
  const tag = url.searchParams.get("tag");
  const limit = parseInt(url.searchParams.get("limit") ?? "10");

  let posts = await getCollection("blog", ({ data }) => !data.draft);

  if (tag) {
    posts = posts.filter((p) => p.data.tags.includes(tag));
  }

  const result = posts
    .sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf())
    .slice(0, limit)
    .map((post) => ({
      slug: post.slug,
      title: post.data.title,
      description: post.data.description,
      pubDate: post.data.pubDate,
      tags: post.data.tags,
    }));

  return new Response(JSON.stringify(result), {
    status: 200,
    headers: {
      "Content-Type": "application/json",
      "Cache-Control": "public, max-age=60",
    },
  });
};
```

### POST Endpoint with Validation

```typescript
// src/pages/api/contact.ts
import type { APIRoute } from "astro";

interface ContactForm {
  name: string;
  email: string;
  message: string;
}

function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

export const POST: APIRoute = async ({ request }) => {
  try {
    const body: ContactForm = await request.json();

    // Validate required fields
    if (!body.name?.trim() || !body.email?.trim() || !body.message?.trim()) {
      return new Response(
        JSON.stringify({ error: "All fields are required" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    if (!validateEmail(body.email)) {
      return new Response(
        JSON.stringify({ error: "Invalid email address" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    // Process the form (send email, save to database, etc.)
    await sendContactEmail(body);

    return new Response(
      JSON.stringify({ success: true, message: "Message sent" }),
      { status: 200, headers: { "Content-Type": "application/json" } }
    );
  } catch {
    return new Response(
      JSON.stringify({ error: "Internal server error" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
};
```

### Dynamic API Route

```typescript
// src/pages/api/posts/[slug].ts
import type { APIRoute } from "astro";
import { getEntry } from "astro:content";

export const GET: APIRoute = async ({ params }) => {
  const post = await getEntry("blog", params.slug!);

  if (!post) {
    return new Response(JSON.stringify({ error: "Not found" }), {
      status: 404,
      headers: { "Content-Type": "application/json" },
    });
  }

  return new Response(
    JSON.stringify({
      slug: post.slug,
      title: post.data.title,
      description: post.data.description,
      pubDate: post.data.pubDate,
      tags: post.data.tags,
    }),
    {
      status: 200,
      headers: { "Content-Type": "application/json" },
    }
  );
};

// DELETE endpoint for the same route
export const DELETE: APIRoute = async ({ params, cookies }) => {
  const session = cookies.get("admin-session")?.value;
  if (!session) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  await deletePost(params.slug!);
  return new Response(null, { status: 204 });
};
```

### RSS Feed Endpoint

```typescript
// src/pages/rss.xml.ts
import rss from "@astrojs/rss";
import { getCollection } from "astro:content";
import type { APIContext } from "astro";
import sanitizeHtml from "sanitize-html";
import MarkdownIt from "markdown-it";

const parser = new MarkdownIt();

export async function GET(context: APIContext) {
  const posts = (await getCollection("blog", ({ data }) => !data.draft))
    .sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());

  return rss({
    title: "My Astro Blog",
    description: "A blog about web development",
    site: context.site!,
    items: posts.map((post) => ({
      title: post.data.title,
      pubDate: post.data.pubDate,
      description: post.data.description,
      link: `/blog/${post.slug}/`,
      content: sanitizeHtml(parser.render(post.body ?? ""), {
        allowedTags: sanitizeHtml.defaults.allowedTags.concat(["img"]),
      }),
    })),
    customData: `<language>en-us</language>`,
  });
}
```

## View Transitions

### Setup

```astro
---
// src/layouts/BaseLayout.astro
import { ViewTransitions } from "astro:transitions";
import Header from "../components/Header.astro";
import Footer from "../components/Footer.astro";

interface Props {
  title: string;
  description?: string;
}

const { title, description = "My Astro Site" } = Astro.props;
---

<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content={description} />
    <title>{title}</title>
    <!-- Enable View Transitions for SPA-like navigation -->
    <ViewTransitions />
  </head>
  <body>
    <!-- transition:persist keeps this element across navigations -->
    <Header transition:persist />

    <!-- transition:animate controls the animation type -->
    <main transition:animate="slide">
      <slot />
    </main>

    <Footer />
  </body>
</html>
```

### Transition Animations

```astro
---
// Built-in animations: fade (default), slide, morph, none
---

<!-- Fade (default for all elements) -->
<div transition:animate="fade">Fades in/out</div>

<!-- Slide: slides content from the side -->
<main transition:animate="slide">
  <slot />
</main>

<!-- None: instant swap, no animation -->
<div transition:animate="none">Instant swap</div>

<!-- Custom animation -->
<div transition:animate={{
  old: {
    name: "slideOutLeft",
    duration: "0.3s",
    easing: "ease-in",
    fillMode: "forwards",
  },
  new: {
    name: "slideInRight",
    duration: "0.3s",
    easing: "ease-out",
    fillMode: "backwards",
  },
}}>
  Custom animated content
</div>

<style is:global>
  @keyframes slideOutLeft {
    to { transform: translateX(-100%); opacity: 0; }
  }
  @keyframes slideInRight {
    from { transform: translateX(100%); opacity: 0; }
  }
</style>
```

### Shared Element Transitions (Morph)

```astro
---
// Blog list page: src/pages/blog/index.astro
// Give each card image a unique transition name
---
{posts.map((post) => (
  <a href={`/blog/${post.slug}`}>
    <img
      src={post.data.heroImage?.src}
      alt={post.data.title}
      transition:name={`hero-${post.slug}`}
    />
    <h2 transition:name={`title-${post.slug}`}>{post.data.title}</h2>
  </a>
))}
```

```astro
---
// Blog post page: src/pages/blog/[...slug].astro
// Same transition:name creates a morphing animation between pages
---
<img
  src={post.data.heroImage?.src}
  alt={post.data.title}
  transition:name={`hero-${post.slug}`}
/>
<h1 transition:name={`title-${post.slug}`}>{post.data.title}</h1>
```

### Persisting Islands Across Navigations

```astro
---
import AudioPlayer from "../components/AudioPlayer.tsx";
---

<!-- This React island survives page navigation. State is preserved. -->
<AudioPlayer client:load transition:persist />

<!-- Persist with a name to match across different component trees -->
<VideoPlayer client:load transition:persist="main-player" />
```

### Lifecycle Events

```astro
<script>
  // Fires before the new page replaces the old one
  document.addEventListener("astro:before-swap", (event) => {
    // Preserve dark mode class during transitions
    const isDark = document.documentElement.classList.contains("dark");
    event.newDocument.documentElement.classList.toggle("dark", isDark);
  });

  // Fires after the new page content is swapped in
  document.addEventListener("astro:after-swap", () => {
    // Re-initialize third-party scripts
    initAnalytics();
  });

  // Fires after the new page is fully loaded and transitions complete
  document.addEventListener("astro:page-load", () => {
    // Runs on every navigation (including initial page load)
    setupEventListeners();
  });
</script>
```

## Image Optimization with astro:assets

### Basic Image Usage

```astro
---
// src/pages/about.astro
import { Image, Picture } from "astro:assets";
import teamPhoto from "../assets/images/team.jpg";
---

<!-- Optimized image: automatically generates WebP, sets width/height -->
<Image
  src={teamPhoto}
  alt="Our team at the office"
  width={800}
  height={450}
  quality={80}
  format="avif"
/>

<!-- Picture element: multiple formats and responsive sizes -->
<Picture
  src={teamPhoto}
  formats={["avif", "webp"]}
  widths={[400, 800, 1200]}
  sizes="(max-width: 600px) 400px, (max-width: 1024px) 800px, 1200px"
  alt="Our team at the office"
/>

<!-- Remote images: must be configured in astro.config.mjs -->
<Image
  src="https://images.unsplash.com/photo-example"
  alt="Unsplash photo"
  width={600}
  height={400}
  inferSize
/>
```

### Image Configuration

```javascript
// astro.config.mjs
import { defineConfig } from "astro/config";

export default defineConfig({
  image: {
    // Allow remote image domains
    domains: ["images.unsplash.com", "cdn.example.com"],
    // Or allow all remote images (less secure)
    remotePatterns: [{ protocol: "https" }],
    // Default image service options
    service: {
      entrypoint: "astro/assets/services/sharp",
      config: {
        limitInputPixels: false,
      },
    },
  },
});
```

### Images in Content Collections

```typescript
// src/content/config.ts
import { defineCollection, z } from "astro:content";

const blog = defineCollection({
  type: "content",
  schema: ({ image }) => z.object({
    title: z.string(),
    // Validates that the image exists and is a valid path
    cover: image(),
    coverAlt: z.string(),
    // Optional with refinements
    thumbnail: image().refine((img) => img.width >= 200, {
      message: "Thumbnail must be at least 200px wide",
    }).optional(),
  }),
});
```

```astro
---
// Rendering a content collection image
import { Image } from "astro:assets";
const { post } = Astro.props;
---

<Image
  src={post.data.cover}
  alt={post.data.coverAlt}
  width={1200}
  height={630}
  class="hero-image"
/>
```

### Background Images and CSS

```astro
---
import heroImage from "../assets/images/hero.jpg";
---

<!-- Use getImage() for CSS background images -->
<div class="hero" style={`background-image: url(${heroImage.src})`}>
  <h1>Welcome</h1>
</div>
```

```astro
---
// Programmatic image processing with getImage()
import { getImage } from "astro:assets";
import rawImage from "../assets/images/background.jpg";

const optimized = await getImage({
  src: rawImage,
  width: 1920,
  format: "avif",
  quality: 70,
});
---

<div
  class="hero"
  style={`background-image: url(${optimized.src}); ${optimized.attributes.style ?? ""}`}
>
  <slot />
</div>
```

## Deployment

### Vercel

```bash
npx astro add vercel
```

```javascript
// astro.config.mjs
import { defineConfig } from "astro/config";
import vercel from "@astrojs/vercel";

export default defineConfig({
  output: "hybrid",
  adapter: vercel({
    webAnalytics: { enabled: true },
    imageService: true,       // Use Vercel Image Optimization
    isr: {
      expiration: 60 * 60,    // ISR: revalidate every hour
    },
  }),
  site: "https://my-site.vercel.app",
});
```

Per-page ISR control:

```astro
---
// This page uses Incremental Static Regeneration
export const prerender = false;

// Vercel-specific: cache for 1 hour, serve stale while revalidating
Astro.response.headers.set(
  "Cache-Control",
  "s-maxage=3600, stale-while-revalidate=86400"
);
---
```

### Netlify

```bash
npx astro add netlify
```

```javascript
// astro.config.mjs
import { defineConfig } from "astro/config";
import netlify from "@astrojs/netlify";

export default defineConfig({
  output: "hybrid",
  adapter: netlify({
    edgeMiddleware: true,     // Use Netlify Edge Functions
    imageCDN: true,           // Use Netlify Image CDN
  }),
  site: "https://my-site.netlify.app",
});
```

Netlify-specific headers and redirects:

```
# public/_redirects
/blog/old-post  /blog/new-post  301
/api/*          /.netlify/functions/:splat  200

# public/_headers
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
```

### Cloudflare Pages

```bash
npx astro add cloudflare
```

```javascript
// astro.config.mjs
import { defineConfig } from "astro/config";
import cloudflare from "@astrojs/cloudflare";

export default defineConfig({
  output: "hybrid",
  adapter: cloudflare({
    platformProxy: {
      enabled: true,          // Access Cloudflare bindings in dev
    },
  }),
  site: "https://my-site.pages.dev",
});
```

Accessing Cloudflare bindings (KV, D1, R2):

```astro
---
// src/pages/api/data.ts (or any .astro page)
export const prerender = false;

const runtime = Astro.locals.runtime;
// Access KV namespace
const value = await runtime.env.MY_KV.get("key");
// Access D1 database
const { results } = await runtime.env.MY_DB
  .prepare("SELECT * FROM posts LIMIT 10")
  .all();
---
```

### Node.js (Self-Hosted / Docker)

```javascript
// astro.config.mjs
import { defineConfig } from "astro/config";
import node from "@astrojs/node";

export default defineConfig({
  output: "server",
  adapter: node({ mode: "standalone" }),  // or "middleware"
});
```

```dockerfile
# Dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runtime
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
COPY package.json .

ENV HOST=0.0.0.0
ENV PORT=4321
EXPOSE 4321

CMD ["node", "./dist/server/entry.mjs"]
```

## Common Patterns

### SEO and Meta Tags Component

```astro
---
// src/components/SEO.astro
interface Props {
  title: string;
  description: string;
  image?: string;
  canonicalUrl?: string;
  type?: "website" | "article";
  publishedDate?: Date;
}

const {
  title,
  description,
  image = "/og-default.png",
  canonicalUrl = Astro.url.href,
  type = "website",
  publishedDate,
} = Astro.props;

const siteName = "My Astro Site";
const fullTitle = `${title} | ${siteName}`;
const imageUrl = new URL(image, Astro.site).href;
---

<title>{fullTitle}</title>
<meta name="description" content={description} />
<link rel="canonical" href={canonicalUrl} />

<!-- Open Graph -->
<meta property="og:title" content={fullTitle} />
<meta property="og:description" content={description} />
<meta property="og:image" content={imageUrl} />
<meta property="og:url" content={canonicalUrl} />
<meta property="og:type" content={type} />
<meta property="og:site_name" content={siteName} />
{publishedDate && (
  <meta property="article:published_time" content={publishedDate.toISOString()} />
)}

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content={fullTitle} />
<meta name="twitter:description" content={description} />
<meta name="twitter:image" content={imageUrl} />

<!-- JSON-LD Structured Data -->
<script type="application/ld+json" set:html={JSON.stringify({
  "@context": "https://schema.org",
  "@type": type === "article" ? "BlogPosting" : "WebPage",
  "headline": title,
  "description": description,
  "image": imageUrl,
  "url": canonicalUrl,
  ...(publishedDate && { "datePublished": publishedDate.toISOString() }),
})} />
```

### Middleware (SSR)

```typescript
// src/middleware.ts
import { defineMiddleware, sequence } from "astro:middleware";

const auth = defineMiddleware(async ({ cookies, url, redirect, locals }, next) => {
  // Skip auth for public routes
  const publicPaths = ["/", "/login", "/api/auth"];
  if (publicPaths.some((p) => url.pathname.startsWith(p))) {
    return next();
  }

  const session = cookies.get("session")?.value;
  if (!session) {
    return redirect("/login?redirect=" + encodeURIComponent(url.pathname));
  }

  // Attach user to locals for downstream components
  locals.user = await validateSession(session);
  return next();
});

const logging = defineMiddleware(async ({ url, request }, next) => {
  const start = Date.now();
  const response = await next();
  const duration = Date.now() - start;
  console.log(`${request.method} ${url.pathname} - ${response.status} (${duration}ms)`);
  return response;
});

// Chain middleware in order
export const onRequest = sequence(logging, auth);
```

### Environment Variables

```typescript
// Access env variables in Astro
// Server-side (frontmatter, API routes): all env vars available
const apiKey = import.meta.env.API_KEY;

// Client-side: only PUBLIC_ prefixed vars are exposed
const publicUrl = import.meta.env.PUBLIC_API_URL;

// Type-safe env with astro:env (Astro 4.10+)
// src/env.d.ts
/// <reference path="../.astro/types.d.ts" />

interface ImportMetaEnv {
  readonly API_KEY: string;
  readonly DATABASE_URL: string;
  readonly PUBLIC_API_URL: string;
}
```

### Sitemap Generation

```javascript
// astro.config.mjs
import sitemap from "@astrojs/sitemap";

export default defineConfig({
  site: "https://example.com",
  integrations: [
    sitemap({
      filter: (page) => !page.includes("/admin/"),
      changefreq: "weekly",
      priority: 0.7,
      lastmod: new Date(),
      i18n: {
        defaultLocale: "en",
        locales: { en: "en-US", es: "es-ES", fr: "fr-FR" },
      },
    }),
  ],
});
```

## Additional Resources

- Astro documentation: https://docs.astro.build/
- Astro integrations library: https://astro.build/integrations/
- Content collections guide: https://docs.astro.build/en/guides/content-collections/
- View Transitions guide: https://docs.astro.build/en/guides/view-transitions/
- Deployment guides: https://docs.astro.build/en/guides/deploy/
- Astro starter themes: https://astro.build/themes/
