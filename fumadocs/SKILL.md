---
name: fumadocs
description: Fumadocs documentation framework patterns covering content collections, MDX components, sidebar configuration, search integration, API reference generation, versioning, and Next.js App Router integration.
---

# Fumadocs

This skill should be used when building documentation sites with Fumadocs. It covers content collections, MDX, sidebar, search, API docs, and Next.js integration.

## When to Use This Skill

Use this skill when you need to:

- Build a documentation site with Next.js App Router
- Configure content collections with frontmatter
- Add full-text search to documentation
- Create custom MDX components for docs
- Generate API reference documentation

## Setup

```typescript
// source.config.ts
import { defineConfig, defineDocs } from "fumadocs-mdx/config";

export const { docs, meta } = defineDocs({
  dir: "content/docs",
});

export default defineConfig();

// app/layout.config.tsx
import { DocsLayout } from "fumadocs-ui/layouts/docs";
import type { BaseLayoutProps } from "fumadocs-ui/layouts/shared";
import { source } from "@/lib/source";

export const baseOptions: BaseLayoutProps = {
  nav: { title: "My Docs" },
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <DocsLayout tree={source.pageTree} {...baseOptions}>
      {children}
    </DocsLayout>
  );
}
```

## Content Structure

```
content/docs/
├── meta.json           # Sidebar ordering
├── index.mdx           # Home page
├── getting-started.mdx
├── guides/
│   ├── meta.json       # Group ordering
│   ├── installation.mdx
│   └── configuration.mdx
└── api/
    ├── meta.json
    └── endpoints.mdx
```

```json
// content/docs/meta.json
{
  "title": "Documentation",
  "pages": [
    "index",
    "getting-started",
    "---Guides---",
    "guides/installation",
    "guides/configuration",
    "---API---",
    "api/endpoints"
  ]
}
```

## MDX Content

```mdx
---
title: Getting Started
description: Learn how to set up the project
---

import { Callout, Steps, Tab, Tabs } from "fumadocs-ui/components";

## Installation

<Tabs items={["npm", "pnpm", "yarn"]}>
  <Tab value="npm">
    ```bash
    npm install my-library
    ```
  </Tab>
  <Tab value="pnpm">
    ```bash
    pnpm add my-library
    ```
  </Tab>
</Tabs>

<Steps>
### Step 1: Install dependencies

Run the install command above.

### Step 2: Configure

Create a config file:

```ts title="config.ts"
export default { theme: "dark" };
```

### Step 3: Start

```bash
npm run dev
```
</Steps>

<Callout type="warn">
  Make sure you have Node.js 18+ installed.
</Callout>
```

## Source Configuration

```typescript
// lib/source.ts
import { docs, meta } from "@/.source";
import { loader } from "fumadocs-core/source";
import { createMDXSource } from "fumadocs-mdx";

export const source = loader({
  baseUrl: "/docs",
  source: createMDXSource(docs, meta),
});
```

## Page Route

```tsx
// app/docs/[[...slug]]/page.tsx
import { source } from "@/lib/source";
import { DocsPage, DocsBody } from "fumadocs-ui/page";
import { notFound } from "next/navigation";

export default async function Page(props: { params: Promise<{ slug?: string[] }> }) {
  const params = await props.params;
  const page = source.getPage(params.slug);
  if (!page) notFound();

  const MDX = page.data.body;

  return (
    <DocsPage toc={page.data.toc}>
      <DocsBody>
        <h1>{page.data.title}</h1>
        <p className="text-muted-foreground">{page.data.description}</p>
        <MDX />
      </DocsBody>
    </DocsPage>
  );
}

export async function generateStaticParams() {
  return source.generateParams();
}

export async function generateMetadata(props: { params: Promise<{ slug?: string[] }> }) {
  const params = await props.params;
  const page = source.getPage(params.slug);
  if (!page) notFound();
  return { title: page.data.title, description: page.data.description };
}
```

## Search

```tsx
// app/api/search/route.ts
import { source } from "@/lib/source";
import { createSearchAPI } from "fumadocs-core/search/server";

export const { GET } = createSearchAPI("advanced", {
  indexes: source.getPages().map((page) => ({
    title: page.data.title,
    description: page.data.description,
    url: page.url,
    id: page.url,
    structuredData: page.data.structuredData,
  })),
});
```

## Additional Resources

- Fumadocs: https://fumadocs.vercel.app/
- MDX components: https://fumadocs.vercel.app/docs/ui/components
- Content collections: https://fumadocs.vercel.app/docs/mdx
