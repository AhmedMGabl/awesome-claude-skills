---
name: sharp-image
description: Sharp image processing covering resize, crop, format conversion, WebP/AVIF optimization, watermarks, metadata extraction, compositing, and batch processing for Node.js applications.
---

# Sharp Image Processing

This skill should be used when processing images with Sharp in Node.js. It covers resizing, format conversion, optimization, compositing, and batch operations.

## When to Use This Skill

Use this skill when you need to:

- Resize and crop images for web delivery
- Convert between formats (WebP, AVIF, PNG, JPEG)
- Optimize images for performance
- Add watermarks and overlay text
- Process images in bulk pipelines

## Basic Operations

```typescript
import sharp from "sharp";

// Resize
await sharp("input.jpg")
  .resize(800, 600, { fit: "cover", position: "center" })
  .toFile("output.jpg");

// Resize with aspect ratio
await sharp("input.jpg")
  .resize({ width: 800 }) // height auto-calculated
  .toFile("output.jpg");

// Resize with max dimensions (fit inside)
await sharp("input.jpg")
  .resize(800, 600, { fit: "inside", withoutEnlargement: true })
  .toFile("output.jpg");
```

## Format Conversion and Optimization

```typescript
// JPEG with quality
await sharp("input.png")
  .jpeg({ quality: 80, mozjpeg: true })
  .toFile("output.jpg");

// WebP
await sharp("input.jpg")
  .webp({ quality: 80, effort: 6 })
  .toFile("output.webp");

// AVIF (best compression, slower)
await sharp("input.jpg")
  .avif({ quality: 50, effort: 4 })
  .toFile("output.avif");

// PNG with compression
await sharp("input.jpg")
  .png({ compressionLevel: 9, palette: true })
  .toFile("output.png");

// Auto-format based on Accept header
function optimizeImage(input: Buffer, acceptHeader: string) {
  const pipeline = sharp(input).resize(800, 600, { fit: "inside" });

  if (acceptHeader.includes("image/avif")) {
    return pipeline.avif({ quality: 50 }).toBuffer();
  }
  if (acceptHeader.includes("image/webp")) {
    return pipeline.webp({ quality: 75 }).toBuffer();
  }
  return pipeline.jpeg({ quality: 80 }).toBuffer();
}
```

## Crop and Extract

```typescript
// Extract region
await sharp("input.jpg")
  .extract({ left: 100, top: 100, width: 400, height: 300 })
  .toFile("cropped.jpg");

// Trim whitespace
await sharp("input.png")
  .trim()
  .toFile("trimmed.png");

// Smart crop (attention-based)
await sharp("input.jpg")
  .resize(400, 400, { fit: "cover", position: sharp.strategy.attention })
  .toFile("smart-crop.jpg");
```

## Compositing (Watermarks and Overlays)

```typescript
// Add watermark
await sharp("photo.jpg")
  .composite([
    {
      input: "watermark.png",
      gravity: "southeast",
      blend: "over",
    },
  ])
  .toFile("watermarked.jpg");

// Text overlay (create SVG text first)
const textSvg = Buffer.from(`
  <svg width="400" height="50">
    <text x="10" y="35" font-size="24" fill="white" font-family="Arial">
      Copyright 2024
    </text>
  </svg>
`);

await sharp("photo.jpg")
  .composite([{ input: textSvg, gravity: "south" }])
  .toFile("labeled.jpg");

// Multiple overlays
await sharp("background.jpg")
  .composite([
    { input: "logo.png", top: 10, left: 10 },
    { input: "badge.png", gravity: "northeast" },
  ])
  .toFile("composed.jpg");
```

## Metadata

```typescript
// Read metadata
const metadata = await sharp("input.jpg").metadata();
console.log(metadata.width, metadata.height, metadata.format);

// Read and strip EXIF
await sharp("photo.jpg")
  .rotate() // Auto-rotate based on EXIF
  .withMetadata({ exif: {} }) // Strip EXIF
  .toFile("clean.jpg");

// Get image stats
const stats = await sharp("input.jpg").stats();
console.log("Dominant color:", stats.dominant);
```

## Batch Processing

```typescript
import { glob } from "glob";
import path from "path";

async function batchOptimize(inputDir: string, outputDir: string) {
  const files = await glob(`${inputDir}/**/*.{jpg,jpeg,png}`);

  await Promise.all(
    files.map(async (file) => {
      const basename = path.basename(file, path.extname(file));
      const outPath = path.join(outputDir, `${basename}.webp`);

      await sharp(file)
        .resize(1200, 1200, { fit: "inside", withoutEnlargement: true })
        .webp({ quality: 80 })
        .toFile(outPath);
    }),
  );

  console.log(`Processed ${files.length} images`);
}
```

## Express Integration

```typescript
import express from "express";
import sharp from "sharp";

app.get("/images/:name", async (req, res) => {
  const { name } = req.params;
  const width = parseInt(req.query.w as string) || undefined;
  const height = parseInt(req.query.h as string) || undefined;
  const format = (req.query.f as string) || "webp";

  const pipeline = sharp(`uploads/${name}`);

  if (width || height) pipeline.resize(width, height, { fit: "inside" });

  if (format === "webp") pipeline.webp({ quality: 80 });
  else if (format === "avif") pipeline.avif({ quality: 50 });
  else pipeline.jpeg({ quality: 85 });

  res.type(`image/${format}`);
  pipeline.pipe(res);
});
```

## Additional Resources

- Sharp docs: https://sharp.pixelplumbing.com/
- API reference: https://sharp.pixelplumbing.com/api-constructor
- Performance tips: https://sharp.pixelplumbing.com/performance
