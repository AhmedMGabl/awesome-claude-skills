---
name: uploadthing
description: UploadThing file upload patterns covering route definitions, file type validation, size limits, middleware authentication, upload callbacks, React components, presigned URLs, and Next.js App Router integration.
---

# UploadThing

This skill should be used when implementing file uploads with UploadThing. It covers route definitions, validation, auth middleware, React components, and Next.js integration.

## When to Use This Skill

Use this skill when you need to:

- Add type-safe file uploads to Next.js applications
- Configure file type and size validation
- Authenticate uploads with middleware
- Use pre-built React upload components
- Handle upload callbacks and metadata

## Route Definition

```typescript
// app/api/uploadthing/core.ts
import { createUploadthing, type FileRouter } from "uploadthing/next";
import { auth } from "@/lib/auth";

const f = createUploadthing();

export const ourFileRouter = {
  // Profile image uploader
  profileImage: f({ image: { maxFileSize: "4MB", maxFileCount: 1 } })
    .middleware(async () => {
      const session = await auth();
      if (!session) throw new Error("Unauthorized");
      return { userId: session.user.id };
    })
    .onUploadComplete(async ({ metadata, file }) => {
      await db.user.update({
        where: { id: metadata.userId },
        data: { avatarUrl: file.url },
      });
      return { url: file.url };
    }),

  // Document uploader
  documentUpload: f({
    pdf: { maxFileSize: "16MB", maxFileCount: 5 },
    "application/msword": { maxFileSize: "16MB" },
  })
    .middleware(async () => {
      const session = await auth();
      if (!session) throw new Error("Unauthorized");
      return { userId: session.user.id };
    })
    .onUploadComplete(async ({ metadata, file }) => {
      await db.document.create({
        data: {
          name: file.name,
          url: file.url,
          size: file.size,
          userId: metadata.userId,
        },
      });
    }),

  // Multi-media uploader
  mediaUpload: f({
    image: { maxFileSize: "8MB", maxFileCount: 10 },
    video: { maxFileSize: "64MB", maxFileCount: 3 },
  })
    .middleware(async () => {
      const session = await auth();
      if (!session) throw new Error("Unauthorized");
      return { userId: session.user.id };
    })
    .onUploadComplete(async ({ metadata, file }) => {
      await db.media.create({
        data: { url: file.url, type: file.type, userId: metadata.userId },
      });
    }),
} satisfies FileRouter;

export type OurFileRouter = typeof ourFileRouter;

// app/api/uploadthing/route.ts
import { createRouteHandler } from "uploadthing/next";
import { ourFileRouter } from "./core";

export const { GET, POST } = createRouteHandler({ router: ourFileRouter });
```

## React Components

```tsx
"use client";
import { UploadButton, UploadDropzone, useUploadThing } from "@/lib/uploadthing";

// Simple button upload
function ProfileImageUpload() {
  return (
    <UploadButton
      endpoint="profileImage"
      onClientUploadComplete={(res) => {
        toast.success("Upload complete!");
        setAvatarUrl(res[0].url);
      }}
      onUploadError={(error) => {
        toast.error(`Upload failed: ${error.message}`);
      }}
    />
  );
}

// Drag and drop zone
function DocumentUpload() {
  return (
    <UploadDropzone
      endpoint="documentUpload"
      onClientUploadComplete={(res) => {
        toast.success(`${res.length} file(s) uploaded`);
      }}
      onUploadError={(error) => {
        toast.error(error.message);
      }}
      appearance={{
        container: "border-2 border-dashed rounded-lg p-8",
        label: "text-lg font-medium",
        allowedContent: "text-sm text-gray-500",
      }}
    />
  );
}

// Programmatic upload with hook
function CustomUpload() {
  const { startUpload, isUploading } = useUploadThing("mediaUpload", {
    onClientUploadComplete: (res) => {
      console.log("Uploaded:", res);
    },
    onUploadError: (error) => {
      console.error(error);
    },
  });

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files ?? []);
    if (files.length > 0) {
      await startUpload(files);
    }
  };

  return (
    <div>
      <input type="file" multiple onChange={handleFileChange} disabled={isUploading} />
      {isUploading && <p>Uploading...</p>}
    </div>
  );
}
```

## Client Setup

```typescript
// lib/uploadthing.ts
import {
  generateUploadButton,
  generateUploadDropzone,
  generateReactHelpers,
} from "@uploadthing/react";
import type { OurFileRouter } from "@/app/api/uploadthing/core";

export const UploadButton = generateUploadButton<OurFileRouter>();
export const UploadDropzone = generateUploadDropzone<OurFileRouter>();
export const { useUploadThing } = generateReactHelpers<OurFileRouter>();
```

## Additional Resources

- UploadThing docs: https://docs.uploadthing.com/
- React components: https://docs.uploadthing.com/api-reference/react
- Next.js setup: https://docs.uploadthing.com/getting-started/appdir
