---
name: yup-validation
description: Yup validation patterns covering schema definitions, type coercion, conditional validation, custom tests, error messages, and React Hook Form/Formik integration.
---

# Yup Validation

This skill should be used when validating data with Yup. It covers schemas, coercion, conditional validation, custom tests, and form library integration.

## When to Use This Skill

Use this skill when you need to:

- Define validation schemas with type coercion
- Apply conditional and dependent field validation
- Create custom validation tests
- Integrate with React Hook Form or Formik
- Validate complex nested data structures

## Setup

```bash
npm install yup
# For React Hook Form:
npm install @hookform/resolvers
```

## Basic Schemas

```ts
import * as yup from "yup";

const userSchema = yup.object({
  name: yup.string().required("Name is required").min(2).max(50),
  email: yup.string().required().email("Invalid email"),
  age: yup.number().required().integer().min(18, "Must be 18+"),
  role: yup.string().oneOf(["admin", "user", "editor"]).required(),
  bio: yup.string().max(500).optional(),
  tags: yup.array().of(yup.string().required()).required(),
  isActive: yup.boolean().required(),
});

// Infer TypeScript type
type User = yup.InferType<typeof userSchema>;

// Validate
try {
  const user = await userSchema.validate(data, { abortEarly: false });
  console.log("Valid:", user);
} catch (err) {
  if (err instanceof yup.ValidationError) {
    console.log("Errors:", err.errors);
    console.log("Inner:", err.inner.map((e) => ({ path: e.path, message: e.message })));
  }
}

// Safe validate
const isValid = await userSchema.isValid(data);
```

## Type Coercion

```ts
import * as yup from "yup";

const formSchema = yup.object({
  // String "42" becomes number 42
  quantity: yup.number().required().positive().integer(),

  // String "true" becomes boolean true
  acceptTerms: yup.boolean().required().oneOf([true], "Must accept terms"),

  // String becomes Date
  birthDate: yup.date().required().max(new Date(), "Cannot be in the future"),

  // Trim and lowercase
  email: yup.string().required().email().trim().lowercase(),

  // Strip unknown fields
  name: yup.string().required().trim(),
});

// Cast without validation
const casted = formSchema.cast({ quantity: "42", email: " TEST@EXAMPLE.COM " });
// { quantity: 42, email: "test@example.com", ... }
```

## Conditional Validation

```ts
import * as yup from "yup";

const paymentSchema = yup.object({
  paymentMethod: yup.string().oneOf(["card", "bank", "paypal"]).required(),

  // Required only when paymentMethod is "card"
  cardNumber: yup.string().when("paymentMethod", {
    is: "card",
    then: (schema) => schema.required("Card number required").matches(/^\d{16}$/, "Invalid card"),
    otherwise: (schema) => schema.optional(),
  }),

  // Required for bank transfer
  bankAccount: yup.string().when("paymentMethod", {
    is: "bank",
    then: (schema) => schema.required("Bank account required"),
    otherwise: (schema) => schema.optional(),
  }),

  // Required for PayPal
  paypalEmail: yup.string().when("paymentMethod", {
    is: "paypal",
    then: (schema) => schema.required().email("Invalid PayPal email"),
    otherwise: (schema) => schema.optional(),
  }),
});
```

## Custom Tests

```ts
import * as yup from "yup";

const passwordSchema = yup.string()
  .required("Password required")
  .min(8, "At least 8 characters")
  .test("uppercase", "Must contain uppercase letter", (val) =>
    val ? /[A-Z]/.test(val) : false
  )
  .test("number", "Must contain a number", (val) =>
    val ? /\d/.test(val) : false
  )
  .test("special", "Must contain special character", (val) =>
    val ? /[^a-zA-Z0-9]/.test(val) : false
  );

// Async custom test
const uniqueEmailSchema = yup.string()
  .email()
  .test("unique", "Email already taken", async (email) => {
    if (!email) return true;
    const exists = await checkEmailExists(email);
    return !exists;
  });

// Cross-field validation
const registerSchema = yup.object({
  password: passwordSchema,
  confirmPassword: yup.string()
    .required("Confirm your password")
    .oneOf([yup.ref("password")], "Passwords must match"),
});
```

## React Hook Form Integration

```tsx
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";

const schema = yup.object({
  name: yup.string().required().min(2),
  email: yup.string().required().email(),
});

function SignupForm() {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: yupResolver(schema),
  });

  return (
    <form onSubmit={handleSubmit((data) => console.log(data))}>
      <input {...register("name")} />
      {errors.name && <p>{errors.name.message}</p>}

      <input {...register("email")} />
      {errors.email && <p>{errors.email.message}</p>}

      <button type="submit">Submit</button>
    </form>
  );
}
```

## Additional Resources

- Yup: https://github.com/jquense/yup
- API: https://github.com/jquense/yup#api
- Typescript: https://github.com/jquense/yup#typescript-integration
