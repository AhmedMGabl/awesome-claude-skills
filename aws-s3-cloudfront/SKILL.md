---
name: aws-s3-cloudfront
description: "Comprehensive toolkit for AWS S3 storage operations and CloudFront CDN configuration. This skill should be used when building file storage systems, generating presigned URLs, configuring CDN distributions, managing cache invalidation, setting up static website hosting, implementing Lambda@Edge functions, or provisioning S3/CloudFront infrastructure with CDK and CloudFormation."
---

# AWS S3 & CloudFront Skill

## Overview

This skill provides production-grade patterns for AWS S3 object storage and CloudFront content delivery. All code examples use AWS SDK v3 (modular imports) with TypeScript. Adapt patterns to JavaScript, Python (boto3), or other SDKs as needed.

---

## S3 Client Setup

Initialize the S3 client with proper configuration before performing any operations.

```typescript
import {
  S3Client,
  PutObjectCommand,
  GetObjectCommand,
  DeleteObjectCommand,
  ListObjectsV2Command,
  CreateMultipartUploadCommand,
  UploadPartCommand,
  CompleteMultipartUploadCommand,
  AbortMultipartUploadCommand,
  HeadObjectCommand,
} from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

const s3 = new S3Client({
  region: process.env.AWS_REGION ?? "us-east-1",
  // Optional: explicit credentials (prefer IAM roles or environment variables)
  // credentials: {
  //   accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
  //   secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  // },
});

const BUCKET = process.env.S3_BUCKET_NAME!;
```

---

## S3 Core Operations

### Upload an Object

```typescript
import { PutObjectCommand } from "@aws-sdk/client-s3";
import { readFile } from "node:fs/promises";
import { lookup } from "mime-types";

async function uploadFile(key: string, filePath: string): Promise<string> {
  const body = await readFile(filePath);
  const contentType = lookup(filePath) || "application/octet-stream";

  await s3.send(
    new PutObjectCommand({
      Bucket: BUCKET,
      Key: key,
      Body: body,
      ContentType: contentType,
      // Optional: server-side encryption
      ServerSideEncryption: "AES256",
      // Optional: storage class
      // StorageClass: "INTELLIGENT_TIERING",
    })
  );

  return `s3://${BUCKET}/${key}`;
}
```

### Upload from a Stream

```typescript
import { Upload } from "@aws-sdk/lib-storage";
import { createReadStream } from "node:fs";

async function uploadStream(key: string, filePath: string): Promise<void> {
  const stream = createReadStream(filePath);

  const upload = new Upload({
    client: s3,
    params: {
      Bucket: BUCKET,
      Key: key,
      Body: stream,
      ContentType: lookup(filePath) || "application/octet-stream",
    },
    // Automatically switches to multipart for large files
    partSize: 10 * 1024 * 1024, // 10 MB parts
    leavePartsOnError: false,
  });

  upload.on("httpUploadProgress", (progress) => {
    console.log(`Uploaded: ${progress.loaded}/${progress.total} bytes`);
  });

  await upload.done();
}
```

### Download an Object

```typescript
import { GetObjectCommand } from "@aws-sdk/client-s3";
import { writeFile } from "node:fs/promises";
import { Readable } from "node:stream";

async function downloadFile(key: string, destPath: string): Promise<void> {
  const response = await s3.send(
    new GetObjectCommand({
      Bucket: BUCKET,
      Key: key,
    })
  );

  if (!response.Body) {
    throw new Error(`Empty response body for key: ${key}`);
  }

  // SDK v3 returns a ReadableStream; convert to Buffer
  const chunks: Uint8Array[] = [];
  for await (const chunk of response.Body as Readable) {
    chunks.push(chunk);
  }
  await writeFile(destPath, Buffer.concat(chunks));
}

// Stream variant for large files
async function downloadStream(key: string): Promise<Readable> {
  const response = await s3.send(
    new GetObjectCommand({ Bucket: BUCKET, Key: key })
  );
  return response.Body as Readable;
}
```

### List Objects

```typescript
import { ListObjectsV2Command } from "@aws-sdk/client-s3";

interface S3Object {
  key: string;
  size: number;
  lastModified: Date;
}

async function listObjects(prefix: string, maxKeys = 1000): Promise<S3Object[]> {
  const objects: S3Object[] = [];
  let continuationToken: string | undefined;

  do {
    const response = await s3.send(
      new ListObjectsV2Command({
        Bucket: BUCKET,
        Prefix: prefix,
        MaxKeys: Math.min(maxKeys - objects.length, 1000),
        ContinuationToken: continuationToken,
      })
    );

    for (const item of response.Contents ?? []) {
      objects.push({
        key: item.Key!,
        size: item.Size!,
        lastModified: item.LastModified!,
      });
    }

    continuationToken = response.IsTruncated
      ? response.NextContinuationToken
      : undefined;
  } while (continuationToken && objects.length < maxKeys);

  return objects;
}
```

### Delete Objects

```typescript
import {
  DeleteObjectCommand,
  DeleteObjectsCommand,
} from "@aws-sdk/client-s3";

// Single delete
async function deleteObject(key: string): Promise<void> {
  await s3.send(
    new DeleteObjectCommand({
      Bucket: BUCKET,
      Key: key,
    })
  );
}

// Batch delete (up to 1000 keys per request)
async function deleteObjects(keys: string[]): Promise<void> {
  const BATCH_SIZE = 1000;

  for (let i = 0; i < keys.length; i += BATCH_SIZE) {
    const batch = keys.slice(i, i + BATCH_SIZE);
    await s3.send(
      new DeleteObjectsCommand({
        Bucket: BUCKET,
        Delete: {
          Objects: batch.map((key) => ({ Key: key })),
          Quiet: true,
        },
      })
    );
  }
}

// Delete all objects under a prefix
async function deletePrefix(prefix: string): Promise<number> {
  const objects = await listObjects(prefix);
  if (objects.length === 0) return 0;

  await deleteObjects(objects.map((o) => o.key));
  return objects.length;
}
```

### Check If Object Exists

```typescript
import { HeadObjectCommand, NotFound } from "@aws-sdk/client-s3";

async function objectExists(key: string): Promise<boolean> {
  try {
    await s3.send(new HeadObjectCommand({ Bucket: BUCKET, Key: key }));
    return true;
  } catch (err) {
    if (err instanceof NotFound || (err as any).name === "NotFound") {
      return false;
    }
    throw err;
  }
}
```

---

## Presigned URLs

Generate time-limited URLs for secure upload and download without exposing AWS credentials.

### Presigned Download URL

```typescript
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
import { GetObjectCommand } from "@aws-sdk/client-s3";

async function getDownloadUrl(
  key: string,
  expiresInSeconds = 3600
): Promise<string> {
  const command = new GetObjectCommand({
    Bucket: BUCKET,
    Key: key,
    // Optional: force download with a specific filename
    ResponseContentDisposition: `attachment; filename="${key.split("/").pop()}"`,
  });

  return getSignedUrl(s3, command, { expiresIn: expiresInSeconds });
}
```

### Presigned Upload URL

```typescript
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
import { PutObjectCommand } from "@aws-sdk/client-s3";

interface UploadUrlResult {
  url: string;
  key: string;
  expiresAt: Date;
}

async function getUploadUrl(
  key: string,
  contentType: string,
  maxSizeBytes?: number,
  expiresInSeconds = 3600
): Promise<UploadUrlResult> {
  const command = new PutObjectCommand({
    Bucket: BUCKET,
    Key: key,
    ContentType: contentType,
    // Optional: limit file size via content-length condition
    ...(maxSizeBytes && { ContentLength: maxSizeBytes }),
    ServerSideEncryption: "AES256",
  });

  const url = await getSignedUrl(s3, command, { expiresIn: expiresInSeconds });

  return {
    url,
    key,
    expiresAt: new Date(Date.now() + expiresInSeconds * 1000),
  };
}
```

### Presigned POST (Browser-Based Uploads with Conditions)

```typescript
import { createPresignedPost } from "@aws-sdk/s3-presigned-post";

interface PostUploadResult {
  url: string;
  fields: Record<string, string>;
}

async function getPresignedPost(
  keyPrefix: string,
  maxSizeMB = 50,
  expiresInSeconds = 3600
): Promise<PostUploadResult> {
  const { url, fields } = await createPresignedPost(s3, {
    Bucket: BUCKET,
    Key: `${keyPrefix}/\${filename}`,
    Conditions: [
      ["content-length-range", 0, maxSizeMB * 1024 * 1024],
      ["starts-with", "$Content-Type", ""],
      ["starts-with", "$key", keyPrefix],
    ],
    Fields: {
      "x-amz-server-side-encryption": "AES256",
    },
    Expires: expiresInSeconds,
  });

  return { url, fields };
}
```

**Client-side usage for presigned POST:**

```html
<form id="upload-form" method="post" enctype="multipart/form-data">
  <!-- Fields injected dynamically from the presigned POST response -->
  <input type="file" name="file" />
  <button type="submit">Upload</button>
</form>

<script>
async function upload(file) {
  const { url, fields } = await fetch("/api/upload-url").then(r => r.json());
  const formData = new FormData();
  Object.entries(fields).forEach(([k, v]) => formData.append(k, v));
  formData.append("file", file); // Must be last
  await fetch(url, { method: "POST", body: formData });
}
</script>
```

---

## Multipart Upload

For files larger than 100 MB, use multipart upload to improve reliability and throughput.

### Manual Multipart Upload

```typescript
import {
  CreateMultipartUploadCommand,
  UploadPartCommand,
  CompleteMultipartUploadCommand,
  AbortMultipartUploadCommand,
} from "@aws-sdk/client-s3";
import { createReadStream, statSync } from "node:fs";

interface MultipartUploadOptions {
  key: string;
  filePath: string;
  partSizeMB?: number;
  contentType?: string;
}

async function multipartUpload(opts: MultipartUploadOptions): Promise<string> {
  const { key, filePath, partSizeMB = 10, contentType } = opts;
  const partSize = partSizeMB * 1024 * 1024;
  const fileSize = statSync(filePath).size;
  const totalParts = Math.ceil(fileSize / partSize);

  // 1. Initiate multipart upload
  const { UploadId } = await s3.send(
    new CreateMultipartUploadCommand({
      Bucket: BUCKET,
      Key: key,
      ContentType: contentType ?? "application/octet-stream",
      ServerSideEncryption: "AES256",
    })
  );

  try {
    // 2. Upload parts (can be parallelized)
    const parts: { ETag: string; PartNumber: number }[] = [];

    for (let partNum = 1; partNum <= totalParts; partNum++) {
      const start = (partNum - 1) * partSize;
      const end = Math.min(start + partSize, fileSize);

      const stream = createReadStream(filePath, { start, end: end - 1 });
      const chunks: Buffer[] = [];
      for await (const chunk of stream) {
        chunks.push(chunk as Buffer);
      }

      const { ETag } = await s3.send(
        new UploadPartCommand({
          Bucket: BUCKET,
          Key: key,
          UploadId,
          PartNumber: partNum,
          Body: Buffer.concat(chunks),
        })
      );

      parts.push({ ETag: ETag!, PartNumber: partNum });
      console.log(`Part ${partNum}/${totalParts} uploaded`);
    }

    // 3. Complete multipart upload
    await s3.send(
      new CompleteMultipartUploadCommand({
        Bucket: BUCKET,
        Key: key,
        UploadId,
        MultipartUpload: {
          Parts: parts.sort((a, b) => a.PartNumber - b.PartNumber),
        },
      })
    );

    return `s3://${BUCKET}/${key}`;
  } catch (err) {
    // Abort on failure to avoid orphaned parts
    await s3.send(
      new AbortMultipartUploadCommand({
        Bucket: BUCKET,
        Key: key,
        UploadId,
      })
    );
    throw err;
  }
}
```

### Parallel Multipart Upload with Retry

```typescript
import pLimit from "p-limit";

async function parallelMultipartUpload(
  key: string,
  filePath: string,
  concurrency = 4,
  maxRetries = 3
): Promise<string> {
  const partSize = 10 * 1024 * 1024; // 10 MB
  const fileSize = statSync(filePath).size;
  const totalParts = Math.ceil(fileSize / partSize);
  const limit = pLimit(concurrency);

  const { UploadId } = await s3.send(
    new CreateMultipartUploadCommand({
      Bucket: BUCKET,
      Key: key,
      ServerSideEncryption: "AES256",
    })
  );

  try {
    const uploadPart = async (partNum: number): Promise<{ ETag: string; PartNumber: number }> => {
      const start = (partNum - 1) * partSize;
      const end = Math.min(start + partSize, fileSize);
      const stream = createReadStream(filePath, { start, end: end - 1 });
      const chunks: Buffer[] = [];
      for await (const chunk of stream) {
        chunks.push(chunk as Buffer);
      }
      const body = Buffer.concat(chunks);

      for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
          const { ETag } = await s3.send(
            new UploadPartCommand({
              Bucket: BUCKET,
              Key: key,
              UploadId,
              PartNumber: partNum,
              Body: body,
            })
          );
          return { ETag: ETag!, PartNumber: partNum };
        } catch (err) {
          if (attempt === maxRetries) throw err;
          await new Promise((r) => setTimeout(r, 1000 * attempt));
        }
      }
      throw new Error("Unreachable");
    };

    const parts = await Promise.all(
      Array.from({ length: totalParts }, (_, i) =>
        limit(() => uploadPart(i + 1))
      )
    );

    await s3.send(
      new CompleteMultipartUploadCommand({
        Bucket: BUCKET,
        Key: key,
        UploadId,
        MultipartUpload: {
          Parts: parts.sort((a, b) => a.PartNumber - b.PartNumber),
        },
      })
    );

    return `s3://${BUCKET}/${key}`;
  } catch (err) {
    await s3.send(
      new AbortMultipartUploadCommand({ Bucket: BUCKET, Key: key, UploadId })
    );
    throw err;
  }
}
```

---

## S3 Bucket Policies and CORS

### Bucket Policy: Public Read for a Prefix

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadForPublicAssets",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-bucket/public/*"
    }
  ]
}
```

### Bucket Policy: Restrict Access to CloudFront Only (OAC)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCloudFrontServicePrincipal",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudfront.amazonaws.com"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-bucket/*",
      "Condition": {
        "StringEquals": {
          "AWS:SourceArn": "arn:aws:cloudfront::123456789012:distribution/EDFDVBD6EXAMPLE"
        }
      }
    }
  ]
}
```

### Bucket Policy: Enforce Encryption in Transit

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyUnencryptedTransport",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/*"
      ],
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    }
  ]
}
```

### CORS Configuration

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
    "AllowedOrigins": [
      "https://example.com",
      "https://*.example.com"
    ],
    "ExposeHeaders": [
      "ETag",
      "x-amz-request-id",
      "x-amz-id-2"
    ],
    "MaxAgeSeconds": 86400
  }
]
```

Apply CORS programmatically:

```typescript
import { PutBucketCorsCommand } from "@aws-sdk/client-s3";

async function setCors(bucket: string, origins: string[]): Promise<void> {
  await s3.send(
    new PutBucketCorsCommand({
      Bucket: bucket,
      CORSConfiguration: {
        CORSRules: [
          {
            AllowedHeaders: ["*"],
            AllowedMethods: ["GET", "PUT", "POST", "DELETE", "HEAD"],
            AllowedOrigins: origins,
            ExposeHeaders: ["ETag"],
            MaxAgeSeconds: 86400,
          },
        ],
      },
    })
  );
}
```

---

## Static Website Hosting

### Enable Static Hosting on S3

```typescript
import { PutBucketWebsiteCommand } from "@aws-sdk/client-s3";

async function enableStaticHosting(bucket: string): Promise<void> {
  await s3.send(
    new PutBucketWebsiteCommand({
      Bucket: bucket,
      WebsiteConfiguration: {
        IndexDocument: { Suffix: "index.html" },
        ErrorDocument: { Key: "404.html" },
        RoutingRules: [
          {
            Condition: { KeyPrefixEquals: "docs/" },
            Redirect: {
              ReplaceKeyPrefixWith: "documentation/",
              HttpRedirectCode: "301",
            },
          },
        ],
      },
    })
  );
}
```

### Deploy a Static Site to S3

```typescript
import { readdirSync, statSync } from "node:fs";
import { join, relative } from "node:path";

async function deploySite(
  buildDir: string,
  bucket: string,
  prefix = ""
): Promise<number> {
  let count = 0;

  function walk(dir: string): string[] {
    const entries: string[] = [];
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      const fullPath = join(dir, entry.name);
      if (entry.isDirectory()) {
        entries.push(...walk(fullPath));
      } else {
        entries.push(fullPath);
      }
    }
    return entries;
  }

  const files = walk(buildDir);

  // Set cache headers based on file type
  function getCacheControl(filePath: string): string {
    if (filePath.endsWith(".html")) return "public, max-age=0, must-revalidate";
    if (/\.(js|css|woff2?|ttf|eot)$/.test(filePath))
      return "public, max-age=31536000, immutable";
    if (/\.(png|jpg|jpeg|gif|svg|ico|webp)$/.test(filePath))
      return "public, max-age=86400";
    return "public, max-age=3600";
  }

  for (const filePath of files) {
    const key = prefix
      ? `${prefix}/${relative(buildDir, filePath)}`
      : relative(buildDir, filePath);

    await s3.send(
      new PutObjectCommand({
        Bucket: bucket,
        Key: key.replace(/\\/g, "/"), // Normalize path separators
        Body: await readFile(filePath),
        ContentType: lookup(filePath) || "application/octet-stream",
        CacheControl: getCacheControl(filePath),
      })
    );
    count++;
  }

  return count;
}
```

---

## CloudFront Distribution Setup

### CloudFront Client Setup

```typescript
import {
  CloudFrontClient,
  CreateDistributionCommand,
  CreateInvalidationCommand,
  GetDistributionCommand,
  UpdateDistributionCommand,
} from "@aws-sdk/client-cloudfront";

const cf = new CloudFrontClient({
  region: "us-east-1", // CloudFront is global but API is in us-east-1
});
```

### Create a Distribution with S3 Origin (OAC)

```typescript
import {
  CreateDistributionCommand,
  CreateOriginAccessControlCommand,
} from "@aws-sdk/client-cloudfront";

async function createDistribution(
  bucket: string,
  domainName: string,
  certificateArn: string
): Promise<string> {
  // 1. Create Origin Access Control
  const { OriginAccessControl } = await cf.send(
    new CreateOriginAccessControlCommand({
      OriginAccessControlConfig: {
        Name: `oac-${bucket}`,
        OriginAccessControlOriginType: "s3",
        SigningBehavior: "always",
        SigningProtocol: "sigv4",
        Description: `OAC for ${bucket}`,
      },
    })
  );

  // 2. Create Distribution
  const { Distribution } = await cf.send(
    new CreateDistributionCommand({
      DistributionConfig: {
        CallerReference: `${bucket}-${Date.now()}`,
        Comment: `CDN for ${domainName}`,
        Enabled: true,

        Origins: {
          Quantity: 1,
          Items: [
            {
              Id: `S3-${bucket}`,
              DomainName: `${bucket}.s3.amazonaws.com`,
              OriginAccessControlId: OriginAccessControl!.Id!,
              S3OriginConfig: {
                OriginAccessIdentity: "", // Empty for OAC
              },
            },
          ],
        },

        DefaultCacheBehavior: {
          TargetOriginId: `S3-${bucket}`,
          ViewerProtocolPolicy: "redirect-to-https",
          AllowedMethods: {
            Quantity: 2,
            Items: ["GET", "HEAD"],
            CachedMethods: { Quantity: 2, Items: ["GET", "HEAD"] },
          },
          CachePolicyId: "658327ea-f89d-4fab-a63d-7e88639e58f6", // CachingOptimized
          OriginRequestPolicyId: "88a5eaf4-2fd4-4709-b370-b4c650ea3fcf", // CORS-S3Origin
          Compress: true,
        },

        // Custom domain
        Aliases: {
          Quantity: 1,
          Items: [domainName],
        },

        ViewerCertificate: {
          ACMCertificateArn: certificateArn,
          SSLSupportMethod: "sni-only",
          MinimumProtocolVersion: "TLSv1.2_2021",
        },

        DefaultRootObject: "index.html",

        // Custom error responses for SPA routing
        CustomErrorResponses: {
          Quantity: 1,
          Items: [
            {
              ErrorCode: 403,
              ResponseCode: 200,
              ResponsePagePath: "/index.html",
              ErrorCachingMinTTL: 10,
            },
          ],
        },

        HttpVersion: "http2and3",
        PriceClass: "PriceClass_100", // US, Canada, Europe only (cheapest)

        Restrictions: {
          GeoRestriction: { RestrictionType: "none", Quantity: 0 },
        },
      },
    })
  );

  return Distribution!.DomainName!;
}
```

### Common CloudFront Cache Policy IDs (Managed)

| Policy Name | ID | Use Case |
|---|---|---|
| CachingOptimized | `658327ea-f89d-4fab-a63d-7e88639e58f6` | Static assets, default |
| CachingDisabled | `4135ea2d-6df8-44a3-9df3-4b5a84be39ad` | Dynamic API responses |
| CachingOptimizedForUncompressedObjects | `b2884449-e4de-46a7-ac36-70bc7f1ddd6d` | Already-compressed assets |

### Common Origin Request Policy IDs (Managed)

| Policy Name | ID | Use Case |
|---|---|---|
| CORS-S3Origin | `88a5eaf4-2fd4-4709-b370-b4c650ea3fcf` | S3 with CORS |
| AllViewer | `216adef6-5c7f-47e4-b989-5492eafa07d3` | Forward all headers |
| AllViewerExceptHostHeader | `b689b0a8-53d0-40ab-baf2-68738e2966ac` | Custom origins |

---

## Cache Invalidation

### Invalidate Specific Paths

```typescript
import { CreateInvalidationCommand } from "@aws-sdk/client-cloudfront";

async function invalidateCache(
  distributionId: string,
  paths: string[]
): Promise<string> {
  // Paths must start with /
  const normalizedPaths = paths.map((p) => (p.startsWith("/") ? p : `/${p}`));

  const { Invalidation } = await cf.send(
    new CreateInvalidationCommand({
      DistributionId: distributionId,
      InvalidationBatch: {
        CallerReference: `inv-${Date.now()}`,
        Paths: {
          Quantity: normalizedPaths.length,
          Items: normalizedPaths,
        },
      },
    })
  );

  return Invalidation!.Id!;
}

// Usage examples:
// Invalidate specific file
await invalidateCache(distId, ["/index.html"]);

// Invalidate directory
await invalidateCache(distId, ["/assets/*"]);

// Invalidate everything (costs $0.005 per path after first 1000/month)
await invalidateCache(distId, ["/*"]);
```

### Wait for Invalidation to Complete

```typescript
import { GetInvalidationCommand } from "@aws-sdk/client-cloudfront";

async function waitForInvalidation(
  distributionId: string,
  invalidationId: string,
  timeoutMs = 300000
): Promise<void> {
  const start = Date.now();

  while (Date.now() - start < timeoutMs) {
    const { Invalidation } = await cf.send(
      new GetInvalidationCommand({
        DistributionId: distributionId,
        Id: invalidationId,
      })
    );

    if (Invalidation?.Status === "Completed") return;

    await new Promise((r) => setTimeout(r, 5000));
  }

  throw new Error(`Invalidation ${invalidationId} timed out after ${timeoutMs}ms`);
}
```

### Deploy and Invalidate Pattern

```typescript
async function deployAndInvalidate(
  buildDir: string,
  bucket: string,
  distributionId: string
): Promise<void> {
  // 1. Upload new files
  const count = await deploySite(buildDir, bucket);
  console.log(`Uploaded ${count} files`);

  // 2. Invalidate CloudFront cache
  const invId = await invalidateCache(distributionId, ["/*"]);
  console.log(`Invalidation ${invId} created`);

  // 3. Wait for propagation
  await waitForInvalidation(distributionId, invId);
  console.log("Invalidation complete");
}
```

---

## Lambda@Edge for Dynamic Content

Lambda@Edge functions run at CloudFront edge locations. There are four trigger points: viewer-request, origin-request, origin-response, and viewer-response.

### URL Rewriting (Origin Request)

Rewrite clean URLs to S3 keys (e.g., `/about` to `/about/index.html`).

```typescript
// Lambda@Edge: origin-request
// Must be deployed in us-east-1
import type {
  CloudFrontRequestEvent,
  CloudFrontRequestResult,
} from "aws-lambda";

export const handler = async (
  event: CloudFrontRequestEvent
): Promise<CloudFrontRequestResult> => {
  const request = event.Records[0].cf.request;
  const uri = request.uri;

  // Add index.html for directory requests
  if (uri.endsWith("/")) {
    request.uri += "index.html";
  } else if (!uri.includes(".")) {
    // Clean URL: /about -> /about/index.html
    request.uri += "/index.html";
  }

  return request;
};
```

### Security Headers (Viewer Response)

```typescript
// Lambda@Edge: viewer-response
import type {
  CloudFrontResponseEvent,
  CloudFrontResponseResult,
} from "aws-lambda";

export const handler = async (
  event: CloudFrontResponseEvent
): Promise<CloudFrontResponseResult> => {
  const response = event.Records[0].cf.response;
  const headers = response.headers;

  headers["strict-transport-security"] = [
    { key: "Strict-Transport-Security", value: "max-age=63072000; includeSubDomains; preload" },
  ];
  headers["x-content-type-options"] = [
    { key: "X-Content-Type-Options", value: "nosniff" },
  ];
  headers["x-frame-options"] = [
    { key: "X-Frame-Options", value: "DENY" },
  ];
  headers["referrer-policy"] = [
    { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  ];
  headers["content-security-policy"] = [
    {
      key: "Content-Security-Policy",
      value: "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self';",
    },
  ];
  headers["permissions-policy"] = [
    { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
  ];

  return response;
};
```

### A/B Testing (Viewer Request)

```typescript
// Lambda@Edge: viewer-request
import type {
  CloudFrontRequestEvent,
  CloudFrontRequestResult,
} from "aws-lambda";

export const handler = async (
  event: CloudFrontRequestEvent
): Promise<CloudFrontRequestResult> => {
  const request = event.Records[0].cf.request;
  const headers = request.headers;

  // Check for existing experiment cookie
  const cookies = headers.cookie || [];
  const experimentCookie = cookies
    .map((c) => c.value)
    .join("; ")
    .match(/experiment=([^;]+)/);

  let variant: string;

  if (experimentCookie) {
    variant = experimentCookie[1];
  } else {
    // Assign a variant: 50/50 split
    variant = Math.random() < 0.5 ? "control" : "treatment";
  }

  // Route to variant-specific origin path
  if (variant === "treatment") {
    request.uri = `/experiment-b${request.uri}`;
  }

  // Pass variant as custom header for origin to use
  request.headers["x-experiment-variant"] = [
    { key: "X-Experiment-Variant", value: variant },
  ];

  return request;
};
```

### Lambda@Edge Constraints

When writing Lambda@Edge functions, observe these constraints:

- **Viewer triggers**: max 128 MB memory, 5 second timeout, 40 KB response body
- **Origin triggers**: max 10 GB (3.008 GB typical) memory, 30 second timeout, 1 MB response body
- **Region**: functions must be created in us-east-1
- **Runtime**: Node.js or Python only (no container images)
- **No environment variables**: bake configuration into the function code or fetch from Parameter Store
- **No VPC access**: functions run at edge locations outside VPCs
- **No layers**: Lambda layers are not supported for Lambda@Edge

---

## CDK Infrastructure

### S3 + CloudFront Static Site (CDK)

```typescript
import * as cdk from "aws-cdk-lib";
import * as s3 from "aws-cdk-lib/aws-s3";
import * as cloudfront from "aws-cdk-lib/aws-cloudfront";
import * as origins from "aws-cdk-lib/aws-cloudfront-origins";
import * as acm from "aws-cdk-lib/aws-certificatemanager";
import * as route53 from "aws-cdk-lib/aws-route53";
import * as route53Targets from "aws-cdk-lib/aws-route53-targets";
import * as s3deploy from "aws-cdk-lib/aws-s3-deployment";
import { Construct } from "constructs";

interface StaticSiteProps {
  domainName: string;
  hostedZoneName: string;
  buildPath: string;
}

export class StaticSiteStack extends cdk.Stack {
  public readonly distributionId: string;
  public readonly bucketName: string;

  constructor(scope: Construct, id: string, props: StaticSiteProps & cdk.StackProps) {
    super(scope, id, props);

    // S3 bucket (private, no public access)
    const siteBucket = new s3.Bucket(this, "SiteBucket", {
      bucketName: `${props.domainName}-assets`,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      encryption: s3.BucketEncryption.S3_MANAGED,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      versioned: true,
      lifecycleRules: [
        {
          noncurrentVersionExpiration: cdk.Duration.days(30),
          abortIncompleteMultipartUploadAfter: cdk.Duration.days(7),
        },
      ],
    });

    // TLS certificate (must be in us-east-1 for CloudFront)
    const hostedZone = route53.HostedZone.fromLookup(this, "Zone", {
      domainName: props.hostedZoneName,
    });

    const certificate = new acm.Certificate(this, "Certificate", {
      domainName: props.domainName,
      subjectAlternativeNames: [`*.${props.domainName}`],
      validation: acm.CertificateValidation.fromDns(hostedZone),
    });

    // CloudFront distribution
    const distribution = new cloudfront.Distribution(this, "Distribution", {
      defaultBehavior: {
        origin: origins.S3BucketOrigin.withOriginAccessControl(siteBucket),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
        compress: true,
      },
      domainNames: [props.domainName],
      certificate,
      defaultRootObject: "index.html",
      httpVersion: cloudfront.HttpVersion.HTTP2_AND_3,
      priceClass: cloudfront.PriceClass.PRICE_CLASS_100,
      errorResponses: [
        {
          httpStatus: 403,
          responseHttpStatus: 200,
          responsePagePath: "/index.html",
          ttl: cdk.Duration.seconds(10),
        },
        {
          httpStatus: 404,
          responseHttpStatus: 200,
          responsePagePath: "/index.html",
          ttl: cdk.Duration.seconds(10),
        },
      ],
    });

    // DNS record
    new route53.ARecord(this, "AliasRecord", {
      zone: hostedZone,
      recordName: props.domainName,
      target: route53.RecordTarget.fromAlias(
        new route53Targets.CloudFrontTarget(distribution)
      ),
    });

    // Deploy site contents
    new s3deploy.BucketDeployment(this, "DeploySite", {
      sources: [s3deploy.Source.asset(props.buildPath)],
      destinationBucket: siteBucket,
      distribution,
      distributionPaths: ["/*"],
      memoryLimit: 1024,
    });

    // Outputs
    this.distributionId = distribution.distributionId;
    this.bucketName = siteBucket.bucketName;

    new cdk.CfnOutput(this, "DistributionDomain", {
      value: distribution.distributionDomainName,
    });
    new cdk.CfnOutput(this, "DistributionId", {
      value: distribution.distributionId,
    });
    new cdk.CfnOutput(this, "BucketName", {
      value: siteBucket.bucketName,
    });
  }
}
```

### CloudFormation Template (S3 + CloudFront)

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Description: S3 bucket with CloudFront distribution

Parameters:
  DomainName:
    Type: String
    Description: Custom domain name (e.g., cdn.example.com)
  CertificateArn:
    Type: String
    Description: ACM certificate ARN (must be in us-east-1)
  HostedZoneId:
    Type: AWS::Route53::HostedZone::Id
    Description: Route 53 hosted zone ID

Resources:
  S3Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      VersioningConfiguration:
        Status: Enabled
      LifecycleConfiguration:
        Rules:
          - Id: CleanupOldVersions
            Status: Enabled
            NoncurrentVersionExpiration:
              NoncurrentDays: 30
          - Id: AbortIncompleteMultipart
            Status: Enabled
            AbortIncompleteMultipartUpload:
              DaysAfterInitiation: 7

  S3BucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref S3Bucket
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Sid: AllowCloudFrontOAC
            Effect: Allow
            Principal:
              Service: cloudfront.amazonaws.com
            Action: s3:GetObject
            Resource: !Sub "${S3Bucket.Arn}/*"
            Condition:
              StringEquals:
                AWS:SourceArn: !Sub "arn:aws:cloudfront::${AWS::AccountId}:distribution/${CloudFrontDistribution}"

  OriginAccessControl:
    Type: AWS::CloudFront::OriginAccessControl
    Properties:
      OriginAccessControlConfig:
        Name: !Sub "${AWS::StackName}-oac"
        OriginAccessControlOriginType: s3
        SigningBehavior: always
        SigningProtocol: sigv4

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Enabled: true
        Comment: !Sub "CDN for ${DomainName}"
        DefaultRootObject: index.html
        HttpVersion: http2and3
        PriceClass: PriceClass_100

        Origins:
          - Id: S3Origin
            DomainName: !GetAtt S3Bucket.RegionalDomainName
            OriginAccessControlId: !Ref OriginAccessControl
            S3OriginConfig:
              OriginAccessIdentity: ""

        DefaultCacheBehavior:
          TargetOriginId: S3Origin
          ViewerProtocolPolicy: redirect-to-https
          CachePolicyId: 658327ea-f89d-4fab-a63d-7e88639e58f6
          OriginRequestPolicyId: 88a5eaf4-2fd4-4709-b370-b4c650ea3fcf
          Compress: true

        CustomErrorResponses:
          - ErrorCode: 403
            ResponseCode: 200
            ResponsePagePath: /index.html
            ErrorCachingMinTTL: 10

        Aliases:
          - !Ref DomainName

        ViewerCertificate:
          AcmCertificateArn: !Ref CertificateArn
          SslSupportMethod: sni-only
          MinimumProtocolVersion: TLSv1.2_2021

        Restrictions:
          GeoRestriction:
            RestrictionType: none

  DNSRecord:
    Type: AWS::Route53::RecordSet
    Properties:
      HostedZoneId: !Ref HostedZoneId
      Name: !Ref DomainName
      Type: A
      AliasTarget:
        DNSName: !GetAtt CloudFrontDistribution.DomainName
        HostedZoneId: Z2FDTNDATAQYW2 # CloudFront hosted zone ID (constant)

Outputs:
  BucketName:
    Value: !Ref S3Bucket
  DistributionId:
    Value: !Ref CloudFrontDistribution
  DistributionDomain:
    Value: !GetAtt CloudFrontDistribution.DomainName
```

---

## Cost Optimization

### S3 Storage Classes

| Storage Class | Use Case | Min Duration | Retrieval Fee |
|---|---|---|---|
| STANDARD | Frequently accessed data | None | None |
| INTELLIGENT_TIERING | Unknown or changing access patterns | None | None (monitoring fee) |
| STANDARD_IA | Infrequently accessed, rapid retrieval | 30 days | Per GB |
| ONE_ZONE_IA | Non-critical infrequent data | 30 days | Per GB |
| GLACIER_INSTANT_RETRIEVAL | Archive with millisecond access | 90 days | Per GB |
| GLACIER_FLEXIBLE_RETRIEVAL | Archive (minutes to hours) | 90 days | Per GB + request |
| GLACIER_DEEP_ARCHIVE | Long-term archive (12+ hours) | 180 days | Per GB + request |

### Lifecycle Rules

```typescript
import { PutBucketLifecycleConfigurationCommand } from "@aws-sdk/client-s3";

async function setLifecycleRules(bucket: string): Promise<void> {
  await s3.send(
    new PutBucketLifecycleConfigurationCommand({
      Bucket: bucket,
      LifecycleConfiguration: {
        Rules: [
          {
            ID: "TransitionToIA",
            Status: "Enabled",
            Filter: { Prefix: "" },
            Transitions: [
              {
                Days: 30,
                StorageClass: "STANDARD_IA",
              },
              {
                Days: 90,
                StorageClass: "GLACIER_INSTANT_RETRIEVAL",
              },
              {
                Days: 365,
                StorageClass: "DEEP_ARCHIVE",
              },
            ],
          },
          {
            ID: "ExpireTempFiles",
            Status: "Enabled",
            Filter: { Prefix: "tmp/" },
            Expiration: { Days: 7 },
          },
          {
            ID: "CleanupOldVersions",
            Status: "Enabled",
            Filter: { Prefix: "" },
            NoncurrentVersionExpiration: { NoncurrentDays: 30 },
          },
          {
            ID: "AbortIncompleteUploads",
            Status: "Enabled",
            Filter: { Prefix: "" },
            AbortIncompleteMultipartUpload: {
              DaysAfterInitiation: 7,
            },
          },
          {
            ID: "DeleteExpiredMarkers",
            Status: "Enabled",
            Filter: { Prefix: "" },
            Expiration: { ExpiredObjectDeleteMarker: true },
          },
        ],
      },
    })
  );
}
```

### Intelligent-Tiering Configuration

```typescript
import { PutBucketIntelligentTieringConfigurationCommand } from "@aws-sdk/client-s3";

async function enableIntelligentTiering(bucket: string): Promise<void> {
  await s3.send(
    new PutBucketIntelligentTieringConfigurationCommand({
      Bucket: bucket,
      Id: "FullTiering",
      IntelligentTieringConfiguration: {
        Id: "FullTiering",
        Status: "Enabled",
        Filter: { Prefix: "" },
        Tierings: [
          {
            Days: 90,
            AccessTier: "ARCHIVE_ACCESS",
          },
          {
            Days: 180,
            AccessTier: "DEEP_ARCHIVE_ACCESS",
          },
        ],
      },
    })
  );
}
```

### CloudFront Cost Tips

- **Price Class**: Use `PriceClass_100` (US/Canada/Europe) unless global distribution is necessary. `PriceClass_All` includes every edge location and costs significantly more.
- **Cache hit ratio**: Aim for 95%+ cache hit ratio. Monitor via CloudFront metrics.
- **Compression**: Always enable Compress on cache behaviors to reduce data transfer.
- **Invalidation**: First 1000 invalidation paths per month are free. Use wildcard paths (`/assets/*`) to reduce path count.
- **HTTP/2 and HTTP/3**: Reduce connection overhead and improve transfer efficiency at no extra cost.
- **Origin Shield**: Enable for workloads with many edge locations fetching from the same origin. Adds a caching layer between edges and origin, reducing origin load and cost.

### S3 Cost Monitoring

```typescript
import {
  CostExplorerClient,
  GetCostAndUsageCommand,
} from "@aws-sdk/client-cost-explorer";

const ce = new CostExplorerClient({ region: "us-east-1" });

async function getS3Costs(
  startDate: string,
  endDate: string
): Promise<void> {
  const response = await ce.send(
    new GetCostAndUsageCommand({
      TimePeriod: { Start: startDate, End: endDate },
      Granularity: "MONTHLY",
      Metrics: ["UnblendedCost"],
      Filter: {
        Dimensions: {
          Key: "SERVICE",
          Values: [
            "Amazon Simple Storage Service",
            "Amazon CloudFront",
          ],
        },
      },
      GroupBy: [{ Type: "DIMENSION", Key: "SERVICE" }],
    })
  );

  for (const result of response.ResultsByTime ?? []) {
    console.log(`Period: ${result.TimePeriod?.Start}`);
    for (const group of result.Groups ?? []) {
      const service = group.Keys?.[0];
      const cost = group.Metrics?.UnblendedCost;
      console.log(`  ${service}: $${parseFloat(cost?.Amount ?? "0").toFixed(2)}`);
    }
  }
}
```

---

## Quick Reference

### AWS CLI Commands

```bash
# Upload file
aws s3 cp ./file.txt s3://my-bucket/path/file.txt

# Sync directory
aws s3 sync ./build s3://my-bucket/ --delete --cache-control "max-age=31536000"

# Create invalidation
aws cloudfront create-invalidation \
  --distribution-id E1234567890 \
  --paths "/*"

# List objects by storage class
aws s3api list-objects-v2 \
  --bucket my-bucket \
  --query "Contents[?StorageClass=='GLACIER'].[Key,Size]" \
  --output table

# Get bucket size
aws cloudwatch get-metric-statistics \
  --namespace AWS/S3 \
  --metric-name BucketSizeBytes \
  --dimensions Name=BucketName,Value=my-bucket Name=StorageType,Value=StandardStorage \
  --start-time "$(date -d '1 day ago' -u +%Y-%m-%dT%H:%M:%S)" \
  --end-time "$(date -u +%Y-%m-%dT%H:%M:%S)" \
  --period 86400 \
  --statistics Average

# Check distribution status
aws cloudfront get-distribution --id E1234567890 \
  --query "Distribution.Status"
```

### Common S3 Errors and Fixes

| Error | Cause | Fix |
|---|---|---|
| `AccessDenied` | Missing bucket policy or IAM permissions | Verify bucket policy and IAM role |
| `NoSuchKey` | Object does not exist at the given key | Check key path, encoding, and trailing slashes |
| `SlowDown` | Request rate exceeds 5,500 GET/s or 3,500 PUT/s per prefix | Add random prefix hashing or use more prefixes |
| `EntityTooLarge` | PUT body exceeds 5 GB | Use multipart upload for files above 5 GB |
| `InvalidBucketName` | Bucket name violates naming rules | Use lowercase, no underscores, 3-63 chars |
| `BucketAlreadyExists` | Bucket name is globally taken | Choose a unique name with org/project prefix |
