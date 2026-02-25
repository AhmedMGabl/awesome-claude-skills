---
name: zod-validation
description: Zod schema validation covering primitive and object schemas, transforms, refinements, discriminated unions, recursive types, error formatting, integration with React Hook Form, tRPC, and Next.js Server Actions, and shared client/server validation.
---

# Zod Validation

This skill should be used when implementing schema validation with Zod. It covers schema definitions, transforms, error handling, and integration with frameworks.

## When to Use This Skill

Use this skill when you need to:

- Validate data at runtime with TypeScript types
- Parse API request/response bodies
- Integrate validation with forms
- Create shared schemas for client and server
- Transform and coerce data during validation

## Schema Definitions

```typescript
import { z } from "zod";

// Primitives
const name = z.string().min(1).max(100);
const age = z.number().int().min(0).max(150);
const email = z.string().email();
const url = z.string().url();
const uuid = z.string().uuid();

// Object schema
const UserSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1, "Name is required"),
  email: z.string().email("Invalid email"),
  age: z.number().int().min(18, "Must be 18+").optional(),
  role: z.enum(["admin", "editor", "viewer"]),
  settings: z
    .object({
      theme: z.enum(["light", "dark"]).default("light"),
      notifications: z.boolean().default(true),
    })
    .default({}),
  createdAt: z.coerce.date(),
});

// Infer TypeScript type
type User = z.infer<typeof UserSchema>;

// Partial, Pick, Omit
const CreateUser = UserSchema.omit({ id: true, createdAt: true });
const UpdateUser = UserSchema.partial().required({ id: true });
```

## Parsing and Error Handling

```typescript
// Safe parse (doesn't throw)
const result = UserSchema.safeParse(data);
if (!result.success) {
  const errors = result.error.flatten();
  // { formErrors: string[], fieldErrors: { name?: string[], email?: string[] } }
  console.log(errors.fieldErrors);
} else {
  const user = result.data; // typed as User
}

// Parse (throws on failure)
try {
  const user = UserSchema.parse(data);
} catch (error) {
  if (error instanceof z.ZodError) {
    const formatted = error.format();
    // { name: { _errors: ["Name is required"] } }
  }
}
```

## Transforms and Refinements

```typescript
// Transform: modify data during parsing
const SlugSchema = z.string().transform((val) => val.toLowerCase().replace(/\s+/g, "-"));

const PriceSchema = z
  .string()
  .transform((val) => parseFloat(val))
  .pipe(z.number().positive());

// Refinement: custom validation
const PasswordSchema = z
  .string()
  .min(8)
  .refine((val) => /[A-Z]/.test(val), "Must contain uppercase")
  .refine((val) => /[0-9]/.test(val), "Must contain a number")
  .refine((val) => /[^a-zA-Z0-9]/.test(val), "Must contain a special character");

// Cross-field validation with superRefine
const SignupSchema = z
  .object({
    password: z.string().min(8),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  });
```

## Discriminated Unions

```typescript
const EventSchema = z.discriminatedUnion("type", [
  z.object({
    type: z.literal("click"),
    x: z.number(),
    y: z.number(),
  }),
  z.object({
    type: z.literal("keypress"),
    key: z.string(),
    modifiers: z.array(z.enum(["ctrl", "shift", "alt"])),
  }),
  z.object({
    type: z.literal("scroll"),
    direction: z.enum(["up", "down"]),
    delta: z.number(),
  }),
]);

type Event = z.infer<typeof EventSchema>;
// Correctly narrows type based on "type" field
```

## React Hook Form Integration

```tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

type FormData = z.infer<typeof schema>;

function LoginForm() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  return (
    <form onSubmit={handleSubmit((data) => console.log(data))}>
      <input {...register("email")} />
      {errors.email && <p>{errors.email.message}</p>}

      <input type="password" {...register("password")} />
      {errors.password && <p>{errors.password.message}</p>}

      <button type="submit">Login</button>
    </form>
  );
}
```

## Server Action Validation

```typescript
// Next.js Server Action
"use server";
import { z } from "zod";

const ContactSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
  message: z.string().min(10).max(1000),
});

export async function submitContact(formData: FormData) {
  const result = ContactSchema.safeParse({
    name: formData.get("name"),
    email: formData.get("email"),
    message: formData.get("message"),
  });

  if (!result.success) {
    return { errors: result.error.flatten().fieldErrors };
  }

  await sendEmail(result.data);
  return { success: true };
}
```

## Additional Resources

- Zod docs: https://zod.dev/
- React Hook Form + Zod: https://react-hook-form.com/get-started#SchemaValidation
- tRPC input validation: https://trpc.io/docs/server/validators
