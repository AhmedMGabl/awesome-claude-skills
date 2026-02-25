---
name: bun-runtime
description: Bun runtime development covering Bun.serve HTTP server, Bun.file and filesystem APIs, built-in SQLite, testing with bun test, bundling, package management, TypeScript execution, Workers, and compatibility with Node.js APIs.
---

# Bun Runtime

This skill should be used when developing with the Bun runtime. It covers HTTP servers, file I/O, SQLite, testing, bundling, and Node.js compatibility.

## When to Use This Skill

Use this skill when you need to:

- Build fast HTTP servers with Bun.serve
- Use Bun's built-in SQLite database
- Run TypeScript without compilation
- Bundle and minify applications
- Leverage Bun's fast package manager

## HTTP Server

```typescript
// server.ts — run with: bun run server.ts
const server = Bun.serve({
  port: 3000,
  async fetch(req) {
    const url = new URL(req.url);

    if (url.pathname === "/api/health") {
      return Response.json({ status: "ok" });
    }

    if (url.pathname === "/api/users" && req.method === "GET") {
      const users = db.query("SELECT * FROM users").all();
      return Response.json(users);
    }

    if (url.pathname === "/api/users" && req.method === "POST") {
      const body = await req.json();
      db.run("INSERT INTO users (name, email) VALUES (?, ?)", [body.name, body.email]);
      return Response.json({ success: true }, { status: 201 });
    }

    return new Response("Not Found", { status: 404 });
  },
});

console.log(`Server running at http://localhost:${server.port}`);
```

## Built-in SQLite

```typescript
import { Database } from "bun:sqlite";

const db = new Database("app.db");
db.run("PRAGMA journal_mode = WAL");

// Create table
db.run(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )
`);

// Prepared statements (fast, reusable)
const insertUser = db.prepare("INSERT INTO users (name, email) VALUES ($name, $email)");
const getUser = db.prepare("SELECT * FROM users WHERE id = ?");
const listUsers = db.prepare("SELECT * FROM users ORDER BY created_at DESC LIMIT ?");

// Usage
insertUser.run({ $name: "Alice", $email: "alice@example.com" });
const user = getUser.get(1);
const users = listUsers.all(20);

// Transactions
const insertMany = db.transaction((users: Array<{ name: string; email: string }>) => {
  for (const u of users) {
    insertUser.run({ $name: u.name, $email: u.email });
  }
});
```

## File I/O

```typescript
// Reading files
const file = Bun.file("data.json");
const text = await file.text();
const json = await file.json();
const bytes = await file.arrayBuffer();

// Writing files
await Bun.write("output.txt", "Hello, Bun!");
await Bun.write("data.json", JSON.stringify({ key: "value" }));

// Streaming large files
const writer = Bun.file("large.csv").writer();
for (const row of generateRows()) {
  writer.write(row + "\n");
}
writer.flush();
```

## Testing

```typescript
// math.test.ts — run with: bun test
import { describe, it, expect, beforeAll, mock } from "bun:test";

describe("math", () => {
  it("adds numbers", () => {
    expect(1 + 2).toBe(3);
  });

  it("handles async", async () => {
    const result = await fetchData();
    expect(result).toBeDefined();
  });
});

// Mocking
const mockedFetch = mock(() => Promise.resolve({ ok: true }));
```

## Bundling

```typescript
// Build script
const result = await Bun.build({
  entrypoints: ["./src/index.ts"],
  outdir: "./dist",
  target: "browser", // or "bun" or "node"
  minify: true,
  splitting: true,
  sourcemap: "external",
});

if (!result.success) {
  console.error("Build failed:", result.logs);
}
```

## Bun vs Node.js vs Deno

```
FEATURE           BUN              NODE.JS          DENO
────────────────────────────────────────────────────────
Package mgr       bun install      npm/pnpm/yarn    deno add
TypeScript        Built-in         Requires tsc     Built-in
Test runner       bun:test         Jest/Vitest      Deno.test
Bundler           Built-in         Webpack/Vite     -
SQLite            Built-in         Better-sqlite3   -
Speed             Very fast        Standard         Fast
npm compat        High             Native           Good
```

## Additional Resources

- Bun docs: https://bun.sh/docs
- Bun API reference: https://bun.sh/docs/api
- Bun recipes: https://bun.sh/guides
