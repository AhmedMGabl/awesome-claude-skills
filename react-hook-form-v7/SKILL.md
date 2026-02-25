---
name: react-hook-form-v7
description: React Hook Form v7 patterns covering useForm, Controller, Zod/Yup resolvers, nested fields, field arrays, multi-step forms, file uploads, conditional validation, and performance optimization for complex form management.
---

# React Hook Form v7

This skill should be used when building complex forms with React Hook Form v7. It covers registration, validation, field arrays, multi-step forms, and performance optimization.

## When to Use This Skill

Use this skill when you need to:

- Build performant forms with minimal re-renders
- Validate forms with Zod or Yup resolvers
- Manage dynamic field arrays
- Build multi-step wizard forms
- Handle file uploads and conditional validation

## Basic Form with Zod

```tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const schema = z.object({
  name: z.string().min(1, "Name is required"),
  email: z.string().email("Invalid email"),
  age: z.coerce.number().min(18, "Must be 18+"),
  role: z.enum(["admin", "user", "editor"]),
});

type FormData = z.infer<typeof schema>;

function UserForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { name: "", email: "", age: 18, role: "user" },
  });

  const onSubmit = async (data: FormData) => {
    await api.createUser(data);
    reset();
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register("name")} />
      {errors.name && <p>{errors.name.message}</p>}

      <input {...register("email")} />
      {errors.email && <p>{errors.email.message}</p>}

      <input type="number" {...register("age")} />
      {errors.age && <p>{errors.age.message}</p>}

      <select {...register("role")}>
        <option value="user">User</option>
        <option value="admin">Admin</option>
        <option value="editor">Editor</option>
      </select>

      <button disabled={isSubmitting}>
        {isSubmitting ? "Saving..." : "Submit"}
      </button>
    </form>
  );
}
```

## Field Arrays

```tsx
import { useForm, useFieldArray } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const schema = z.object({
  teamName: z.string().min(1),
  members: z
    .array(
      z.object({
        name: z.string().min(1, "Name required"),
        email: z.string().email("Invalid email"),
        role: z.string().min(1),
      }),
    )
    .min(1, "At least one member required"),
});

type FormData = z.infer<typeof schema>;

function TeamForm() {
  const { register, control, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { teamName: "", members: [{ name: "", email: "", role: "" }] },
  });

  const { fields, append, remove, move } = useFieldArray({
    control,
    name: "members",
  });

  return (
    <form onSubmit={handleSubmit(console.log)}>
      <input {...register("teamName")} placeholder="Team name" />

      {fields.map((field, index) => (
        <div key={field.id}>
          <input {...register(`members.${index}.name`)} placeholder="Name" />
          {errors.members?.[index]?.name && (
            <p>{errors.members[index].name.message}</p>
          )}
          <input {...register(`members.${index}.email`)} placeholder="Email" />
          <input {...register(`members.${index}.role`)} placeholder="Role" />
          <button type="button" onClick={() => remove(index)}>Remove</button>
        </div>
      ))}

      <button type="button" onClick={() => append({ name: "", email: "", role: "" })}>
        Add Member
      </button>
      <button type="submit">Submit</button>
    </form>
  );
}
```

## Multi-Step Form

```tsx
import { useForm, FormProvider, useFormContext } from "react-hook-form";
import { useState } from "react";

function MultiStepForm() {
  const [step, setStep] = useState(0);
  const methods = useForm({
    defaultValues: {
      name: "", email: "",
      address: "", city: "", zip: "",
      cardNumber: "", expiry: "",
    },
  });

  const steps = [
    <PersonalInfo key="personal" />,
    <AddressInfo key="address" />,
    <PaymentInfo key="payment" />,
  ];

  const next = async () => {
    const fields = [
      ["name", "email"],
      ["address", "city", "zip"],
      ["cardNumber", "expiry"],
    ][step];
    const valid = await methods.trigger(fields as any);
    if (valid) setStep((s) => s + 1);
  };

  return (
    <FormProvider {...methods}>
      <form onSubmit={methods.handleSubmit(console.log)}>
        {steps[step]}
        <div>
          {step > 0 && <button type="button" onClick={() => setStep((s) => s - 1)}>Back</button>}
          {step < steps.length - 1 ? (
            <button type="button" onClick={next}>Next</button>
          ) : (
            <button type="submit">Submit</button>
          )}
        </div>
      </form>
    </FormProvider>
  );
}

function PersonalInfo() {
  const { register, formState: { errors } } = useFormContext();
  return (
    <div>
      <input {...register("name", { required: "Name required" })} />
      {errors.name && <p>{errors.name.message as string}</p>}
      <input {...register("email", { required: "Email required" })} />
    </div>
  );
}
```

## Controller for UI Libraries

```tsx
import { useForm, Controller } from "react-hook-form";
import { Select, DatePicker, Slider } from "some-ui-library";

function ControlledForm() {
  const { control, handleSubmit } = useForm();

  return (
    <form onSubmit={handleSubmit(console.log)}>
      <Controller
        name="category"
        control={control}
        rules={{ required: "Category required" }}
        render={({ field, fieldState: { error } }) => (
          <>
            <Select {...field} options={["Tech", "Design", "Marketing"]} />
            {error && <p>{error.message}</p>}
          </>
        )}
      />
      <Controller
        name="date"
        control={control}
        render={({ field }) => <DatePicker {...field} />}
      />
    </form>
  );
}
```

## Additional Resources

- React Hook Form docs: https://react-hook-form.com/
- Zod resolver: https://github.com/react-hook-form/resolvers
- Field arrays: https://react-hook-form.com/docs/usefieldarray
