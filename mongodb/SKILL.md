---
name: mongodb
description: MongoDB database operations covering Mongoose schemas, CRUD operations, aggregation pipeline, indexing, transactions, change streams, Atlas Search, population, and connection management patterns.
---

# MongoDB

This skill should be used when working with MongoDB databases. It covers Mongoose ODM, aggregation pipeline, indexing, transactions, and Atlas features.

## When to Use This Skill

Use this skill when you need to:

- Model and query document-based data
- Build aggregation pipelines for analytics
- Set up Mongoose schemas with validation
- Handle transactions across collections
- Implement full-text search with Atlas Search

## Setup (Mongoose)

```typescript
import mongoose from "mongoose";

await mongoose.connect(process.env.MONGODB_URI!, {
  maxPoolSize: 10,
  serverSelectionTimeoutMS: 5000,
});
```

## Schema & Model

```typescript
import { Schema, model, Types } from "mongoose";

interface IUser {
  name: string;
  email: string;
  role: "user" | "admin";
  profile: { bio?: string; avatar?: string };
  tags: string[];
  createdAt: Date;
}

const userSchema = new Schema<IUser>(
  {
    name: { type: String, required: true, trim: true },
    email: { type: String, required: true, unique: true, lowercase: true },
    role: { type: String, enum: ["user", "admin"], default: "user" },
    profile: {
      bio: { type: String, maxlength: 500 },
      avatar: String,
    },
    tags: [{ type: String }],
  },
  { timestamps: true },
);

// Indexes
userSchema.index({ email: 1 }, { unique: true });
userSchema.index({ tags: 1 });
userSchema.index({ name: "text", "profile.bio": "text" });

const User = model<IUser>("User", userSchema);
```

## CRUD Operations

```typescript
// Create
const user = await User.create({ name: "Alice", email: "alice@example.com", tags: ["dev"] });

// Read
const found = await User.findById(userId);
const users = await User.find({ role: "admin" }).sort({ createdAt: -1 }).limit(10).lean();

// Update
await User.findByIdAndUpdate(userId, { $set: { role: "admin" }, $push: { tags: "staff" } }, { new: true });

// Delete
await User.findByIdAndDelete(userId);

// Upsert
await User.findOneAndUpdate({ email: "bob@example.com" }, { name: "Bob" }, { upsert: true, new: true });
```

## Aggregation Pipeline

```typescript
const stats = await User.aggregate([
  { $match: { createdAt: { $gte: new Date("2024-01-01") } } },
  { $unwind: "$tags" },
  {
    $group: {
      _id: "$tags",
      count: { $sum: 1 },
      users: { $push: "$name" },
    },
  },
  { $sort: { count: -1 } },
  { $limit: 10 },
  {
    $project: {
      tag: "$_id",
      count: 1,
      topUsers: { $slice: ["$users", 3] },
    },
  },
]);
```

## Population (References)

```typescript
const postSchema = new Schema({
  title: String,
  content: String,
  author: { type: Schema.Types.ObjectId, ref: "User" },
  comments: [{ type: Schema.Types.ObjectId, ref: "Comment" }],
});

const Post = model("Post", postSchema);

// Populate references
const post = await Post.findById(postId)
  .populate("author", "name email")
  .populate({ path: "comments", populate: { path: "author", select: "name" } });
```

## Transactions

```typescript
const session = await mongoose.startSession();
try {
  session.startTransaction();

  const order = await Order.create([{ userId, items, total }], { session });
  await User.findByIdAndUpdate(userId, { $inc: { balance: -total } }, { session });
  await Inventory.bulkWrite(
    items.map((item) => ({
      updateOne: { filter: { _id: item.productId }, update: { $inc: { stock: -item.quantity } } },
    })),
    { session },
  );

  await session.commitTransaction();
} catch (error) {
  await session.abortTransaction();
  throw error;
} finally {
  session.endSession();
}
```

## Change Streams

```typescript
const changeStream = User.watch([{ $match: { operationType: { $in: ["insert", "update"] } } }]);

changeStream.on("change", (change) => {
  if (change.operationType === "insert") {
    console.log("New user:", change.fullDocument);
  } else if (change.operationType === "update") {
    console.log("Updated fields:", change.updateDescription.updatedFields);
  }
});
```

## Additional Resources

- Mongoose docs: https://mongoosejs.com/docs/
- MongoDB manual: https://www.mongodb.com/docs/manual/
- Aggregation pipeline: https://www.mongodb.com/docs/manual/core/aggregation-pipeline/
