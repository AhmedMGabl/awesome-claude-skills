---
name: contentlayer
description: Contentlayer and MDX content management covering document type definitions, computed fields, content validation, MDX components, Next.js integration, and static content generation patterns.
---

# Contentlayer

This skill should be used when managing structured content with Contentlayer or MDX. It covers document types, computed fields, MDX components, and Next.js integration.

## When to Use This Skill

Use this skill when you need to:

- Define typed content schemas for MDX/Markdown files
- Generate type-safe content collections
- Build blogs, docs, or content-heavy sites
- Add computed fields and content validation
- Integrate MDX with custom React components

## Content Configuration

```typescript
// contentlayer.config.ts
import { defineDocumentType, makeSource } from "contentlayer2/source-files";
import rehypePrettyCode from "rehype-pretty-code";
import remarkGfm from "remark-gfm";

export const Post = defineDocumentType(() => ({
  name: "Post",
  filePathPattern: "posts/**/*.mdx",
  contentType: "mdx",
  fields: {
    title: { type: "string", required: true },
    description: { type: "string", required: true },
    date: { type: "date", required: true },
    published: { type: "boolean", default: true },
    image: { type: "string" },
    tags: { type: "list", of: { type: "string" }, default: [] },
    author: { type: "string", required: true },
  },
  computedFields: {
    slug: {
      type: "string",
      resolve: (doc) => doc._raw.flattenedPath.replace("posts/", ""),
    },
    readingTime: {
      type: "number",
      resolve: (doc) => Math.ceil(doc.body.raw.split(/\s+/).length / 200),
    },
    url: {
      type: "string",
      resolve: (doc) => `/blog/${doc._raw.flattenedPath.replace("posts/", "")}`,
    },
  },
}));

export const Doc = defineDocumentType(() => ({
  name: "Doc",
  filePathPattern: "docs/**/*.mdx",
  contentType: "mdx",
  fields: {
    title: { type: "string", required: true },
    description: { type: "string" },
    order: { type: "number", default: 999 },
  },
  computedFields: {
    slug: {
      type: "string",
      resolve: (doc) => doc._raw.flattenedPath.replace("docs/", ""),
    },
  },
}));

export default makeSource({
  contentDirPath: "content",
  documentTypes: [Post, Doc],
  mdx: {
    remarkPlugins: [remarkGfm],
    rehypePlugins: [[rehypePrettyCode, { theme: "github-dark" }]],
  },
});
```

## Content Files

```mdx
---
title: Getting Started with Next.js
description: A comprehensive guide to building apps with Next.js
date: 2024-03-15
author: Jane Doe
tags: [nextjs, react, tutorial]
published: true
---

# Getting Started

Welcome to this guide on building with Next.js.

<Callout type="info">
  This guide assumes familiarity with React.
</Callout>

## Installation

```bash
npx create-next-app@latest
```

<Steps>
  <Step title="Create project">Run the create command above.</Step>
  <Step title="Install dependencies">Run `npm install`.</Step>
  <Step title="Start development">Run `npm run dev`.</Step>
</Steps>
```

## Next.js Integration

```typescript
// next.config.mjs
import { withContentlayer } from "next-contentlayer2";

export default withContentlayer({
  // Next.js config
});
```

```tsx
// app/blog/page.tsx
import { allPosts } from "contentlayer/generated";
import { compareDesc } from "date-fns";

export default function BlogPage() {
  const posts = allPosts
    .filter((p) => p.published)
    .sort((a, b) => compareDesc(new Date(a.date), new Date(b.date)));

  return (
    <div>
      <h1>Blog</h1>
      {posts.map((post) => (
        <article key={post.slug}>
          <a href={post.url}>
            <h2>{post.title}</h2>
            <p>{post.description}</p>
            <span>{post.readingTime} min read</span>
          </a>
        </article>
      ))}
    </div>
  );
}

// app/blog/[slug]/page.tsx
import { allPosts } from "contentlayer/generated";
import { useMDXComponent } from "next-contentlayer2/hooks";
import { notFound } from "next/navigation";

const mdxComponents = {
  Callout: ({ type, children }) => (
    <div className={`callout callout-${type}`}>{children}</div>
  ),
  Steps: ({ children }) => <div className="steps">{children}</div>,
  Step: ({ title, children }) => (
    <div className="step"><h3>{title}</h3>{children}</div>
  ),
};

export default function PostPage({ params }: { params: { slug: string } }) {
  const post = allPosts.find((p) => p.slug === params.slug);
  if (!post) notFound();

  const MDXContent = useMDXComponent(post.body.code);

  return (
    <article>
      <h1>{post.title}</h1>
      <time>{post.date}</time>
      <MDXContent components={mdxComponents} />
    </article>
  );
}

export function generateStaticParams() {
  return allPosts.map((post) => ({ slug: post.slug }));
}
```

## Additional Resources

- Contentlayer docs: https://contentlayer.dev/docs
- MDX: https://mdxjs.com/docs/
- Next.js MDX: https://nextjs.org/docs/pages/building-your-application/configuring/mdx
