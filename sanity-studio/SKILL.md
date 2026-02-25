---
name: sanity-studio
description: Sanity Studio patterns covering schema definitions, GROQ queries, image handling with asset pipeline, portable text, real-time collaboration, custom input components, and Next.js/Remix integration.
---

# Sanity Studio

This skill should be used when building content platforms with Sanity CMS. It covers schema definitions, GROQ queries, image handling, portable text, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Define structured content schemas
- Query content with GROQ
- Handle images with Sanity's asset pipeline
- Render portable text (rich text)
- Integrate Sanity with Next.js or Remix

## Setup

```bash
npm create sanity@latest -- --project-id=<id> --dataset=production
# or add to existing project
npm install sanity @sanity/client @sanity/image-url next-sanity
```

## Schema Definitions

```ts
// schemas/post.ts
import { defineType, defineField } from "sanity";

export const post = defineType({
  name: "post",
  title: "Post",
  type: "document",
  fields: [
    defineField({
      name: "title",
      type: "string",
      validation: (Rule) => Rule.required().max(100),
    }),
    defineField({
      name: "slug",
      type: "slug",
      options: { source: "title", maxLength: 96 },
      validation: (Rule) => Rule.required(),
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
      fields: [
        defineField({ name: "alt", type: "string", title: "Alt text" }),
      ],
    }),
    defineField({
      name: "categories",
      type: "array",
      of: [{ type: "reference", to: [{ type: "category" }] }],
    }),
    defineField({
      name: "body",
      type: "array",
      of: [
        { type: "block" },
        { type: "image", options: { hotspot: true } },
        {
          type: "object",
          name: "code",
          fields: [
            { name: "language", type: "string" },
            { name: "code", type: "text" },
          ],
        },
      ],
    }),
    defineField({
      name: "publishedAt",
      type: "datetime",
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

```ts
import { createClient } from "@sanity/client";

const client = createClient({
  projectId: "your-project-id",
  dataset: "production",
  apiVersion: "2024-01-01",
  useCdn: true,
});

// List posts
const posts = await client.fetch(`
  *[_type == "post" && defined(slug.current)] | order(publishedAt desc) [0...10] {
    _id,
    title,
    slug,
    publishedAt,
    "author": author->name,
    "category": categories[]->title,
    "imageUrl": mainImage.asset->url
  }
`);

// Single post by slug
const post = await client.fetch(
  `*[_type == "post" && slug.current == $slug][0] {
    ...,
    "author": author->{name, image},
    "categories": categories[]->title,
    body[] {
      ...,
      _type == "image" => { "url": asset->url, alt }
    }
  }`,
  { slug: "my-post" }
);
```

## Image Handling

```ts
import imageUrlBuilder from "@sanity/image-url";

const builder = imageUrlBuilder(client);

function urlFor(source: any) {
  return builder.image(source);
}

// Usage
const imageUrl = urlFor(post.mainImage)
  .width(800)
  .height(400)
  .fit("crop")
  .auto("format")
  .url();
```

## Portable Text Rendering (React)

```tsx
import { PortableText } from "@portabletext/react";

const components = {
  types: {
    image: ({ value }: any) => (
      <img src={urlFor(value).width(800).url()} alt={value.alt || ""} />
    ),
    code: ({ value }: any) => (
      <pre><code className={`language-${value.language}`}>{value.code}</code></pre>
    ),
  },
  marks: {
    link: ({ children, value }: any) => (
      <a href={value.href} target="_blank" rel="noopener noreferrer">{children}</a>
    ),
  },
};

function PostBody({ body }: { body: any[] }) {
  return <PortableText value={body} components={components} />;
}
```

## Next.js Integration

```ts
// lib/sanity.ts
import { createClient } from "next-sanity";

export const client = createClient({
  projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID!,
  dataset: "production",
  apiVersion: "2024-01-01",
  useCdn: process.env.NODE_ENV === "production",
});

// app/posts/[slug]/page.tsx
export async function generateStaticParams() {
  const slugs = await client.fetch(`*[_type == "post"].slug.current`);
  return slugs.map((slug: string) => ({ slug }));
}

export default async function PostPage({ params }: { params: { slug: string } }) {
  const post = await client.fetch(
    `*[_type == "post" && slug.current == $slug][0]`,
    { slug: params.slug }
  );
  return <article><h1>{post.title}</h1></article>;
}
```

## Additional Resources

- Sanity: https://www.sanity.io/docs
- GROQ: https://www.sanity.io/docs/groq
- next-sanity: https://github.com/sanity-io/next-sanity
