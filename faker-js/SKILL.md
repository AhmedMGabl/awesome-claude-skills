---
name: faker-js
description: Faker.js patterns covering realistic test data generation, locale support, seeded reproducibility, custom providers, factories, and database seeding workflows.
---

# Faker.js

This skill should be used when generating realistic test data with Faker.js. It covers data generation, locales, seeding, custom providers, and factory patterns.

## When to Use This Skill

Use this skill when you need to:

- Generate realistic fake data for testing
- Seed databases with sample data
- Create factory functions for test fixtures
- Generate locale-specific data
- Build reproducible test datasets

## Setup

```bash
npm install @faker-js/faker
```

## Basic Data Generation

```ts
import { faker } from "@faker-js/faker";

// Person
const person = {
  firstName: faker.person.firstName(),
  lastName: faker.person.lastName(),
  fullName: faker.person.fullName(),
  email: faker.internet.email(),
  avatar: faker.image.avatar(),
  jobTitle: faker.person.jobTitle(),
  bio: faker.person.bio(),
};

// Address
const address = {
  street: faker.location.streetAddress(),
  city: faker.location.city(),
  state: faker.location.state(),
  zip: faker.location.zipCode(),
  country: faker.location.country(),
  latitude: faker.location.latitude(),
  longitude: faker.location.longitude(),
};

// Commerce
const product = {
  name: faker.commerce.productName(),
  price: faker.commerce.price({ min: 10, max: 500, dec: 2 }),
  description: faker.commerce.productDescription(),
  department: faker.commerce.department(),
  isbn: faker.commerce.isbn(),
};

// Dates
const dates = {
  past: faker.date.past(),
  future: faker.date.future(),
  recent: faker.date.recent({ days: 7 }),
  between: faker.date.between({ from: "2024-01-01", to: "2024-12-31" }),
  birthdate: faker.date.birthdate({ min: 18, max: 65, mode: "age" }),
};
```

## Factory Pattern

```ts
import { faker } from "@faker-js/faker";

interface User {
  id: string;
  name: string;
  email: string;
  role: "admin" | "user" | "editor";
  createdAt: Date;
  isActive: boolean;
}

function createUser(overrides: Partial<User> = {}): User {
  return {
    id: faker.string.uuid(),
    name: faker.person.fullName(),
    email: faker.internet.email(),
    role: faker.helpers.arrayElement(["admin", "user", "editor"]),
    createdAt: faker.date.past(),
    isActive: faker.datatype.boolean(),
    ...overrides,
  };
}

function createUsers(count: number, overrides: Partial<User> = {}): User[] {
  return Array.from({ length: count }, () => createUser(overrides));
}

// Usage
const adminUsers = createUsers(5, { role: "admin", isActive: true });
const testUser = createUser({ name: "Test User", email: "test@example.com" });
```

## Seeded Reproducibility

```ts
import { faker } from "@faker-js/faker";

// Set seed for reproducible data
faker.seed(42);

const user1 = faker.person.fullName(); // Always same name
const user2 = faker.person.fullName(); // Always same name

// Reset seed
faker.seed(42);
const sameUser1 = faker.person.fullName(); // Same as user1
```

## Locale Support

```ts
import { faker } from "@faker-js/faker";
import { fakerDE } from "@faker-js/faker";
import { fakerJA } from "@faker-js/faker";

// German locale
const germanName = fakerDE.person.fullName();
const germanCity = fakerDE.location.city();

// Japanese locale
const japaneseName = fakerJA.person.fullName();
const japaneseCity = fakerJA.location.city();

// Set locale dynamically
faker.locale = "fr";
const frenchName = faker.person.fullName();
```

## Database Seeding

```ts
import { faker } from "@faker-js/faker";

async function seedDatabase(db: any) {
  faker.seed(123); // Reproducible seed data

  // Create categories
  const categories = Array.from({ length: 5 }, () => ({
    id: faker.string.uuid(),
    name: faker.commerce.department(),
    slug: faker.helpers.slugify(faker.commerce.department()).toLowerCase(),
  }));

  await db.insert("categories", categories);

  // Create products linked to categories
  const products = Array.from({ length: 50 }, () => ({
    id: faker.string.uuid(),
    name: faker.commerce.productName(),
    price: parseFloat(faker.commerce.price({ min: 5, max: 200 })),
    categoryId: faker.helpers.arrayElement(categories).id,
    description: faker.commerce.productDescription(),
    imageUrl: faker.image.urlPicsumPhotos({ width: 400, height: 400 }),
    createdAt: faker.date.past({ years: 1 }),
  }));

  await db.insert("products", products);

  console.log(`Seeded ${categories.length} categories, ${products.length} products`);
}
```

## Additional Resources

- Faker.js: https://fakerjs.dev/
- API: https://fakerjs.dev/api/
- Locales: https://fakerjs.dev/guide/localization
