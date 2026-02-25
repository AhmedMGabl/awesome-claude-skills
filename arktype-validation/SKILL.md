---
name: arktype-validation
description: ArkType validation patterns covering 1:1 TypeScript syntax, type inference, morphs, scoped types, default values, discriminated unions, and runtime type checking.
---

# ArkType Validation

This skill should be used when validating data with ArkType. It covers TypeScript-native syntax, type inference, morphs, scoped types, and runtime validation.

## When to Use This Skill

Use this skill when you need to:

- Define runtime validators using TypeScript-like syntax
- Get 1:1 TypeScript type inference from validators
- Apply morphs (transformations) during validation
- Create scoped and reusable type definitions
- Validate complex nested data structures

## Setup

```bash
npm install arktype
```

## Basic Types

```ts
import { type } from "arktype";

// Define types using TypeScript-like syntax
const user = type({
  name: "string > 0",
  email: "string.email",
  age: "integer >= 18",
  role: "'admin' | 'user' | 'editor'",
  bio: "string <= 500 | undefined",
  tags: "string[]",
  isActive: "boolean",
});

// Infer TypeScript type
type User = typeof user.infer;

// Validate
const result = user({ name: "Alice", email: "alice@test.com", age: 25, role: "user", tags: [], isActive: true });

if (result instanceof type.errors) {
  console.log("Errors:", result.summary);
} else {
  console.log("Valid:", result);
}
```

## Advanced Types

```ts
import { type, scope } from "arktype";

// Union types
const response = type({
  status: "'success' | 'error'",
  "data?": "unknown",
  "message?": "string",
});

// Arrays and tuples
const coordinates = type(["number", "number"]);
const matrix = type("number[][]");

// Nested objects
const order = type({
  id: "string",
  items: [{
    productId: "string",
    quantity: "integer > 0",
    price: "number > 0",
  }, "[]"],
  total: "number >= 0",
  status: "'pending' | 'shipped' | 'delivered'",
});

// Record type
const config = type("Record<string, string | number | boolean>");

// Date validation
const event = type({
  name: "string",
  date: "Date",
});
```

## Morphs (Transformations)

```ts
import { type } from "arktype";

// Transform string to number
const numericString = type("string.numeric.parse");

const result = numericString("42"); // 42 (number)

// Transform with pipe
const normalizedEmail = type("string.email").pipe((s) => s.toLowerCase().trim());

// Coerce to Date
const dateString = type("string").pipe((s) => new Date(s));

// Multiple transforms
const formInput = type({
  name: "string.trim",
  email: type("string.email").pipe((s) => s.toLowerCase()),
  age: "string.numeric.parse",
});
```

## Scoped Types

```ts
import { scope } from "arktype";

const types = scope({
  user: {
    id: "string",
    name: "string > 0",
    email: "string.email",
    role: "role",
  },
  role: "'admin' | 'user' | 'editor'",
  post: {
    id: "string",
    title: "string > 0",
    content: "string",
    author: "user",
    tags: "string[]",
  },
  createPost: {
    title: "string > 0",
    content: "string",
    tags: "string[]",
  },
}).export();

// Use exported types
const post = types.post(inputData);
const newPost = types.createPost(formData);
```

## Default Values

```ts
import { type } from "arktype";

const settings = type({
  theme: "'light' | 'dark' = 'light'",
  "pageSize?": "integer = 20",
  "notifications?": "boolean = true",
  "language?": "string = 'en'",
});

const result = settings({});
// { theme: "light", pageSize: 20, notifications: true, language: "en" }
```

## Error Handling

```ts
import { type } from "arktype";

const schema = type({
  name: "string > 0",
  email: "string.email",
  age: "integer >= 18",
});

const result = schema({ name: "", email: "bad", age: 15 });

if (result instanceof type.errors) {
  // Formatted summary
  console.log(result.summary);

  // Individual errors
  for (const error of result) {
    console.log(`Path: ${error.path}, Message: ${error.message}`);
  }
}
```

## Additional Resources

- ArkType: https://arktype.io/
- Docs: https://arktype.io/docs/intro
- Scopes: https://arktype.io/docs/scopes-and-modules
