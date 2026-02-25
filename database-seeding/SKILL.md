---
name: database-seeding
description: Database seeding and test data generation covering Prisma seed scripts, Drizzle seeders, SQLAlchemy fixtures, factory patterns with Faker, deterministic seeding for tests, large dataset generation, referential integrity in seed data, and environment-specific seed strategies.
---

# Database Seeding

This skill should be used when creating database seed scripts, generating test data, or setting up development environments with realistic data. It covers ORM seeders, factory patterns, and deterministic data generation.

## When to Use This Skill

Use this skill when you need to:

- Create seed scripts for development databases
- Generate realistic test data with referential integrity
- Set up factories for consistent test fixtures
- Seed large datasets for performance testing
- Create environment-specific seed strategies

## Prisma Seed Script

```typescript
// prisma/seed.ts
import { PrismaClient } from "@prisma/client";
import { faker } from "@faker-js/faker";

const prisma = new PrismaClient();

async function main() {
  // Clear existing data (dev only)
  await prisma.comment.deleteMany();
  await prisma.post.deleteMany();
  await prisma.user.deleteMany();

  console.log("Seeding database...");

  // Create users
  const users = await Promise.all(
    Array.from({ length: 20 }, () =>
      prisma.user.create({
        data: {
          email: faker.internet.email(),
          name: faker.person.fullName(),
          avatar: faker.image.avatar(),
          role: faker.helpers.arrayElement(["USER", "ADMIN", "EDITOR"]),
        },
      }),
    ),
  );

  // Create posts for each user
  for (const user of users) {
    const postCount = faker.number.int({ min: 0, max: 5 });
    for (let i = 0; i < postCount; i++) {
      await prisma.post.create({
        data: {
          title: faker.lorem.sentence(),
          content: faker.lorem.paragraphs(3),
          published: faker.datatype.boolean(0.7),
          authorId: user.id,
          comments: {
            create: Array.from(
              { length: faker.number.int({ min: 0, max: 3 }) },
              () => ({
                text: faker.lorem.paragraph(),
                authorId: faker.helpers.arrayElement(users).id,
              }),
            ),
          },
        },
      });
    }
  }

  console.log(`Seeded ${users.length} users with posts and comments`);
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(() => prisma.$disconnect());
```

```json
// package.json
{
  "prisma": {
    "seed": "tsx prisma/seed.ts"
  }
}
```

## Factory Pattern

```typescript
// tests/factories.ts
import { faker } from "@faker-js/faker";

type UserData = {
  email: string;
  name: string;
  role: "USER" | "ADMIN" | "EDITOR";
  avatar: string;
};

type PostData = {
  title: string;
  content: string;
  published: boolean;
  authorId: string;
};

// Base factory function
function defineFactory<T>(defaults: () => T) {
  return (overrides?: Partial<T>): T => ({
    ...defaults(),
    ...overrides,
  });
}

export const createUser = defineFactory<UserData>(() => ({
  email: faker.internet.email(),
  name: faker.person.fullName(),
  role: "USER",
  avatar: faker.image.avatar(),
}));

export const createPost = defineFactory<PostData>(() => ({
  title: faker.lorem.sentence(),
  content: faker.lorem.paragraphs(2),
  published: true,
  authorId: faker.string.uuid(),
}));

// Deterministic seeding for reproducible tests
export function seedRandom(seed: number) {
  faker.seed(seed);
}

// Usage in tests
// seedRandom(42);
// const user = createUser({ role: "ADMIN" });
// const post = createPost({ authorId: user.id, published: false });
```

## Drizzle Seed Script

```typescript
// drizzle/seed.ts
import { drizzle } from "drizzle-orm/node-postgres";
import { faker } from "@faker-js/faker";
import { users, posts, comments } from "./schema";

const db = drizzle(process.env.DATABASE_URL!);

async function seed() {
  // Insert users
  const insertedUsers = await db
    .insert(users)
    .values(
      Array.from({ length: 20 }, () => ({
        email: faker.internet.email(),
        name: faker.person.fullName(),
        role: faker.helpers.arrayElement(["user", "admin"] as const),
      })),
    )
    .returning();

  // Insert posts with references
  const insertedPosts = await db
    .insert(posts)
    .values(
      insertedUsers.flatMap((user) =>
        Array.from({ length: faker.number.int({ min: 1, max: 4 }) }, () => ({
          title: faker.lorem.sentence(),
          body: faker.lorem.paragraphs(2),
          authorId: user.id,
          publishedAt: faker.datatype.boolean(0.6) ? new Date() : null,
        })),
      ),
    )
    .returning();

  // Insert comments
  await db.insert(comments).values(
    insertedPosts.flatMap((post) =>
      Array.from({ length: faker.number.int({ min: 0, max: 5 }) }, () => ({
        text: faker.lorem.paragraph(),
        postId: post.id,
        authorId: faker.helpers.arrayElement(insertedUsers).id,
      })),
    ),
  );

  console.log("Seeding complete");
}

seed().catch(console.error);
```

## SQLAlchemy / Alembic Seeding (Python)

```python
# seeds/seed_db.py
import random
from faker import Faker
from sqlalchemy.orm import Session
from app.models import User, Post, Comment
from app.database import engine, SessionLocal

fake = Faker()

def seed_users(db: Session, count: int = 20) -> list[User]:
    users = []
    for _ in range(count):
        user = User(
            email=fake.email(),
            name=fake.name(),
            role=random.choice(["user", "admin", "editor"]),
            avatar=fake.image_url(),
        )
        db.add(user)
        users.append(user)
    db.flush()
    return users

def seed_posts(db: Session, users: list[User]) -> list[Post]:
    posts = []
    for user in users:
        for _ in range(random.randint(0, 5)):
            post = Post(
                title=fake.sentence(),
                content=fake.text(max_nb_chars=500),
                published=random.random() > 0.3,
                author_id=user.id,
            )
            db.add(post)
            posts.append(post)
    db.flush()
    return posts

def seed_comments(db: Session, posts: list[Post], users: list[User]):
    for post in posts:
        for _ in range(random.randint(0, 3)):
            comment = Comment(
                text=fake.paragraph(),
                post_id=post.id,
                author_id=random.choice(users).id,
            )
            db.add(comment)

def run_seed():
    db = SessionLocal()
    try:
        users = seed_users(db)
        posts = seed_posts(db, users)
        seed_comments(db, posts, users)
        db.commit()
        print(f"Seeded {len(users)} users, {len(posts)} posts")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    run_seed()
```

## Seed Best Practices

```
GUIDELINES:
  [ ] Use faker.seed(N) for deterministic test data
  [ ] Clear tables in reverse dependency order (comments → posts → users)
  [ ] Maintain referential integrity across related entities
  [ ] Create minimal seed for tests, larger seed for dev
  [ ] Use transactions so partial seeds don't leave bad state
  [ ] Separate dev seeds (realistic) from test seeds (minimal, deterministic)

ENVIRONMENT STRATEGY:
  development  → Rich, realistic data (~100-500 records)
  test         → Minimal, deterministic (faker.seed(42))
  staging      → Anonymized production data or large synthetic set
  production   → Only essential reference data (roles, categories, etc.)
```

## Additional Resources

- Faker.js: https://fakerjs.dev/
- Python Faker: https://faker.readthedocs.io/
- Prisma seeding: https://www.prisma.io/docs/guides/migrate/seed-database
