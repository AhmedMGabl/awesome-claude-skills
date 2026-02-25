---
name: seo-optimization
description: SEO optimization for web applications covering meta tags, Open Graph, structured data (JSON-LD), Next.js metadata API, sitemap generation, robots.txt, canonical URLs, Core Web Vitals, image optimization for SEO, and technical SEO audit checklists.
---

# SEO Optimization

This skill should be used when optimizing web applications for search engines. It covers meta tags, structured data, sitemaps, Core Web Vitals, and technical SEO.

## When to Use This Skill

Use this skill when you need to:

- Add proper meta tags and Open Graph data
- Implement structured data (JSON-LD)
- Generate sitemaps and robots.txt
- Optimize Core Web Vitals for SEO
- Audit and fix technical SEO issues

## Next.js Metadata API

```typescript
// app/layout.tsx
import type { Metadata } from "next";

export const metadata: Metadata = {
  metadataBase: new URL("https://example.com"),
  title: { default: "My App", template: "%s | My App" },
  description: "A description of my application",
  openGraph: {
    type: "website",
    locale: "en_US",
    siteName: "My App",
    images: [{ url: "/og-image.png", width: 1200, height: 630 }],
  },
  twitter: { card: "summary_large_image", creator: "@handle" },
  robots: { index: true, follow: true },
  alternates: { canonical: "https://example.com" },
};

// Dynamic metadata for pages
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const post = await getPost(params.slug);
  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      images: [{ url: post.coverImage }],
      type: "article",
      publishedTime: post.publishedAt,
    },
  };
}
```

## Structured Data (JSON-LD)

```tsx
export function ArticleJsonLd({ post }: { post: Post }) {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: post.title,
    description: post.excerpt,
    image: post.coverImage,
    datePublished: post.publishedAt,
    dateModified: post.updatedAt,
    author: { "@type": "Person", name: post.author.name },
    publisher: {
      "@type": "Organization",
      name: "My App",
      logo: { "@type": "ImageObject", url: "https://example.com/logo.png" },
    },
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
    />
  );
}
```

## Sitemap Generation

```typescript
// app/sitemap.ts (Next.js)
import type { MetadataRoute } from "next";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const posts = await db.posts.findMany({
    select: { slug: true, updatedAt: true },
  });

  return [
    { url: "https://example.com", lastModified: new Date(), priority: 1.0 },
    { url: "https://example.com/about", priority: 0.5 },
    ...posts.map((post) => ({
      url: `https://example.com/blog/${post.slug}`,
      lastModified: post.updatedAt,
      changeFrequency: "weekly" as const,
      priority: 0.7,
    })),
  ];
}
```

## robots.txt

```typescript
// app/robots.ts
import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      { userAgent: "*", allow: "/", disallow: ["/api/", "/admin/"] },
    ],
    sitemap: "https://example.com/sitemap.xml",
  };
}
```

## Technical SEO Checklist

```
CATEGORY         CHECK                           TOOL
───────────────────────────────────────────────────────
Meta tags        Title < 60 chars                Lighthouse
                 Description 120-160 chars
                 Canonical URL set
Structured data  Valid JSON-LD                   Rich Results Test
Performance      LCP < 2.5s                      PageSpeed Insights
                 INP < 200ms, CLS < 0.1
Crawlability     Sitemap submitted               Google Search Console
                 robots.txt correct
Mobile           Responsive design               Mobile-Friendly Test
                 Touch targets > 48px
```

## Additional Resources

- Google SEO guide: https://developers.google.com/search/docs
- Schema.org: https://schema.org/
- PageSpeed Insights: https://pagespeed.web.dev/
