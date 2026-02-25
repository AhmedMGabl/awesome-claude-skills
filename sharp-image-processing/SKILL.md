---
name: sharp-image-processing
description: Sharp image processing covering resizing, format conversion, compression, watermarks, metadata extraction, batch processing, thumbnail generation, and integration with Node.js upload pipelines.
---

# Sharp Image Processing

This skill should be used when processing images in Node.js with Sharp. It covers resizing, format conversion, watermarks, metadata, and batch processing.

## When to Use This Skill

Use this skill when you need to:

- Resize and optimize images for the web
- Convert between image formats (WebP, AVIF, PNG, JPEG)
- Generate thumbnails and responsive image variants
- Add watermarks and overlays
- Extract and modify image metadata

## Basic Operations

```typescript
import sharp from "sharp";

// Resize and convert
await sharp("input.jpg")
  .resize(800, 600, { fit: "cover", position: "center" })
  .webp({ quality: 80 })
  .toFile("output.webp");

// Resize to width, maintain aspect ratio
await sharp("input.png")
  .resize({ width: 1200 })
  .jpeg({ quality: 85, progressive: true })
  .toFile("output.jpg");

// Buffer in, buffer out
const buffer = await sharp(inputBuffer)
  .resize(400, 400, { fit: "inside" })
  .avif({ quality: 65 })
  .toBuffer();
```

## Responsive Image Variants

```typescript
const sizes = [
  { width: 320, suffix: "sm" },
  { width: 640, suffix: "md" },
  { width: 1024, suffix: "lg" },
  { width: 1920, suffix: "xl" },
];

async function generateVariants(inputPath: string, outputDir: string) {
  const filename = path.parse(inputPath).name;

  return Promise.all(
    sizes.map(({ width, suffix }) =>
      sharp(inputPath)
        .resize({ width })
        .webp({ quality: 80 })
        .toFile(path.join(outputDir, `${filename}-${suffix}.webp`)),
    ),
  );
}
```

## Watermark

```typescript
async function addWatermark(imagePath: string, watermarkPath: string) {
  const image = sharp(imagePath);
  const metadata = await image.metadata();

  const watermark = await sharp(watermarkPath)
    .resize({
      width: Math.round((metadata.width ?? 800) * 0.2),
    })
    .ensureAlpha(0.5)
    .toBuffer();

  return image
    .composite([
      {
        input: watermark,
        gravity: "southeast",
        blend: "over",
      },
    ])
    .toBuffer();
}

// Text watermark
async function addTextWatermark(imagePath: string, text: string) {
  const metadata = await sharp(imagePath).metadata();
  const width = metadata.width ?? 800;

  const svgText = `
    <svg width="${width}" height="50">
      <text x="50%" y="50%" text-anchor="middle" font-size="24"
            fill="white" opacity="0.7" font-family="Arial">
        ${text}
      </text>
    </svg>
  `;

  return sharp(imagePath)
    .composite([{ input: Buffer.from(svgText), gravity: "south" }])
    .toBuffer();
}
```

## Metadata

```typescript
async function getImageInfo(imagePath: string) {
  const metadata = await sharp(imagePath).metadata();
  return {
    width: metadata.width,
    height: metadata.height,
    format: metadata.format,
    size: metadata.size,
    hasAlpha: metadata.hasAlpha,
    orientation: metadata.orientation,
    exif: metadata.exif,
  };
}

// Strip EXIF data
await sharp("photo.jpg")
  .rotate() // Auto-rotate based on EXIF
  .withMetadata({ orientation: undefined }) // Strip orientation
  .jpeg({ quality: 85 })
  .toFile("clean.jpg");
```

## Upload Pipeline

```typescript
import multer from "multer";

const upload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 10 * 1024 * 1024 } });

app.post("/upload", upload.single("image"), async (req, res) => {
  if (!req.file) return res.status(400).json({ error: "No file" });

  const processed = await sharp(req.file.buffer)
    .resize({ width: 1200, withoutEnlargement: true })
    .webp({ quality: 80 })
    .toBuffer();

  // Upload to S3
  await s3.send(new PutObjectCommand({
    Bucket: "images",
    Key: `uploads/${Date.now()}.webp`,
    Body: processed,
    ContentType: "image/webp",
  }));

  res.json({ success: true });
});
```

## Batch Processing

```typescript
import { glob } from "glob";

async function batchOptimize(inputDir: string, outputDir: string) {
  const files = await glob(`${inputDir}/**/*.{jpg,jpeg,png}`);

  const results = await Promise.allSettled(
    files.map(async (file) => {
      const relative = path.relative(inputDir, file);
      const output = path.join(outputDir, relative.replace(/\.\w+$/, ".webp"));
      await fs.mkdir(path.dirname(output), { recursive: true });

      const info = await sharp(file)
        .resize({ width: 1920, withoutEnlargement: true })
        .webp({ quality: 80 })
        .toFile(output);

      return { file, output, savedBytes: (await fs.stat(file)).size - info.size };
    }),
  );

  const succeeded = results.filter((r) => r.status === "fulfilled").length;
  console.log(`Processed ${succeeded}/${files.length} images`);
}
```

## Additional Resources

- Sharp docs: https://sharp.pixelplumbing.com/
- Sharp API: https://sharp.pixelplumbing.com/api-constructor
