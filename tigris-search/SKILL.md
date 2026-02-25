---
name: tigris-search
description: Tigris Data patterns covering serverless NoSQL database, full-text search, real-time subscriptions, TypeScript SDK, schema definition, indexing, faceted search, and S3-compatible object storage.
---

# Tigris Data

This skill should be used when building applications with Tigris serverless database and search. It covers collections, queries, full-text search, real-time events, and object storage.

## When to Use This Skill

Use this skill when you need to:

- Use serverless NoSQL with built-in search
- Define typed collection schemas
- Perform full-text and faceted search
- Subscribe to real-time data changes
- Store files with S3-compatible API

## Setup

```bash
npm install @tigrisdata/core
```

## Schema Definition

```ts
import {
  TigrisCollection,
  TigrisDataTypes,
  Field,
  PrimaryKey,
  SearchField,
} from "@tigrisdata/core";

@TigrisCollection("products")
export class Product {
  @PrimaryKey({ order: 1, autoGenerate: true })
  id!: string;

  @SearchField()
  @Field()
  name!: string;

  @SearchField()
  @Field()
  description!: string;

  @Field()
  price!: number;

  @SearchField({ facet: true })
  @Field()
  category!: string;

  @SearchField({ facet: true })
  @Field({ elements: TigrisDataTypes.STRING })
  tags!: string[];

  @Field()
  inStock!: boolean;

  @Field()
  imageUrl?: string;

  @Field({ timestamp: "createdAt" })
  createdAt!: Date;
}
```

## Client Setup

```ts
import { Tigris } from "@tigrisdata/core";

const tigris = new Tigris({
  serverUrl: process.env.TIGRIS_URI!,
  projectName: process.env.TIGRIS_PROJECT!,
  clientId: process.env.TIGRIS_CLIENT_ID!,
  clientSecret: process.env.TIGRIS_CLIENT_SECRET!,
});

const db = tigris.getDatabase();
const products = db.getCollection<Product>(Product);
```

## CRUD Operations

```ts
// Insert
const product = await products.insertOne({
  name: "Wireless Headphones",
  description: "Noise-cancelling over-ear headphones",
  price: 299.99,
  category: "Electronics",
  tags: ["audio", "wireless", "bluetooth"],
  inStock: true,
});

// Insert many
await products.insertMany([
  { name: "USB-C Cable", price: 12.99, category: "Accessories", tags: ["cable"], inStock: true },
  { name: "Laptop Stand", price: 49.99, category: "Accessories", tags: ["ergonomic"], inStock: true },
]);

// Read one
const item = await products.findOne({ filter: { id: "product-id" } });

// Read many with filter
const electronics = await products.findMany({
  filter: {
    category: "Electronics",
    inStock: true,
    price: { $lte: 500 },
  },
  sort: { field: "price", order: "$asc" },
  options: { limit: 20, offset: 0 },
});

// Update
await products.updateOne({
  filter: { id: "product-id" },
  fields: { $set: { price: 249.99, inStock: false } },
});

// Delete
await products.deleteOne({ filter: { id: "product-id" } });
```

## Full-Text Search

```ts
// Basic search
const results = await products.search({
  q: "wireless headphones",
  searchFields: ["name", "description"],
  filter: { inStock: true },
  sort: [{ field: "price", order: "$asc" }],
  facets: { category: { size: 10 }, tags: { size: 20 } },
  page: 1,
  pageSize: 20,
});

console.log(results.hits);    // Matching products
console.log(results.facets);  // Facet counts for filtering
console.log(results.meta);    // Total count, page info
```

## Real-Time Events

```ts
// Subscribe to collection changes
const stream = products.subscribe(
  { filter: { category: "Electronics" } },
  {
    onNext(event) {
      console.log(event.type); // "insert", "update", "delete"
      console.log(event.data);
    },
    onError(err) {
      console.error("Subscription error:", err);
    },
  }
);

// Later: unsubscribe
stream.cancel();
```

## Object Storage (S3-Compatible)

```ts
import { S3Client, PutObjectCommand, GetObjectCommand } from "@aws-sdk/client-s3";

const s3 = new S3Client({
  region: "auto",
  endpoint: process.env.TIGRIS_S3_ENDPOINT!,
  credentials: {
    accessKeyId: process.env.TIGRIS_ACCESS_KEY!,
    secretAccessKey: process.env.TIGRIS_SECRET_KEY!,
  },
});

// Upload file
await s3.send(new PutObjectCommand({
  Bucket: "my-bucket",
  Key: `uploads/${filename}`,
  Body: fileBuffer,
  ContentType: "image/png",
}));

// Generate signed URL
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
const url = await getSignedUrl(s3, new GetObjectCommand({
  Bucket: "my-bucket",
  Key: `uploads/${filename}`,
}), { expiresIn: 3600 });
```

## Additional Resources

- Tigris: https://www.tigrisdata.com/docs/
- TypeScript SDK: https://www.tigrisdata.com/docs/sdkstools/typescript/
- Search: https://www.tigrisdata.com/docs/concepts/searching/
