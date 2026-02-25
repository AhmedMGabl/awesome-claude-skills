---
name: effect-schema
description: Effect Schema patterns covering type-safe schema definitions, transformations, branded types, recursive schemas, JSON Schema generation, parsing with detailed errors, and integration with Effect runtime.
---

# Effect Schema

This skill should be used when defining type-safe schemas with @effect/schema. It covers schema definitions, transformations, branded types, parsing, and Effect integration.

## When to Use This Skill

Use this skill when you need to:

- Define type-safe schemas with Effect ecosystem
- Transform data between different representations
- Create branded types for domain modeling
- Generate JSON Schema from TypeScript types
- Parse and validate with detailed error reporting

## Basic Schemas

```typescript
import { Schema } from "@effect/schema";

// Primitive schemas
const Name = Schema.String.pipe(Schema.minLength(1), Schema.maxLength(100));
const Age = Schema.Number.pipe(Schema.int(), Schema.between(0, 150));
const Email = Schema.String.pipe(Schema.pattern(/^[^\s@]+@[^\s@]+\.[^\s@]+$/));

// Object schema
const User = Schema.Struct({
  id: Schema.String.pipe(Schema.ULID),
  name: Name,
  email: Email,
  age: Schema.optional(Age),
  role: Schema.Literal("admin", "user", "moderator"),
  createdAt: Schema.DateFromString,
});

type User = Schema.Schema.Type<typeof User>;

// Parse and validate
const parseUser = Schema.decodeUnknownSync(User);

const user = parseUser({
  id: "01ARZ3NDEKTSV4RRFFQ69G5FAV",
  name: "Alice",
  email: "alice@example.com",
  role: "admin",
  createdAt: "2024-01-15T00:00:00Z",
});
```

## Transformations

```typescript
// Transform between encoded and decoded types
const NumberFromString = Schema.transform(
  Schema.String,
  Schema.Number,
  {
    decode: (s) => Number(s),
    encode: (n) => String(n),
  }
);

// Date from ISO string (built-in)
const DateSchema = Schema.DateFromString;

// Trim and lowercase
const NormalizedEmail = Schema.String.pipe(
  Schema.trim,
  Schema.lowercase,
  Schema.pattern(/^[^\s@]+@[^\s@]+\.[^\s@]+$/),
);

// Transform entire objects
const CreateUserInput = Schema.Struct({
  name: Schema.String,
  email: NormalizedEmail,
  password: Schema.String.pipe(Schema.minLength(8)),
});

const UserRecord = Schema.transform(
  CreateUserInput,
  Schema.Struct({
    name: Schema.String,
    email: Schema.String,
    passwordHash: Schema.String,
    createdAt: Schema.DateFromSelf,
  }),
  {
    decode: (input) => ({
      name: input.name,
      email: input.email,
      passwordHash: hashPassword(input.password),
      createdAt: new Date(),
    }),
    encode: (record) => ({
      name: record.name,
      email: record.email,
      password: "", // Cannot reverse hash
    }),
  }
);
```

## Branded Types

```typescript
// Create branded types for domain safety
const UserId = Schema.String.pipe(Schema.brand("UserId"));
type UserId = Schema.Schema.Type<typeof UserId>;

const OrderId = Schema.String.pipe(Schema.brand("OrderId"));
type OrderId = Schema.Schema.Type<typeof OrderId>;

const PositiveAmount = Schema.Number.pipe(
  Schema.positive(),
  Schema.brand("PositiveAmount"),
);
type PositiveAmount = Schema.Schema.Type<typeof PositiveAmount>;

// These are now distinct types
function getUser(id: UserId): Promise<User> { /* ... */ }
function getOrder(id: OrderId): Promise<Order> { /* ... */ }

// TypeScript prevents mixing up IDs
const userId = Schema.decodeSync(UserId)("user-123");
const orderId = Schema.decodeSync(OrderId)("order-456");
// getUser(orderId) // Type error!
```

## Unions and Enums

```typescript
// Discriminated unions
const Shape = Schema.Union(
  Schema.Struct({
    type: Schema.Literal("circle"),
    radius: Schema.Number.pipe(Schema.positive()),
  }),
  Schema.Struct({
    type: Schema.Literal("rectangle"),
    width: Schema.Number.pipe(Schema.positive()),
    height: Schema.Number.pipe(Schema.positive()),
  }),
  Schema.Struct({
    type: Schema.Literal("triangle"),
    base: Schema.Number.pipe(Schema.positive()),
    height: Schema.Number.pipe(Schema.positive()),
  }),
);

type Shape = Schema.Schema.Type<typeof Shape>;

// Enums
const Status = Schema.Literal("draft", "published", "archived");
```

## Arrays and Records

```typescript
const Tags = Schema.Array(Schema.String.pipe(Schema.minLength(1)));

const UserMap = Schema.Record(
  Schema.String, // key type
  User,          // value type
);

const NonEmptyList = Schema.NonEmptyArray(Schema.Number);

// Tuple
const Coordinate = Schema.Tuple(Schema.Number, Schema.Number);
```

## Error Handling

```typescript
import { Schema, ParseResult } from "@effect/schema";
import { Effect, Either } from "effect";

// Sync with Either
const result = Schema.decodeUnknownEither(User)(data);
if (Either.isRight(result)) {
  console.log("Valid:", result.right);
} else {
  const errors = ParseResult.ArrayFormatter.formatErrorSync(result.left);
  console.error("Errors:", errors);
}

// With Effect
const program = Schema.decodeUnknown(User)(data).pipe(
  Effect.tap((user) => Effect.log(`Parsed user: ${user.name}`)),
  Effect.catchTag("ParseError", (e) =>
    Effect.logError(`Validation failed: ${e.message}`)
  ),
);
```

## Additional Resources

- Effect Schema: https://effect.website/docs/schema/introduction
- Transformations: https://effect.website/docs/schema/transformations
- Branded types: https://effect.website/docs/schema/branded-types
