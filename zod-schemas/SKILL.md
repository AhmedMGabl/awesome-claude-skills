---
name: zod-schemas
description: Zod advanced schema patterns covering discriminated unions, recursive types, branded types, schema composition, coercion, custom error maps, form integration, and API contract validation.
---

# Zod Advanced Schemas

This skill should be used when building advanced validation schemas with Zod. It covers discriminated unions, recursive types, branded types, and schema composition patterns.

## When to Use This Skill

Use this skill when you need to:

- Define complex discriminated union types
- Build recursive or self-referencing schemas
- Create branded types for domain modeling
- Compose schemas with merge, extend, and pipe
- Validate API contracts and form data

## Discriminated Unions

```typescript
import { z } from "zod";

const NotificationSchema = z.discriminatedUnion("type", [
  z.object({
    type: z.literal("email"),
    to: z.string().email(),
    subject: z.string(),
    body: z.string(),
  }),
  z.object({
    type: z.literal("sms"),
    phone: z.string().regex(/^\+\d{10,15}$/),
    message: z.string().max(160),
  }),
  z.object({
    type: z.literal("push"),
    deviceToken: z.string(),
    title: z.string(),
    body: z.string(),
    data: z.record(z.string()).optional(),
  }),
]);

type Notification = z.infer<typeof NotificationSchema>;
```

## Recursive Types

```typescript
// Tree structure
interface Category {
  name: string;
  children: Category[];
}

const CategorySchema: z.ZodType<Category> = z.lazy(() =>
  z.object({
    name: z.string(),
    children: z.array(CategorySchema),
  }),
);

// JSON value
type JsonValue = string | number | boolean | null | JsonValue[] | { [key: string]: JsonValue };

const JsonValueSchema: z.ZodType<JsonValue> = z.lazy(() =>
  z.union([
    z.string(),
    z.number(),
    z.boolean(),
    z.null(),
    z.array(JsonValueSchema),
    z.record(JsonValueSchema),
  ]),
);
```

## Branded Types

```typescript
const UserId = z.string().uuid().brand<"UserId">();
const Email = z.string().email().brand<"Email">();
const PositiveInt = z.number().int().positive().brand<"PositiveInt">();

type UserId = z.infer<typeof UserId>;
type Email = z.infer<typeof Email>;

// Type-safe function signatures
function getUser(id: UserId): Promise<User> { /* ... */ }
function sendEmail(to: Email, subject: string): Promise<void> { /* ... */ }

// Must parse through schema — raw strings won't type-check
const userId = UserId.parse("550e8400-e29b-41d4-a716-446655440000");
getUser(userId); // OK
// getUser("raw-string"); // Type error
```

## Schema Composition

```typescript
// Base schema
const BaseEntity = z.object({
  id: z.string().uuid(),
  createdAt: z.coerce.date(),
  updatedAt: z.coerce.date(),
});

// Extend
const UserSchema = BaseEntity.extend({
  name: z.string().min(1),
  email: z.string().email(),
  role: z.enum(["admin", "user", "editor"]),
});

// Merge two schemas
const ProfileSchema = z.object({ bio: z.string(), avatar: z.string().url() });
const FullUserSchema = UserSchema.merge(ProfileSchema);

// Pick / Omit
const UserCreateSchema = UserSchema.omit({ id: true, createdAt: true, updatedAt: true });
const UserSummarySchema = UserSchema.pick({ id: true, name: true, email: true });

// Partial (all fields optional)
const UserUpdateSchema = UserCreateSchema.partial();
```

## Transform and Pipe

```typescript
// Transform output
const SlugSchema = z.string().transform((val) =>
  val.toLowerCase().replace(/\s+/g, "-").replace(/[^a-z0-9-]/g, ""),
);

// Coercion
const QueryParamsSchema = z.object({
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
  search: z.string().optional(),
  active: z.coerce.boolean().default(true),
});

// Pipe (validate → transform → validate)
const NumberFromString = z
  .string()
  .transform((val) => parseInt(val, 10))
  .pipe(z.number().int().positive());
```

## Custom Error Messages

```typescript
const PasswordSchema = z
  .string()
  .min(8, "Password must be at least 8 characters")
  .regex(/[A-Z]/, "Must contain at least one uppercase letter")
  .regex(/[a-z]/, "Must contain at least one lowercase letter")
  .regex(/[0-9]/, "Must contain at least one number");

const RegisterSchema = z
  .object({
    email: z.string().email("Please enter a valid email"),
    password: PasswordSchema,
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });
```

## API Contract Validation

```typescript
// Request/response schemas
const CreateOrderRequest = z.object({
  items: z.array(z.object({
    productId: z.string().uuid(),
    quantity: z.number().int().positive(),
  })).min(1, "Order must have at least one item"),
  shippingAddress: z.object({
    street: z.string(),
    city: z.string(),
    country: z.string().length(2),
    zip: z.string(),
  }),
});

const CreateOrderResponse = z.object({
  orderId: z.string().uuid(),
  total: z.number(),
  status: z.enum(["pending", "confirmed", "shipped"]),
});

// Use in API handler
async function handleCreateOrder(req: Request) {
  const body = CreateOrderRequest.parse(await req.json());
  const order = await createOrder(body);
  return Response.json(CreateOrderResponse.parse(order));
}
```

## Additional Resources

- Zod docs: https://zod.dev/
- Error handling: https://zod.dev/error-handling
- Ecosystem: https://zod.dev/?id=ecosystem
