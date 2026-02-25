---
name: astro-framework
description: Astro framework development covering content collections, island architecture with partial hydration, MDX integration, SSG and SSR modes, View Transitions API, Astro DB, image optimization, SEO components, and deployment to Vercel, Netlify, and Cloudflare Pages.
---

# Astro Framework

This skill should be used when building content-driven websites with Astro. It covers content collections, island architecture, SSG/SSR, View Transitions, and deployment patterns.

## When to Use This Skill

Use this skill when you need to:

- Build content-heavy websites (blogs, docs, marketing)
- Use island architecture for partial hydration
- Create MDX-powered documentation sites
- Implement View Transitions for SPA-like navigation
- Deploy static or server-rendered Astro sites

## Project Structure

```
src/
├── components/      # .astro, .tsx, .vue, .svelte
├── content/
│   ├── config.ts    # Content collection schemas
│   ├── blog/        # MDX/MD blog posts
│   └── docs/        # Documentation pages
├── layouts/
│   └── BaseLayout.astro
├── pages/
│   ├── index.astro
│   ├── blog/
│   │   ├── index.astro
│   │   └── [...slug].astro
│   └── api/         # API routes
└── styles/
    └── global.css
```

## Content Collections

```typescript
// src/content/config.ts
import { defineCollection, z } from "astro:content";

const blog = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    heroImage: z.string().optional(),
    tags: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
  }),
});

const docs = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string(),
    description: z.string(),
    order: z.number().default(0),
    section: z.string(),
  }),
});

export const collections = { blog, docs };
```

```astro
---
// src/pages/blog/[...slug].astro
import { getCollection } from "astro:content";
import BlogLayout from "../../layouts/BlogLayout.astro";

export async function getStaticPaths() {
  const posts = await getCollection("blog", ({ data }) => !data.draft);
  return posts.map((post) => ({
    params: { slug: post.slug },
    props: { post },
  }));
}

const { post } = Astro.props;
const { Content } = await post.render();
---

<BlogLayout title={post.data.title} description={post.data.description}>
  <article>
    <h1>{post.data.title}</h1>
    <time datetime={post.data.pubDate.toISOString()}>
      {post.data.pubDate.toLocaleDateString()}
    </time>
    <Content />
  </article>
</BlogLayout>
```

## Island Architecture (Partial Hydration)

```astro
---
// Islands: interactive components in a sea of static HTML
import Counter from "../components/Counter.tsx";
import Newsletter from "../components/Newsletter.tsx";
import Carousel from "../components/Carousel.svelte";
---

<!-- Static by default — zero JS shipped -->
<h1>Welcome to my site</h1>
<p>This is static HTML. No JavaScript.</p>

<!-- client:load — hydrate immediately (above fold, critical) -->
<Counter client:load initialCount={0} />

<!-- client:visible — hydrate when scrolled into view (lazy) -->
<Newsletter client:visible />

<!-- client:idle — hydrate when browser is idle -->
<Carousel client:idle images={images} />

<!-- client:media — hydrate on media query match -->
<MobileMenu client:media="(max-width: 768px)" />

<!-- client:only="react" — render ONLY on client (no SSR) -->
<ThreeScene client:only="react" />
```

## View Transitions

```astro
---
// src/layouts/BaseLayout.astro
import { ViewTransitions } from "astro:transitions";
---

<html>
  <head>
    <ViewTransitions />
  </head>
  <body>
    <nav transition:persist>
      <!-- Nav persists across pages -->
    </nav>
    <main transition:animate="slide">
      <slot />
    </main>
  </body>
</html>
```

```astro
---
// Named transitions for shared elements
---
<img
  src={post.heroImage}
  transition:name={`hero-${post.slug}`}
  transition:animate="morph"
/>
```

## API Routes

```typescript
// src/pages/api/subscribe.ts
import type { APIRoute } from "astro";

export const POST: APIRoute = async ({ request }) => {
  const data = await request.json();
  const email = data.email;

  if (!email || !email.includes("@")) {
    return new Response(JSON.stringify({ error: "Invalid email" }), { status: 400 });
  }

  await addToNewsletter(email);
  return new Response(JSON.stringify({ success: true }), { status: 200 });
};
```

## Deployment

```typescript
// astro.config.mjs
import { defineConfig } from "astro/config";
import vercel from "@astrojs/vercel";     // or: netlify, cloudflare, node
import tailwind from "@astrojs/tailwind";
import mdx from "@astrojs/mdx";
import react from "@astrojs/react";
import sitemap from "@astrojs/sitemap";

export default defineConfig({
  site: "https://example.com",
  output: "hybrid",  // "static" | "server" | "hybrid"
  adapter: vercel(),
  integrations: [tailwind(), mdx(), react(), sitemap()],
  image: { domains: ["images.unsplash.com"] },
});
```

## Additional Resources

- Astro docs: https://docs.astro.build/
- Astro integrations: https://astro.build/integrations/
- Content collections: https://docs.astro.build/en/guides/content-collections/
- View Transitions: https://docs.astro.build/en/guides/view-transitions/
