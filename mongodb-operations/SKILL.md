---
name: mongodb-operations
description: This skill should be used when users need to work with MongoDB databases, including schema design, query optimization, aggregation pipelines, indexing strategies, and database operations. Provides best practices for MongoDB development and operations.
---

# MongoDB Operations

Comprehensive MongoDB database operations, query optimization, schema design, and best practices guide.

## When to Use This Skill

Use this skill when:
- User mentions "MongoDB", "Mongo", or "NoSQL database"
- User needs to design MongoDB schemas or collections
- User wants to write MongoDB queries or aggregation pipelines
- User asks about indexing strategies or performance optimization
- User needs help with MongoDB Atlas, Compass, or mongosh
- User mentions "document database" or "BSON"

## Key Features

### 1. Schema Design
- Document structure design
- Embedding vs referencing strategies
- Schema validation
- Data modeling patterns

### 2. Query Operations
- CRUD operations (Create, Read, Update, Delete)
- Complex queries with filters
- Projection and sorting
- Query optimization

### 3. Aggregation Framework
- Pipeline stages
- Data transformation
- Analytics queries
- Performance optimization

### 4. Indexing
- Index types and strategies
- Compound indexes
- Index performance analysis
- Index management

### 5. Operations
- Database administration
- Backup and restore
- Monitoring and diagnostics
- Security configuration

## Connection Examples

### Node.js (MongoDB Driver)

```javascript
const { MongoClient } = require('mongodb');

// Connection URI
const uri = 'mongodb://localhost:27017';

// Create client
const client = new MongoClient(uri);

async function connect() {
  try {
    // Connect to MongoDB
    await client.connect();
    console.log('Connected to MongoDB');

    // Get database and collection
    const database = client.db('myDatabase');
    const collection = database.collection('myCollection');

    return { database, collection };
  } catch (error) {
    console.error('Connection error:', error);
    throw error;
  }
}
```

### Python (PyMongo)

```python
from pymongo import MongoClient

# Create client
client = MongoClient('mongodb://localhost:27017/')

# Get database and collection
db = client['myDatabase']
collection = db['myCollection']

# Connection with MongoDB Atlas
client = MongoClient(
    f'mongodb+srv://{username}:{password}@cluster.mongodb.net/'
)
```

### Mongoose (ODM for Node.js)

```javascript
const mongoose = require('mongoose');

mongoose.connect('mongodb://localhost:27017/myDatabase', {
  useNewUrlParser: true,
  useUnifiedTopology: true
});

// Define schema
const userSchema = new mongoose.Schema({
  name: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  age: Number,
  createdAt: { type: Date, default: Date.now }
});

// Create model
const User = mongoose.model('User', userSchema);
```

## CRUD Operations

### Create (Insert)

```javascript
// Insert one document
await collection.insertOne({
  name: 'John Doe',
  email: 'john@example.com',
  age: 30,
  tags: ['developer', 'javascript']
});

// Insert many documents
await collection.insertMany([
  { name: 'Alice', age: 25 },
  { name: 'Bob', age: 35 }
]);
```

### Read (Find)

```javascript
// Find all documents
const allDocs = await collection.find({}).toArray();

// Find with filter
const users = await collection.find({ age: { $gte: 25 } }).toArray();

// Find one document
const user = await collection.findOne({ email: 'john@example.com' });

// Find with projection (select specific fields)
const names = await collection.find(
  {},
  { projection: { name: 1, _id: 0 } }
).toArray();

// Find with sort
const sorted = await collection.find({})
  .sort({ age: -1 })  // Descending order
  .limit(10)
  .toArray();
```

### Update

```javascript
// Update one document
await collection.updateOne(
  { email: 'john@example.com' },
  { $set: { age: 31 } }
);

// Update many documents
await collection.updateMany(
  { age: { $lt: 30 } },
  { $set: { category: 'young' } }
);

// Replace document
await collection.replaceOne(
  { _id: someId },
  { name: 'New Name', age: 25 }
);

// Update with operators
await collection.updateOne(
  { _id: userId },
  {
    $set: { status: 'active' },
    $inc: { loginCount: 1 },
    $push: { tags: 'verified' },
    $currentDate: { lastModified: true }
  }
);
```

### Delete

```javascript
// Delete one document
await collection.deleteOne({ email: 'john@example.com' });

// Delete many documents
await collection.deleteMany({ age: { $lt: 18 } });

// Find and delete
const deleted = await collection.findOneAndDelete(
  { email: 'john@example.com' }
);
```

## Query Operators

### Comparison Operators

```javascript
// $eq (equal), $ne (not equal)
{ age: { $eq: 30 } }
{ status: { $ne: 'inactive' } }

// $gt (greater than), $gte (greater than or equal)
{ age: { $gt: 18 } }
{ price: { $gte: 100 } }

// $lt (less than), $lte (less than or equal)
{ age: { $lt: 65 } }
{ stock: { $lte: 10 } }

// $in (in array), $nin (not in array)
{ category: { $in: ['electronics', 'computers'] } }
{ status: { $nin: ['cancelled', 'refunded'] } }
```

### Logical Operators

```javascript
// $and
{ $and: [
  { age: { $gte: 18 } },
  { country: 'USA' }
]}

// $or
{ $or: [
  { category: 'electronics' },
  { price: { $lt: 50 } }
]}

// $not
{ age: { $not: { $lt: 18 } } }

// $nor
{ $nor: [
  { status: 'inactive' },
  { deleted: true }
]}
```

### Element Operators

```javascript
// $exists
{ email: { $exists: true } }

// $type
{ age: { $type: 'number' } }
```

### Array Operators

```javascript
// $all (contains all elements)
{ tags: { $all: ['mongodb', 'database'] } }

// $elemMatch (array element matches conditions)
{
  scores: {
    $elemMatch: { $gte: 80, $lt: 90 }
  }
}

// $size (array has specific length)
{ tags: { $size: 3 } }
```

## Aggregation Framework

### Basic Pipeline

```javascript
const result = await collection.aggregate([
  // Stage 1: Match (filter)
  { $match: { status: 'active' } },

  // Stage 2: Group (aggregate)
  {
    $group: {
      _id: '$category',
      total: { $sum: '$amount' },
      count: { $sum: 1 },
      avgAmount: { $avg: '$amount' }
    }
  },

  // Stage 3: Sort
  { $sort: { total: -1 } },

  // Stage 4: Limit
  { $limit: 10 }
]).toArray();
```

### Advanced Aggregation

```javascript
// Lookup (join with another collection)
await collection.aggregate([
  {
    $lookup: {
      from: 'orders',
      localField: '_id',
      foreignField: 'userId',
      as: 'userOrders'
    }
  },
  {
    $project: {
      name: 1,
      orderCount: { $size: '$userOrders' }
    }
  }
]);

// Unwind (deconstruct array)
await collection.aggregate([
  { $unwind: '$items' },
  {
    $group: {
      _id: '$items.category',
      totalQuantity: { $sum: '$items.quantity' }
    }
  }
]);

// Facet (multiple aggregations in one query)
await collection.aggregate([
  {
    $facet: {
      byCategory: [
        { $group: { _id: '$category', count: { $sum: 1 } } }
      ],
      byPrice: [
        {
          $bucket: {
            groupBy: '$price',
            boundaries: [0, 50, 100, 500, 1000],
            default: '1000+',
            output: { count: { $sum: 1 } }
          }
        }
      ]
    }
  }
]);
```

## Indexing

### Create Indexes

```javascript
// Single field index
await collection.createIndex({ email: 1 });

// Compound index
await collection.createIndex({
  category: 1,
  price: -1
});

// Unique index
await collection.createIndex(
  { email: 1 },
  { unique: true }
);

// Text index for full-text search
await collection.createIndex({
  description: 'text',
  title: 'text'
});

// TTL index (auto-delete after time)
await collection.createIndex(
  { createdAt: 1 },
  { expireAfterSeconds: 86400 }  // 24 hours
);

// Partial index (index subset of documents)
await collection.createIndex(
  { status: 1 },
  {
    partialFilterExpression: {
      status: { $exists: true }
    }
  }
);
```

### Index Management

```javascript
// List indexes
const indexes = await collection.indexes();

// Drop index
await collection.dropIndex('email_1');

// Get index stats
const stats = await collection.stats();
```

## Schema Design Patterns

### Embedding Pattern

```javascript
// Good for: 1-to-few relationships
// Example: User with embedded addresses
{
  _id: ObjectId('...'),
  name: 'John Doe',
  email: 'john@example.com',
  addresses: [
    {
      type: 'home',
      street: '123 Main St',
      city: 'New York',
      zip: '10001'
    },
    {
      type: 'work',
      street: '456 Office Ave',
      city: 'New York',
      zip: '10002'
    }
  ]
}
```

### Referencing Pattern

```javascript
// Good for: 1-to-many or many-to-many
// Example: User and Orders (separate collections)

// Users collection
{
  _id: ObjectId('user123'),
  name: 'John Doe',
  email: 'john@example.com'
}

// Orders collection
{
  _id: ObjectId('order456'),
  userId: ObjectId('user123'),  // Reference
  items: [...],
  total: 150.00
}
```

### Subset Pattern

```javascript
// Store frequently accessed subset of data
// Example: Product with reviews

// Products collection
{
  _id: ObjectId('...'),
  name: 'Laptop',
  price: 999,
  recentReviews: [
    // Last 10 reviews embedded
    { author: 'Alice', rating: 5, text: 'Great!' }
  ],
  reviewCount: 247
}

// Reviews collection (complete data)
{
  _id: ObjectId('...'),
  productId: ObjectId('...'),
  author: 'Alice',
  rating: 5,
  text: 'Great laptop!',
  createdAt: ISODate('...')
}
```

## Performance Optimization

### Use Explain to Analyze Queries

```javascript
// Analyze query performance
const explain = await collection.find({ age: { $gt: 25 } })
  .explain('executionStats');

console.log(explain.executionStats.totalDocsExamined);
console.log(explain.executionStats.executionTimeMillis);
```

### Best Practices

1. **Use Indexes Wisely**
   - Create indexes for frequently queried fields
   - Use compound indexes for multi-field queries
   - Monitor index usage with `$indexStats`

2. **Optimize Aggregation Pipelines**
   - Place `$match` early to reduce documents
   - Use `$project` to limit field selection
   - Leverage indexes in `$match` and `$sort`

3. **Query Optimization**
   - Use projections to select only needed fields
   - Limit results when appropriate
   - Avoid scanning entire collections

4. **Schema Design**
   - Embed for 1-to-few relationships
   - Reference for 1-to-many relationships
   - Denormalize for read-heavy workloads

## Security Best Practices

### Authentication

```javascript
// Connect with authentication
const client = new MongoClient(uri, {
  auth: {
    username: 'myuser',
    password: 'mypassword'
  }
});
```

### Role-Based Access Control

```javascript
// Create user with specific role
db.createUser({
  user: 'appUser',
  pwd: 'securePassword',
  roles: [
    { role: 'readWrite', db: 'myDatabase' }
  ]
});
```

### Field-Level Encryption

```javascript
// Client-side field level encryption configuration
const clientEncryption = new ClientEncryption(client, {
  keyVaultNamespace: 'encryption.__keyVault',
  kmsProviders: {
    local: {
      key: localMasterKey
    }
  }
});
```

## Common Use Cases

### User Authentication System

```javascript
// Register user
async function registerUser(email, passwordHash) {
  return await users.insertOne({
    email,
    passwordHash,
    createdAt: new Date(),
    lastLogin: null,
    profile: {
      name: '',
      avatarUrl: ''
    }
  });
}

// Login user
async function loginUser(email, passwordHash) {
  const user = await users.findOne({ email, passwordHash });
  if (user) {
    await users.updateOne(
      { _id: user._id },
      { $set: { lastLogin: new Date() } }
    );
  }
  return user;
}
```

### E-Commerce Product Catalog

```javascript
// Product schema with inventory tracking
{
  _id: ObjectId('...'),
  sku: 'LAPTOP-001',
  name: 'Gaming Laptop',
  description: '...',
  price: 1299.99,
  category: 'electronics',
  tags: ['gaming', 'laptop', 'nvidia'],
  stock: 15,
  images: ['url1', 'url2'],
  specifications: {
    cpu: 'Intel i7',
    ram: '16GB',
    storage: '512GB SSD'
  },
  reviews: {
    average: 4.5,
    count: 128
  }
}
```

### Analytics and Reporting

```javascript
// Sales report by category
const salesReport = await orders.aggregate([
  {
    $match: {
      orderDate: {
        $gte: new Date('2026-01-01'),
        $lte: new Date('2026-01-31')
      }
    }
  },
  { $unwind: '$items' },
  {
    $group: {
      _id: '$items.category',
      totalRevenue: { $sum: '$items.total' },
      itemsSold: { $sum: '$items.quantity' },
      orderCount: { $sum: 1 }
    }
  },
  { $sort: { totalRevenue: -1 } }
]);
```

## Troubleshooting

### Common Issues

**Slow Queries**:
- Use `.explain()` to analyze execution
- Add appropriate indexes
- Optimize aggregation pipeline order

**High Memory Usage**:
- Use pagination with `skip()` and `limit()`
- Stream large result sets
- Use `allowDiskUse: true` for large aggregations

**Connection Issues**:
- Check connection string format
- Verify network connectivity
- Ensure MongoDB service is running
- Check authentication credentials

**Index Not Being Used**:
- Verify index exists with `getIndexes()`
- Check query matches index fields
- Use `.explain()` to confirm index usage

## Tools and Utilities

### MongoDB Compass
- GUI for MongoDB
- Visual query builder
- Performance monitoring
- Schema analysis

### mongosh (MongoDB Shell)
- Interactive JavaScript shell
- Execute queries directly
- Database administration
- Scripting and automation

### MongoDB Atlas
- Cloud-hosted MongoDB
- Automatic backups
- Monitoring and alerts
- Global distribution

## References

- MongoDB Manual: https://docs.mongodb.com/manual/
- Aggregation Pipeline: https://docs.mongodb.com/manual/core/aggregation-pipeline/
- Query Operators: https://docs.mongodb.com/manual/reference/operator/query/
- Schema Design Best Practices: https://docs.mongodb.com/manual/core/data-model-design/
- Performance Best Practices: https://docs.mongodb.com/manual/administration/analyzing-mongodb-performance/

---

**Created for**: awesome-claude-skills repository
**Version**: 1.0.0
**Last Updated**: January 25, 2026
