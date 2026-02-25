---
name: valibot-schemas
description: Valibot schema validation patterns covering string, number, object, and array schemas, pipe transformations, custom validations, form validation, API input parsing, error formatting, and comparison with Zod for tree-shakeable type-safe validation.
---

# Valibot Schemas

This skill should be used when validating data with Valibot. It covers schema definitions, pipe transformations, custom validations, form integration, and API parsing.

## When to Use This Skill

Use this skill when you need to:

- Validate data with a tree-shakeable, lightweight library
- Define schemas with pipe-based transformations
- Parse API inputs and form data with type inference
- Create custom validation rules
- Migrate from Zod to a smaller bundle alternative

## Basic Schemas

```typescript
import * as v from "valibot";

// Primitives
const StringSchema = v.string();
const NumberSchema = v.number();
const BooleanSchema = v.boolean();
const DateSchema = v.date();

// With validations using pipe
const EmailSchema = v.pipe(v.string(), v.email(), v.maxLength(255));

const AgeSchema = v.pipe(v.number(), v.integer(), v.minValue(0), v.maxValue(150));

const UrlSchema = v.pipe(v.string(), v.url());

const UuidSchema = v.pipe(v.string(), v.uuid());

// Literals and enums
const StatusSchema = v.picklist(["active", "inactive", "pending"]);
const RoleSchema = v.enum_({ Admin: "admin", User: "user", Guest: "guest" });

// Optional and nullable
const OptionalString = v.optional(v.string());
const NullableString = v.nullable(v.string());
const OptionalWithDefault = v.optional(v.string(), "default-value");
```

## Object Schemas

```typescript
import * as v from "valibot";

const UserSchema = v.object({
  id: v.pipe(v.string(), v.uuid()),
  name: v.pipe(v.string(), v.minLength(1), v.maxLength(100)),
  email: v.pipe(v.string(), v.email()),
  age: v.optional(v.pipe(v.number(), v.integer(), v.minValue(0))),
  role: v.picklist(["admin", "user"]),
  tags: v.array(v.pipe(v.string(), v.minLength(1))),
  address: v.optional(
    v.object({
      street: v.string(),
      city: v.string(),
      zip: v.pipe(v.string(), v.regex(/^\d{5}(-\d{4})?$/)),
    }),
  ),
  createdAt: v.date(),
});

// Infer TypeScript type
type User = v.InferOutput<typeof UserSchema>;

// Partial and required
const PartialUser = v.partial(UserSchema);
const UpdateUser = v.partial(v.omit(UserSchema, ["id", "createdAt"]));

// Pick specific fields
const UserPreview = v.pick(UserSchema, ["id", "name", "email"]);

// Merge schemas
const AdminUser = v.intersect([
  UserSchema,
  v.object({ permissions: v.array(v.string()) }),
]);
```

## Pipe Transformations

```typescript
import * as v from "valibot";

// Transform while validating
const TrimmedString = v.pipe(v.string(), v.trim());

const LowercaseEmail = v.pipe(v.string(), v.trim(), v.toLowerCase(), v.email());

const CoercedNumber = v.pipe(v.unknown(), v.transform(Number), v.number(), v.minValue(0));

const ParsedDate = v.pipe(
  v.string(),
  v.transform((input) => new Date(input)),
  v.date(),
);

// Custom validation in pipe
const PasswordSchema = v.pipe(
  v.string(),
  v.minLength(8),
  v.regex(/[A-Z]/, "Must contain uppercase letter"),
  v.regex(/[a-z]/, "Must contain lowercase letter"),
  v.regex(/[0-9]/, "Must contain number"),
  v.regex(/[^A-Za-z0-9]/, "Must contain special character"),
);

// Dependent field validation
const FormSchema = v.pipe(
  v.object({
    password: PasswordSchema,
    confirmPassword: v.string(),
  }),
  v.forward(
    v.check(
      (input) => input.password === input.confirmPassword,
      "Passwords must match",
    ),
    ["confirmPassword"],
  ),
);
```

## Parsing and Error Handling

```typescript
import * as v from "valibot";

const UserSchema = v.object({
  name: v.pipe(v.string(), v.minLength(1)),
  email: v.pipe(v.string(), v.email()),
});

// Parse (throws on failure)
try {
  const user = v.parse(UserSchema, data);
  // user is typed as { name: string; email: string }
} catch (error) {
  if (v.isValiError(error)) {
    for (const issue of error.issues) {
      console.log(issue.path, issue.message);
    }
  }
}

// Safe parse (returns result object)
const result = v.safeParse(UserSchema, data);
if (result.success) {
  console.log(result.output); // Typed output
} else {
  // Format errors
  const flat = v.flatten(result.issues);
  console.log(flat.nested);
  // { name: ["String must have at least 1 character"], email: ["Invalid email"] }
}
```

## Discriminated Unions

```typescript
import * as v from "valibot";

const ShapeSchema = v.variant("type", [
  v.object({
    type: v.literal("circle"),
    radius: v.pipe(v.number(), v.minValue(0)),
  }),
  v.object({
    type: v.literal("rectangle"),
    width: v.pipe(v.number(), v.minValue(0)),
    height: v.pipe(v.number(), v.minValue(0)),
  }),
  v.object({
    type: v.literal("triangle"),
    base: v.pipe(v.number(), v.minValue(0)),
    height: v.pipe(v.number(), v.minValue(0)),
  }),
]);

type Shape = v.InferOutput<typeof ShapeSchema>;
```

## API Route Validation

```typescript
import * as v from "valibot";

// Express/Hono middleware pattern
function validate<T extends v.BaseSchema<unknown, unknown, v.BaseIssue<unknown>>>(
  schema: T,
) {
  return (req: Request, res: Response, next: NextFunction) => {
    const result = v.safeParse(schema, req.body);
    if (!result.success) {
      return res.status(400).json({
        error: "Validation failed",
        details: v.flatten(result.issues).nested,
      });
    }
    req.body = result.output;
    next();
  };
}

const CreatePostSchema = v.object({
  title: v.pipe(v.string(), v.minLength(1), v.maxLength(200)),
  body: v.pipe(v.string(), v.minLength(10)),
  tags: v.optional(v.array(v.string()), []),
});

app.post("/api/posts", validate(CreatePostSchema), (req, res) => {
  // req.body is fully typed
  const post = createPost(req.body);
  res.status(201).json(post);
});
```

## Additional Resources

- Valibot docs: https://valibot.dev/
- API reference: https://valibot.dev/api/
- Migration from Zod: https://valibot.dev/guides/migrate-from-zod/
