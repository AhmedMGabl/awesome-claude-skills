---
name: io-ts-validation
description: io-ts validation patterns covering runtime type checking, codec composition, branded types, reporters, Either-based error handling, and fp-ts integration.
---

# io-ts Validation

This skill should be used when validating data with io-ts. It covers codecs, branded types, reporters, Either-based errors, and fp-ts integration.

## When to Use This Skill

Use this skill when you need to:

- Validate data with functional programming patterns
- Compose codecs for complex type validation
- Create branded/newtype types for domain safety
- Handle validation errors with Either monad
- Integrate with fp-ts ecosystem

## Setup

```bash
npm install io-ts fp-ts io-ts-types
```

## Basic Codecs

```ts
import * as t from "io-ts";
import { isRight } from "fp-ts/Either";

const User = t.type({
  name: t.string,
  email: t.string,
  age: t.number,
  role: t.union([t.literal("admin"), t.literal("user"), t.literal("editor")]),
  isActive: t.boolean,
});

// Infer TypeScript type
type User = t.TypeOf<typeof User>;

// Validate
const result = User.decode(inputData);

if (isRight(result)) {
  console.log("Valid:", result.right);
} else {
  console.log("Errors:", result.left);
}
```

## Codec Composition

```ts
import * as t from "io-ts";

// Optional fields
const UserProfile = t.intersection([
  t.type({
    name: t.string,
    email: t.string,
  }),
  t.partial({
    bio: t.string,
    website: t.string,
    avatar: t.string,
  }),
]);

// Arrays
const UserList = t.array(UserProfile);

// Record types
const Config = t.record(t.string, t.union([t.string, t.number, t.boolean]));

// Tuple
const Coordinate = t.tuple([t.number, t.number]);

// Readonly
const ImmutableUser = t.readonly(UserProfile);

// Exact (strip unknown keys)
const StrictUser = t.exact(t.type({
  name: t.string,
  email: t.string,
}));
```

## Branded Types

```ts
import * as t from "io-ts";

// Email branded type
interface EmailBrand {
  readonly Email: unique symbol;
}

const Email = t.brand(
  t.string,
  (s): s is t.Branded<string, EmailBrand> =>
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s),
  "Email"
);

type Email = t.TypeOf<typeof Email>;

// Positive integer
interface PositiveIntBrand {
  readonly PositiveInt: unique symbol;
}

const PositiveInt = t.brand(
  t.number,
  (n): n is t.Branded<number, PositiveIntBrand> =>
    Number.isInteger(n) && n > 0,
  "PositiveInt"
);

// Use in schemas
const Order = t.type({
  customerEmail: Email,
  quantity: PositiveInt,
});
```

## Error Reporting

```ts
import * as t from "io-ts";
import { isLeft } from "fp-ts/Either";
import { PathReporter } from "io-ts/PathReporter";

const schema = t.type({
  name: t.string,
  age: t.number,
  email: t.string,
});

const result = schema.decode({ name: 123, age: "old", email: null });

if (isLeft(result)) {
  // Path reporter
  const messages = PathReporter.report(result);
  console.log(messages);
  // ["Invalid value 123 supplied to : .../name: string",
  //  "Invalid value \"old\" supplied to : .../age: number", ...]
}
```

## io-ts-types Extras

```ts
import * as t from "io-ts";
import { DateFromISOString, NumberFromString, NonEmptyString, UUID } from "io-ts-types";

const APIInput = t.type({
  id: UUID,
  name: NonEmptyString,
  amount: NumberFromString, // "42" -> 42
  createdAt: DateFromISOString, // ISO string -> Date
});

type APIInput = t.TypeOf<typeof APIInput>;
// { id: string, name: string, amount: number, createdAt: Date }
```

## Additional Resources

- io-ts: https://github.com/gcanti/io-ts
- Branded types: https://github.com/gcanti/io-ts/blob/master/index.md#branded-types--refinements
- io-ts-types: https://github.com/gcanti/io-ts-types
