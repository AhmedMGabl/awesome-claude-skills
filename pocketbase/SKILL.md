---
name: pocketbase
description: PocketBase patterns covering collection schemas, real-time subscriptions, authentication, file uploads, API rules, hooks, JavaScript SDK, and single-binary deployment for backend-as-a-service.
---

# PocketBase

This skill should be used when building applications with PocketBase as a backend-as-a-service. It covers collections, authentication, real-time subscriptions, file uploads, and SDK usage.

## When to Use This Skill

Use this skill when you need to:

- Set up a backend with single-binary deployment
- Define collection schemas and API rules
- Handle authentication with email/OAuth
- Subscribe to real-time collection changes
- Upload and serve files with PocketBase

## Setup

```bash
# Download PocketBase
# https://pocketbase.io/docs/

# JavaScript SDK
npm install pocketbase
```

## Client Setup

```ts
import PocketBase from "pocketbase";

const pb = new PocketBase("http://127.0.0.1:8090");

// Authentication
async function login(email: string, password: string) {
  const authData = await pb.collection("users").authWithPassword(email, password);
  console.log(pb.authStore.isValid);
  console.log(pb.authStore.token);
  console.log(pb.authStore.model?.id);
  return authData;
}

// OAuth2
async function loginWithGoogle() {
  const authData = await pb.collection("users").authWithOAuth2({ provider: "google" });
  return authData;
}

// Register
async function register(email: string, password: string, name: string) {
  const user = await pb.collection("users").create({
    email,
    password,
    passwordConfirm: password,
    name,
  });
  await pb.collection("users").requestVerification(email);
  return user;
}
```

## CRUD Operations

```ts
// List with pagination and filtering
const posts = await pb.collection("posts").getList(1, 20, {
  filter: 'status = "published" && created >= "2024-01-01"',
  sort: "-created",
  expand: "author,tags",
});

// Get single record
const post = await pb.collection("posts").getOne("RECORD_ID", {
  expand: "author,comments(post)",
});

// Create record
const newPost = await pb.collection("posts").create({
  title: "Hello World",
  content: "My first post",
  author: pb.authStore.model?.id,
  status: "draft",
});

// Update record
const updated = await pb.collection("posts").update("RECORD_ID", {
  title: "Updated Title",
  status: "published",
});

// Delete record
await pb.collection("posts").delete("RECORD_ID");
```

## Real-Time Subscriptions

```ts
// Subscribe to collection changes
pb.collection("messages").subscribe("*", (e) => {
  console.log(e.action); // "create", "update", "delete"
  console.log(e.record);
});

// Subscribe to specific record
pb.collection("posts").subscribe("RECORD_ID", (e) => {
  console.log("Post updated:", e.record);
});

// Unsubscribe
pb.collection("messages").unsubscribe("*");
pb.collection("messages").unsubscribe(); // all subscriptions
```

## File Uploads

```ts
// Upload file
const formData = new FormData();
formData.append("title", "My Document");
formData.append("file", fileInput.files[0]);
formData.append("thumbnail", imageInput.files[0]);

const record = await pb.collection("documents").create(formData);

// Get file URL
const url = pb.files.getURL(record, record.file);
const thumbUrl = pb.files.getURL(record, record.thumbnail, { thumb: "100x100" });
```

## API Rules (Collection Schema)

```json
{
  "name": "posts",
  "type": "base",
  "schema": [
    { "name": "title", "type": "text", "required": true },
    { "name": "content", "type": "editor" },
    { "name": "author", "type": "relation", "options": { "collectionId": "users" } },
    { "name": "status", "type": "select", "options": { "values": ["draft", "published"] } }
  ],
  "listRule": "status = 'published' || author = @request.auth.id",
  "viewRule": "status = 'published' || author = @request.auth.id",
  "createRule": "@request.auth.id != ''",
  "updateRule": "author = @request.auth.id",
  "deleteRule": "author = @request.auth.id"
}
```

## Additional Resources

- PocketBase: https://pocketbase.io/
- JavaScript SDK: https://github.com/pocketbase/js-sdk
- API Rules: https://pocketbase.io/docs/api-rules-and-filters/
