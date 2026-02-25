---
name: s3-storage
description: AWS S3 and object storage patterns covering bucket configuration, presigned URLs for uploads and downloads, multipart uploads, lifecycle policies, access control, CloudFront CDN integration, S3-compatible stores (R2, MinIO), and cost optimization strategies.
---

# S3 Storage

This skill should be used when working with AWS S3 or S3-compatible object storage. It covers uploads, downloads, presigned URLs, CDN integration, and lifecycle management.

## When to Use This Skill

Use this skill when you need to:

- Upload and download files from S3
- Generate presigned URLs for direct browser uploads
- Set up lifecycle policies and versioning
- Integrate with CloudFront CDN
- Use S3-compatible stores (R2, MinIO)

## AWS SDK v3 Setup

```typescript
import { S3Client, PutObjectCommand, GetObjectCommand, DeleteObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

const s3 = new S3Client({
  region: process.env.AWS_REGION ?? "us-east-1",
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  },
});

const BUCKET = process.env.S3_BUCKET!;
```

## Presigned Upload URL

```typescript
// Server: generate presigned PUT URL
async function getUploadUrl(key: string, contentType: string) {
  const command = new PutObjectCommand({
    Bucket: BUCKET,
    Key: key,
    ContentType: contentType,
  });

  const url = await getSignedUrl(s3, command, { expiresIn: 600 }); // 10 minutes
  return { url, key };
}

// API route
app.post("/api/upload-url", async (req, res) => {
  const { filename, contentType } = req.body;
  const key = `uploads/${Date.now()}-${filename}`;
  const { url } = await getUploadUrl(key, contentType);
  res.json({ uploadUrl: url, key });
});
```

```typescript
// Client: upload directly to S3
async function uploadFile(file: File) {
  // 1. Get presigned URL from server
  const res = await fetch("/api/upload-url", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ filename: file.name, contentType: file.type }),
  });
  const { uploadUrl, key } = await res.json();

  // 2. Upload directly to S3
  await fetch(uploadUrl, {
    method: "PUT",
    headers: { "Content-Type": file.type },
    body: file,
  });

  return key;
}
```

## Download with Presigned URL

```typescript
async function getDownloadUrl(key: string, filename?: string) {
  const command = new GetObjectCommand({
    Bucket: BUCKET,
    Key: key,
    ResponseContentDisposition: filename ? `attachment; filename="${filename}"` : undefined,
  });

  return getSignedUrl(s3, command, { expiresIn: 3600 }); // 1 hour
}
```

## Server-Side Upload

```typescript
import { Upload } from "@aws-sdk/lib-storage";

async function uploadStream(key: string, stream: ReadableStream, contentType: string) {
  const upload = new Upload({
    client: s3,
    params: {
      Bucket: BUCKET,
      Key: key,
      Body: stream,
      ContentType: contentType,
    },
    partSize: 10 * 1024 * 1024, // 10 MB parts
    leavePartsOnError: false,
  });

  upload.on("httpUploadProgress", (progress) => {
    console.log(`Uploaded: ${progress.loaded}/${progress.total}`);
  });

  await upload.done();
}
```

## Cloudflare R2 (S3-Compatible)

```typescript
const r2 = new S3Client({
  region: "auto",
  endpoint: `https://${process.env.CF_ACCOUNT_ID}.r2.cloudflarestorage.com`,
  credentials: {
    accessKeyId: process.env.R2_ACCESS_KEY!,
    secretAccessKey: process.env.R2_SECRET_KEY!,
  },
});

// Same API as S3
await r2.send(new PutObjectCommand({
  Bucket: "my-bucket",
  Key: "file.txt",
  Body: "Hello R2",
}));
```

## Lifecycle Policies

```json
{
  "Rules": [
    {
      "ID": "move-to-glacier-after-90-days",
      "Status": "Enabled",
      "Transitions": [
        { "Days": 90, "StorageClass": "GLACIER" }
      ]
    },
    {
      "ID": "delete-temp-after-1-day",
      "Status": "Enabled",
      "Filter": { "Prefix": "tmp/" },
      "Expiration": { "Days": 1 }
    }
  ]
}
```

## Storage Strategy

```
STORAGE CLASS       COST      ACCESS TIME    USE CASE
────────────────────────────────────────────────────────
S3 Standard         $$$       Milliseconds   Frequently accessed
S3 IA               $$        Milliseconds   Infrequent (>30 days)
S3 Glacier IR       $         Milliseconds   Archive, instant retrieval
S3 Glacier          ¢         Minutes-hours  Long-term archive
S3 Deep Glacier     ¢¢        12-48 hours    Compliance/backup

COST OPTIMIZATION:
  [ ] Use lifecycle rules to transition old objects
  [ ] Enable S3 Intelligent-Tiering for unpredictable access
  [ ] Compress files before upload
  [ ] Use CloudFront or R2 to avoid S3 egress fees
  [ ] Set appropriate expiration for temporary uploads
```

## Additional Resources

- AWS S3 docs: https://docs.aws.amazon.com/s3/
- Cloudflare R2: https://developers.cloudflare.com/r2/
- MinIO: https://min.io/
