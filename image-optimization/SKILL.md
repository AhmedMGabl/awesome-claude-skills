---
name: image-optimization
description: Image optimization patterns covering Next.js Image component, sharp for server-side processing, responsive images with srcset, WebP/AVIF format conversion, lazy loading, blur placeholders, CDN delivery, SVG optimization, and Core Web Vitals LCP improvement strategies.
---

# Image Optimization

This skill should be used when optimizing images for web performance. It covers responsive images, format conversion, lazy loading, server-side processing, and CDN delivery patterns.

## When to Use This Skill

Use this skill when you need to:

- Optimize images for web performance
- Implement responsive images with srcset
- Convert to modern formats (WebP, AVIF)
- Add blur placeholders and lazy loading
- Process images server-side with sharp
- Improve LCP (Largest Contentful Paint)

## Next.js Image Component

```tsx
import Image from "next/image";

// Responsive image with automatic optimization
function HeroImage() {
  return (
    <Image
      src="/hero.jpg"
      alt="Hero banner"
      width={1200}
      height={630}
      priority                // Preload for LCP
      sizes="(max-width: 768px) 100vw, (max-width: 1200px) 80vw, 1200px"
      className="w-full h-auto rounded-lg"
    />
  );
}

// Blur placeholder
function ProductImage({ src, alt }: { src: string; alt: string }) {
  return (
    <Image
      src={src}
      alt={alt}
      width={400}
      height={400}
      placeholder="blur"
      blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ..."  // Generate with sharp
      sizes="(max-width: 640px) 50vw, 25vw"
      className="object-cover aspect-square"
    />
  );
}

// Fill mode for dynamic aspect ratios
function Avatar({ src, name }: { src: string; name: string }) {
  return (
    <div className="relative w-12 h-12 rounded-full overflow-hidden">
      <Image src={src} alt={name} fill sizes="48px" className="object-cover" />
    </div>
  );
}
```

## Sharp (Server-Side Processing)

```typescript
import sharp from "sharp";

// Resize and convert to WebP
async function optimizeImage(input: Buffer, width: number): Promise<Buffer> {
  return sharp(input)
    .resize(width, null, { withoutEnlargement: true })
    .webp({ quality: 80 })
    .toBuffer();
}

// Generate responsive sizes
async function generateResponsiveSizes(inputPath: string, outputDir: string) {
  const sizes = [320, 640, 960, 1280, 1920];
  const image = sharp(inputPath);
  const metadata = await image.metadata();

  const results = await Promise.all(
    sizes
      .filter((w) => w <= (metadata.width ?? Infinity))
      .map(async (width) => {
        const filename = `image-${width}w.webp`;
        await sharp(inputPath)
          .resize(width)
          .webp({ quality: 80 })
          .toFile(`${outputDir}/${filename}`);
        return { width, filename };
      }),
  );

  return results;
}

// Generate blur placeholder (tiny base64)
async function generateBlurPlaceholder(inputPath: string): Promise<string> {
  const buffer = await sharp(inputPath)
    .resize(10, 10, { fit: "inside" })
    .blur()
    .toBuffer();
  return `data:image/jpeg;base64,${buffer.toString("base64")}`;
}

// Batch optimization
async function optimizeBatch(files: string[], outputDir: string) {
  for (const file of files) {
    const name = file.replace(/\.[^.]+$/, "");
    await sharp(file)
      .resize(1920, null, { withoutEnlargement: true })
      .webp({ quality: 80, effort: 6 })
      .toFile(`${outputDir}/${name}.webp`);

    // Also generate AVIF for browsers that support it
    await sharp(file)
      .resize(1920, null, { withoutEnlargement: true })
      .avif({ quality: 65 })
      .toFile(`${outputDir}/${name}.avif`);
  }
}
```

## Responsive HTML Images

```html
<!-- Picture element with format fallbacks -->
<picture>
  <source srcset="/hero.avif" type="image/avif" />
  <source srcset="/hero.webp" type="image/webp" />
  <img src="/hero.jpg" alt="Hero" width="1200" height="630" loading="lazy" decoding="async" />
</picture>

<!-- Responsive srcset with sizes -->
<img
  srcset="
    /product-320w.webp 320w,
    /product-640w.webp 640w,
    /product-960w.webp 960w,
    /product-1280w.webp 1280w
  "
  sizes="(max-width: 640px) 100vw, (max-width: 960px) 50vw, 320px"
  src="/product-640w.webp"
  alt="Product"
  width="640"
  height="640"
  loading="lazy"
  decoding="async"
/>
```

## Performance Checklist

```
IMAGE OPTIMIZATION CHECKLIST:
  [ ] Use WebP/AVIF with JPEG/PNG fallback
  [ ] Set explicit width and height to prevent layout shift (CLS)
  [ ] Use loading="lazy" for below-the-fold images
  [ ] Use loading="eager" or priority for LCP image
  [ ] Add srcset + sizes for responsive images
  [ ] Use decoding="async" for non-critical images
  [ ] Serve from CDN with cache headers
  [ ] Generate blur placeholder for perceived performance
  [ ] Compress: 80 quality for WebP, 65 for AVIF
  [ ] Max width: don't serve images larger than display size
```

## Additional Resources

- Next.js Image: https://nextjs.org/docs/app/api-reference/components/image
- Sharp: https://sharp.pixelplumbing.com/
- Squoosh (compression): https://squoosh.app/
- web.dev image optimization: https://web.dev/learn/images
