---
name: contentful-cms
description: Contentful CMS integration covering content modeling, Delivery and Management APIs, rich text rendering, image optimization, localization, webhooks, and Next.js integration with preview mode. This skill should be used when building applications that consume or manage content through Contentful's headless CMS platform.
---

# Contentful CMS

This skill should be used when integrating Contentful as a headless CMS. It covers client setup, content modeling, querying, rich text, images, localization, webhooks, and Next.js ISR with preview mode.

## When to Use This Skill

Use this skill when you need to set up Delivery, Management, or Preview API clients; model content types and query entries with filters and pagination; render rich text with React; optimize images via the Images API; implement localization; sync content via signed webhooks; integrate with Next.js ISR and draft/preview mode; or generate TypeScript types from content models.

## Client Setup

```typescript
// lib/contentful.ts
import { createClient } from "contentful";

export const deliveryClient = createClient({
  space: process.env.CONTENTFUL_SPACE_ID!,
  accessToken: process.env.CONTENTFUL_ACCESS_TOKEN!,
  environment: process.env.CONTENTFUL_ENVIRONMENT ?? "master",
});

export const previewClient = createClient({
  space: process.env.CONTENTFUL_SPACE_ID!,
  accessToken: process.env.CONTENTFUL_PREVIEW_TOKEN!,
  host: "preview.contentful.com",
});

// Management API for write operations
import { createClient as mgmt } from "contentful-management";
export const managementClient = mgmt({ accessToken: process.env.CONTENTFUL_MANAGEMENT_TOKEN! });

export const getClient = (preview = false) => preview ? previewClient : deliveryClient;
```

## Content Type Modeling

```typescript
// types/contentful.ts
import type { EntryFieldTypes } from "contentful";

export interface BlogPostSkeleton {
  contentTypeId: "blogPost";
  fields: {
    title: EntryFieldTypes.Symbol;
    slug: EntryFieldTypes.Symbol;
    body: EntryFieldTypes.RichText;
    heroImage: EntryFieldTypes.AssetLink;
    author: EntryFieldTypes.EntryLink<AuthorSkeleton>;
    tags: EntryFieldTypes.Array<EntryFieldTypes.Symbol>;
    publishedAt: EntryFieldTypes.Date;
  };
}
```

## Querying Entries

```typescript
// Fetch list with filters, includes, and pagination
const { items, total } = await deliveryClient.getEntries<BlogPostSkeleton>({
  content_type: "blogPost",
  "fields.tags[in]": "typescript,react",
  order: ["-fields.publishedAt"],
  include: 2,       // resolve linked entries 2 levels deep
  limit: 10,
  skip: (page - 1) * 10,
  locale: "en-US",
});

// Fetch single entry by slug
const result = await deliveryClient.getEntries<BlogPostSkeleton>({
  content_type: "blogPost",
  "fields.slug": slug,
  include: 2,
  limit: 1,
});
const post = result.items[0] ?? null;
```

## Rich Text Rendering

```tsx
// components/RichTextRenderer.tsx
import { documentToReactComponents, Options } from "@contentful/rich-text-react-renderer";
import { BLOCKS, INLINES, MARKS } from "@contentful/rich-text-types";
import type { Document } from "@contentful/rich-text-types";

const options: Options = {
  renderMark: {
    [MARKS.CODE]: (text) => <code className="bg-muted px-1 rounded">{text}</code>,
  },
  renderNode: {
    [BLOCKS.PARAGRAPH]: (_, children) => <p className="mb-4">{children}</p>,
    [BLOCKS.HEADING_2]: (_, children) => <h2 className="text-2xl font-bold mt-8">{children}</h2>,
    [BLOCKS.EMBEDDED_ASSET]: (node) => {
      const { file, title, description } = node.data.target.fields;
      return (
        <img
          src={`https:${file.url}?w=800&fm=webp&q=75`}
          alt={description ?? title ?? ""}
          width={file.details.image.width}
          height={file.details.image.height}
          className="rounded-lg my-6"
        />
      );
    },
    [INLINES.HYPERLINK]: (node, children) => (
      <a href={node.data.uri} target="_blank" rel="noopener noreferrer">{children}</a>
    ),
  },
};

export function RichTextRenderer({ document }: { document: Document }) {
  return <div className="prose">{documentToReactComponents(document, options)}</div>;
}
```

## Image API

```typescript
const assetUrl = `https:${asset.fields.file.url}`;
const optimized = `${assetUrl}?w=800&h=400&fit=fill&f=face&fm=webp&q=75`;

export function buildSrcSet(url: string, widths = [400, 800, 1200]): string {
  return widths.map((w) => `https:${url}?w=${w}&fm=webp&q=75 ${w}w`).join(", ");
}
```

## Localization

```typescript
// Single locale
const entries = await deliveryClient.getEntries<BlogPostSkeleton>({ content_type: "blogPost", locale: "de-DE" });

// All locales — fields become { "en-US": "Hello", "de-DE": "Hallo" }
const all = await deliveryClient.getEntries<BlogPostSkeleton>({ content_type: "blogPost", locale: "*" });

// List available locales
const { items: locales } = await deliveryClient.getLocales();
```

## Webhooks for Content Sync

```typescript
// app/api/revalidate/route.ts
import { NextRequest, NextResponse } from "next/server";
import { revalidatePath, revalidateTag } from "next/cache";
import crypto from "crypto";

export async function POST(req: NextRequest) {
  const secret = process.env.CONTENTFUL_WEBHOOK_SECRET!;
  const body = await req.text();
  const sig = req.headers.get("x-contentful-signature") ?? "";
  const expected = crypto.createHmac("sha256", secret).update(body).digest("base64");

  if (sig !== expected) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { sys, fields } = JSON.parse(body);
  const contentType = sys?.contentType?.sys?.id as string;
  const slug: string | undefined = fields?.slug?.["en-US"];

  if (contentType === "blogPost" && slug) revalidatePath(`/blog/${slug}`);
  revalidateTag(contentType);

  return NextResponse.json({ revalidated: true });
}
```

## Next.js Integration — ISR and Preview Mode

```tsx
// app/blog/[slug]/page.tsx
import { draftMode } from "next/headers";
import { notFound } from "next/navigation";
import { getClient, deliveryClient } from "@/lib/contentful";
import { RichTextRenderer } from "@/components/RichTextRenderer";
import type { BlogPostSkeleton } from "@/types/contentful";

export const revalidate = 60;

export async function generateStaticParams() {
  const res = await deliveryClient.getEntries<BlogPostSkeleton>({
    content_type: "blogPost",
    select: ["fields.slug"],
  });
  return res.items.map((item) => ({ slug: item.fields.slug }));
}

export default async function BlogPostPage({ params }: { params: { slug: string } }) {
  const { isEnabled: preview } = await draftMode();
  const res = await getClient(preview).getEntries<BlogPostSkeleton>({
    content_type: "blogPost",
    "fields.slug": params.slug,
    include: 2,
    limit: 1,
  });
  const post = res.items[0];
  if (!post) notFound();
  return (
    <article>
      <h1>{post.fields.title}</h1>
      <RichTextRenderer document={post.fields.body} />
    </article>
  );
}

// app/api/draft/route.ts — enable Next.js draft mode
import { draftMode } from "next/headers";
import { redirect } from "next/navigation";

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  if (searchParams.get("secret") !== process.env.CONTENTFUL_PREVIEW_SECRET) {
    return new Response("Invalid token", { status: 401 });
  }
  (await draftMode()).enable();
  redirect(`/blog/${searchParams.get("slug")}`);
}
```

## TypeScript Code Generation

```bash
# Generate types with cf-content-types-generator
npm install --save-dev cf-content-types-generator
npx cf-content-types-generator \
  --spaceId $CONTENTFUL_SPACE_ID \
  --token $CONTENTFUL_MANAGEMENT_TOKEN \
  --out src/types/contentful-generated.ts
```

## Additional Resources

- Contentful docs: https://www.contentful.com/developers/docs/
- JavaScript SDK: https://github.com/contentful/contentful.js
- Rich text types: https://github.com/contentful/rich-text
- Images API: https://www.contentful.com/developers/docs/references/images-api/
