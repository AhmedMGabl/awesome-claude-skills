---
name: prisma-orm
description: This skill should be used when working with Prisma ORM for TypeScript/Node.js projects. It covers schema definition with models, relations, and enums, migrations for development and production, CRUD operations, advanced queries including aggregations, raw SQL, and transactions, seeding, middleware, client extensions, and integration with Next.js and Express.
---

# Prisma ORM
## Setup and Client Singleton
```bash
npm install prisma --save-dev && npm install @prisma/client && npx prisma init
```
```typescript
// src/lib/prisma.ts -- singleton to prevent multiple instances during hot reload
import { PrismaClient } from "@prisma/client";
const g = globalThis as unknown as { prisma: PrismaClient | undefined };
export const prisma = g.prisma ?? new PrismaClient({
  log: process.env.NODE_ENV === "development" ? ["query", "warn", "error"] : ["error"],
});
if (process.env.NODE_ENV !== "production") g.prisma = prisma;
```
## Schema -- Models, Relations, Enums
```prisma
datasource db { provider = "postgresql"; url = env("DATABASE_URL") }
generator client { provider = "prisma-client-js" }
enum Role { USER; EDITOR; ADMIN }
model User {
  id String @id @default(cuid()); email String @unique; name String?
  role Role @default(USER); createdAt DateTime @default(now()) @map("created_at")
  updatedAt DateTime @updatedAt @map("updated_at")
  profile Profile?; posts Post[]
  @@map("users")
}
model Profile {
  id String @id @default(cuid()); bio String? @db.Text
  userId String @unique @map("user_id")
  user User @relation(fields: [userId], references: [id], onDelete: Cascade)
}
model Post {
  id String @id @default(cuid()); title String @db.VarChar(255); slug String @unique
  content String @db.Text; published Boolean @default(false); views Int @default(0)
  authorId String @map("author_id"); metadata Json?; createdAt DateTime @default(now())
  author User @relation(fields: [authorId], references: [id], onDelete: Cascade)
  tags Tag[]   // implicit many-to-many
  @@map("posts") @@index([authorId])
}
model Tag { id String @id @default(cuid()); name String @unique; posts Post[] }
```
## Migrations
```bash
npx prisma migrate dev --name init            # Create + apply (dev)
npx prisma migrate deploy                     # Apply pending (production)
npx prisma migrate dev --name x --create-only # Generate SQL only, edit before applying
npx prisma generate                           # Regenerate client after schema changes
npx prisma db push                            # Push schema without migration files
npx prisma db pull                            # Introspect DB into schema
npx prisma studio                             # Visual database browser
```
## CRUD Operations
```typescript
// Create with nested relations
const post = await prisma.post.create({
  data: {
    title: "Hello", slug: "hello", content: "...",
    author: { connect: { id: userId } },
    tags: { connectOrCreate: [{ where: { name: "prisma" }, create: { name: "prisma" } }] },
  },
  include: { author: true, tags: true },
});
// Read with filtering, select, and relation counts
const posts = await prisma.post.findMany({
  where: { published: true, title: { contains: "prisma", mode: "insensitive" } },
  select: { id: true, title: true, author: { select: { name: true } }, _count: { select: { tags: true } } },
  orderBy: { createdAt: "desc" }, take: 20, skip: 0,
});
const user = await prisma.user.findUniqueOrThrow({ where: { id: userId } });
// Update and upsert
await prisma.post.update({ where: { id: postId }, data: { views: { increment: 1 } } });
await prisma.user.upsert({
  where: { email: "a@b.com" }, update: { name: "New" },
  create: { email: "a@b.com", name: "New", password: h },
});
// Delete
await prisma.session.deleteMany({ where: { expiresAt: { lt: new Date() } } });
```
## Advanced Queries -- Aggregations, Raw SQL, Transactions
```typescript
// Aggregation and groupBy
const stats = await prisma.post.aggregate({
  where: { published: true }, _count: { _all: true }, _avg: { views: true }, _sum: { views: true },
});
const byAuthor = await prisma.post.groupBy({
  by: ["authorId"], _count: { _all: true }, orderBy: { _count: { _all: "desc" } },
  having: { views: { _avg: { gt: 100 } } },
});
// Cursor-based pagination
const results = await prisma.post.findMany({
  take: 20, ...(cursor && { cursor: { id: cursor }, skip: 1 }), orderBy: { createdAt: "desc" },
});
// Raw SQL
const rows = await prisma.$queryRaw`
  SELECT u.id, COUNT(p.id)::int AS cnt FROM users u
  LEFT JOIN posts p ON p.author_id = u.id GROUP BY u.id HAVING COUNT(p.id) > ${min}`;
await prisma.$executeRaw`UPDATE posts SET views = views + 1 WHERE id = ${postId}`;
// Interactive transaction with isolation level
await prisma.$transaction(async (tx) => {
  const sender = await tx.user.findUniqueOrThrow({ where: { id: fromId } });
  if (sender.credits < amount) throw new Error("Insufficient credits");
  await tx.user.update({ where: { id: fromId }, data: { credits: { decrement: amount } } });
  await tx.user.update({ where: { id: toId }, data: { credits: { increment: amount } } });
}, { maxWait: 5000, timeout: 10000, isolationLevel: "Serializable" });
// Batched transaction (all-or-nothing array of operations)
const [a, b] = await prisma.$transaction([
  prisma.post.update({ where: { id: postId }, data: { views: { increment: 1 } } }),
  prisma.comment.create({ data: { body: "Nice!", postId, authorId: userId } }),
]);
```
## Seeding
```typescript
// prisma/seed.ts -- add "prisma": { "seed": "npx tsx prisma/seed.ts" } to package.json
import { PrismaClient } from "@prisma/client";
import { faker } from "@faker-js/faker";
const prisma = new PrismaClient();
async function main() {
  await prisma.post.deleteMany();
  await prisma.user.deleteMany();
  await prisma.user.create({
    data: {
      email: "admin@example.com", name: "Admin", password: "hashed",
      posts: { create: Array.from({ length: 5 }).map(() => ({
        title: faker.lorem.sentence(), slug: faker.helpers.slugify(faker.lorem.words(3)),
        content: faker.lorem.paragraphs(2), published: faker.datatype.boolean(),
      })) },
    },
  });
}
main().finally(() => prisma.$disconnect());
// Run: npx prisma db seed  |  npx prisma migrate reset (auto-seeds after reset)
```
## Middleware and Client Extensions
```typescript
// Middleware -- slow query warning
prisma.$use(async (params, next) => {
  const t = performance.now();
  const r = await next(params);
  const ms = Math.round(performance.now() - t);
  if (ms > 1000) console.warn(`[SLOW] ${params.model}.${params.action} ${ms}ms`);
  return r;
});
// Client extension -- computed fields and soft delete (type-safe, preferred over middleware)
const xprisma = prisma.$extends({
  result: { user: { displayName: { needs: { name: true, email: true },
    compute: (u) => u.name ?? u.email } } },
  query: { $allModels: { async delete({ model, args }) {
    return (prisma as any)[model.charAt(0).toLowerCase() + model.slice(1)]
      .update({ ...args, data: { deletedAt: new Date() } });
  } } },
});
```
## Integration -- Next.js App Router
```typescript
// app/api/posts/route.ts
import { prisma } from "@/lib/prisma";
import { NextRequest, NextResponse } from "next/server";
export async function GET(req: NextRequest) {
  const page = parseInt(req.nextUrl.searchParams.get("page") ?? "1");
  const where = { published: true };
  const [posts, total] = await Promise.all([
    prisma.post.findMany({ where, skip: (page - 1) * 20, take: 20, orderBy: { createdAt: "desc" },
      select: { id: true, title: true, slug: true, author: { select: { name: true } } } }),
    prisma.post.count({ where }),
  ]);
  return NextResponse.json({ data: posts, meta: { total, page, totalPages: Math.ceil(total / 20) } });
}
```
## Integration -- Express
```typescript
import express from "express";
import { prisma } from "./lib/prisma";
const app = express();
app.use(express.json());
app.get("/users/:id", async (req, res) => {
  try {
    const user = await prisma.user.findUniqueOrThrow({
      where: { id: req.params.id }, include: { profile: true, _count: { select: { posts: true } } },
    });
    res.json(user);
  } catch (e: any) {
    res.status(e.code === "P2025" ? 404 : 500).json({ error: e.code === "P2025" ? "Not found" : "Server error" });
  }
  // Common error codes: P2002 = unique violation, P2003 = FK violation, P2025 = not found
});
app.listen(3000);
```
## Additional Resources
- Prisma documentation: https://www.prisma.io/docs
- Prisma Client API: https://www.prisma.io/docs/reference/api-reference/prisma-client-reference
- Schema reference: https://www.prisma.io/docs/reference/api-reference/prisma-schema-reference
- Prisma with Next.js: https://www.prisma.io/docs/guides/nextjs
- Prisma Migrate: https://www.prisma.io/docs/concepts/components/prisma-migrate
- Client Extensions: https://www.prisma.io/docs/concepts/components/prisma-client/client-extensions
