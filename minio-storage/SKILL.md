---
name: minio-storage
description: MinIO object storage patterns covering bucket operations, presigned URLs, notifications, versioning, lifecycle policies, and S3-compatible API usage.
---

# MinIO Storage

This skill should be used when implementing S3-compatible object storage with MinIO. It covers bucket operations, presigned URLs, notifications, versioning, and lifecycle policies.

## When to Use This Skill

Use this skill when you need to:

- Set up S3-compatible object storage
- Upload and download files with presigned URLs
- Configure bucket notifications and events
- Implement versioning and lifecycle policies
- Use MinIO for local development and testing

## Basic Operations

```typescript
import { Client } from "minio";

const minio = new Client({
  endPoint: "localhost",
  port: 9000,
  useSSL: false,
  accessKey: "minioadmin",
  secretKey: "minioadmin",
});

// Create bucket
const exists = await minio.bucketExists("uploads");
if (!exists) {
  await minio.makeBucket("uploads", "us-east-1");
}

// Upload file
await minio.fPutObject("uploads", "photos/image.jpg", "/path/to/image.jpg", {
  "Content-Type": "image/jpeg",
  "x-amz-meta-user-id": "user-123",
});

// Upload from buffer/stream
await minio.putObject("uploads", "data/report.json", Buffer.from(JSON.stringify(data)), {
  "Content-Type": "application/json",
});

// Download file
await minio.fGetObject("uploads", "photos/image.jpg", "/tmp/image.jpg");

// Get object as stream
const stream = await minio.getObject("uploads", "photos/image.jpg");
```

## Presigned URLs

```typescript
// Generate upload URL (PUT)
const uploadUrl = await minio.presignedPutObject("uploads", "photos/new-image.jpg", 3600);

// Generate download URL (GET)
const downloadUrl = await minio.presignedGetObject("uploads", "photos/image.jpg", 3600);

// Presigned POST policy (for browser uploads)
const policy = minio.newPostPolicy();
policy.setBucket("uploads");
policy.setKeyStartsWith("uploads/user-123/");
policy.setContentLengthRange(0, 10 * 1024 * 1024); // max 10MB
policy.setExpires(new Date(Date.now() + 3600 * 1000));

const { postURL, formData } = await minio.presignedPostPolicy(policy);
```

## List and Delete

```typescript
// List objects
const objects = [];
const stream = minio.listObjectsV2("uploads", "photos/", true);
for await (const obj of stream) {
  objects.push({ name: obj.name, size: obj.size, lastModified: obj.lastModified });
}

// Delete object
await minio.removeObject("uploads", "photos/old-image.jpg");

// Delete multiple objects
await minio.removeObjects("uploads", [
  "photos/temp1.jpg",
  "photos/temp2.jpg",
]);
```

## Bucket Notifications

```typescript
// Listen for object events
const listener = minio.listenBucketNotification("uploads", "photos/", ".jpg", [
  "s3:ObjectCreated:*",
  "s3:ObjectRemoved:*",
]);

listener.on("notification", (record) => {
  console.log("Event:", record.eventName);
  console.log("Object:", record.s3.object.key);
});
```

## Versioning and Lifecycle

```typescript
// Enable versioning
await minio.setBucketVersioning("uploads", { Status: "Enabled" });

// Set lifecycle rules
await minio.setBucketLifecycle("uploads", {
  Rule: [
    {
      ID: "expire-temp",
      Status: "Enabled",
      Filter: { Prefix: "temp/" },
      Expiration: { Days: 7 },
    },
    {
      ID: "transition-archive",
      Status: "Enabled",
      Filter: { Prefix: "archive/" },
      Transition: { Days: 30, StorageClass: "GLACIER" },
    },
  ],
});
```

## Docker Compose

```yaml
services:
  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
    volumes:
      - minio-data:/data

volumes:
  minio-data:
```

## Additional Resources

- MinIO: https://min.io/docs/minio/linux/
- JavaScript Client: https://min.io/docs/minio/linux/developers/javascript/
- S3 Compatibility: https://min.io/docs/minio/linux/reference/s3-api-compatibility.html
