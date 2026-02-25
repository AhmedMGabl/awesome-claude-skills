---
name: conform-forms
description: Conform form library patterns covering progressive enhancement, Zod schema validation, server actions, nested objects, field arrays, file uploads, and integration with React/Remix/Next.js for type-safe form handling.
---

# Conform Forms

This skill should be used when building progressively enhanced forms with Conform. It covers validation, server actions, nested fields, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Build forms that work without JavaScript (progressive enhancement)
- Validate forms with Zod schemas on client and server
- Handle server actions with type-safe form data
- Manage nested objects and field arrays
- Integrate with React, Remix, or Next.js

## Basic Form with Next.js

```tsx
// actions.ts
"use server";
import { parseWithZod } from "@conform-to/zod";
import { z } from "zod";

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

export async function login(prevState: unknown, formData: FormData) {
  const submission = parseWithZod(formData, { schema });

  if (submission.status !== "success") {
    return submission.reply();
  }

  // Process login
  const { email, password } = submission.value;
  await authenticate(email, password);
  redirect("/dashboard");
}

// LoginForm.tsx
"use client";
import { useForm } from "@conform-to/react";
import { parseWithZod } from "@conform-to/zod";
import { useActionState } from "react";
import { login } from "./actions";

function LoginForm() {
  const [lastResult, action] = useActionState(login, undefined);
  const [form, fields] = useForm({
    lastResult,
    onValidate({ formData }) {
      return parseWithZod(formData, { schema });
    },
    shouldValidate: "onBlur",
    shouldRevalidate: "onInput",
  });

  return (
    <form id={form.id} onSubmit={form.onSubmit} action={action} noValidate>
      <div>
        <label htmlFor={fields.email.id}>Email</label>
        <input
          id={fields.email.id}
          name={fields.email.name}
          type="email"
          defaultValue={fields.email.initialValue}
          aria-invalid={!fields.email.valid || undefined}
          aria-describedby={fields.email.errorId}
        />
        <p id={fields.email.errorId}>{fields.email.errors}</p>
      </div>
      <div>
        <label htmlFor={fields.password.id}>Password</label>
        <input
          id={fields.password.id}
          name={fields.password.name}
          type="password"
          aria-invalid={!fields.password.valid || undefined}
        />
        <p id={fields.password.errorId}>{fields.password.errors}</p>
      </div>
      <button type="submit">Log in</button>
    </form>
  );
}
```

## Nested Objects

```tsx
const addressSchema = z.object({
  name: z.string().min(1),
  address: z.object({
    street: z.string().min(1),
    city: z.string().min(1),
    zip: z.string().regex(/^\d{5}$/),
  }),
});

function AddressForm() {
  const [form, fields] = useForm({
    onValidate({ formData }) {
      return parseWithZod(formData, { schema: addressSchema });
    },
  });

  const address = fields.address.getFieldset();

  return (
    <form id={form.id} onSubmit={form.onSubmit}>
      <input name={fields.name.name} />
      <input name={address.street.name} placeholder="Street" />
      <input name={address.city.name} placeholder="City" />
      <input name={address.zip.name} placeholder="ZIP" />
      <button type="submit">Save</button>
    </form>
  );
}
```

## Field Arrays

```tsx
import { useForm, useFieldList, insert, remove } from "@conform-to/react";

const schema = z.object({
  title: z.string().min(1),
  items: z.array(
    z.object({
      name: z.string().min(1),
      quantity: z.coerce.number().min(1),
    }),
  ).min(1),
});

function OrderForm() {
  const [form, fields] = useForm({
    onValidate({ formData }) {
      return parseWithZod(formData, { schema });
    },
    defaultValue: {
      items: [{ name: "", quantity: 1 }],
    },
  });

  const items = fields.items.getFieldList();

  return (
    <form id={form.id} onSubmit={form.onSubmit}>
      <input name={fields.title.name} />

      {items.map((item, index) => {
        const itemFields = item.getFieldset();
        return (
          <div key={item.key}>
            <input name={itemFields.name.name} placeholder="Item name" />
            <input name={itemFields.quantity.name} type="number" min="1" />
            <button {...form.remove.getButtonProps({ name: fields.items.name, index })}>
              Remove
            </button>
          </div>
        );
      })}

      <button {...form.insert.getButtonProps({ name: fields.items.name })}>
        Add Item
      </button>
      <button type="submit">Submit Order</button>
    </form>
  );
}
```

## File Uploads

```tsx
const uploadSchema = z.object({
  title: z.string().min(1),
  file: z.instanceof(File).refine((f) => f.size < 5 * 1024 * 1024, "Max 5MB"),
});

function UploadForm() {
  const [form, fields] = useForm({
    onValidate({ formData }) {
      return parseWithZod(formData, { schema: uploadSchema });
    },
  });

  return (
    <form id={form.id} onSubmit={form.onSubmit} encType="multipart/form-data">
      <input name={fields.title.name} />
      <input name={fields.file.name} type="file" accept="image/*" />
      {fields.file.errors && <p>{fields.file.errors}</p>}
      <button type="submit">Upload</button>
    </form>
  );
}
```

## Additional Resources

- Conform docs: https://conform.guide/
- Next.js integration: https://conform.guide/integration/nextjs
- Remix integration: https://conform.guide/integration/remix
