---
name: mongodb
description: This skill should be used when building TypeScript applications with MongoDB, including connection setup with Mongoose and the native driver, schema definition and models, CRUD operations, aggregation pipelines, indexing strategies, transactions, change streams, Atlas Search, and population/references.
---

# MongoDB

This skill provides comprehensive guidance for working with MongoDB in TypeScript projects. It covers both Mongoose (the most popular ODM) and the native MongoDB driver, with practical patterns for schema design, querying, aggregation, indexing, transactions, and real-time data with change streams.

## When to Use This Skill

- Setting up MongoDB connections with Mongoose or the native driver
- Defining Mongoose schemas, models, and validation
- Performing CRUD operations against MongoDB collections
- Building aggregation pipelines for analytics and data transformation
- Designing indexes for query performance
- Running multi-document transactions
- Listening to real-time database changes with change streams
- Implementing Atlas Search for full-text and fuzzy search
- Working with document references and population

---

## 1. Connection Setup

### Mongoose Connection

```bash
npm install mongoose
npm install -D @types/mongoose
```

```typescript
// src/db/mongoose.ts
import mongoose from "mongoose";

const MONGODB_URI = process.env.MONGODB_URI ?? "mongodb://localhost:27017/myapp";

export async function connectDB(): Promise<typeof mongoose> {
  mongoose.connection.on("connected", () => console.log("MongoDB connected"));
  mongoose.connection.on("error", (err) => console.error("MongoDB error:", err));

  return mongoose.connect(MONGODB_URI, {
    maxPoolSize: 10,
    minPoolSize: 2,
    serverSelectionTimeoutMS: 5000,
    socketTimeoutMS: 45000,
  });
}

export async function disconnectDB(): Promise<void> {
  await mongoose.disconnect();
}
```

#### Singleton Pattern (Next.js / Hot Reload Safe)

```typescript
// src/lib/mongoose.ts
import mongoose from "mongoose";

const MONGODB_URI = process.env.MONGODB_URI!;

const globalForMongoose = globalThis as unknown as {
  mongoosePromise: Promise<typeof mongoose> | undefined;
};

export const dbPromise =
  globalForMongoose.mongoosePromise ??
  mongoose.connect(MONGODB_URI, { maxPoolSize: 10 });

if (process.env.NODE_ENV !== "production") {
  globalForMongoose.mongoosePromise = dbPromise;
}
```

### Native MongoDB Driver

```bash
npm install mongodb
```

```typescript
// src/db/native.ts
import { MongoClient, Db } from "mongodb";

const MONGODB_URI = process.env.MONGODB_URI ?? "mongodb://localhost:27017";
const DB_NAME = process.env.DB_NAME ?? "myapp";

const client = new MongoClient(MONGODB_URI, {
  maxPoolSize: 10,
  minPoolSize: 2,
  retryWrites: true,
  w: "majority",
});

let db: Db;

export async function connectDB(): Promise<Db> {
  await client.connect();
  db = client.db(DB_NAME);
  return db;
}

export function getDB(): Db {
  if (!db) throw new Error("Database not initialized. Call connectDB() first.");
  return db;
}

export async function disconnectDB(): Promise<void> {
  await client.close();
}
```

---

## 2. Schema Definition and Models (Mongoose)

### Basic Schema with Validation

```typescript
// src/models/user.model.ts
import mongoose, { Schema, Document, Model } from "mongoose";

interface IUser extends Document {
  email: string;
  name: string;
  passwordHash: string;
  role: "user" | "admin" | "moderator";
  isActive: boolean;
  profile: {
    bio?: string;
    avatarUrl?: string;
    socialLinks?: Map<string, string>;
  };
  tags: string[];
  loginCount: number;
  lastLoginAt?: Date;
  createdAt: Date;
  updatedAt: Date;
}

const userSchema = new Schema<IUser>(
  {
    email: {
      type: String,
      required: [true, "Email is required"],
      unique: true,
      lowercase: true,
      trim: true,
      match: [/^\S+@\S+\.\S+$/, "Invalid email format"],
    },
    name: {
      type: String,
      required: true,
      trim: true,
      minlength: 2,
      maxlength: 100,
    },
    passwordHash: { type: String, required: true, select: false },
    role: {
      type: String,
      enum: ["user", "admin", "moderator"],
      default: "user",
    },
    isActive: { type: Boolean, default: true },
    profile: {
      bio: { type: String, maxlength: 500 },
      avatarUrl: String,
      socialLinks: { type: Map, of: String },
    },
    tags: [{ type: String, trim: true }],
    loginCount: { type: Number, default: 0 },
    lastLoginAt: Date,
  },
  {
    timestamps: true,
    toJSON: {
      transform(_doc, ret) {
        ret.id = ret._id.toString();
        delete ret._id;
        delete ret.__v;
        delete ret.passwordHash;
        return ret;
      },
    },
  },
);

export const User: Model<IUser> =
  mongoose.models.User ?? mongoose.model<IUser>("User", userSchema);
```

### Schema with Methods, Statics, and Virtuals

```typescript
// src/models/post.model.ts
import mongoose, { Schema, Document, Model, Types } from "mongoose";

interface IPost extends Document {
  title: string;
  slug: string;
  content: string;
  status: "draft" | "published" | "archived";
  author: Types.ObjectId;
  category: Types.ObjectId;
  tags: Types.ObjectId[];
  metadata: {
    readTimeMinutes: number;
    wordCount: number;
    featured: boolean;
  };
  viewCount: number;
  publishedAt?: Date;
  createdAt: Date;
  updatedAt: Date;
  isPublished: boolean;
  publish(): Promise<IPost>;
}

interface IPostModel extends Model<IPost> {
  findPublished(limit?: number): Promise<IPost[]>;
  findBySlug(slug: string): Promise<IPost | null>;
}

const postSchema = new Schema<IPost, IPostModel>(
  {
    title: { type: String, required: true, trim: true, maxlength: 200 },
    slug: { type: String, required: true, unique: true, lowercase: true },
    content: { type: String, required: true },
    status: {
      type: String,
      enum: ["draft", "published", "archived"],
      default: "draft",
      index: true,
    },
    author: {
      type: Schema.Types.ObjectId,
      ref: "User",
      required: true,
      index: true,
    },
    category: { type: Schema.Types.ObjectId, ref: "Category" },
    tags: [{ type: Schema.Types.ObjectId, ref: "Tag" }],
    metadata: {
      readTimeMinutes: { type: Number, default: 0 },
      wordCount: { type: Number, default: 0 },
      featured: { type: Boolean, default: false },
    },
    viewCount: { type: Number, default: 0 },
    publishedAt: Date,
  },
  { timestamps: true },
);

// Virtual -- computed field not persisted to database
postSchema.virtual("isPublished").get(function () {
  return this.status === "published";
});

// Instance method
postSchema.methods.publish = async function (): Promise<IPost> {
  this.status = "published";
  this.publishedAt = new Date();
  return this.save();
};

// Static methods
postSchema.statics.findPublished = function (limit = 20): Promise<IPost[]> {
  return this.find({ status: "published" })
    .sort({ publishedAt: -1 })
    .limit(limit)
    .populate("author", "name email")
    .exec();
};

postSchema.statics.findBySlug = function (
  slug: string,
): Promise<IPost | null> {
  return this.findOne({ slug })
    .populate("author", "name email")
    .populate("tags", "name")
    .exec();
};

// Middleware -- auto-generate slug before validation
postSchema.pre("validate", function (next) {
  if (this.isModified("title") && !this.slug) {
    this.slug =
      this.title
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/(^-|-$)/g, "") +
      "-" +
      Date.now().toString(36);
  }
  if (this.isModified("content")) {
    const words = this.content.split(/\s+/).length;
    this.metadata.wordCount = words;
    this.metadata.readTimeMinutes = Math.ceil(words / 200);
  }
  next();
});

export const Post: IPostModel =
  (mongoose.models.Post as IPostModel) ??
  mongoose.model<IPost, IPostModel>("Post", postSchema);
```

### Discriminators (Polymorphic Models)

```typescript
const eventSchema = new Schema(
  {
    type: {
      type: String,
      required: true,
      enum: ["click", "purchase", "signup"],
    },
    userId: { type: Schema.Types.ObjectId, ref: "User", required: true },
    timestamp: { type: Date, default: Date.now },
  },
  { discriminatorKey: "type", timestamps: true },
);

const Event = mongoose.model("Event", eventSchema);

const ClickEvent = Event.discriminator(
  "click",
  new Schema({ url: String, elementId: String }),
);

const PurchaseEvent = Event.discriminator(
  "purchase",
  new Schema({ productId: String, amount: Number, currency: String }),
);
```

---

## 3. CRUD Operations

### Create

```typescript
// Single document
const user = await User.create({
  email: "alice@example.com",
  name: "Alice",
  passwordHash: hashedPassword,
  tags: ["developer", "typescript"],
});

// Batch insert
const users = await User.insertMany([
  { email: "bob@example.com", name: "Bob", passwordHash: h1 },
  { email: "carol@example.com", name: "Carol", passwordHash: h2 },
]);

// Create with native driver (typed)
import { getDB } from "./db/native";

interface UserDoc {
  email: string;
  name: string;
  role: string;
  createdAt: Date;
}

const db = getDB();
const result = await db.collection<UserDoc>("users").insertOne({
  email: "dave@example.com",
  name: "Dave",
  role: "user",
  createdAt: new Date(),
});
```

### Read

```typescript
// Find with filters, projection, sort, pagination
const publishedPosts = await Post.find({ status: "published" })
  .select("title slug author publishedAt viewCount")
  .sort({ publishedAt: -1 })
  .skip(0)
  .limit(20)
  .populate("author", "name")
  .lean();

// Find one by ID
const post = await Post.findById(postId).populate("author tags").lean();

// Find one with conditions
const admin = await User.findOne({ role: "admin", isActive: true }).lean();

// Count documents
const totalPublished = await Post.countDocuments({ status: "published" });

// Distinct values
const categories = await Post.distinct("category", { status: "published" });

// Exists check
const emailTaken = await User.exists({ email: "alice@example.com" });

// Complex query with native driver
const recentPosts = await db
  .collection("posts")
  .find({
    status: "published",
    publishedAt: { $gte: new Date("2026-01-01") },
    $or: [
      { "metadata.featured": true },
      { viewCount: { $gte: 1000 } },
    ],
  })
  .sort({ publishedAt: -1 })
  .limit(10)
  .toArray();
```

### Update

```typescript
// Update one document
await Post.findByIdAndUpdate(
  postId,
  {
    $set: { status: "published", publishedAt: new Date() },
    $inc: { viewCount: 1 },
  },
  { new: true, runValidators: true },
);

// Update many
const result = await User.updateMany(
  { lastLoginAt: { $lt: new Date("2025-01-01") } },
  { $set: { isActive: false } },
);
console.log(`Deactivated ${result.modifiedCount} users`);

// Upsert
await User.findOneAndUpdate(
  { email: "alice@example.com" },
  {
    $set: { name: "Alice Updated" },
    $setOnInsert: { role: "user", isActive: true },
  },
  { upsert: true, new: true },
);

// Array operations
await Post.findByIdAndUpdate(postId, { $push: { tags: newTagId } });
await Post.findByIdAndUpdate(postId, { $pull: { tags: removedTagId } });
await Post.findByIdAndUpdate(postId, {
  $addToSet: { tags: { $each: [tagId1, tagId2] } },
});
```

### Delete

```typescript
// Delete one
await Post.findByIdAndDelete(postId);

// Delete many
const result = await Post.deleteMany({
  status: "archived",
  updatedAt: { $lt: new Date("2025-01-01") },
});
console.log(`Deleted ${result.deletedCount} archived posts`);

// Find and delete (returns the deleted document)
const deleted = await User.findOneAndDelete({ email: "alice@example.com" });

// Soft delete pattern
await Post.findByIdAndUpdate(postId, {
  $set: { deletedAt: new Date(), status: "archived" },
});
```

---

## 4. Aggregation Pipeline

### Basic Aggregation

```typescript
// Posts per author with stats
const authorStats = await Post.aggregate([
  { $match: { status: "published" } },
  {
    $group: {
      _id: "$author",
      postCount: { $sum: 1 },
      totalViews: { $sum: "$viewCount" },
      avgViews: { $avg: "$viewCount" },
      latestPost: { $max: "$publishedAt" },
    },
  },
  { $sort: { totalViews: -1 } },
  { $limit: 10 },
]);
```

### Lookup (Join)

```typescript
// Posts with author details and tag names
const postsWithDetails = await Post.aggregate([
  { $match: { status: "published" } },
  {
    $lookup: {
      from: "users",
      localField: "author",
      foreignField: "_id",
      as: "authorDoc",
      pipeline: [{ $project: { name: 1, email: 1 } }],
    },
  },
  { $unwind: "$authorDoc" },
  {
    $lookup: {
      from: "tags",
      localField: "tags",
      foreignField: "_id",
      as: "tagDocs",
    },
  },
  {
    $project: {
      title: 1,
      slug: 1,
      publishedAt: 1,
      viewCount: 1,
      author: "$authorDoc",
      tags: "$tagDocs.name",
    },
  },
  { $sort: { publishedAt: -1 } },
  { $limit: 20 },
]);
```

### Faceted Search

```typescript
// Multiple aggregations in a single query
const searchResults = await Post.aggregate([
  { $match: { status: "published" } },
  {
    $facet: {
      results: [
        { $sort: { publishedAt: -1 } },
        { $skip: 0 },
        { $limit: 20 },
        { $project: { title: 1, slug: 1, publishedAt: 1, viewCount: 1 } },
      ],
      totalCount: [{ $count: "count" }],
      byCategory: [
        { $group: { _id: "$category", count: { $sum: 1 } } },
        { $sort: { count: -1 } },
      ],
      viewDistribution: [
        {
          $bucket: {
            groupBy: "$viewCount",
            boundaries: [0, 100, 500, 1000, 5000],
            default: "5000+",
            output: { count: { $sum: 1 } },
          },
        },
      ],
    },
  },
]);
```

### Time-Series Aggregation

```typescript
// Daily post counts and views for the last 30 days
const dailyStats = await Post.aggregate([
  {
    $match: {
      publishedAt: {
        $gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
      },
      status: "published",
    },
  },
  {
    $group: {
      _id: {
        $dateToString: { format: "%Y-%m-%d", date: "$publishedAt" },
      },
      posts: { $sum: 1 },
      views: { $sum: "$viewCount" },
    },
  },
  { $sort: { _id: 1 } },
  {
    $project: {
      _id: 0,
      date: "$_id",
      posts: 1,
      views: 1,
    },
  },
]);
```

### Aggregation with $expr and Computed Fields

```typescript
// Find posts where viewCount exceeds the author's average
const outperformingPosts = await Post.aggregate([
  { $match: { status: "published" } },
  {
    $lookup: {
      from: "posts",
      let: { authorId: "$author" },
      pipeline: [
        {
          $match: {
            $expr: { $eq: ["$author", "$$authorId"] },
            status: "published",
          },
        },
        { $group: { _id: null, avgViews: { $avg: "$viewCount" } } },
      ],
      as: "authorAvg",
    },
  },
  { $unwind: "$authorAvg" },
  {
    $match: {
      $expr: { $gt: ["$viewCount", "$authorAvg.avgViews"] },
    },
  },
  {
    $project: {
      title: 1,
      viewCount: 1,
      authorAvg: "$authorAvg.avgViews",
    },
  },
]);
```

---

## 5. Indexing Strategies

### Index Types

```typescript
// Single field index
userSchema.index({ email: 1 });

// Compound index (order matters for query planner)
postSchema.index({ status: 1, publishedAt: -1 });

// Unique index
userSchema.index({ email: 1 }, { unique: true });

// Text index for full-text search
postSchema.index(
  { title: "text", content: "text" },
  { weights: { title: 10, content: 1 }, name: "post_text_search" },
);

// TTL index (auto-expire documents)
const sessionSchema = new Schema({
  userId: { type: Schema.Types.ObjectId, required: true },
  token: { type: String, required: true },
  expiresAt: {
    type: Date,
    required: true,
    index: { expireAfterSeconds: 0 },
  },
});

// Partial index (index a subset of documents)
postSchema.index(
  { publishedAt: -1 },
  { partialFilterExpression: { status: "published" } },
);

// Sparse index (only index documents where the field exists)
userSchema.index({ "profile.avatarUrl": 1 }, { sparse: true });

// Wildcard index (index all fields in a subdocument)
postSchema.index({ "metadata.$**": 1 });
```

### Index Management with Native Driver

```typescript
const db = getDB();
const collection = db.collection("posts");

// Create indexes programmatically
await collection.createIndexes([
  { key: { slug: 1 }, unique: true },
  { key: { status: 1, publishedAt: -1 } },
  { key: { author: 1, status: 1 } },
  { key: { tags: 1 } },
]);

// List all indexes
const indexes = await collection.indexes();

// Drop unused index
await collection.dropIndex("old_index_name");

// Analyze query performance
const explanation = await collection
  .find({ status: "published" })
  .sort({ publishedAt: -1 })
  .explain("executionStats");

console.log("Docs examined:", explanation.executionStats.totalDocsExamined);
console.log("Time (ms):", explanation.executionStats.executionTimeMillis);
console.log("Index used:", explanation.queryPlanner.winningPlan.inputStage?.indexName);
```

### Compound Index Design Rules

Follow the **ESR rule** (Equality, Sort, Range) when designing compound indexes:

```typescript
// Query: find published posts by author, sorted by date, with view filter
// Equality first, then Sort, then Range
postSchema.index({ author: 1, status: 1, publishedAt: -1, viewCount: 1 });

// This index supports all of these queries:
// { author: id }
// { author: id, status: "published" }
// { author: id, status: "published" } + sort({ publishedAt: -1 })
// { author: id, status: "published", viewCount: { $gte: 100 } } + sort({ publishedAt: -1 })
```

---

## 6. Transactions

MongoDB transactions require a replica set or sharded cluster (including Atlas).

### Session-Based Transactions (Mongoose)

```typescript
import mongoose from "mongoose";

async function transferCredits(
  fromUserId: string,
  toUserId: string,
  amount: number,
): Promise<void> {
  const session = await mongoose.startSession();

  try {
    await session.withTransaction(async () => {
      const sender = await User.findById(fromUserId).session(session);
      if (!sender || sender.loginCount < amount) {
        throw new Error("Insufficient credits");
      }

      await User.findByIdAndUpdate(
        fromUserId,
        { $inc: { loginCount: -amount } },
        { session },
      );

      await User.findByIdAndUpdate(
        toUserId,
        { $inc: { loginCount: amount } },
        { session },
      );

      await TransactionLog.create(
        [{ from: fromUserId, to: toUserId, amount, type: "transfer" }],
        { session },
      );
    });
  } finally {
    await session.endSession();
  }
}
```

### Transaction with Native Driver

```typescript
import { MongoClient } from "mongodb";

async function createOrderWithInventory(
  client: MongoClient,
  orderId: string,
  items: Array<{ productId: string; quantity: number }>,
): Promise<void> {
  const session = client.startSession();

  try {
    await session.withTransaction(async () => {
      const db = client.db("myapp");
      const orders = db.collection("orders");
      const inventory = db.collection("inventory");

      for (const item of items) {
        const result = await inventory.updateOne(
          { productId: item.productId, stock: { $gte: item.quantity } },
          { $inc: { stock: -item.quantity } },
          { session },
        );

        if (result.modifiedCount === 0) {
          throw new Error(
            `Insufficient stock for product ${item.productId}`,
          );
        }
      }

      await orders.insertOne(
        { orderId, items, status: "confirmed", createdAt: new Date() },
        { session },
      );
    });
  } finally {
    await session.endSession();
  }
}
```

---

## 7. Change Streams

Change streams provide real-time notifications for data changes. They require a replica set or sharded cluster.

### Watching a Collection

```typescript
import { ChangeStreamDocument } from "mongodb";

const changeStream = Post.watch([], { fullDocument: "updateLookup" });

changeStream.on("change", (change: ChangeStreamDocument) => {
  switch (change.operationType) {
    case "insert":
      console.log("New post:", change.fullDocument?.title);
      break;
    case "update":
      console.log("Updated post:", change.fullDocument?.title);
      console.log("Changed fields:", change.updateDescription?.updatedFields);
      break;
    case "delete":
      console.log("Deleted post:", change.documentKey._id);
      break;
  }
});

process.on("SIGTERM", () => changeStream.close());
```

### Filtered Change Stream with Resume

```typescript
const pipeline = [
  {
    $match: {
      $or: [
        { operationType: "insert", "fullDocument.status": "published" },
        {
          operationType: "update",
          "updateDescription.updatedFields.status": "published",
        },
      ],
    },
  },
];

let resumeToken: unknown;

async function startWatching(): Promise<void> {
  const options: Record<string, unknown> = { fullDocument: "updateLookup" };
  if (resumeToken) {
    options.resumeAfter = resumeToken;
  }

  const stream = Post.watch(pipeline, options);

  stream.on("change", (change) => {
    resumeToken = change._id;
    notifySubscribers(change.fullDocument);
  });

  stream.on("error", (err) => {
    console.error("Change stream error:", err);
    setTimeout(startWatching, 5000);
  });
}
```

---

## 8. Atlas Search

Atlas Search provides Lucene-based full-text search on MongoDB Atlas. Define search indexes in the Atlas UI or with the `createSearchIndex` command.

### Search Index Definition (Atlas UI / JSON)

```json
{
  "mappings": {
    "dynamic": false,
    "fields": {
      "title": { "type": "string", "analyzer": "lucene.english" },
      "content": { "type": "string", "analyzer": "lucene.english" },
      "tags": { "type": "token" },
      "status": { "type": "token" },
      "publishedAt": { "type": "date" },
      "viewCount": { "type": "number" }
    }
  }
}
```

### Full-Text Search

```typescript
const results = await Post.aggregate([
  {
    $search: {
      index: "posts_search",
      text: {
        query: "typescript mongodb",
        path: ["title", "content"],
        fuzzy: { maxEdits: 1 },
      },
    },
  },
  { $match: { status: "published" } },
  {
    $project: {
      title: 1,
      slug: 1,
      publishedAt: 1,
      score: { $meta: "searchScore" },
    },
  },
  { $limit: 20 },
]);
```

### Compound Search with Filters

```typescript
const searchResults = await Post.aggregate([
  {
    $search: {
      index: "posts_search",
      compound: {
        must: [
          {
            text: {
              query: searchQuery,
              path: ["title", "content"],
              fuzzy: { maxEdits: 1 },
            },
          },
        ],
        filter: [
          { text: { query: "published", path: "status" } },
          {
            range: {
              path: "publishedAt",
              gte: new Date("2025-01-01"),
            },
          },
        ],
        should: [
          {
            text: {
              query: searchQuery,
              path: "title",
              score: { boost: { value: 3 } },
            },
          },
        ],
      },
      highlight: { path: ["title", "content"] },
    },
  },
  {
    $project: {
      title: 1,
      slug: 1,
      publishedAt: 1,
      score: { $meta: "searchScore" },
      highlights: { $meta: "searchHighlights" },
    },
  },
  { $limit: 20 },
]);
```

### Autocomplete

```typescript
// Requires an autocomplete field mapping in the search index
const suggestions = await Post.aggregate([
  {
    $search: {
      index: "posts_autocomplete",
      autocomplete: {
        query: partialInput,
        path: "title",
        tokenOrder: "sequential",
        fuzzy: { maxEdits: 1, prefixLength: 2 },
      },
    },
  },
  { $project: { title: 1, slug: 1, score: { $meta: "searchScore" } } },
  { $limit: 10 },
]);
```

---

## 9. Population and References

### Basic Population

```typescript
// Populate single reference
const post = await Post.findById(postId)
  .populate("author", "name email")
  .lean();

// Populate multiple references
const postFull = await Post.findById(postId)
  .populate("author", "name email")
  .populate("category", "name slug")
  .populate("tags", "name")
  .lean();

// Nested population
const postNested = await Post.findById(postId)
  .populate({
    path: "author",
    select: "name email profile",
    populate: { path: "profile.organization", select: "name" },
  })
  .lean();
```

### Conditional and Filtered Population

```typescript
// Populate with match filter
const user = await User.findById(userId)
  .populate({
    path: "posts",
    match: { status: "published" },
    select: "title slug publishedAt",
    options: { sort: { publishedAt: -1 }, limit: 10 },
  })
  .lean();

// Virtual populate (when there is no explicit ref array on the parent)
userSchema.virtual("posts", {
  ref: "Post",
  localField: "_id",
  foreignField: "author",
  options: { sort: { createdAt: -1 } },
});

// Must enable virtuals in toJSON/toObject
userSchema.set("toJSON", { virtuals: true });
userSchema.set("toObject", { virtuals: true });

// Then populate the virtual
const userWithPosts = await User.findById(userId)
  .populate("posts")
  .lean({ virtuals: true });
```

### Manual Population with Aggregation $lookup

Use `$lookup` when `populate()` is insufficient (cross-database joins, complex pipelines, or performance-critical paths).

```typescript
const usersWithPostStats = await User.aggregate([
  { $match: { isActive: true } },
  {
    $lookup: {
      from: "posts",
      let: { userId: "$_id" },
      pipeline: [
        {
          $match: {
            $expr: { $eq: ["$author", "$$userId"] },
            status: "published",
          },
        },
        {
          $group: {
            _id: null,
            count: { $sum: 1 },
            totalViews: { $sum: "$viewCount" },
          },
        },
      ],
      as: "postStats",
    },
  },
  {
    $addFields: {
      postCount: { $ifNull: [{ $first: "$postStats.count" }, 0] },
      totalViews: { $ifNull: [{ $first: "$postStats.totalViews" }, 0] },
    },
  },
  { $project: { postStats: 0, passwordHash: 0 } },
  { $sort: { totalViews: -1 } },
]);
```

---

## 10. Practical Patterns

### Cursor-Based Pagination

```typescript
interface PaginationResult<T> {
  data: T[];
  nextCursor: string | null;
  hasMore: boolean;
}

async function paginatePosts(
  cursor?: string,
  limit: number = 20,
): Promise<PaginationResult<IPost>> {
  const query: Record<string, unknown> = { status: "published" };

  if (cursor) {
    query._id = { $lt: new mongoose.Types.ObjectId(cursor) };
  }

  const posts = await Post.find(query)
    .sort({ _id: -1 })
    .limit(limit + 1)
    .populate("author", "name")
    .lean();

  const hasMore = posts.length > limit;
  const data = hasMore ? posts.slice(0, -1) : posts;

  return {
    data,
    nextCursor: hasMore ? data[data.length - 1]._id.toString() : null,
    hasMore,
  };
}
```

### Bulk Write Operations

```typescript
const bulkOps = [
  {
    updateOne: {
      filter: { email: "alice@example.com" },
      update: { $set: { role: "admin" } },
    },
  },
  {
    updateMany: {
      filter: { lastLoginAt: { $lt: new Date("2025-06-01") } },
      update: { $set: { isActive: false } },
    },
  },
  {
    insertOne: {
      document: {
        email: "new@example.com",
        name: "New User",
        passwordHash: h,
      },
    },
  },
  {
    deleteMany: {
      filter: { role: "guest", createdAt: { $lt: new Date("2025-01-01") } },
    },
  },
];

const result = await User.bulkWrite(bulkOps, { ordered: false });
console.log("Matched:", result.matchedCount);
console.log("Modified:", result.modifiedCount);
console.log("Inserted:", result.insertedCount);
console.log("Deleted:", result.deletedCount);
```

### Middleware Patterns

```typescript
// Pre-save: hash password
userSchema.pre("save", async function (next) {
  if (!this.isModified("passwordHash")) return next();
  const bcrypt = await import("bcryptjs");
  this.passwordHash = await bcrypt.hash(this.passwordHash, 12);
  next();
});

// Post-save: emit event
postSchema.post("save", function (doc) {
  if (doc.status === "published") {
    eventEmitter.emit("post:published", {
      postId: doc._id,
      title: doc.title,
    });
  }
});

// Pre-deleteOne: cascade delete related documents
userSchema.pre(
  "deleteOne",
  { document: true, query: false },
  async function () {
    await Post.deleteMany({ author: this._id });
    await Comment.deleteMany({ author: this._id });
  },
);
```

---

## Additional Resources

- Mongoose documentation: https://mongoosejs.com/docs/
- MongoDB Node.js driver: https://www.mongodb.com/docs/drivers/node/current/
- Aggregation pipeline reference: https://www.mongodb.com/docs/manual/reference/operator/aggregation/
- Atlas Search: https://www.mongodb.com/docs/atlas/atlas-search/
- Change streams: https://www.mongodb.com/docs/manual/changeStreams/
- Index strategies: https://www.mongodb.com/docs/manual/applications/indexes/
- Transaction guide: https://www.mongodb.com/docs/manual/core/transactions/
