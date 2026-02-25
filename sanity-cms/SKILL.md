---
name: sanity-cms
description: Sanity CMS headless content management covering schema definition, GROQ queries, image handling with next-sanity, real-time preview, portable text rendering, custom studio configuration, webhooks, and integration with Next.js and Astro.
---

# Sanity CMS

This skill should be used when building content-managed applications with Sanity. It covers schema definition, GROQ queries, image handling, live preview, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Define content schemas for a headless CMS
- Query content with GROQ
- Handle images and media assets
- Set up real-time content preview
- Integrate Sanity with Next.js or Astro

## Schema Definition

```typescript
// sanity/schemaTypes/post.ts
import { defineType, defineField } from "sanity";

export const postType = defineType({
  name: "post",
  title: "Post",
  type: "document",
  fields: [
    defineField({
      name: "title",
      type: "string",
      validation: (rule) => rule.required().max(100),
    }),
    defineField({
      name: "slug",
      type: "slug",
      options: { source: "title", maxLength: 96 },
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: "author",
      type: "reference",
      to: [{ type: "author" }],
    }),
    defineField({
      name: "mainImage",
      type: "image",
      options: { hotspot: true },
      fields: [{ name: "alt", type: "string", title: "Alt text" }],
    }),
    defineField({
      name: "body",
      type: "blockContent", // Portable Text
    }),
    defineField({
      name: "publishedAt",
      type: "datetime",
    }),
    defineField({
      name: "categories",
      type: "array",
      of: [{ type: "reference", to: [{ type: "category" }] }],
    }),
  ],
  preview: {
    select: { title: "title", author: "author.name", media: "mainImage" },
    prepare({ title, author, media }) {
      return { title, subtitle: author ? `by ${author}` : "", media };
    },
  },
});
```

## GROQ Queries

```typescript
import { createClient } from "next-sanity";

const client = createClient({
  projectId: process.env.SANITY_PROJECT_ID!,
  dataset: "production",
  apiVersion: "2024-01-01",
  useCdn: true,
});

// List posts
const posts = await client.fetch(`
  *[_type == "post"] | order(publishedAt desc) {
    _id,
    title,
    slug,
    publishedAt,
    "author": author->name,
    "categories": categories[]->title,
    "imageUrl": mainImage.asset->url
  }[0...10]
`);

// Single post by slug
const post = await client.fetch(`
  *[_type == "post" && slug.current == $slug][0] {
    title,
    body,
    publishedAt,
    "author": author->{name, image},
    "imageUrl": mainImage.asset->url
  }
`, { slug });
```

## Next.js Integration

```tsx
// app/blog/[slug]/page.tsx
import { PortableText } from "@portabletext/react";
import { urlFor } from "@/lib/sanity-image";

export default async function PostPage({ params }: { params: { slug: string } }) {
  const post = await client.fetch(postQuery, { slug: params.slug });

  return (
    <article>
      <h1>{post.title}</h1>
      {post.mainImage && (
        <img
          src={urlFor(post.mainImage).width(800).height(400).url()}
          alt={post.mainImage.alt ?? ""}
        />
      )}
      <PortableText value={post.body} />
    </article>
  );
}
```

## Image URL Builder

```typescript
// lib/sanity-image.ts
import imageUrlBuilder from "@sanity/image-url";

const builder = imageUrlBuilder(client);

export function urlFor(source: any) {
  return builder.image(source);
}

// Usage
urlFor(post.mainImage).width(800).height(400).auto("format").url();
urlFor(post.mainImage).size(200, 200).fit("crop").url();
```

## Portable Text Components

```tsx
import { PortableText, PortableTextComponents } from "@portabletext/react";

const components: PortableTextComponents = {
  types: {
    image: ({ value }) => (
      <img src={urlFor(value).width(700).url()} alt={value.alt ?? ""} />
    ),
    code: ({ value }) => (
      <pre><code className={`language-${value.language}`}>{value.code}</code></pre>
    ),
  },
  marks: {
    link: ({ children, value }) => (
      <a href={value.href} target="_blank" rel="noopener noreferrer">{children}</a>
    ),
  },
};

<PortableText value={post.body} components={components} />;
```

## CLI Commands

```bash
npm create sanity@latest          # Create new project
npx sanity dev                    # Start studio locally
npx sanity deploy                 # Deploy studio
npx sanity dataset export prod    # Export dataset
npx sanity typegen generate       # Generate TypeScript types
```

## Additional Resources

- Sanity docs: https://www.sanity.io/docs
- GROQ reference: https://www.sanity.io/docs/groq
- next-sanity: https://github.com/sanity-io/next-sanity
