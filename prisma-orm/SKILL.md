
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

  // Clean existing data (order matters for foreign keys)
  await prisma.comment.deleteMany();
  await prisma.post.deleteMany();
  await prisma.profile.deleteMany();
  await prisma.session.deleteMany();
  await prisma.user.deleteMany();
  await prisma.category.deleteMany();
  await prisma.tag.deleteMany();

  // Create categories
  const categories = await Promise.all(
    ["Technology", "Science", "Design", "Business"].map((name) =>
      prisma.category.create({
        data: {
          name,
          slug: name.toLowerCase().replace(/s+/g, "-"),
        },
      })
    )
  );

  // Create tags
  const tagNames = [
    "typescript", "prisma", "react", "nextjs",
    "node", "graphql", "rest", "testing",
  ];
  const tags = await Promise.all(
    tagNames.map((name) => prisma.tag.create({ data: { name } }))
  );

  // Create admin user
  const admin = await prisma.user.create({
    data: {
      email: "admin@example.com",
      name: "Admin User",
      password: await hash("admin123", 12),
      role: Role.ADMIN,
      profile: {
        create: { bio: "Platform administrator" },
      },
    },
  });

  // Create regular users with profiles and posts
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
            create: {
              bio: faker.lorem.paragraph(),
              avatar: faker.image.avatar(),
            },
          },
          posts: {
            create: Array.from({
              length: faker.number.int({ min: 1, max: 5 }),
            }).map(() => {
              const title = faker.lorem.sentence();
              return {
                title,
                slug:
                  faker.helpers.slugify(title).toLowerCase() +
                  "-" +
                  faker.string.nanoid(6),
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

  // Create comments on random posts
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
  .catch((e) => {
    console.error("Seed error:", e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
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
# Run seed manually
npx prisma db seed

# Seed runs automatically after prisma migrate reset
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
        id: true,
        title: true,
        slug: true,
        publishedAt: true,
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

  // In real applications, extract userId from authentication session
  const userId = "authenticated-user-id";

  const slug =
    title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/(^-|-$)/g, "") +
    "-" +
    Date.now().toString(36);

  const post = await prisma.post.create({
    data: {
      title,
      slug,
      content,
      author: { connect: { id: userId } },
      ...(categoryId && { category: { connect: { id: categoryId } } }),
      ...(tags?.length && {
        tags: {
          connectOrCreate: tags.map((tag: string) => ({
            where: { name: tag },
            create: { name: tag },
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
        select: {
          id: true,
          name: true,
          profile: { select: { avatar: true } },
        },
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

  // Increment views without blocking the render
  prisma.post
    .update({
      where: { id: post.id },
      data: { views: { increment: 1 } },
    })
    .catch(() => {});

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
// src/app.ts
import express from "express";
import { prisma } from "./lib/prisma";

const app = express();
app.use(express.json());

// Graceful shutdown
process.on("SIGTERM", async () => {
  await prisma.$disconnect();
  process.exit(0);
});

// GET /users/:id
app.get("/users/:id", async (req, res) => {
  try {
    const user = await prisma.user.findUniqueOrThrow({
      where: { id: req.params.id },
      select: {
        id: true,
        email: true,
        name: true,
        role: true,
        profile: true,
        _count: { select: { posts: true } },
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

// POST /users
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

// Error code reference:
// P2002 -- Unique constraint violation
// P2025 -- Record not found
// P2003 -- Foreign key constraint violation
// P2014 -- Required relation violation

app.listen(3000, () => console.log("Server running on port 3000"));
```
