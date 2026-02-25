---
name: mdx-content
description: MDX content authoring covering custom components, remark/rehype plugins, frontmatter parsing, syntax highlighting, Next.js MDX integration, and content collection patterns.
---

# MDX Content

This skill should be used when building content-driven sites with MDX. It covers custom components, plugins, syntax highlighting, and Next.js integration.

## When to Use This Skill

Use this skill when you need to:

- Write interactive content with JSX in Markdown
- Create custom MDX components for documentation
- Configure remark and rehype plugins
- Build blog or documentation with MDX
- Handle frontmatter and content collections

## Next.js MDX Setup

```javascript
// next.config.mjs
import createMDX from "@next/mdx";
import remarkGfm from "remark-gfm";
import rehypePrettyCode from "rehype-pretty-code";

const withMDX = createMDX({
  options: {
    remarkPlugins: [remarkGfm],
    rehypePlugins: [
      [rehypePrettyCode, { theme: "github-dark", keepBackground: false }],
    ],
  },
});

export default withMDX({
  pageExtensions: ["js", "jsx", "ts", "tsx", "md", "mdx"],
});
```

## Custom Components

```tsx
// components/mdx-components.tsx
import type { MDXComponents } from "mdx/types";
import Image from "next/image";

export function useMDXComponents(components: MDXComponents): MDXComponents {
  return {
    h1: ({ children }) => (
      <h1 className="text-4xl font-bold mt-8 mb-4">{children}</h1>
    ),
    h2: ({ children }) => (
      <h2 className="text-2xl font-semibold mt-6 mb-3" id={slugify(children)}>
        {children}
      </h2>
    ),
    a: ({ href, children }) => (
      <a href={href} className="text-blue-600 underline hover:text-blue-800">
        {children}
      </a>
    ),
    code: ({ children, className }) => {
      if (className) return <code className={className}>{children}</code>;
      return (
        <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono">
          {children}
        </code>
      );
    },
    img: ({ src, alt, ...props }) => (
      <Image src={src!} alt={alt!} width={800} height={400} className="rounded-lg" {...props} />
    ),
    Callout,
    Steps,
    Tabs,
    ...components,
  };
}

function Callout({ type = "info", children }: { type?: "info" | "warning" | "error"; children: React.ReactNode }) {
  const styles = {
    info: "bg-blue-50 border-blue-200 text-blue-800",
    warning: "bg-yellow-50 border-yellow-200 text-yellow-800",
    error: "bg-red-50 border-red-200 text-red-800",
  };
  return (
    <div className={`p-4 border-l-4 rounded-r-lg my-4 ${styles[type]}`}>
      {children}
    </div>
  );
}

function Steps({ children }: { children: React.ReactNode }) {
  return <div className="steps ml-4 border-l-2 border-gray-200 pl-6 space-y-6">{children}</div>;
}
```

## Frontmatter

```mdx
---
title: Building a REST API
description: Step-by-step guide to building REST APIs with Express
date: 2024-03-15
tags: [api, express, node]
author: Jane Doe
---

# {frontmatter.title}

Published on {new Date(frontmatter.date).toLocaleDateString()}

<Callout type="info">
  This guide covers Express.js v4 and Node.js 20+.
</Callout>
```

```typescript
// Parse frontmatter with gray-matter
import matter from "gray-matter";
import { readFileSync } from "fs";

const file = readFileSync("content/post.mdx", "utf-8");
const { data: frontmatter, content } = matter(file);
```

## Interactive Components in MDX

```mdx
import { useState } from 'react'

export function Counter() {
  const [count, setCount] = useState(0)
  return (
    <button onClick={() => setCount(c => c + 1)}>
      Count: {count}
    </button>
  )
}

# Interactive Demo

Click the button below to see it in action:

<Counter />

## Tabs Example

<Tabs items={["npm", "yarn", "pnpm"]}>
  <Tab>```bash
  npm install my-package
  ```</Tab>
  <Tab>```bash
  yarn add my-package
  ```</Tab>
  <Tab>```bash
  pnpm add my-package
  ```</Tab>
</Tabs>
```

## Content Collection Pattern

```typescript
// lib/content.ts
import { readdirSync, readFileSync } from "fs";
import path from "path";
import matter from "gray-matter";

const CONTENT_DIR = path.join(process.cwd(), "content/posts");

export function getAllPosts() {
  const files = readdirSync(CONTENT_DIR).filter((f) => f.endsWith(".mdx"));

  return files
    .map((filename) => {
      const filePath = path.join(CONTENT_DIR, filename);
      const { data } = matter(readFileSync(filePath, "utf-8"));
      return {
        slug: filename.replace(".mdx", ""),
        ...data,
      };
    })
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
}
```

## Additional Resources

- MDX docs: https://mdxjs.com/docs/
- @next/mdx: https://nextjs.org/docs/pages/building-your-application/configuring/mdx
- rehype plugins: https://github.com/rehypejs/rehype/blob/main/doc/plugins.md
