---
name: astro-content
description: Astro Content Collections patterns covering type-safe content schemas, Zod validation, MDX components, content queries, dynamic routing, related content, RSS feeds, and static site generation.
---

# Astro Content Collections

This skill should be used when managing structured content in Astro with Content Collections. It covers schemas, queries, MDX, dynamic routes, and RSS feeds.

## When to Use This Skill

Use this skill when you need to:

- Define type-safe content schemas with Zod
- Query and filter content collections
- Render MDX with custom components
- Generate dynamic routes from content
- Build RSS feeds and sitemaps

## Content Schema Definition

```ts
// src/content/config.ts
import { defineCollection, z, reference } from "astro:content";

const blog = defineCollection({
  type: "content",
  schema: ({ image }) =>
    z.object({
      title: z.string().max(100),
      description: z.string().max(300),
      pubDate: z.coerce.date(),
      updatedDate: z.coerce.date().optional(),
      heroImage: image().optional(),
      author: reference("authors"),
      tags: z.array(z.string()).default([]),
      draft: z.boolean().default(false),
      category: z.enum(["tutorial", "guide", "news", "opinion"]),
    }),
});

const authors = defineCollection({
  type: "data",
  schema: z.object({
    name: z.string(),
    bio: z.string(),
    avatar: z.string().url(),
    social: z.object({
      twitter: z.string().optional(),
      github: z.string().optional(),
    }),
  }),
});

const docs = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string(),
    description: z.string(),
    sidebar: z.object({
      order: z.number(),
      label: z.string().optional(),
    }),
  }),
});

export const collections = { blog, authors, docs };
```

## Querying Collections

```astro
---
// src/pages/blog/index.astro
import { getCollection } from "astro:content";

const posts = (await getCollection("blog", ({ data }) => !data.draft))
  .sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());

// Filter by tag
const taggedPosts = await getCollection("blog", ({ data }) =>
  data.tags.includes("astro") && !data.draft
);

// Get single entry
import { getEntry } from "astro:content";
const author = await getEntry("authors", "john-doe");
---

<ul>
  {posts.map((post) => (
    <li>
      <a href={`/blog/${post.slug}`}>
        <h2>{post.data.title}</h2>
        <time datetime={post.data.pubDate.toISOString()}>
          {post.data.pubDate.toLocaleDateString()}
        </time>
        <p>{post.data.description}</p>
      </a>
    </li>
  ))}
</ul>
```

## Dynamic Routes from Content

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
const { Content, headings } = await post.render();
const author = await getEntry(post.data.author);
---

<BlogLayout title={post.data.title}>
  <article>
    <h1>{post.data.title}</h1>
    <p>By {author.data.name}</p>
    <time>{post.data.pubDate.toLocaleDateString()}</time>
    <Content />
  </article>
  <aside>
    <h3>Table of Contents</h3>
    <ul>
      {headings.map((h) => (
        <li style={`margin-left: ${(h.depth - 2) * 16}px`}>
          <a href={`#${h.slug}`}>{h.text}</a>
        </li>
      ))}
    </ul>
  </aside>
</BlogLayout>
```

## Custom MDX Components

```astro
---
// src/pages/blog/[...slug].astro
import Callout from "../../components/Callout.astro";
import CodeBlock from "../../components/CodeBlock.astro";

const { Content } = await post.render();
---

<Content components={{ Callout, CodeBlock, pre: CodeBlock }} />
```

```astro
---
// src/components/Callout.astro
interface Props {
  type?: "info" | "warning" | "tip";
}
const { type = "info" } = Astro.props;
const styles = {
  info: "bg-blue-50 border-blue-400",
  warning: "bg-yellow-50 border-yellow-400",
  tip: "bg-green-50 border-green-400",
};
---

<div class={`p-4 border-l-4 rounded ${styles[type]}`}>
  <slot />
</div>
```

## RSS Feed

```ts
// src/pages/rss.xml.ts
import rss from "@astrojs/rss";
import { getCollection } from "astro:content";

export async function GET(context: any) {
  const posts = (await getCollection("blog", ({ data }) => !data.draft))
    .sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());

  return rss({
    title: "My Blog",
    description: "A blog about web development",
    site: context.site,
    items: posts.map((post) => ({
      title: post.data.title,
      description: post.data.description,
      pubDate: post.data.pubDate,
      link: `/blog/${post.slug}/`,
      categories: post.data.tags,
    })),
  });
}
```

## Additional Resources

- Content Collections: https://docs.astro.build/en/guides/content-collections/
- Content Queries: https://docs.astro.build/en/reference/modules/astro-content/
- MDX Integration: https://docs.astro.build/en/guides/integrations-guide/mdx/
