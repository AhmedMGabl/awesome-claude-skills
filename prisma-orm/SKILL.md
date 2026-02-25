---
name: prisma-orm
description: Prisma ORM for TypeScript/Node.js covering schema design, migrations, CRUD operations, relations, transactions, raw queries, middleware, seeding, testing patterns, and production database management.
---

# Prisma ORM

This skill provides comprehensive guidance for working with Prisma ORM in TypeScript and Node.js projects. It covers the full lifecycle from initial setup through production database management.

---

## 1. Setup and Initialization

### Install Prisma

```bash
npm install prisma --save-dev
npm install @prisma/client
npx prisma init
```

This creates a `prisma/` directory with `schema.prisma` and a `.env` file containing `DATABASE_URL`.

### schema.prisma -- Datasource and Generators

```prisma
// prisma/schema.prisma

generator client {
  provider        = "prisma-client-js"
  previewFeatures = ["fullTextSearch", "metrics"]
  binaryTargets   = ["native", "linux-musl-openssl-3.0.x"]
}

datasource db {
  provider = "postgresql"  // "mysql" | "sqlite" | "sqlserver" | "mongodb"
  url      = env("DATABASE_URL")
}
```

### Environment Configuration

```env
# .env
DATABASE_URL="postgresql://user:password@localhost:5432/mydb?schema=public"

# Connection pooling for serverless environments
DATABASE_URL="postgresql://user:password@host:5432/mydb?pgbouncer=true&connection_limit=1"
```

### Client Instantiation (Singleton Pattern)

```typescript
// src/lib/prisma.ts
import { PrismaClient } from "@prisma/client";

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    log:
      process.env.NODE_ENV === "development"
        ? ["query", "info", "warn", "error"]
        : ["error"],
  });

if (process.env.NODE_ENV !== "production") {
  globalForPrisma.prisma = prisma;
}
```

---

## 2. Schema Design

### Models, Fields, and Attributes

```prisma
model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String?
  password  String
  role      Role     @default(USER)
  active    Boolean  @default(true)
  createdAt DateTime @default(now()) @map("created_at")
  updatedAt DateTime @updatedAt @map("updated_at")

  profile  Profile?
  posts    Post[]
  comments Comment[]
  sessions Session[]

  @@map("users")
  @@index([email])
  @@index([createdAt])
}

model Profile {
  id     String  @id @default(cuid())
  bio    String? @db.Text
  avatar String?
  userId String  @unique @map("user_id")
  user   User    @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@map("profiles")
}

model Post {
  id          String     @id @default(cuid())
  title       String     @db.VarChar(255)
  slug        String     @unique
  content     String     @db.Text
  published   Boolean    @default(false)
  views       Int        @default(0)
  authorId    String     @map("author_id")
  author      User       @relation(fields: [authorId], references: [id], onDelete: Cascade)
  categoryId  String?    @map("category_id")
  category    Category?  @relation(fields: [categoryId], references: [id], onDelete: SetNull)
  tags        Tag[]
  comments    Comment[]
  metadata    Json?
  publishedAt DateTime?  @map("published_at")
  createdAt   DateTime   @default(now()) @map("created_at")
  updatedAt   DateTime   @updatedAt @map("updated_at")

  @@map("posts")
  @@index([authorId])
  @@index([slug])
  @@index([published, createdAt])
  @@fulltext([title, content])
}

model Category {
  id       String  @id @default(cuid())
  name     String  @unique
  slug     String  @unique
  parentId String? @map("parent_id")
  parent   Category?  @relation("CategoryTree", fields: [parentId], references: [id])
  children Category[] @relation("CategoryTree")
  posts    Post[]

  @@map("categories")
}

model Tag {
  id    String @id @default(cuid())
  name  String @unique
  posts Post[]

  @@map("tags")
}

model Comment {
  id        String   @id @default(cuid())
  body      String   @db.Text
  postId    String   @map("post_id")
  post      Post     @relation(fields: [postId], references: [id], onDelete: Cascade)
  authorId  String   @map("author_id")
  author    User     @relation(fields: [authorId], references: [id], onDelete: Cascade)
  parentId  String?  @map("parent_id")
  parent    Comment? @relation("CommentThread", fields: [parentId], references: [id])
  replies   Comment[] @relation("CommentThread")
  createdAt DateTime @default(now()) @map("created_at")

  @@map("comments")
  @@index([postId])
  @@index([authorId])
}

model Session {
  id        String   @id @default(cuid())
  token     String   @unique
  userId    String   @map("user_id")
  user      User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  expiresAt DateTime @map("expires_at")
  ipAddress String?  @map("ip_address")
  userAgent String?  @map("user_agent") @db.Text
  createdAt DateTime @default(now()) @map("created_at")

  @@map("sessions")
  @@index([userId])
  @@index([expiresAt])
}
```

### Enums

```prisma
enum Role {
  USER
  EDITOR
  ADMIN
  SUPER_ADMIN
}

enum PostStatus {
  DRAFT
  IN_REVIEW
  PUBLISHED
  ARCHIVED
}
```

### Compound Unique Constraints and Composite Keys

```prisma
model Subscription {
  userId    String
  planId    String
  startDate DateTime
  endDate   DateTime?
  status    SubscriptionStatus @default(ACTIVE)

  user User @relation(fields: [userId], references: [id])
  plan Plan @relation(fields: [planId], references: [id])

  @@id([userId, planId])
  @@map("subscriptions")
}

model Like {
  userId String
  postId String
  user   User @relation(fields: [userId], references: [id])
  post   Post @relation(fields: [postId], references: [id])

  @@unique([userId, postId])
  @@map("likes")
}
```

---

## 3. Relations

### One-to-One

```prisma
model User {
  id      String   @id @default(cuid())
  profile Profile?
}

model Profile {
  id     String @id @default(cuid())
  userId String @unique
  user   User   @relation(fields: [userId], references: [id])
}
```

```typescript
const user = await prisma.user.create({
  data: {
    email: "alice@example.com",
    name: "Alice",
    password: hashedPassword,
    profile: {
      create: {
        bio: "Software engineer and writer",
        avatar: "https://cdn.example.com/avatars/alice.jpg",
      },
    },
  },
  include: { profile: true },
});

const userWithProfile = await prisma.user.findUnique({
  where: { email: "alice@example.com" },
  include: { profile: true },
});
```

### One-to-Many

```typescript
const post = await prisma.post.create({
  data: {
    title: "Getting Started with Prisma",
    slug: "getting-started-prisma",
    content: "Prisma is a next-generation ORM...",
    author: { connect: { id: userId } },
    comments: {
      create: [
        { body: "Great article!", author: { connect: { id: commenterId } } },
        { body: "Very helpful.", author: { connect: { id: anotherUserId } } },
      ],
    },
  },
  include: { comments: { include: { author: true } } },
});

const postsWithCounts = await prisma.post.findMany({
  include: { _count: { select: { comments: true } } },
});
```

### Many-to-Many (Implicit)

```typescript
const post = await prisma.post.update({
  where: { id: postId },
  data: {
    tags: {
      connectOrCreate: [
        { where: { name: "prisma" }, create: { name: "prisma" } },
        { where: { name: "typescript" }, create: { name: "typescript" } },
      ],
    },
  },
  include: { tags: true },
});

await prisma.post.update({
  where: { id: postId },
  data: { tags: { disconnect: { name: "typescript" } } },
});

const prismaPosts = await prisma.post.findMany({
  where: { tags: { some: { name: "prisma" } } },
  include: { tags: true, author: true },
});
```

### Self-Relations

```typescript
const techCategory = await prisma.category.create({
  data: {
    name: "Technology",
    slug: "technology",
    children: {
      create: [
        { name: "Web Development", slug: "web-development" },
        { name: "Mobile Development", slug: "mobile-development" },
      ],
    },
  },
  include: { children: true },
});

const reply = await prisma.comment.create({
  data: {
    body: "I agree with this point!",
    post: { connect: { id: postId } },
    author: { connect: { id: userId } },
    parent: { connect: { id: parentCommentId } },
  },
});

const commentsWithReplies = await prisma.comment.findMany({
  where: { postId, parentId: null },
  include: {
    author: { select: { id: true, name: true } },
    replies: {
      include: {
        author: { select: { id: true, name: true } },
        replies: {
          include: { author: { select: { id: true, name: true } } },
        },
      },
    },
  },
  orderBy: { createdAt: "asc" },
});
```

---

## 4. Migrations

### Development Workflow

```bash
npx prisma migrate dev --name init
npx prisma migrate dev --name add_post_status_field
npx prisma generate
npx prisma migrate reset
npx prisma migrate status
npx prisma studio
```

### Production Deployment

```bash
npx prisma migrate deploy
npx prisma db pull
npx prisma db push
```

### Custom Migration -- Data Migration Example

After running `npx prisma migrate dev --name add_full_name --create-only`, edit the generated SQL:

```sql
ALTER TABLE "users" ADD COLUMN "full_name" TEXT;
UPDATE "users" SET "full_name" = "name" WHERE "name" IS NOT NULL;
UPDATE "users" SET "full_name" = split_part("email", '@', 1) WHERE "name" IS NULL;
ALTER TABLE "users" ALTER COLUMN "full_name" SET NOT NULL;
```

Then apply:

```bash
npx prisma migrate dev
```

---

## 5. CRUD Operations

### Create

```typescript
const user = await prisma.user.create({
  data: {
    email: "bob@example.com",
    name: "Bob",
    password: await hash("secure123", 12),
  },
});

const postWithAuthor = await prisma.post.create({
  data: {
    title: "Prisma Best Practices",
    slug: "prisma-best-practices",
    content: "Here are some tips for working with Prisma...",
    author: { connect: { id: user.id } },
    category: { connect: { slug: "web-development" } },
    tags: {
      connectOrCreate: [
        { where: { name: "orm" }, create: { name: "orm" } },
      ],
    },
  },
  include: { author: true, tags: true },
});

const newUsers = await prisma.user.createMany({
  data: [
    { email: "user1@example.com", name: "User 1", password: hashed },
    { email: "user2@example.com", name: "User 2", password: hashed },
    { email: "user3@example.com", name: "User 3", password: hashed },
  ],
  skipDuplicates: true,
});
```

### Read

```typescript
const user = await prisma.user.findUnique({
  where: { email: "bob@example.com" },
});

const user = await prisma.user.findUniqueOrThrow({
  where: { id: userId },
});

const firstAdmin = await prisma.user.findFirst({
  where: { role: "ADMIN" },
  orderBy: { createdAt: "asc" },
});

const userEmails = await prisma.user.findMany({
  where: { active: true },
  select: {
    id: true,
    email: true,
    name: true,
    _count: { select: { posts: true } },
  },
  orderBy: { name: "asc" },
});
```

### Update

```typescript
const updatedUser = await prisma.user.update({
  where: { id: userId },
  data: { role: "EDITOR" },
});

const post = await prisma.post.update({
  where: { id: postId },
  data: { views: { increment: 1 } },
});

const deactivated = await prisma.user.updateMany({
  where: {
    active: true,
    sessions: { none: { expiresAt: { gt: new Date() } } },
  },
  data: { active: false },
});
```

### Upsert

```typescript
const user = await prisma.user.upsert({
  where: { email: "carol@example.com" },
  update: { name: "Carol Updated" },
  create: {
    email: "carol@example.com",
    name: "Carol",
    password: await hash("password", 12),
  },
});
```

### Delete

```typescript
const deleted = await prisma.user.delete({
  where: { id: userId },
});

const purged = await prisma.session.deleteMany({
  where: { expiresAt: { lt: new Date() } },
});

// Cascade: deleting a user removes their posts, comments, sessions
await prisma.user.delete({ where: { id: userId } });
```

---

## 6. Advanced Queries

### Filtering

```typescript
const posts = await prisma.post.findMany({
  where: {
    AND: [
      { published: true },
      { publishedAt: { gte: new Date("2025-01-01") } },
      {
        OR: [
          { title: { contains: "prisma", mode: "insensitive" } },
          { content: { contains: "prisma", mode: "insensitive" } },
        ],
      },
      { author: { role: { in: ["ADMIN", "EDITOR"] } } },
      { tags: { some: { name: { in: ["typescript", "orm"] } } } },
      { NOT: { category: null } },
    ],
  },
  include: {
    author: { select: { id: true, name: true } },
    tags: true,
    _count: { select: { comments: true } },
  },
});
```

### Sorting

```typescript
const sortedPosts = await prisma.post.findMany({
  orderBy: [
    { published: "desc" },
    { publishedAt: "desc" },
    { title: "asc" },
  ],
});

const usersByPostCount = await prisma.user.findMany({
  orderBy: { posts: { _count: "desc" } },
  include: { _count: { select: { posts: true } } },
});
```

### Offset Pagination

```typescript
async function getPaginatedPosts(page: number, pageSize: number = 20) {
  const [posts, total] = await Promise.all([
    prisma.post.findMany({
      where: { published: true },
      skip: (page - 1) * pageSize,
      take: pageSize,
      orderBy: { publishedAt: "desc" },
      include: {
        author: { select: { id: true, name: true } },
        _count: { select: { comments: true } },
      },
    }),
    prisma.post.count({ where: { published: true } }),
  ]);

  return {
    data: posts,
    meta: { total, page, pageSize, totalPages: Math.ceil(total / pageSize) },
  };
}
```

### Cursor-Based Pagination

```typescript
async function getCursorPaginatedPosts(cursor?: string, take: number = 20) {
  const posts = await prisma.post.findMany({
    take: take + 1,
    ...(cursor && { cursor: { id: cursor }, skip: 1 }),
    where: { published: true },
    orderBy: { createdAt: "desc" },
    include: { author: { select: { id: true, name: true } } },
  });

  const hasNextPage = posts.length > take;
  const results = hasNextPage ? posts.slice(0, -1) : posts;

  return {
    data: results,
    nextCursor: hasNextPage ? results[results.length - 1].id : null,
    hasNextPage,
  };
}
```

### Aggregations and Grouping

```typescript
const stats = await prisma.post.aggregate({
  where: { published: true },
  _count: { _all: true },
  _avg: { views: true },
  _max: { views: true },
  _sum: { views: true },
});

const postsByCategory = await prisma.post.groupBy({
  by: ["categoryId"],
  where: { published: true },
  _count: { _all: true },
  _avg: { views: true },
  orderBy: { _count: { _all: "desc" } },
  having: { views: { _avg: { gt: 100 } } },
});
```

### Raw Queries

```typescript
const users = await prisma.$queryRaw`
  SELECT u.id, u.email, u.name, COUNT(p.id)::int AS post_count
  FROM users u
  LEFT JOIN posts p ON p.author_id = u.id AND p.published = true
  GROUP BY u.id
  HAVING COUNT(p.id) > ${minPosts}
  ORDER BY post_count DESC
  LIMIT ${limit}
`;

const affected = await prisma.$executeRaw`
  UPDATE posts SET views = views + 1 WHERE id = ${postId}
`;
```

---

## 7. Transactions

### Sequential Transaction (Auto-Batched)

```typescript
const [updatedPost, newComment, notification] = await prisma.$transaction([
  prisma.post.update({
    where: { id: postId },
    data: { views: { increment: 1 } },
  }),
  prisma.comment.create({
    data: {
      body: commentBody,
      post: { connect: { id: postId } },
      author: { connect: { id: userId } },
    },
  }),
  prisma.notification.create({
    data: {
      type: "NEW_COMMENT",
      recipientId: postAuthorId,
      message: "New comment on your post",
    },
  }),
]);
```

### Interactive Transaction

```typescript
async function transferCredits(fromId: string, toId: string, amount: number) {
  return prisma.$transaction(async (tx) => {
    const sender = await tx.user.findUniqueOrThrow({
      where: { id: fromId },
      select: { id: true, credits: true },
    });

    if (sender.credits < amount) {
      throw new Error("Insufficient credits. Available: " + sender.credits);
    }

    const [updatedSender, updatedReceiver] = await Promise.all([
      tx.user.update({
        where: { id: fromId },
        data: { credits: { decrement: amount } },
      }),
      tx.user.update({
        where: { id: toId },
        data: { credits: { increment: amount } },
      }),
    ]);

    await tx.transaction.create({
      data: { fromUserId: fromId, toUserId: toId, amount, type: "CREDIT_TRANSFER" },
    });

    return { sender: updatedSender, receiver: updatedReceiver };
  }, {
    maxWait: 5000,
    timeout: 10000,
    isolationLevel: "Serializable",
  });
}
```

### Nested Writes (Implicit Transaction)

```typescript
const user = await prisma.user.create({
  data: {
    email: "dave@example.com",
    name: "Dave",
    password: hashedPassword,
    profile: { create: { bio: "Full-stack developer" } },
    posts: {
      create: [
        {
          title: "My First Post",
          slug: "my-first-post",
          content: "Hello world!",
          tags: {
            connectOrCreate: [
              { where: { name: "introduction" }, create: { name: "introduction" } },
            ],
          },
        },
      ],
    },
  },
  include: { profile: true, posts: { include: { tags: true } } },
});
```

---

## 8. Middleware

### Query Logging Middleware

```typescript
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

prisma.$use(async (params, next) => {
  const startTime = performance.now();
  const result = await next(params);
  const duration = Math.round(performance.now() - startTime);

  console.log("[Prisma] " + params.model + "." + params.action + " -- " + duration + "ms");

  if (duration > 1000) {
    console.warn(
      "[Prisma SLOW QUERY] " + params.model + "." + params.action + " took " + duration + "ms",
      JSON.stringify(params.args, null, 2)
    );
  }

  return result;
});
```

### Soft Delete Middleware

```prisma
model Post {
  // ... other fields
  deletedAt DateTime? @map("deleted_at")
}
```

```typescript
prisma.$use(async (params, next) => {
  const softDeleteModels = ["Post", "Comment", "User"];

  if (params.model && softDeleteModels.includes(params.model)) {
    if (params.action === "delete") {
      params.action = "update";
      params.args.data = { deletedAt: new Date() };
    }
    if (params.action === "deleteMany") {
      params.action = "updateMany";
      params.args.data = { deletedAt: new Date() };
    }
    if (params.action === "findUnique" || params.action === "findFirst") {
      params.action = "findFirst";
      params.args.where = { ...params.args.where, deletedAt: null };
    }
    if (params.action === "findMany") {
      if (!params.args) params.args = {};
      if (!params.args.where) params.args.where = {};
      params.args.where.deletedAt = null;
    }
  }

  return next(params);
});
```

### Audit Trail with Prisma Client Extensions

Prisma Client Extensions (stable since v4.16) offer a more type-safe alternative to middleware:

```typescript
const prisma = new PrismaClient().$extends({
  query: {
    $allModels: {
      async create({ model, args, query }) {
        const result = await query(args);
        await logAuditEvent(model, "CREATE", null, result);
        return result;
      },
      async update({ model, args, query }) {
        const before = await (prisma as any)[uncapitalize(model)].findUnique({
          where: args.where,
        });
        const result = await query(args);
        await logAuditEvent(model, "UPDATE", before, result);
        return result;
      },
      async delete({ model, args, query }) {
        const before = await (prisma as any)[uncapitalize(model)].findUnique({
          where: args.where,
        });
        const result = await query(args);
        await logAuditEvent(model, "DELETE", before, null);
        return result;
      },
    },
  },
});

function uncapitalize(str: string): string {
  return str.charAt(0).toLowerCase() + str.slice(1);
}

async function logAuditEvent(
  model: string,
  action: string,
  before: unknown,
  after: unknown
) {
  await prisma.auditLog.create({
    data: {
      model,
      action,
      before: before ? JSON.parse(JSON.stringify(before)) : undefined,
      after: after ? JSON.parse(JSON.stringify(after)) : undefined,
      timestamp: new Date(),
    },
  });
}
```

---

## 9. Seeding

### Seed Script

```typescript
// prisma/seed.ts
import { PrismaClient, Role } from "@prisma/client";
import { faker } from "@faker-js/faker";
import { hash } from "bcryptjs";

const prisma = new PrismaClient();

async function main() {
  console.log("Seeding database...");

  await prisma.comment.deleteMany();
  await prisma.post.deleteMany();
  await prisma.profile.deleteMany();
  await prisma.session.deleteMany();
  await prisma.user.deleteMany();
  await prisma.category.deleteMany();
  await prisma.tag.deleteMany();

  const categories = await Promise.all(
    ["Technology", "Science", "Design", "Business"].map((name) =>
      prisma.category.create({
        data: { name, slug: name.toLowerCase().replace(/s+/g, "-") },
      })
    )
  );

  const tagNames = ["typescript", "prisma", "react", "nextjs", "node", "graphql", "rest", "testing"];
  const tags = await Promise.all(
    tagNames.map((name) => prisma.tag.create({ data: { name } }))
  );

  const admin = await prisma.user.create({
    data: {
      email: "admin@example.com",
      name: "Admin User",
      password: await hash("admin123", 12),
      role: Role.ADMIN,
      profile: { create: { bio: "Platform administrator" } },
    },
  });

  const users = await Promise.all(
    Array.from({ length: 10 }).map(async () => {
      const firstName = faker.person.firstName();
      const lastName = faker.person.lastName();
      return prisma.user.create({
        data: {
          email: faker.internet.email({ firstName, lastName }).toLowerCase(),
          name: firstName + " " + lastName,
          password: await hash("password123", 12),
          role: Role.USER,
          profile: {
            create: { bio: faker.lorem.paragraph(), avatar: faker.image.avatar() },
          },
          posts: {
            create: Array.from({
              length: faker.number.int({ min: 1, max: 5 }),
            }).map(() => {
              const title = faker.lorem.sentence();
              return {
                title,
                slug: faker.helpers.slugify(title).toLowerCase() + "-" + faker.string.nanoid(6),
                content: faker.lorem.paragraphs(3),
                published: faker.datatype.boolean(0.7),
                views: faker.number.int({ min: 0, max: 5000 }),
                publishedAt: faker.date.past(),
                categoryId: faker.helpers.arrayElement(categories).id,
                tags: {
                  connect: faker.helpers
                    .arrayElements(tags, faker.number.int({ min: 1, max: 3 }))
                    .map((t) => ({ id: t.id })),
                },
              };
            }),
          },
        },
      });
    })
  );

  const allPosts = await prisma.post.findMany({ select: { id: true } });
  const allUsers = await prisma.user.findMany({ select: { id: true } });

  for (const post of allPosts) {
    const commentCount = faker.number.int({ min: 0, max: 8 });
    for (let i = 0; i < commentCount; i++) {
      await prisma.comment.create({
        data: {
          body: faker.lorem.paragraph(),
          postId: post.id,
          authorId: faker.helpers.arrayElement(allUsers).id,
        },
      });
    }
  }

  console.log("Seeded: " + allUsers.length + " users, " + allPosts.length + " posts");
}

main()
  .catch((e) => { console.error("Seed error:", e); process.exit(1); })
  .finally(async () => { await prisma.$disconnect(); });
```

### package.json Configuration

```json
{
  "prisma": {
    "seed": "npx tsx prisma/seed.ts"
  }
}
```

```bash
npx prisma db seed
npx prisma migrate reset
```

---

## 10. Integration Patterns

### Next.js App Router -- Route Handler

```typescript
// app/api/posts/route.ts
import { prisma } from "@/lib/prisma";
import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const page = parseInt(searchParams.get("page") || "1");
  const pageSize = parseInt(searchParams.get("pageSize") || "20");
  const search = searchParams.get("q");

  const where = {
    published: true,
    ...(search && {
      OR: [
        { title: { contains: search, mode: "insensitive" as const } },
        { content: { contains: search, mode: "insensitive" as const } },
      ],
    }),
  };

  const [posts, total] = await Promise.all([
    prisma.post.findMany({
      where,
      skip: (page - 1) * pageSize,
      take: pageSize,
      orderBy: { publishedAt: "desc" },
      select: {
        id: true, title: true, slug: true, publishedAt: true,
        author: { select: { id: true, name: true } },
        _count: { select: { comments: true } },
      },
    }),
    prisma.post.count({ where }),
  ]);

  return NextResponse.json({
    data: posts,
    meta: { total, page, pageSize, totalPages: Math.ceil(total / pageSize) },
  });
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  const { title, content, categoryId, tags } = body;
  const userId = "authenticated-user-id";

  const slug =
    title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "") +
    "-" + Date.now().toString(36);

  const post = await prisma.post.create({
    data: {
      title, slug, content,
      author: { connect: { id: userId } },
      ...(categoryId && { category: { connect: { id: categoryId } } }),
      ...(tags?.length && {
        tags: {
          connectOrCreate: tags.map((tag: string) => ({
            where: { name: tag }, create: { name: tag },
          })),
        },
      }),
    },
    include: { author: true, tags: true },
  });

  return NextResponse.json(post, { status: 201 });
}
```
### Next.js Server Component

```typescript
// app/posts/[slug]/page.tsx
import { prisma } from "@/lib/prisma";
import { notFound } from "next/navigation";

export default async function PostPage({
  params,
}: {
  params: { slug: string };
}) {
  const post = await prisma.post.findUnique({
    where: { slug: params.slug, published: true },
    include: {
      author: {
        select: { id: true, name: true, profile: { select: { avatar: true } } },
      },
      tags: true,
      comments: {
        where: { parentId: null },
        include: {
          author: { select: { id: true, name: true } },
          replies: {
            include: { author: { select: { id: true, name: true } } },
          },
        },
        orderBy: { createdAt: "desc" },
      },
    },
  });

  if (!post) notFound();

  prisma.post.update({
    where: { id: post.id },
    data: { views: { increment: 1 } },
  }).catch(() => {});

  return (
    <article>
      <h1>{post.title}</h1>
      <p>By {post.author.name}</p>
      <div>{post.content}</div>
    </article>
  );
}
```

### Express.js Integration

```typescript
import express from "express";
import { prisma } from "./lib/prisma";

const app = express();
app.use(express.json());

process.on("SIGTERM", async () => {
  await prisma.$disconnect();
  process.exit(0);
});

app.get("/users/:id", async (req, res) => {
  try {
    const user = await prisma.user.findUniqueOrThrow({
      where: { id: req.params.id },
      select: {
        id: true, email: true, name: true, role: true,
        profile: true, _count: { select: { posts: true } },
      },
    });
    res.json(user);
  } catch (error) {
    if ((error as any).code === "P2025") {
      return res.status(404).json({ error: "User not found" });
    }
    res.status(500).json({ error: "Internal server error" });
  }
});

app.post("/users", async (req, res) => {
  try {
    const user = await prisma.user.create({
      data: {
        email: req.body.email,
        name: req.body.name,
        password: await hash(req.body.password, 12),
        profile: req.body.bio
          ? { create: { bio: req.body.bio } }
          : undefined,
      },
      select: { id: true, email: true, name: true },
    });
    res.status(201).json(user);
  } catch (error) {
    if ((error as any).code === "P2002") {
      return res.status(409).json({ error: "Email already exists" });
    }
    res.status(500).json({ error: "Internal server error" });
  }
});

// P2002: Unique constraint violation
// P2025: Record not found
// P2003: Foreign key constraint violation
// P2014: Required relation violation

app.listen(3000, () => console.log("Server running on port 3000"));
```
### Testing with Prisma

```typescript
// tests/helpers/prisma.ts
import { PrismaClient } from "@prisma/client";
import { execSync } from "child_process";
import { randomUUID } from "crypto";

function createTestPrisma() {
  const schema = "test_" + randomUUID().replace(/-/g, "").slice(0, 12);
  const url = process.env.DATABASE_URL + "?schema=" + schema;
  const prisma = new PrismaClient({
    datasources: { db: { url } },
  });
  return { prisma, schema, url };
}

export async function setupTestDB() {
  const { prisma, url } = createTestPrisma();
  execSync("npx prisma migrate deploy", {
    env: { ...process.env, DATABASE_URL: url },
  });
  return prisma;
}

export async function teardownTestDB(prisma: PrismaClient) {
  const result = await prisma.$queryRaw<{ schema: string }[]>(
    Prisma.sql`SELECT current_schema() as schema`
  );
  const schemaName = result[0].schema;
  await prisma.$executeRawUnsafe(
    "DROP SCHEMA IF EXISTS " + schemaName + " CASCADE"
  );
  await prisma.$disconnect();
}

export async function cleanDB(prisma: PrismaClient) {
  const models = Reflect.ownKeys(prisma).filter(
    (key) =>
      typeof key === "string" &&
      !key.startsWith("_") &&
      !key.startsWith("$")
  ) as string[];
  await prisma.$transaction(
    models.map((model) => (prisma as any)[model].deleteMany())
  );
}
```

```typescript
// tests/user.service.test.ts
import { describe, it, expect, beforeAll, afterAll, beforeEach } from "vitest";
import { PrismaClient } from "@prisma/client";
import { setupTestDB, teardownTestDB, cleanDB } from "./helpers/prisma";
import { UserService } from "../src/services/user.service";

describe("UserService", () => {
  let prisma: PrismaClient;
  let userService: UserService;

  beforeAll(async () => {
    prisma = await setupTestDB();
    userService = new UserService(prisma);
  });

  afterAll(async () => { await teardownTestDB(prisma); });
  beforeEach(async () => { await cleanDB(prisma); });

  it("should create a user with profile", async () => {
    const user = await userService.createUser({
      email: "test@example.com",
      name: "Test User",
      password: "password123",
      bio: "A test user",
    });
    expect(user.email).toBe("test@example.com");
    expect(user.profile?.bio).toBe("A test user");
  });

  it("should reject duplicate emails", async () => {
    await userService.createUser({
      email: "dup@example.com", name: "User A", password: "pass",
    });
    await expect(
      userService.createUser({
        email: "dup@example.com", name: "User B", password: "pass",
      })
    ).rejects.toThrow(/email already exists/i);
  });

  it("should paginate users correctly", async () => {
    await prisma.user.createMany({
      data: Array.from({ length: 15 }).map((_, i) => ({
        email: "user" + i + "@example.com",
        name: "User " + i,
        password: "hashed",
      })),
    });

    const page1 = await userService.listUsers({ page: 1, pageSize: 10 });
    expect(page1.data).toHaveLength(10);
    expect(page1.meta.total).toBe(15);
    expect(page1.meta.totalPages).toBe(2);

    const page2 = await userService.listUsers({ page: 2, pageSize: 10 });
    expect(page2.data).toHaveLength(5);
  });
});
```

---

## Quick Reference -- Common Prisma CLI Commands

| Command | Purpose |
| --- | --- |
| `npx prisma init` | Initialize Prisma in a project |
| `npx prisma generate` | Regenerate Prisma Client |
| `npx prisma migrate dev --name X` | Create and apply a migration |
| `npx prisma migrate deploy` | Apply pending migrations (production) |
| `npx prisma migrate reset` | Drop database and re-apply all migrations |
| `npx prisma migrate status` | Show current migration status |
| `npx prisma db push` | Push schema without creating migration files |
| `npx prisma db pull` | Introspect database and update schema |
| `npx prisma db seed` | Run the seed script |
| `npx prisma studio` | Open visual database browser |
| `npx prisma validate` | Validate the schema file |
| `npx prisma format` | Format the schema file |

## Quick Reference -- Common Error Codes

| Code | Meaning | Typical Resolution |
| --- | --- | --- |
| P2002 | Unique constraint violation | Check for duplicate values |
| P2003 | Foreign key constraint failure | Ensure referenced record exists |
| P2014 | Required relation violation | Include required related records |
| P2025 | Record not found | Verify ID/filter or handle gracefully |
| P1001 | Cannot reach database server | Check DATABASE_URL and connectivity |
| P1008 | Operation timed out | Optimize query or increase timeout |