---
name: sqlite-patterns
description: SQLite patterns covering schema design, WAL mode, FTS5 full-text search, JSON functions, CTEs, triggers, virtual tables, and integration with Node.js and Python.
---

# SQLite Patterns

This skill should be used when building applications with SQLite. It covers schema design, WAL mode, full-text search, JSON functions, CTEs, triggers, and language integration.

## When to Use This Skill

Use this skill when you need to:

- Use SQLite for local or embedded databases
- Enable WAL mode for concurrent access
- Implement full-text search with FTS5
- Work with JSON data in SQLite
- Integrate SQLite with Node.js or Python

## Schema Design

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    metadata TEXT DEFAULT '{}',  -- JSON column
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    tags TEXT DEFAULT '[]',  -- JSON array
    published INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_posts_user ON posts(user_id);
CREATE INDEX idx_posts_published ON posts(published, created_at);
```

## Performance Configuration

```sql
PRAGMA journal_mode = WAL;       -- Write-Ahead Logging
PRAGMA synchronous = NORMAL;     -- Safe with WAL
PRAGMA cache_size = -64000;      -- 64MB cache
PRAGMA foreign_keys = ON;        -- Enforce FK constraints
PRAGMA busy_timeout = 5000;      -- Wait 5s on lock
PRAGMA temp_store = MEMORY;      -- Temp tables in memory
```

## FTS5 Full-Text Search

```sql
CREATE VIRTUAL TABLE posts_fts USING fts5(title, body, content=posts, content_rowid=id);

-- Rebuild index
INSERT INTO posts_fts(posts_fts) VALUES('rebuild');

-- Triggers to keep FTS in sync
CREATE TRIGGER posts_ai AFTER INSERT ON posts BEGIN
    INSERT INTO posts_fts(rowid, title, body) VALUES (new.id, new.title, new.body);
END;

CREATE TRIGGER posts_ad AFTER DELETE ON posts BEGIN
    INSERT INTO posts_fts(posts_fts, rowid, title, body) VALUES('delete', old.id, old.title, old.body);
END;

-- Search
SELECT p.*, rank
FROM posts_fts fts
JOIN posts p ON p.id = fts.rowid
WHERE posts_fts MATCH 'database AND optimization'
ORDER BY rank;

-- Highlight results
SELECT highlight(posts_fts, 0, '<b>', '</b>') AS title,
       snippet(posts_fts, 1, '<b>', '</b>', '...', 32) AS body_snippet
FROM posts_fts WHERE posts_fts MATCH 'sqlite';
```

## JSON Functions

```sql
-- Extract JSON values
SELECT json_extract(metadata, '$.bio') AS bio FROM users;

-- Query JSON arrays
SELECT * FROM posts WHERE EXISTS (
    SELECT 1 FROM json_each(posts.tags) WHERE json_each.value = 'sql'
);

-- Modify JSON
UPDATE users SET metadata = json_set(metadata, '$.theme', 'dark') WHERE id = 1;
UPDATE users SET metadata = json_remove(metadata, '$.temp') WHERE id = 1;

-- Aggregate to JSON array
SELECT json_group_array(json_object('id', id, 'name', name)) FROM users;
```

## Common Table Expressions

```sql
-- Recursive CTE for hierarchical data
WITH RECURSIVE category_tree AS (
    SELECT id, name, parent_id, 0 AS depth
    FROM categories WHERE parent_id IS NULL
    UNION ALL
    SELECT c.id, c.name, c.parent_id, ct.depth + 1
    FROM categories c
    JOIN category_tree ct ON ct.id = c.parent_id
)
SELECT * FROM category_tree ORDER BY depth, name;
```

## Node.js Integration (better-sqlite3)

```typescript
import Database from "better-sqlite3";

const db = new Database("app.db");
db.pragma("journal_mode = WAL");
db.pragma("foreign_keys = ON");

// Prepared statements
const getUser = db.prepare("SELECT * FROM users WHERE id = ?");
const user = getUser.get(1);

const createUser = db.prepare("INSERT INTO users (name, email) VALUES (?, ?)");
const result = createUser.run("Alice", "alice@example.com");

// Transaction
const insertMany = db.transaction((users: { name: string; email: string }[]) => {
  for (const u of users) {
    createUser.run(u.name, u.email);
  }
});
insertMany([{ name: "Bob", email: "bob@example.com" }, { name: "Carol", email: "carol@example.com" }]);
```

## Python Integration

```python
import sqlite3

conn = sqlite3.connect("app.db")
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA foreign_keys=ON")

cursor = conn.execute("SELECT * FROM users WHERE role = ?", ("admin",))
users = [dict(row) for row in cursor.fetchall()]
conn.close()
```

## Additional Resources

- SQLite: https://www.sqlite.org/docs.html
- FTS5: https://www.sqlite.org/fts5.html
- JSON: https://www.sqlite.org/json1.html
