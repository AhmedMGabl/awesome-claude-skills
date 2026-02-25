---
name: typebox-validation
description: TypeBox validation patterns covering JSON Schema-compatible type definitions, value checking, type compilation, default values, transformations, and Fastify integration.
---

# TypeBox Validation

This skill should be used when defining JSON Schema-compatible types with TypeBox. It covers type definitions, validation, compilation, transformations, and Fastify integration.

## When to Use This Skill

Use this skill when you need to:

- Define JSON Schema-compatible TypeScript types
- Validate data at runtime with compiled validators
- Generate JSON Schema from TypeScript definitions
- Integrate validation with Fastify
- Build type-safe API contracts

## Setup

```bash
npm install @sinclair/typebox
```

## Basic Types

```ts
import { Type, Static } from "@sinclair/typebox";
import { Value } from "@sinclair/typebox/value";

const UserSchema = Type.Object({
  name: Type.String({ minLength: 2, maxLength: 50 }),
  email: Type.String({ format: "email" }),
  age: Type.Integer({ minimum: 18 }),
  role: Type.Union([
    Type.Literal("admin"),
    Type.Literal("user"),
    Type.Literal("editor"),
  ]),
  bio: Type.Optional(Type.String({ maxLength: 500 })),
  tags: Type.Array(Type.String()),
  isActive: Type.Boolean(),
});

// Infer TypeScript type
type User = Static<typeof UserSchema>;

// Validate
const isValid = Value.Check(UserSchema, inputData);

// Get errors
const errors = [...Value.Errors(UserSchema, inputData)];
errors.forEach((err) => {
  console.log(`${err.path}: ${err.message}`);
});
```

## Advanced Types

```ts
import { Type, Static } from "@sinclair/typebox";

// Enum-like
const StatusSchema = Type.Union([
  Type.Literal("active"),
  Type.Literal("inactive"),
  Type.Literal("pending"),
]);

// Record
const ConfigSchema = Type.Record(
  Type.String(),
  Type.Union([Type.String(), Type.Number(), Type.Boolean()])
);

// Tuple
const PointSchema = Type.Tuple([Type.Number(), Type.Number()]);

// Intersect
const BaseSchema = Type.Object({ id: Type.String() });
const TimestampSchema = Type.Object({
  createdAt: Type.String({ format: "date-time" }),
  updatedAt: Type.String({ format: "date-time" }),
});
const EntitySchema = Type.Intersect([BaseSchema, TimestampSchema]);

// Recursive
const TreeSchema = Type.Recursive((Self) =>
  Type.Object({
    value: Type.String(),
    children: Type.Array(Self),
  })
);

// Partial and Required
const PartialUser = Type.Partial(UserSchema);
const RequiredUser = Type.Required(PartialUser);
```

## Compiled Validation

```ts
import { TypeCompiler } from "@sinclair/typebox/compiler";
import { Type } from "@sinclair/typebox";

const schema = Type.Object({
  name: Type.String(),
  email: Type.String({ format: "email" }),
  age: Type.Integer({ minimum: 0 }),
});

// Compile for faster validation
const compiled = TypeCompiler.Compile(schema);

// Check
const isValid = compiled.Check(data);

// Get errors
const errors = [...compiled.Errors(data)];

// Decode (validate + apply defaults)
const decoded = compiled.Decode(data);
```

## Default Values and Coercion

```ts
import { Type } from "@sinclair/typebox";
import { Value } from "@sinclair/typebox/value";

const SettingsSchema = Type.Object({
  theme: Type.String({ default: "light" }),
  pageSize: Type.Integer({ default: 20, minimum: 1, maximum: 100 }),
  notifications: Type.Boolean({ default: true }),
  language: Type.String({ default: "en" }),
});

// Create with defaults
const settings = Value.Create(SettingsSchema);
// { theme: "light", pageSize: 20, notifications: true, language: "en" }

// Clean unknown properties
const cleaned = Value.Clean(SettingsSchema, inputWithExtraProps);

// Convert types (string "42" to number 42)
const converted = Value.Convert(SettingsSchema, { pageSize: "20" });
```

## Fastify Integration

```ts
import Fastify from "fastify";
import { Type, Static } from "@sinclair/typebox";

const app = Fastify();

const CreateUserBody = Type.Object({
  name: Type.String({ minLength: 1 }),
  email: Type.String({ format: "email" }),
});

const UserResponse = Type.Object({
  id: Type.String(),
  name: Type.String(),
  email: Type.String(),
});

app.post<{
  Body: Static<typeof CreateUserBody>;
  Reply: Static<typeof UserResponse>;
}>("/users", {
  schema: {
    body: CreateUserBody,
    response: { 201: UserResponse },
  },
  handler: async (request, reply) => {
    const { name, email } = request.body; // Fully typed
    const user = { id: "uuid", name, email };
    reply.status(201).send(user);
  },
});
```

## Additional Resources

- TypeBox: https://github.com/sinclairzx81/typebox
- Value API: https://github.com/sinclairzx81/typebox#values
- Compiler: https://github.com/sinclairzx81/typebox#typecompiler
