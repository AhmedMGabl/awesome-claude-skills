---
name: sqlite-libsql
description: SQLite and LibSQL/Turso development covering better-sqlite3 for Node.js, Turso embedded replicas, Drizzle and Prisma integration, WAL mode configuration, full-text search with FTS5, JSON functions, migrations, connection pooling, and edge deployment with LibSQL.
---

# SQLite & LibSQL

This skill should be used when working with SQLite or LibSQL/Turso databases. It covers Node.js drivers, Turso cloud, ORM integration, FTS5, and edge deployment.

## When to Use This Skill

Use this skill when you need to:

- Use SQLite for local or embedded databases
- Deploy to Turso (LibSQL) for distributed SQLite
- Implement full-text search with FTS5
- Configure WAL mode and performance tuning
- Integrate with Drizzle or Prisma ORM

## better-sqlite3 (Node.js)

```typescript
import Database from "better-sqlite3";

const db = new Database("app.db", { verbose: console.log });

// Enable WAL mode for better concurrent performance
db.pragma("journal_mode = WAL");
db.pragma("foreign_keys = ON");

// Create tables
db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
  );
  CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
`);

// Prepared statements (recommended for repeated queries)
const insertUser = db.prepare(
  "INSERT INTO users (email, name) VALUES (@email, @name)",
);
const getUser = db.prepare("SELECT * FROM users WHERE id = ?");
const listUsers = db.prepare("SELECT * FROM users ORDER BY created_at DESC LIMIT ?");

// Usage
const result = insertUser.run({ email: "user@test.com", name: "Test User" });
console.log("Inserted ID:", result.lastInsertRowid);

const user = getUser.get(1);
const users = listUsers.all(20);

// Transactions
const createManyUsers = db.transaction((users: { email: string; name: string }[]) => {
  for (const u of users) {
    insertUser.run(u);
  }
});
createManyUsers([
  { email: "a@test.com", name: "Alice" },
  { email: "b@test.com", name: "Bob" },
]);
```

## Turso (LibSQL) Client

```typescript
import { createClient } from "@libsql/client";

const db = createClient({
  url: process.env.TURSO_DATABASE_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN,
});

// Query
const result = await db.execute("SELECT * FROM users WHERE id = ?", [userId]);
const user = result.rows[0];

// Batch operations (single round-trip)
const batchResult = await db.batch([
  { sql: "INSERT INTO users (email, name) VALUES (?, ?)", args: ["a@test.com", "Alice"] },
  { sql: "INSERT INTO users (email, name) VALUES (?, ?)", args: ["b@test.com", "Bob"] },
], "write");

// Transaction
const tx = await db.transaction("write");
await tx.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", [100, fromId]);
await tx.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", [100, toId]);
await tx.commit();

// Embedded replica (edge performance)
const replicaDb = createClient({
  url: "file:local-replica.db",
  syncUrl: process.env.TURSO_DATABASE_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN,
  syncInterval: 60,  // sync every 60 seconds
});
```

## Full-Text Search (FTS5)

```sql
-- Create FTS table
CREATE VIRTUAL TABLE posts_fts USING fts5(title, body, content=posts, content_rowid=id);

-- Keep FTS in sync with triggers
CREATE TRIGGER posts_ai AFTER INSERT ON posts BEGIN
  INSERT INTO posts_fts(rowid, title, body) VALUES (new.id, new.title, new.body);
END;

CREATE TRIGGER posts_ad AFTER DELETE ON posts BEGIN
  INSERT INTO posts_fts(posts_fts, rowid, title, body) VALUES('delete', old.id, old.title, old.body);
END;

-- Search
SELECT p.*, rank FROM posts p
JOIN posts_fts ON posts_fts.rowid = p.id
WHERE posts_fts MATCH 'sqlite AND performance'
ORDER BY rank;
```

## JSON Functions

```sql
-- Store and query JSON
SELECT json_extract(metadata, '$.tags') FROM posts WHERE id = 1;

-- JSON array operations
SELECT * FROM posts
WHERE json_array_length(json_extract(metadata, '$.tags')) > 0;

-- Build JSON objects
SELECT json_object('id', id, 'name', name, 'email', email) AS user_json
FROM users;
```

## Drizzle ORM + LibSQL

```typescript
import { drizzle } from "drizzle-orm/libsql";
import { createClient } from "@libsql/client";
import { sqliteTable, text, integer } from "drizzle-orm/sqlite-core";
import { eq } from "drizzle-orm";

const client = createClient({ url: process.env.TURSO_DATABASE_URL! });
const db = drizzle(client);

const users = sqliteTable("users", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  email: text("email").notNull().unique(),
  name: text("name").notNull(),
});

const allUsers = await db.select().from(users).where(eq(users.name, "Alice"));
```

## CLI Commands

```bash
# Turso CLI
turso db create my-app
turso db shell my-app
turso db tokens create my-app
turso group locations add default lhr  # Add London replica

# SQLite CLI
sqlite3 app.db ".tables"
sqlite3 app.db ".schema users"
sqlite3 app.db "PRAGMA integrity_check;"
```

## Additional Resources

- better-sqlite3: https://github.com/WiseLibs/better-sqlite3
- Turso docs: https://docs.turso.tech/
- SQLite FTS5: https://www.sqlite.org/fts5.html
