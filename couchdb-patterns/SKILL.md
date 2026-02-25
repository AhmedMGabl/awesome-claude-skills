---
name: couchdb-patterns
description: Apache CouchDB patterns covering document design, MapReduce views, Mango queries, replication, conflict resolution, PouchDB sync, and offline-first applications.
---

# CouchDB Patterns

This skill should be used when building applications with Apache CouchDB. It covers document design, views, Mango queries, replication, conflicts, and PouchDB sync.

## When to Use This Skill

Use this skill when you need to:

- Design document-oriented databases
- Build offline-first apps with PouchDB sync
- Use MapReduce views for querying
- Implement multi-master replication
- Handle conflict resolution strategies

## Document Design

```json
{
  "_id": "user:alice@example.com",
  "_rev": "1-abc123",
  "type": "user",
  "name": "Alice",
  "email": "alice@example.com",
  "roles": ["admin"],
  "created_at": "2024-01-01T00:00:00Z"
}
```

```typescript
import Nano from "nano";

const couch = Nano("http://admin:password@localhost:5984");
const db = couch.db.use("myapp");

// Create document
const { id, rev } = await db.insert({
  type: "user",
  name: "Alice",
  email: "alice@example.com",
});

// Read document
const doc = await db.get(id);

// Update document
await db.insert({ ...doc, name: "Alice Smith" });

// Delete document
await db.destroy(id, doc._rev);

// Bulk operations
const result = await db.bulk({
  docs: [
    { type: "user", name: "Bob" },
    { type: "user", name: "Charlie" },
  ],
});
```

## MapReduce Views

```javascript
// Design document: _design/users
{
  "_id": "_design/users",
  "views": {
    "by_email": {
      "map": "function(doc) { if (doc.type === 'user') emit(doc.email, { name: doc.name }); }"
    },
    "count_by_role": {
      "map": "function(doc) { if (doc.type === 'user' && doc.roles) doc.roles.forEach(function(r) { emit(r, 1); }); }",
      "reduce": "_count"
    }
  }
}
```

```typescript
// Query view
const result = await db.view("users", "by_email", {
  key: "alice@example.com",
  include_docs: true,
});

// Range query
const admins = await db.view("users", "count_by_role", {
  key: "admin",
  group: true,
});
```

## Mango Queries

```typescript
// Create index
await db.createIndex({
  index: { fields: ["type", "created_at"] },
  name: "type-date-index",
});

// Query with selector
const result = await db.find({
  selector: {
    type: "user",
    created_at: { $gte: "2024-01-01" },
  },
  sort: [{ created_at: "desc" }],
  limit: 20,
  fields: ["name", "email", "created_at"],
});
```

## Replication

```typescript
// One-time replication
await couch.db.replicate("myapp", "myapp-backup");

// Continuous replication
await couch.db.replicate("myapp", "http://remote:5984/myapp", {
  continuous: true,
  filter: "myapp/by_type",
  query_params: { type: "user" },
});
```

## PouchDB (Client-Side Sync)

```typescript
import PouchDB from "pouchdb";

const localDb = new PouchDB("myapp");
const remoteDb = new PouchDB("http://localhost:5984/myapp");

// Sync (bidirectional)
const sync = localDb.sync(remoteDb, {
  live: true,
  retry: true,
});

sync.on("change", (info) => console.log("Sync change:", info.direction));
sync.on("error", (err) => console.error("Sync error:", err));

// Local CRUD
await localDb.put({ _id: "todo:1", text: "Buy groceries", done: false });
const doc = await localDb.get("todo:1");
```

## Conflict Resolution

```typescript
// Fetch conflicts
const doc = await db.get("user:alice", { conflicts: true });

if (doc._conflicts) {
  // Fetch conflicting revisions
  const conflicts = await Promise.all(
    doc._conflicts.map((rev) => db.get("user:alice", { rev }))
  );

  // Merge strategy: pick latest
  const winner = [doc, ...conflicts]
    .sort((a, b) => b.updated_at.localeCompare(a.updated_at))[0];

  // Delete losing revisions
  await db.bulk({
    docs: doc._conflicts.map((rev) => ({
      _id: doc._id,
      _rev: rev,
      _deleted: true,
    })),
  });
}
```

## Additional Resources

- CouchDB: https://docs.couchdb.org/
- Nano: https://github.com/apache/nano
- PouchDB: https://pouchdb.com/guides/
