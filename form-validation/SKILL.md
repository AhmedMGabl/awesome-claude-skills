---
name: form-validation
description: Form validation patterns covering Zod schema validation, React Hook Form integration, server-side validation, error message display, multi-step form wizards, file upload validation, real-time field validation, and accessible error handling for web applications.
---

# Form Validation

This skill should be used when implementing form validation in web applications. It covers client-side validation with Zod and React Hook Form, server-side validation, and accessible error patterns.

## When to Use This Skill

Use this skill when you need to:

- Validate user input in web forms
- Build multi-step form wizards
- Implement real-time field validation
- Display accessible error messages
- Share validation schemas between client and server

## Zod + React Hook Form

```tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const signupSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Invalid email address"),
  password: z.string()
    .min(8, "Password must be at least 8 characters")
    .regex(/[A-Z]/, "Must contain an uppercase letter")
    .regex(/[0-9]/, "Must contain a number"),
  confirmPassword: z.string(),
  terms: z.literal(true, { errorMap: () => ({ message: "You must accept the terms" }) }),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type SignupForm = z.infer<typeof signupSchema>;

function SignupForm() {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<SignupForm>({
    resolver: zodResolver(signupSchema),
  });

  const onSubmit = async (data: SignupForm) => {
    const res = await fetch("/api/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) { /* handle server errors */ }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <FieldGroup label="Name" error={errors.name?.message}>
        <input {...register("name")} aria-invalid={!!errors.name} />
      </FieldGroup>

      <FieldGroup label="Email" error={errors.email?.message}>
        <input type="email" {...register("email")} aria-invalid={!!errors.email} />
      </FieldGroup>

      <FieldGroup label="Password" error={errors.password?.message}>
        <input type="password" {...register("password")} aria-invalid={!!errors.password} />
      </FieldGroup>

      <FieldGroup label="Confirm Password" error={errors.confirmPassword?.message}>
        <input type="password" {...register("confirmPassword")} />
      </FieldGroup>

      <label>
        <input type="checkbox" {...register("terms")} />
        I accept the terms and conditions
      </label>
      {errors.terms && <p role="alert" className="text-red-500 text-sm">{errors.terms.message}</p>}

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Creating account..." : "Sign Up"}
      </button>
    </form>
  );
}

// Accessible field wrapper
function FieldGroup({ label, error, children }: { label: string; error?: string; children: React.ReactNode }) {
  const id = label.toLowerCase().replace(/\s/g, "-");
  return (
    <div className="mb-4">
      <label htmlFor={id} className="block text-sm font-medium mb-1">{label}</label>
      {children}
      {error && <p id={`${id}-error`} role="alert" className="text-red-500 text-sm mt-1">{error}</p>}
    </div>
  );
}
```

## Server-Side Validation

```typescript
// Share the same Zod schema on server
import { z } from "zod";

const createUserSchema = z.object({
  name: z.string().min(2).max(100),
  email: z.string().email(),
  password: z.string().min(8),
});

// Express route
app.post("/api/signup", async (req, res) => {
  const result = createUserSchema.safeParse(req.body);

  if (!result.success) {
    return res.status(400).json({
      error: "Validation failed",
      details: result.error.flatten().fieldErrors,
    });
  }

  // result.data is fully typed and validated
  await createUser(result.data);
  res.status(201).json({ message: "User created" });
});

// Next.js Server Action
async function signupAction(formData: FormData) {
  "use server";
  const result = createUserSchema.safeParse({
    name: formData.get("name"),
    email: formData.get("email"),
    password: formData.get("password"),
  });

  if (!result.success) {
    return { errors: result.error.flatten().fieldErrors };
  }

  await createUser(result.data);
  redirect("/dashboard");
}
```

## Common Validation Patterns

```typescript
// Reusable field validators
const v = {
  email: z.string().email("Invalid email"),
  phone: z.string().regex(/^\+?[1-9]\d{1,14}$/, "Invalid phone number"),
  url: z.string().url("Invalid URL"),
  slug: z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, "Invalid slug"),
  password: z.string().min(8).regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, "Weak password"),
  date: z.string().datetime({ message: "Invalid date" }),
  price: z.number().positive().multipleOf(0.01),
  fileSize: (maxMB: number) => z.number().max(maxMB * 1024 * 1024, `File must be under ${maxMB}MB`),
};
```

## Additional Resources

- Zod: https://zod.dev/
- React Hook Form: https://react-hook-form.com/
- Conform (progressive enhancement): https://conform.guide/
