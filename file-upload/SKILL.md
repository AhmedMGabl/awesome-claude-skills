---
name: file-upload
description: File upload implementation covering multipart uploads with Multer, presigned S3 URLs for direct-to-cloud uploads, chunked/resumable uploads with tus protocol, image/video processing pipelines, file type validation, progress tracking, drag-and-drop UI, and storage provider abstraction patterns.
---

# File Upload

This skill should be used when implementing file upload functionality. It covers server-side upload handling, direct-to-cloud uploads, chunked transfers, validation, and processing pipelines.

## When to Use This Skill

Use this skill when you need to:

- Handle file uploads in web applications
- Upload directly to S3/cloud storage
- Implement chunked/resumable uploads
- Validate file types and sizes
- Process uploaded files (images, videos)
- Build drag-and-drop upload UI

## Multer (Server-Side)

```typescript
import multer from "multer";
import path from "path";

// File validation
const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 },  // 10MB
  fileFilter: (req, file, cb) => {
    const allowed = [".jpg", ".jpeg", ".png", ".webp", ".pdf"];
    const ext = path.extname(file.originalname).toLowerCase();
    if (allowed.includes(ext)) {
      cb(null, true);
    } else {
      cb(new Error(`File type ${ext} not allowed`));
    }
  },
});

// Single file upload
app.post("/api/upload/avatar", authenticate, upload.single("avatar"), async (req, res) => {
  if (!req.file) return res.status(400).json({ error: "No file provided" });

  // Process and upload to S3
  const optimized = await sharp(req.file.buffer).resize(256, 256).webp({ quality: 80 }).toBuffer();

  const key = `avatars/${req.user.id}.webp`;
  await s3.putObject({ Bucket: BUCKET, Key: key, Body: optimized, ContentType: "image/webp" });

  res.json({ url: `${CDN_URL}/${key}` });
});

// Multiple files
app.post("/api/upload/documents", authenticate, upload.array("files", 5), async (req, res) => {
  const files = req.files as Express.Multer.File[];
  const results = await Promise.all(
    files.map((file) => uploadToS3(file.buffer, file.originalname, file.mimetype)),
  );
  res.json({ files: results });
});
```

## Presigned URL (Direct-to-S3)

```typescript
import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

const s3 = new S3Client({ region: process.env.AWS_REGION });

// Server: Generate presigned URL
app.post("/api/upload/presign", authenticate, async (req, res) => {
  const { filename, contentType } = req.body;

  // Validate
  const allowedTypes = ["image/jpeg", "image/png", "image/webp", "application/pdf"];
  if (!allowedTypes.includes(contentType)) {
    return res.status(400).json({ error: "File type not allowed" });
  }

  const key = `uploads/${req.user.id}/${Date.now()}-${filename}`;
  const command = new PutObjectCommand({
    Bucket: process.env.S3_BUCKET!,
    Key: key,
    ContentType: contentType,
  });

  const uploadUrl = await getSignedUrl(s3, command, { expiresIn: 300 });
  res.json({ uploadUrl, key });
});

// Client: Upload directly to S3
async function uploadFile(file: File, onProgress?: (pct: number) => void) {
  // Get presigned URL
  const { uploadUrl, key } = await fetch("/api/upload/presign", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ filename: file.name, contentType: file.type }),
  }).then((r) => r.json());

  // Upload with progress tracking
  return new Promise<string>((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.upload.addEventListener("progress", (e) => {
      if (e.lengthComputable) onProgress?.(Math.round((e.loaded / e.total) * 100));
    });
    xhr.addEventListener("load", () => {
      if (xhr.status === 200) resolve(key);
      else reject(new Error(`Upload failed: ${xhr.status}`));
    });
    xhr.addEventListener("error", () => reject(new Error("Upload failed")));
    xhr.open("PUT", uploadUrl);
    xhr.setRequestHeader("Content-Type", file.type);
    xhr.send(file);
  });
}
```

## React Drag-and-Drop Upload

```tsx
import { useCallback, useState } from "react";

function FileDropZone({ onUpload }: { onUpload: (files: File[]) => void }) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    onUpload(files);
  }, [onUpload]);

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors
        ${isDragging ? "border-blue-500 bg-blue-50" : "border-gray-300"}`}
    >
      <input
        type="file"
        multiple
        onChange={(e) => onUpload(Array.from(e.target.files ?? []))}
        className="hidden"
        id="file-input"
      />
      <label htmlFor="file-input" className="cursor-pointer">
        <p className="text-gray-600">Drag and drop files here, or click to browse</p>
        <p className="text-sm text-gray-400 mt-1">Max 10MB per file. JPG, PNG, PDF.</p>
      </label>
    </div>
  );
}
```

## Additional Resources

- Multer: https://github.com/expressjs/multer
- AWS S3 presigned URLs: https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html
- tus (resumable uploads): https://tus.io/
- UploadThing: https://uploadthing.com/
