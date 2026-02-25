---
name: seo-optimization
description: SEO technical optimization covering meta tags, structured data (JSON-LD), Open Graph, sitemap generation, robots.txt, Core Web Vitals, semantic HTML, canonical URLs, internationalization (hreflang), and performance optimization for search engine visibility.
---

# SEO Optimization

This skill should be used when optimizing web applications for search engine visibility. It covers technical SEO, structured data, meta tags, Core Web Vitals, and performance patterns.

## When to Use This Skill

Use this skill when you need to:

- Add meta tags and Open Graph data to web pages
- Implement structured data (JSON-LD/Schema.org)
- Generate sitemaps and robots.txt
- Optimize Core Web Vitals (LCP, FID, CLS)
- Set up canonical URLs and redirects
- Implement internationalization (hreflang)
- Audit and fix SEO issues

## Meta Tags

### Next.js App Router

```typescript
// app/layout.tsx
import type { Metadata } from "next";

export const metadata: Metadata = {
  metadataBase: new URL("https://example.com"),
  title: {
    default: "My App",
    template: "%s | My App", // Page title | My App
  },
  description: "A comprehensive web application for...",
  keywords: ["keyword1", "keyword2", "keyword3"],
  authors: [{ name: "Author Name" }],
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true, "max-snippet": -1, "max-image-preview": "large" },
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://example.com",
    siteName: "My App",
    title: "My App - Tagline",
    description: "Description for social sharing",
    images: [{ url: "/og-image.png", width: 1200, height: 630, alt: "My App" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "My App",
    description: "Description for Twitter",
    images: ["/og-image.png"],
    creator: "@handle",
  },
  alternates: {
    canonical: "https://example.com",
    languages: { "es": "https://example.com/es", "fr": "https://example.com/fr" },
  },
  verification: {
    google: "google-site-verification-code",
  },
};

// Dynamic page metadata
// app/blog/[slug]/page.tsx
export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  const post = await getPost(params.slug);
  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      type: "article",
      publishedTime: post.publishedAt,
      authors: [post.author.name],
      images: [{ url: post.coverImage, width: 1200, height: 630 }],
    },
  };
}
```

### HTML Meta Tags (Non-Framework)

```html
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Page Title | Site Name</title>
  <meta name="description" content="155 chars max description">
  <link rel="canonical" href="https://example.com/page">

  <!-- Open Graph -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://example.com/page">
  <meta property="og:title" content="Page Title">
  <meta property="og:description" content="Description for sharing">
  <meta property="og:image" content="https://example.com/og-image.png">

  <!-- Twitter -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Page Title">
  <meta name="twitter:description" content="Description">
  <meta name="twitter:image" content="https://example.com/og-image.png">

  <!-- Internationalization -->
  <link rel="alternate" hreflang="en" href="https://example.com/en/page">
  <link rel="alternate" hreflang="es" href="https://example.com/es/page">
  <link rel="alternate" hreflang="x-default" href="https://example.com/page">
</head>
```

## Structured Data (JSON-LD)

```typescript
// Reusable JSON-LD component (Next.js built-in approach - safe rendering)
// In Next.js 14+, use the metadata API for JSON-LD:
function JsonLd({ data }: { data: Record<string, unknown> }) {
  // Use Next.js Script component for safe JSON-LD injection
  return (
    <script
      type="application/ld+json"
      // Note: JSON-LD scripts are safe from XSS as browsers do not execute
      // application/ld+json content. JSON.stringify also escapes HTML entities.
      children={JSON.stringify(data)}
    />
  );
}

// Article
const articleSchema = {
  "@context": "https://schema.org",
  "@type": "Article",
  headline: post.title,
  description: post.excerpt,
  image: post.coverImage,
  datePublished: post.publishedAt,
  dateModified: post.updatedAt,
  author: { "@type": "Person", name: post.author.name, url: post.author.url },
  publisher: {
    "@type": "Organization",
    name: "Site Name",
    logo: { "@type": "ImageObject", url: "https://example.com/logo.png" },
  },
};

// Product
const productSchema = {
  "@context": "https://schema.org",
  "@type": "Product",
  name: product.name,
  description: product.description,
  image: product.images,
  offers: {
    "@type": "Offer",
    price: product.price,
    priceCurrency: "USD",
    availability: product.inStock
      ? "https://schema.org/InStock"
      : "https://schema.org/OutOfStock",
  },
  aggregateRating: {
    "@type": "AggregateRating",
    ratingValue: product.rating,
    reviewCount: product.reviewCount,
  },
};

// FAQ
const faqSchema = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: faqs.map((faq) => ({
    "@type": "Question",
    name: faq.question,
    acceptedAnswer: { "@type": "Answer", text: faq.answer },
  })),
};

// Breadcrumb
const breadcrumbSchema = {
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  itemListElement: breadcrumbs.map((item, i) => ({
    "@type": "ListItem",
    position: i + 1,
    name: item.label,
    item: item.url,
  })),
};

// Organization
const orgSchema = {
  "@context": "https://schema.org",
  "@type": "Organization",
  name: "Company Name",
  url: "https://example.com",
  logo: "https://example.com/logo.png",
  sameAs: [
    "https://twitter.com/company",
    "https://linkedin.com/company/name",
    "https://github.com/company",
  ],
};
```

## Sitemap and Robots.txt

```typescript
// Next.js app/sitemap.ts
import type { MetadataRoute } from "next";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const posts = await getAllPosts();
  const products = await getAllProducts();

  const staticPages = [
    { url: "https://example.com", lastModified: new Date(), changeFrequency: "weekly" as const, priority: 1.0 },
    { url: "https://example.com/about", lastModified: new Date(), changeFrequency: "monthly" as const, priority: 0.8 },
    { url: "https://example.com/blog", lastModified: new Date(), changeFrequency: "daily" as const, priority: 0.9 },
  ];

  const postPages = posts.map((post) => ({
    url: `https://example.com/blog/${post.slug}`,
    lastModified: new Date(post.updatedAt),
    changeFrequency: "weekly" as const,
    priority: 0.7,
  }));

  const productPages = products.map((product) => ({
    url: `https://example.com/products/${product.slug}`,
    lastModified: new Date(product.updatedAt),
    changeFrequency: "daily" as const,
    priority: 0.8,
  }));

  return [...staticPages, ...postPages, ...productPages];
}

// Next.js app/robots.ts
export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      { userAgent: "*", allow: "/", disallow: ["/api/", "/admin/", "/private/"] },
    ],
    sitemap: "https://example.com/sitemap.xml",
  };
}
```

## Core Web Vitals

```typescript
// Optimize Largest Contentful Paint (LCP)
// Priority load above-fold images
import Image from "next/image";
<Image src="/hero.jpg" alt="Hero" width={1200} height={600} priority />

// Preload critical resources
<link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossOrigin="" />

// Optimize Cumulative Layout Shift (CLS)
// Always set explicit dimensions on images and embeds
<Image src="/photo.jpg" width={800} height={600} alt="Photo" />
<iframe width="560" height="315" src="..." title="Video" />

// Use aspect-ratio for responsive containers
<div style={{ aspectRatio: "16/9", width: "100%" }}>
  <video src="/video.mp4" style={{ width: "100%", height: "100%" }} />
</div>

// Optimize Interaction to Next Paint (INP)
// Defer non-critical JavaScript
<script src="/analytics.js" defer />

// Use dynamic imports for heavy components
const HeavyChart = dynamic(() => import("./Chart"), {
  loading: () => <ChartSkeleton />,
  ssr: false,
});
```

## Semantic HTML for SEO

```html
<!-- Use proper heading hierarchy -->
<h1>Main page title (one per page)</h1>
  <h2>Section heading</h2>
    <h3>Sub-section heading</h3>

<!-- Use semantic landmarks -->
<header>Site header/nav</header>
<nav aria-label="Main">Navigation</nav>
<main>Primary content</main>
<article>Self-contained content (blog post, product)</article>
<aside>Related content (sidebar)</aside>
<footer>Site footer</footer>

<!-- Use descriptive link text -->
<a href="/pricing">View pricing plans</a>  <!-- GOOD -->
<a href="/pricing">Click here</a>          <!-- BAD for SEO -->

<!-- Use alt text on images -->
<img src="/product.jpg" alt="Blue wireless headphones with noise cancellation">
```

## Performance Checklist

```
Images optimized (WebP/AVIF, lazy loading, responsive srcset)
Fonts optimized (subset, preload, font-display: swap)
CSS critical path inlined, non-critical deferred
JavaScript code-split and lazy-loaded
Server response time < 200ms (TTFB)
Gzip/Brotli compression enabled
CDN configured for static assets
HTTP/2 or HTTP/3 enabled
Cache headers set (immutable for hashed assets)
No render-blocking resources
```

## Additional Resources

- Google Search Central: https://developers.google.com/search
- Schema.org: https://schema.org/
- Web Vitals: https://web.dev/vitals/
- Lighthouse: https://developer.chrome.com/docs/lighthouse/
- Rich Results Test: https://search.google.com/test/rich-results
