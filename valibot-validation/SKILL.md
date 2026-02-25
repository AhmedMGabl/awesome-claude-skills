---
name: valibot-validation
description: Valibot validation patterns covering tree-shakeable schema definitions, type inference, transformations, custom validators, error formatting, and React form integration.
---

# Valibot Validation

This skill should be used when validating data with Valibot. It covers schema definitions, type inference, transformations, custom validators, and form integration.

## When to Use This Skill

Use this skill when you need to:

- Validate data with a tree-shakeable schema library
- Infer TypeScript types from validation schemas
- Transform and coerce input data
- Build custom validation pipelines
- Integrate validation with React forms

## Setup

```bash
npm install valibot
```

## Basic Schemas

```ts
import * as v from "valibot";

const UserSchema = v.object({
  name: v.pipe(v.string(), v.minLength(2), v.maxLength(50)),
  email: v.pipe(v.string(), v.email()),
  age: v.pipe(v.number(), v.integer(), v.minValue(18)),
  role: v.picklist(["admin", "user", "editor"]),
  bio: v.optional(v.pipe(v.string(), v.maxLength(500))),
  tags: v.array(v.string()),
  isActive: v.boolean(),
});

// Infer TypeScript type
type User = v.InferOutput<typeof UserSchema>;

// Validate
const result = v.safeParse(UserSchema, inputData);
if (result.success) {
  console.log("Valid:", result.output);
} else {
  console.log("Errors:", result.issues);
}

// Parse (throws on invalid)
const user = v.parse(UserSchema, inputData);
```

## Advanced Types

```ts
import * as v from "valibot";

// Union types
const ResponseSchema = v.variant("type", [
  v.object({ type: v.literal("success"), data: v.any() }),
  v.object({ type: v.literal("error"), message: v.string() }),
]);

// Recursive types
type TreeNode = v.InferOutput<typeof TreeNodeSchema>;
const TreeNodeSchema: v.GenericSchema<TreeNode> = v.object({
  value: v.string(),
  children: v.array(v.lazy(() => TreeNodeSchema)),
});

// Record types
const ConfigSchema = v.record(v.string(), v.union([v.string(), v.number(), v.boolean()]));

// Tuple
const CoordinateSchema = v.tuple([v.number(), v.number()]);

// Intersection
const BaseSchema = v.object({ id: v.string() });
const TimestampSchema = v.object({ createdAt: v.date(), updatedAt: v.date() });
const EntitySchema = v.intersect([BaseSchema, TimestampSchema]);
```

## Transformations

```ts
import * as v from "valibot";

// Transform string to number
const NumericStringSchema = v.pipe(
  v.string(),
  v.transform((input) => Number(input)),
  v.number(),
  v.minValue(0)
);

// Trim and lowercase
const NormalizedEmailSchema = v.pipe(
  v.string(),
  v.trim(),
  v.toLowerCase(),
  v.email()
);

// Default values
const SettingsSchema = v.object({
  theme: v.optional(v.picklist(["light", "dark"]), "light"),
  pageSize: v.optional(v.pipe(v.number(), v.integer()), 20),
  language: v.optional(v.string(), "en"),
});
```

## Custom Validators

```ts
import * as v from "valibot";

// Custom validation
const PasswordSchema = v.pipe(
  v.string(),
  v.minLength(8),
  v.check(
    (input) => /[A-Z]/.test(input),
    "Must contain uppercase letter"
  ),
  v.check(
    (input) => /[0-9]/.test(input),
    "Must contain a number"
  ),
  v.check(
    (input) => /[^a-zA-Z0-9]/.test(input),
    "Must contain a special character"
  )
);

// Async validation
const UniqueEmailSchema = v.pipeAsync(
  v.string(),
  v.email(),
  v.checkAsync(async (email) => {
    const exists = await checkEmailExists(email);
    return !exists;
  }, "Email already registered")
);
```

## Error Formatting

```ts
import * as v from "valibot";

function formatErrors(issues: v.BaseIssue<unknown>[]): Record<string, string[]> {
  const errors: Record<string, string[]> = {};

  for (const issue of issues) {
    const path = issue.path?.map((p) => p.key).join(".") || "root";
    if (!errors[path]) errors[path] = [];
    errors[path].push(issue.message);
  }

  return errors;
}

const result = v.safeParse(UserSchema, data);
if (!result.success) {
  const formatted = formatErrors(result.issues);
  // { "email": ["Invalid email"], "age": ["Must be >= 18"] }
}
```

## Additional Resources

- Valibot: https://valibot.dev/
- API: https://valibot.dev/api/
- Guides: https://valibot.dev/guides/
