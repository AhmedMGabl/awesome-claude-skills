---
name: mongodb-mongoose
description: MongoDB Mongoose patterns covering schema definitions, validation, middleware hooks, population, aggregation pipelines, indexes, transactions, and TypeScript integration.
---

# MongoDB Mongoose

This skill should be used when building Node.js applications with MongoDB and Mongoose. It covers schemas, validation, middleware, population, aggregation, and transactions.

## When to Use This Skill

Use this skill when you need to:

- Define MongoDB schemas with Mongoose
- Validate and transform data with middleware
- Use population for document references
- Build aggregation pipelines
- Handle transactions and TypeScript types

## Setup

```bash
npm install mongoose
```

## Schema Definition

```typescript
import mongoose, { Schema, Document, Model } from "mongoose";

interface IUser extends Document {
  name: string;
  email: string;
  role: "admin" | "user" | "editor";
  posts: mongoose.Types.ObjectId[];
  createdAt: Date;
}

const userSchema = new Schema<IUser>(
  {
    name: { type: String, required: true, trim: true, minlength: 2 },
    email: { type: String, required: true, unique: true, lowercase: true },
    role: { type: String, enum: ["admin", "user", "editor"], default: "user" },
    posts: [{ type: Schema.Types.ObjectId, ref: "Post" }],
  },
  { timestamps: true }
);

userSchema.index({ email: 1 });
userSchema.index({ name: "text" });

const User: Model<IUser> = mongoose.model("User", userSchema);
```

## CRUD Operations

```typescript
// Create
const user = await User.create({ name: "Alice", email: "alice@example.com" });

// Read
const users = await User.find({ role: "admin" }).sort({ createdAt: -1 }).limit(10);
const user = await User.findById(id);
const user = await User.findOne({ email: "alice@example.com" });

// Update
await User.findByIdAndUpdate(id, { name: "Bob" }, { new: true, runValidators: true });
await User.updateMany({ role: "user" }, { $set: { active: true } });

// Delete
await User.findByIdAndDelete(id);
await User.deleteMany({ createdAt: { $lt: oneYearAgo } });
```

## Population

```typescript
const postSchema = new Schema({
  title: { type: String, required: true },
  author: { type: Schema.Types.ObjectId, ref: "User", required: true },
  tags: [{ type: Schema.Types.ObjectId, ref: "Tag" }],
});

// Populate references
const post = await Post.findById(id)
  .populate("author", "name email")
  .populate("tags", "name");

// Deep populate
const post = await Post.findById(id).populate({
  path: "author",
  populate: { path: "posts", select: "title" },
});
```

## Middleware (Hooks)

```typescript
userSchema.pre("save", async function (next) {
  if (this.isModified("password")) {
    this.password = await bcrypt.hash(this.password, 12);
  }
  next();
});

userSchema.post("save", function (doc) {
  console.log("User saved:", doc.email);
});

userSchema.pre("find", function () {
  this.where({ deleted: { $ne: true } });
});
```

## Aggregation Pipeline

```typescript
const stats = await Post.aggregate([
  { $match: { published: true } },
  { $group: {
      _id: "$author",
      postCount: { $sum: 1 },
      avgLikes: { $avg: "$likes" },
    },
  },
  { $sort: { postCount: -1 } },
  { $limit: 10 },
  { $lookup: {
      from: "users",
      localField: "_id",
      foreignField: "_id",
      as: "authorInfo",
    },
  },
  { $unwind: "$authorInfo" },
  { $project: {
      author: "$authorInfo.name",
      postCount: 1,
      avgLikes: { $round: ["$avgLikes", 1] },
    },
  },
]);
```

## Transactions

```typescript
const session = await mongoose.startSession();
try {
  session.startTransaction();
  const user = await User.create([{ name: "Alice", email: "alice@example.com" }], { session });
  await Post.create([{ title: "First Post", author: user[0]._id }], { session });
  await session.commitTransaction();
} catch (error) {
  await session.abortTransaction();
  throw error;
} finally {
  session.endSession();
}
```

## Connection

```typescript
await mongoose.connect("mongodb://localhost:27017/mydb", {
  maxPoolSize: 10,
});
```

## Additional Resources

- Mongoose: https://mongoosejs.com/docs/
- MongoDB: https://www.mongodb.com/docs/manual/
- Aggregation: https://www.mongodb.com/docs/manual/aggregation/
