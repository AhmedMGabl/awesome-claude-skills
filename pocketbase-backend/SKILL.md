---
name: pocketbase-backend
description: PocketBase backend covering collections, real-time subscriptions, authentication, file storage, hooks, migrations, JavaScript SDK integration, and single-binary deployment.
---

# PocketBase Backend

This skill should be used when building applications with PocketBase as the backend. It covers collections, authentication, real-time subscriptions, and SDK integration.

## When to Use This Skill

Use this skill when you need to:

- Set up a backend with a single binary
- Create collections with real-time subscriptions
- Handle authentication with email/password and OAuth
- Store and serve files
- Extend with custom hooks and migrations

## JavaScript SDK Setup

```typescript
import PocketBase from "pocketbase";

const pb = new PocketBase("http://127.0.0.1:8090");

// Authenticate
await pb.collection("users").authWithPassword("user@example.com", "password123");

// Check auth state
console.log(pb.authStore.isValid);
console.log(pb.authStore.model);
```

## CRUD Operations

```typescript
// Create record
const record = await pb.collection("posts").create({
  title: "My Post",
  content: "Hello world",
  author: pb.authStore.model?.id,
  published: true,
});

// Read single record with expand
const post = await pb.collection("posts").getOne(recordId, {
  expand: "author,tags",
});

// List with filtering and pagination
const result = await pb.collection("posts").getList(1, 20, {
  filter: 'published = true && created >= "2024-01-01"',
  sort: "-created",
  expand: "author",
});

// Full list (no pagination)
const allPosts = await pb.collection("posts").getFullList({
  filter: `author = "${userId}"`,
  sort: "-created",
});

// Update
await pb.collection("posts").update(recordId, {
  title: "Updated Title",
});

// Delete
await pb.collection("posts").delete(recordId);
```

## Real-Time Subscriptions

```typescript
// Subscribe to collection changes
pb.collection("messages").subscribe("*", (e) => {
  console.log(e.action); // "create", "update", "delete"
  console.log(e.record);

  switch (e.action) {
    case "create":
      addMessage(e.record);
      break;
    case "update":
      updateMessage(e.record);
      break;
    case "delete":
      removeMessage(e.record.id);
      break;
  }
});

// Subscribe to specific record
pb.collection("posts").subscribe(recordId, (e) => {
  console.log("Record changed:", e.record);
});

// Unsubscribe
pb.collection("messages").unsubscribe("*");
pb.collection("messages").unsubscribe(); // all subscriptions
```

## Authentication

```typescript
// Register new user
const user = await pb.collection("users").create({
  email: "new@example.com",
  password: "securepass123",
  passwordConfirm: "securepass123",
  name: "New User",
});

// OAuth2 login
const authData = await pb.collection("users").authWithOAuth2({ provider: "google" });

// Request password reset
await pb.collection("users").requestPasswordReset("user@example.com");

// Request email verification
await pb.collection("users").requestVerification("user@example.com");

// Auth refresh
await pb.collection("users").authRefresh();

// Logout
pb.authStore.clear();
```

## File Uploads

```typescript
// Upload files with FormData
const formData = new FormData();
formData.append("title", "Photo Post");
formData.append("image", fileInput.files[0]);
formData.append("attachments", file1);
formData.append("attachments", file2);

const record = await pb.collection("posts").create(formData);

// Get file URL
const url = pb.files.getURL(record, record.image);
const thumbUrl = pb.files.getURL(record, record.image, { thumb: "200x200" });
```

## React Integration

```tsx
import PocketBase from "pocketbase";
import { useEffect, useState } from "react";

const pb = new PocketBase("http://127.0.0.1:8090");

function useCollection<T>(collection: string, filter?: string) {
  const [records, setRecords] = useState<T[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    pb.collection(collection)
      .getFullList({ filter, sort: "-created" })
      .then((data) => {
        setRecords(data as T[]);
        setLoading(false);
      });

    // Real-time updates
    pb.collection(collection).subscribe("*", (e) => {
      if (e.action === "create") setRecords((prev) => [e.record as T, ...prev]);
      if (e.action === "delete") setRecords((prev) => prev.filter((r: any) => r.id !== e.record.id));
    });

    return () => { pb.collection(collection).unsubscribe(); };
  }, [collection, filter]);

  return { records, loading };
}
```

## Additional Resources

- PocketBase docs: https://pocketbase.io/docs/
- JavaScript SDK: https://github.com/pocketbase/js-sdk
- API reference: https://pocketbase.io/docs/api-records/
