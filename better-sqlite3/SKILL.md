---
name: better-sqlite3
description: better-sqlite3 patterns covering synchronous SQLite operations, prepared statements, transactions, WAL mode, migrations, full-text search, JSON support, and Node.js/Bun integration.
---

# better-sqlite3

This skill should be used when working with SQLite databases in Node.js using better-sqlite3. It covers queries, prepared statements, transactions, migrations, and full-text search.

## When to Use This Skill

Use this skill when you need to:

- Use SQLite for local or embedded databases
- Perform synchronous SQL queries in Node.js
- Handle transactions with automatic rollback
- Set up WAL mode for concurrent reads
- Implement full-text search with FTS5

## Setup

```bash
npm install better-sqlite3
npm install -D @types/better-sqlite3
```

## Database Initialization

```ts
import Database from "better-sqlite3";

const db = new Database("app.db");

// Enable WAL mode for better concurrency
db.pragma("journal_mode = WAL");
db.pragma("foreign_keys = ON");

// Schema setup
db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'user' CHECK(role IN ('admin', 'user', 'editor')),
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
  );

  CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    content TEXT,
    status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'published', 'archived')),
    author_id INTEGER NOT NULL REFERENCES users(id),
    published_at TEXT,
    created_at TEXT DEFAULT (datetime('now'))
  );

  CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status);
  CREATE INDEX IF NOT EXISTS idx_posts_author ON posts(author_id);
`);
```

## Prepared Statements

```ts
// Insert
const insertUser = db.prepare(`
  INSERT INTO users (email, name, password_hash, role)
  VALUES (@email, @name, @passwordHash, @role)
`);

const result = insertUser.run({
  email: "alice@example.com",
  name: "Alice",
  passwordHash: "$2b$10$...",
  role: "user",
});
console.log(result.lastInsertRowid);

// Select one
const getUser = db.prepare("SELECT * FROM users WHERE id = ?");
const user = getUser.get(1);

// Select many
const listUsers = db.prepare("SELECT id, email, name, role FROM users WHERE role = ?");
const admins = listUsers.all("admin");

// Update
const updateUser = db.prepare("UPDATE users SET name = ?, updated_at = datetime('now') WHERE id = ?");
const changes = updateUser.run("Alice Smith", 1);
console.log(changes.changes); // rows affected

// Delete
const deleteUser = db.prepare("DELETE FROM users WHERE id = ?");
deleteUser.run(1);
```

## Transactions

```ts
// Transaction with automatic rollback on error
const transferPosts = db.transaction((fromUserId: number, toUserId: number) => {
  const posts = db.prepare("SELECT id FROM posts WHERE author_id = ?").all(fromUserId);

  const updatePost = db.prepare("UPDATE posts SET author_id = ? WHERE id = ?");
  for (const post of posts) {
    updatePost.run(toUserId, (post as any).id);
  }

  db.prepare("DELETE FROM users WHERE id = ?").run(fromUserId);
  return posts.length;
});

const count = transferPosts(1, 2);

// Bulk insert with transaction (much faster)
const insertMany = db.transaction((users: { email: string; name: string; hash: string }[]) => {
  const insert = db.prepare("INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?)");
  for (const user of users) {
    insert.run(user.email, user.name, user.hash);
  }
  return users.length;
});

insertMany([
  { email: "a@test.com", name: "A", hash: "..." },
  { email: "b@test.com", name: "B", hash: "..." },
]);
```

## Full-Text Search

```ts
// Create FTS5 table
db.exec(`
  CREATE VIRTUAL TABLE IF NOT EXISTS posts_fts USING fts5(
    title, content, content='posts', content_rowid='id'
  );

  CREATE TRIGGER IF NOT EXISTS posts_ai AFTER INSERT ON posts BEGIN
    INSERT INTO posts_fts(rowid, title, content) VALUES (new.id, new.title, new.content);
  END;

  CREATE TRIGGER IF NOT EXISTS posts_ad AFTER DELETE ON posts BEGIN
    INSERT INTO posts_fts(posts_fts, rowid, title, content) VALUES('delete', old.id, old.title, old.content);
  END;

  CREATE TRIGGER IF NOT EXISTS posts_au AFTER UPDATE ON posts BEGIN
    INSERT INTO posts_fts(posts_fts, rowid, title, content) VALUES('delete', old.id, old.title, old.content);
    INSERT INTO posts_fts(rowid, title, content) VALUES (new.id, new.title, new.content);
  END;
`);

// Search
const search = db.prepare(`
  SELECT p.*, rank
  FROM posts_fts fts
  JOIN posts p ON p.id = fts.rowid
  WHERE posts_fts MATCH ?
  ORDER BY rank
  LIMIT 20
`);

const results = search.all("javascript OR typescript");
```

## JSON Support

```ts
db.exec(`
  CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
  );
`);

// Store JSON
const setSetting = db.prepare("INSERT OR REPLACE INTO settings (key, value) VALUES (?, json(?))");
setSetting.run("theme", JSON.stringify({ mode: "dark", fontSize: 14 }));

// Query JSON fields
const getThemeMode = db.prepare("SELECT json_extract(value, '$.mode') as mode FROM settings WHERE key = ?");
const mode = getThemeMode.get("theme");
```

## Additional Resources

- better-sqlite3: https://github.com/WiseLibs/better-sqlite3
- API Docs: https://github.com/WiseLibs/better-sqlite3/blob/master/docs/api.md
- SQLite FTS5: https://www.sqlite.org/fts5.html
