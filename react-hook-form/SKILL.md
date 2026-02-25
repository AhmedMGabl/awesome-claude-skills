---
name: react-hook-form
description: React Hook Form patterns for performant form management covering useForm setup, Zod schema validation with resolvers, field arrays, dynamic forms with watch/setValue/getValues, Controller for controlled UI libraries, multi-step wizard forms, file uploads, error display, and TypeScript integration.
---

# React Hook Form

This skill should be used when building forms in React applications using React Hook Form. It covers form setup, validation with Zod, dynamic fields, controlled components, multi-step wizards, file uploads, error handling, and performance optimization.

## When to Use This Skill

Use this skill when you need to:

- Build performant forms with React Hook Form and TypeScript
- Validate forms using Zod schemas via @hookform/resolvers
- Manage dynamic field arrays with useFieldArray
- Integrate controlled UI component libraries (MUI, Radix, Headless UI)
- Build multi-step wizard forms with step validation
- Handle file uploads within forms
- Display validation errors with accessible patterns
- Optimize form performance and avoid unnecessary re-renders

## Installation

```bash
npm install react-hook-form zod @hookform/resolvers

# For DevTools (development only)
npm install -D @hookform/devtools
```

## Basic Form Setup

### useForm, register, and handleSubmit

```tsx
import { useForm } from "react-hook-form";
import type { SubmitHandler } from "react-hook-form";

interface ContactFormValues {
  firstName: string;
  lastName: string;
  email: string;
  message: string;
}

export function ContactForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<ContactFormValues>({
    defaultValues: {
      firstName: "",
      lastName: "",
      email: "",
      message: "",
    },
  });

  const onSubmit: SubmitHandler<ContactFormValues> = async (data) => {
    await fetch("/api/contact", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    reset();
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <div>
        <label htmlFor="firstName">First Name</label>
        <input
          id="firstName"
          {...register("firstName", {
            required: "First name is required",
            minLength: { value: 2, message: "At least 2 characters" },
          })}
          aria-invalid={errors.firstName ? "true" : "false"}
          aria-describedby={errors.firstName ? "firstName-error" : undefined}
        />
        {errors.firstName && (
          <span id="firstName-error" role="alert">
            {errors.firstName.message}
          </span>
        )}
      </div>

      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          {...register("email", {
            required: "Email is required",
            pattern: {
              value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
              message: "Invalid email address",
            },
          })}
          aria-invalid={errors.email ? "true" : "false"}
        />
        {errors.email && <span role="alert">{errors.email.message}</span>}
      </div>

      <div>
        <label htmlFor="message">Message</label>
        <textarea
          id="message"
          rows={4}
          {...register("message", {
            required: "Message is required",
            maxLength: { value: 500, message: "Maximum 500 characters" },
          })}
        />
        {errors.message && <span role="alert">{errors.message.message}</span>}
      </div>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Sending..." : "Send"}
      </button>
    </form>
  );
}
```

## Zod Schema Validation

### Setup with @hookform/resolvers

```tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const registrationSchema = z
  .object({
    username: z
      .string()
      .min(3, "Username must be at least 3 characters")
      .max(20, "Username must be at most 20 characters")
      .regex(/^[a-zA-Z0-9_]+$/, "Only letters, numbers, and underscores"),
    email: z.string().email("Invalid email address"),
    password: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .regex(/[A-Z]/, "Must contain at least one uppercase letter")
      .regex(/[a-z]/, "Must contain at least one lowercase letter")
      .regex(/[0-9]/, "Must contain at least one number"),
    confirmPassword: z.string(),
    age: z.coerce
      .number({ invalid_type_error: "Age must be a number" })
      .int("Age must be a whole number")
      .min(13, "Must be at least 13 years old")
      .max(120, "Invalid age"),
    role: z.enum(["user", "admin", "moderator"], {
      errorMap: () => ({ message: "Select a valid role" }),
    }),
    acceptTerms: z.literal(true, {
      errorMap: () => ({ message: "Terms must be accepted" }),
    }),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });

// Infer the TypeScript type from the schema
type RegistrationFormValues = z.infer<typeof registrationSchema>;

export function RegistrationForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegistrationFormValues>({
    resolver: zodResolver(registrationSchema),
    defaultValues: {
      username: "",
      email: "",
      password: "",
      confirmPassword: "",
      age: undefined,
      role: "user",
      acceptTerms: false as unknown as true,
    },
  });

  const onSubmit = async (data: RegistrationFormValues) => {
    const response = await fetch("/api/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error("Registration failed");
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <div>
        <label htmlFor="username">Username</label>
        <input id="username" {...register("username")} />
        {errors.username && <span role="alert">{errors.username.message}</span>}
      </div>

      <div>
        <label htmlFor="email">Email</label>
        <input id="email" type="email" {...register("email")} />
        {errors.email && <span role="alert">{errors.email.message}</span>}
      </div>

      <div>
        <label htmlFor="password">Password</label>
        <input id="password" type="password" {...register("password")} />
        {errors.password && <span role="alert">{errors.password.message}</span>}
      </div>

      <div>
        <label htmlFor="confirmPassword">Confirm Password</label>
        <input id="confirmPassword" type="password" {...register("confirmPassword")} />
        {errors.confirmPassword && (
          <span role="alert">{errors.confirmPassword.message}</span>
        )}
      </div>

      <div>
        <label htmlFor="age">Age</label>
        <input id="age" type="number" {...register("age")} />
        {errors.age && <span role="alert">{errors.age.message}</span>}
      </div>

      <div>
        <label htmlFor="role">Role</label>
        <select id="role" {...register("role")}>
          <option value="user">User</option>
          <option value="admin">Admin</option>
          <option value="moderator">Moderator</option>
        </select>
        {errors.role && <span role="alert">{errors.role.message}</span>}
      </div>

      <div>
        <label>
          <input type="checkbox" {...register("acceptTerms")} />
          Accept Terms and Conditions
        </label>
        {errors.acceptTerms && <span role="alert">{errors.acceptTerms.message}</span>}
      </div>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Registering..." : "Register"}
      </button>
    </form>
  );
}
```

### Async Validation with Zod

```tsx
const usernameSchema = z.object({
  username: z
    .string()
    .min(3)
    .refine(
      async (username) => {
        const res = await fetch(`/api/check-username?username=${username}`);
        const { available } = await res.json();
        return available;
      },
      { message: "Username is already taken" }
    ),
});
```

### Conditional Schema Validation

```tsx
const orderSchema = z.discriminatedUnion("shippingMethod", [
  z.object({
    shippingMethod: z.literal("delivery"),
    address: z.string().min(1, "Address is required for delivery"),
    city: z.string().min(1, "City is required"),
    zipCode: z.string().regex(/^\d{5}(-\d{4})?$/, "Invalid ZIP code"),
  }),
  z.object({
    shippingMethod: z.literal("pickup"),
    pickupLocation: z.string().min(1, "Select a pickup location"),
  }),
]);
```

## Field Arrays with useFieldArray

### Dynamic Repeatable Fields

```tsx
import { useForm, useFieldArray } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const invoiceSchema = z.object({
  clientName: z.string().min(1, "Client name is required"),
  items: z
    .array(
      z.object({
        description: z.string().min(1, "Description is required"),
        quantity: z.coerce.number().min(1, "Minimum quantity is 1"),
        unitPrice: z.coerce.number().min(0.01, "Price must be positive"),
      })
    )
    .min(1, "At least one item is required"),
});

type InvoiceFormValues = z.infer<typeof invoiceSchema>;

export function InvoiceForm() {
  const {
    register,
    control,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<InvoiceFormValues>({
    resolver: zodResolver(invoiceSchema),
    defaultValues: {
      clientName: "",
      items: [{ description: "", quantity: 1, unitPrice: 0 }],
    },
  });

  const { fields, append, remove, move, swap } = useFieldArray({
    control,
    name: "items",
  });

  const watchItems = watch("items");

  const total = watchItems.reduce(
    (sum, item) => sum + (item.quantity || 0) * (item.unitPrice || 0),
    0
  );

  const onSubmit = async (data: InvoiceFormValues) => {
    await fetch("/api/invoices", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...data, total }),
    });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <label htmlFor="clientName">Client Name</label>
        <input id="clientName" {...register("clientName")} />
        {errors.clientName && <span role="alert">{errors.clientName.message}</span>}
      </div>

      <h3>Line Items</h3>
      {fields.map((field, index) => (
        <fieldset key={field.id}>
          <legend>Item {index + 1}</legend>

          <div>
            <label htmlFor={`items.${index}.description`}>Description</label>
            <input
              id={`items.${index}.description`}
              {...register(`items.${index}.description`)}
            />
            {errors.items?.[index]?.description && (
              <span role="alert">{errors.items[index].description.message}</span>
            )}
          </div>

          <div>
            <label htmlFor={`items.${index}.quantity`}>Qty</label>
            <input
              id={`items.${index}.quantity`}
              type="number"
              {...register(`items.${index}.quantity`)}
            />
            {errors.items?.[index]?.quantity && (
              <span role="alert">{errors.items[index].quantity.message}</span>
            )}
          </div>

          <div>
            <label htmlFor={`items.${index}.unitPrice`}>Unit Price</label>
            <input
              id={`items.${index}.unitPrice`}
              type="number"
              step="0.01"
              {...register(`items.${index}.unitPrice`)}
            />
            {errors.items?.[index]?.unitPrice && (
              <span role="alert">{errors.items[index].unitPrice.message}</span>
            )}
          </div>

          <div>
            Subtotal: ${((watchItems[index]?.quantity || 0) * (watchItems[index]?.unitPrice || 0)).toFixed(2)}
          </div>

          <button type="button" onClick={() => remove(index)} disabled={fields.length === 1}>
            Remove
          </button>
          {index > 0 && (
            <button type="button" onClick={() => move(index, index - 1)}>
              Move Up
            </button>
          )}
        </fieldset>
      ))}

      <button type="button" onClick={() => append({ description: "", quantity: 1, unitPrice: 0 })}>
        Add Item
      </button>

      {errors.items?.root && <span role="alert">{errors.items.root.message}</span>}

      <div>
        <strong>Total: ${total.toFixed(2)}</strong>
      </div>

      <button type="submit">Create Invoice</button>
    </form>
  );
}
```

### Nested Field Arrays

```tsx
const surveySchema = z.object({
  title: z.string().min(1),
  sections: z.array(
    z.object({
      sectionTitle: z.string().min(1),
      questions: z.array(
        z.object({
          text: z.string().min(1),
          type: z.enum(["text", "multiple_choice", "rating"]),
          required: z.boolean(),
        })
      ).min(1),
    })
  ).min(1),
});

type SurveyFormValues = z.infer<typeof surveySchema>;

function SurveyBuilder() {
  const { register, control, handleSubmit } = useForm<SurveyFormValues>({
    resolver: zodResolver(surveySchema),
    defaultValues: {
      title: "",
      sections: [{ sectionTitle: "", questions: [{ text: "", type: "text", required: false }] }],
    },
  });

  const { fields: sections, append: appendSection, remove: removeSection } = useFieldArray({
    control,
    name: "sections",
  });

  return (
    <form onSubmit={handleSubmit((data) => console.log(data))}>
      <input {...register("title")} placeholder="Survey Title" />

      {sections.map((section, sectionIndex) => (
        <SectionFields
          key={section.id}
          sectionIndex={sectionIndex}
          control={control}
          register={register}
          onRemove={() => removeSection(sectionIndex)}
        />
      ))}

      <button
        type="button"
        onClick={() =>
          appendSection({
            sectionTitle: "",
            questions: [{ text: "", type: "text", required: false }],
          })
        }
      >
        Add Section
      </button>

      <button type="submit">Save Survey</button>
    </form>
  );
}

function SectionFields({
  sectionIndex,
  control,
  register,
  onRemove,
}: {
  sectionIndex: number;
  control: any;
  register: any;
  onRemove: () => void;
}) {
  const { fields, append, remove } = useFieldArray({
    control,
    name: `sections.${sectionIndex}.questions`,
  });

  return (
    <fieldset>
      <input {...register(`sections.${sectionIndex}.sectionTitle`)} placeholder="Section Title" />

      {fields.map((field, questionIndex) => (
        <div key={field.id}>
          <input
            {...register(`sections.${sectionIndex}.questions.${questionIndex}.text`)}
            placeholder="Question text"
          />
          <select
            {...register(`sections.${sectionIndex}.questions.${questionIndex}.type`)}
          >
            <option value="text">Text</option>
            <option value="multiple_choice">Multiple Choice</option>
            <option value="rating">Rating</option>
          </select>
          <label>
            <input
              type="checkbox"
              {...register(`sections.${sectionIndex}.questions.${questionIndex}.required`)}
            />
            Required
          </label>
          <button type="button" onClick={() => remove(questionIndex)}>
            Remove Question
          </button>
        </div>
      ))}

      <button
        type="button"
        onClick={() => append({ text: "", type: "text", required: false })}
      >
        Add Question
      </button>
      <button type="button" onClick={onRemove}>
        Remove Section
      </button>
    </fieldset>
  );
}
```

## Dynamic Forms with watch, setValue, getValues

### watch for Reactive Field Dependencies

```tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const productSchema = z.object({
  category: z.enum(["electronics", "clothing", "food"]),
  subcategory: z.string().min(1, "Subcategory is required"),
  price: z.coerce.number().min(0),
  taxRate: z.coerce.number().min(0).max(100),
  quantity: z.coerce.number().int().min(1),
});

type ProductFormValues = z.infer<typeof productSchema>;

const subcategoryOptions: Record<string, string[]> = {
  electronics: ["Phones", "Laptops", "Tablets", "Accessories"],
  clothing: ["Shirts", "Pants", "Shoes", "Outerwear"],
  food: ["Fresh", "Frozen", "Canned", "Snacks"],
};

export function ProductForm() {
  const { register, handleSubmit, watch, setValue, getValues, formState: { errors } } =
    useForm<ProductFormValues>({
      resolver: zodResolver(productSchema),
      defaultValues: {
        category: "electronics",
        subcategory: "",
        price: 0,
        taxRate: 10,
        quantity: 1,
      },
    });

  // Watch specific fields for reactive updates
  const category = watch("category");
  const price = watch("price");
  const taxRate = watch("taxRate");
  const quantity = watch("quantity");

  // Computed values
  const subtotal = price * quantity;
  const tax = subtotal * (taxRate / 100);
  const total = subtotal + tax;

  // Reset subcategory when category changes
  useEffect(() => {
    setValue("subcategory", "", { shouldValidate: false });
  }, [category, setValue]);

  const onSubmit = (data: ProductFormValues) => {
    console.log({ ...data, subtotal, tax, total });
  };

  // Programmatic access with getValues
  const handleDuplicate = () => {
    const currentValues = getValues();
    console.log("Duplicating product:", currentValues);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <label htmlFor="category">Category</label>
        <select id="category" {...register("category")}>
          <option value="electronics">Electronics</option>
          <option value="clothing">Clothing</option>
          <option value="food">Food</option>
        </select>
      </div>

      <div>
        <label htmlFor="subcategory">Subcategory</label>
        <select id="subcategory" {...register("subcategory")}>
          <option value="">Select...</option>
          {subcategoryOptions[category]?.map((sub) => (
            <option key={sub} value={sub}>
              {sub}
            </option>
          ))}
        </select>
        {errors.subcategory && <span role="alert">{errors.subcategory.message}</span>}
      </div>

      <div>
        <label htmlFor="price">Price</label>
        <input id="price" type="number" step="0.01" {...register("price")} />
      </div>

      <div>
        <label htmlFor="quantity">Quantity</label>
        <input id="quantity" type="number" {...register("quantity")} />
      </div>

      <div>
        <label htmlFor="taxRate">Tax Rate (%)</label>
        <input id="taxRate" type="number" step="0.1" {...register("taxRate")} />
      </div>

      <div aria-live="polite">
        <p>Subtotal: ${subtotal.toFixed(2)}</p>
        <p>Tax: ${tax.toFixed(2)}</p>
        <p><strong>Total: ${total.toFixed(2)}</strong></p>
      </div>

      <button type="button" onClick={handleDuplicate}>
        Duplicate
      </button>
      <button type="submit">Save Product</button>
    </form>
  );
}
```

### setValue for Programmatic Updates

```tsx
// Auto-fill from API lookup
async function handleZipCodeLookup() {
  const zip = getValues("zipCode");
  if (zip.length === 5) {
    const res = await fetch(`/api/zip/${zip}`);
    const data = await res.json();
    setValue("city", data.city, { shouldValidate: true, shouldDirty: true });
    setValue("state", data.state, { shouldValidate: true, shouldDirty: true });
  }
}

// Bulk update from template
function applyTemplate(template: Partial<ProductFormValues>) {
  Object.entries(template).forEach(([key, value]) => {
    setValue(key as keyof ProductFormValues, value, {
      shouldValidate: true,
      shouldDirty: true,
    });
  });
}
```

## Controller Component for Controlled Inputs

### Material UI Integration

```tsx
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  FormHelperText,
  Autocomplete,
  Switch,
  FormControlLabel,
  Slider,
  Rating,
} from "@mui/material";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";

const eventSchema = z.object({
  title: z.string().min(1, "Title is required"),
  description: z.string().max(500).optional(),
  category: z.enum(["conference", "workshop", "meetup"]),
  date: z.date({ required_error: "Date is required" }),
  tags: z.array(z.string()).min(1, "At least one tag is required"),
  isPublic: z.boolean(),
  maxAttendees: z.number().min(1).max(1000),
  rating: z.number().min(1).max(5).optional(),
});

type EventFormValues = z.infer<typeof eventSchema>;

const availableTags = ["React", "TypeScript", "Node.js", "GraphQL", "Testing", "DevOps"];

export function EventForm() {
  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<EventFormValues>({
    resolver: zodResolver(eventSchema),
    defaultValues: {
      title: "",
      description: "",
      category: "conference",
      date: undefined,
      tags: [],
      isPublic: true,
      maxAttendees: 50,
      rating: undefined,
    },
  });

  return (
    <form onSubmit={handleSubmit((data) => console.log(data))}>
      {/* TextField */}
      <Controller
        name="title"
        control={control}
        render={({ field, fieldState: { error } }) => (
          <TextField
            {...field}
            label="Event Title"
            error={!!error}
            helperText={error?.message}
            fullWidth
            margin="normal"
          />
        )}
      />

      {/* Select */}
      <Controller
        name="category"
        control={control}
        render={({ field, fieldState: { error } }) => (
          <FormControl fullWidth margin="normal" error={!!error}>
            <InputLabel>Category</InputLabel>
            <Select {...field} label="Category">
              <MenuItem value="conference">Conference</MenuItem>
              <MenuItem value="workshop">Workshop</MenuItem>
              <MenuItem value="meetup">Meetup</MenuItem>
            </Select>
            {error && <FormHelperText>{error.message}</FormHelperText>}
          </FormControl>
        )}
      />

      {/* DatePicker */}
      <Controller
        name="date"
        control={control}
        render={({ field, fieldState: { error } }) => (
          <DatePicker
            label="Event Date"
            value={field.value ?? null}
            onChange={field.onChange}
            slotProps={{
              textField: {
                error: !!error,
                helperText: error?.message,
                fullWidth: true,
                margin: "normal",
              },
            }}
          />
        )}
      />

      {/* Autocomplete (multi-select) */}
      <Controller
        name="tags"
        control={control}
        render={({ field: { onChange, value, ref }, fieldState: { error } }) => (
          <Autocomplete
            multiple
            options={availableTags}
            value={value}
            onChange={(_, newValue) => onChange(newValue)}
            renderInput={(params) => (
              <TextField
                {...params}
                inputRef={ref}
                label="Tags"
                error={!!error}
                helperText={error?.message}
                margin="normal"
              />
            )}
          />
        )}
      />

      {/* Switch */}
      <Controller
        name="isPublic"
        control={control}
        render={({ field }) => (
          <FormControlLabel
            control={<Switch {...field} checked={field.value} />}
            label="Public Event"
          />
        )}
      />

      {/* Slider */}
      <Controller
        name="maxAttendees"
        control={control}
        render={({ field }) => (
          <div>
            <label>Max Attendees: {field.value}</label>
            <Slider
              {...field}
              min={1}
              max={1000}
              onChange={(_, value) => field.onChange(value)}
              valueLabelDisplay="auto"
            />
          </div>
        )}
      />

      {/* Rating */}
      <Controller
        name="rating"
        control={control}
        render={({ field }) => (
          <div>
            <label>Rating</label>
            <Rating
              value={field.value ?? null}
              onChange={(_, value) => field.onChange(value)}
            />
          </div>
        )}
      />

      <button type="submit">Create Event</button>
    </form>
  );
}
```

### Radix UI Integration

```tsx
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import * as Select from "@radix-ui/react-select";
import * as Checkbox from "@radix-ui/react-checkbox";
import * as RadioGroup from "@radix-ui/react-radio-group";
import * as Switch from "@radix-ui/react-switch";

const preferencesSchema = z.object({
  theme: z.enum(["light", "dark", "system"]),
  language: z.string().min(1),
  notifications: z.boolean(),
  fontSize: z.enum(["small", "medium", "large"]),
});

type PreferencesFormValues = z.infer<typeof preferencesSchema>;

export function PreferencesForm() {
  const { control, handleSubmit } = useForm<PreferencesFormValues>({
    resolver: zodResolver(preferencesSchema),
    defaultValues: {
      theme: "system",
      language: "en",
      notifications: true,
      fontSize: "medium",
    },
  });

  return (
    <form onSubmit={handleSubmit((data) => console.log(data))}>
      {/* Radix Select */}
      <Controller
        name="language"
        control={control}
        render={({ field }) => (
          <Select.Root value={field.value} onValueChange={field.onChange}>
            <Select.Trigger ref={field.ref}>
              <Select.Value placeholder="Select language" />
            </Select.Trigger>
            <Select.Content>
              <Select.Item value="en">English</Select.Item>
              <Select.Item value="es">Spanish</Select.Item>
              <Select.Item value="fr">French</Select.Item>
            </Select.Content>
          </Select.Root>
        )}
      />

      {/* Radix Switch */}
      <Controller
        name="notifications"
        control={control}
        render={({ field }) => (
          <label>
            <Switch.Root
              checked={field.value}
              onCheckedChange={field.onChange}
              ref={field.ref}
            >
              <Switch.Thumb />
            </Switch.Root>
            Enable Notifications
          </label>
        )}
      />

      {/* Radix RadioGroup */}
      <Controller
        name="fontSize"
        control={control}
        render={({ field }) => (
          <RadioGroup.Root value={field.value} onValueChange={field.onChange}>
            <div>
              <RadioGroup.Item value="small" id="small">
                <RadioGroup.Indicator />
              </RadioGroup.Item>
              <label htmlFor="small">Small</label>
            </div>
            <div>
              <RadioGroup.Item value="medium" id="medium">
                <RadioGroup.Indicator />
              </RadioGroup.Item>
              <label htmlFor="medium">Medium</label>
            </div>
            <div>
              <RadioGroup.Item value="large" id="large">
                <RadioGroup.Indicator />
              </RadioGroup.Item>
              <label htmlFor="large">Large</label>
            </div>
          </RadioGroup.Root>
        )}
      />

      <button type="submit">Save Preferences</button>
    </form>
  );
}
```

## Multi-Step Wizard Forms

### Step-by-Step Form with Per-Step Validation

```tsx
import { useForm, FormProvider, useFormContext } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useState } from "react";

// Define schemas for each step
const personalInfoSchema = z.object({
  firstName: z.string().min(1, "First name is required"),
  lastName: z.string().min(1, "Last name is required"),
  email: z.string().email("Invalid email"),
  phone: z.string().regex(/^\+?[\d\s-()]+$/, "Invalid phone number").optional().or(z.literal("")),
});

const addressSchema = z.object({
  street: z.string().min(1, "Street is required"),
  city: z.string().min(1, "City is required"),
  state: z.string().min(1, "State is required"),
  zipCode: z.string().regex(/^\d{5}(-\d{4})?$/, "Invalid ZIP code"),
  country: z.string().min(1, "Country is required"),
});

const paymentSchema = z.object({
  cardNumber: z.string().regex(/^\d{16}$/, "Card number must be 16 digits"),
  expiryDate: z.string().regex(/^(0[1-9]|1[0-2])\/\d{2}$/, "Format: MM/YY"),
  cvv: z.string().regex(/^\d{3,4}$/, "CVV must be 3 or 4 digits"),
  nameOnCard: z.string().min(1, "Name on card is required"),
});

// Combined schema for the full form
const checkoutSchema = personalInfoSchema.merge(addressSchema).merge(paymentSchema);

type CheckoutFormValues = z.infer<typeof checkoutSchema>;

// Per-step validation schemas
const stepSchemas = [personalInfoSchema, addressSchema, paymentSchema];

// Fields belonging to each step (for trigger validation)
const stepFields: (keyof CheckoutFormValues)[][] = [
  ["firstName", "lastName", "email", "phone"],
  ["street", "city", "state", "zipCode", "country"],
  ["cardNumber", "expiryDate", "cvv", "nameOnCard"],
];

const stepTitles = ["Personal Info", "Address", "Payment"];

export function CheckoutWizard() {
  const [currentStep, setCurrentStep] = useState(0);

  const methods = useForm<CheckoutFormValues>({
    resolver: zodResolver(checkoutSchema),
    defaultValues: {
      firstName: "",
      lastName: "",
      email: "",
      phone: "",
      street: "",
      city: "",
      state: "",
      zipCode: "",
      country: "",
      cardNumber: "",
      expiryDate: "",
      cvv: "",
      nameOnCard: "",
    },
    mode: "onTouched",
  });

  const { trigger, handleSubmit, formState: { isSubmitting } } = methods;

  const goToNext = async () => {
    const fieldsToValidate = stepFields[currentStep];
    const isValid = await trigger(fieldsToValidate);
    if (isValid) setCurrentStep((prev) => Math.min(prev + 1, stepSchemas.length - 1));
  };

  const goToPrevious = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 0));
  };

  const onSubmit = async (data: CheckoutFormValues) => {
    await fetch("/api/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
  };

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmit)}>
        {/* Step Indicator */}
        <nav aria-label="Checkout progress">
          <ol>
            {stepTitles.map((title, index) => (
              <li
                key={title}
                aria-current={index === currentStep ? "step" : undefined}
                className={index <= currentStep ? "active" : ""}
              >
                {title}
              </li>
            ))}
          </ol>
        </nav>

        {/* Step Content */}
        {currentStep === 0 && <PersonalInfoStep />}
        {currentStep === 1 && <AddressStep />}
        {currentStep === 2 && <PaymentStep />}

        {/* Navigation */}
        <div>
          {currentStep > 0 && (
            <button type="button" onClick={goToPrevious}>
              Back
            </button>
          )}
          {currentStep < stepSchemas.length - 1 ? (
            <button type="button" onClick={goToNext}>
              Next
            </button>
          ) : (
            <button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Processing..." : "Place Order"}
            </button>
          )}
        </div>
      </form>
    </FormProvider>
  );
}

// Step components use useFormContext to access form methods
function PersonalInfoStep() {
  const { register, formState: { errors } } = useFormContext<CheckoutFormValues>();

  return (
    <fieldset>
      <legend>Personal Information</legend>
      <div>
        <label htmlFor="firstName">First Name</label>
        <input id="firstName" {...register("firstName")} />
        {errors.firstName && <span role="alert">{errors.firstName.message}</span>}
      </div>
      <div>
        <label htmlFor="lastName">Last Name</label>
        <input id="lastName" {...register("lastName")} />
        {errors.lastName && <span role="alert">{errors.lastName.message}</span>}
      </div>
      <div>
        <label htmlFor="email">Email</label>
        <input id="email" type="email" {...register("email")} />
        {errors.email && <span role="alert">{errors.email.message}</span>}
      </div>
      <div>
        <label htmlFor="phone">Phone (optional)</label>
        <input id="phone" type="tel" {...register("phone")} />
        {errors.phone && <span role="alert">{errors.phone.message}</span>}
      </div>
    </fieldset>
  );
}

function AddressStep() {
  const { register, formState: { errors } } = useFormContext<CheckoutFormValues>();

  return (
    <fieldset>
      <legend>Shipping Address</legend>
      <div>
        <label htmlFor="street">Street</label>
        <input id="street" {...register("street")} />
        {errors.street && <span role="alert">{errors.street.message}</span>}
      </div>
      <div>
        <label htmlFor="city">City</label>
        <input id="city" {...register("city")} />
        {errors.city && <span role="alert">{errors.city.message}</span>}
      </div>
      <div>
        <label htmlFor="state">State</label>
        <input id="state" {...register("state")} />
        {errors.state && <span role="alert">{errors.state.message}</span>}
      </div>
      <div>
        <label htmlFor="zipCode">ZIP Code</label>
        <input id="zipCode" {...register("zipCode")} />
        {errors.zipCode && <span role="alert">{errors.zipCode.message}</span>}
      </div>
      <div>
        <label htmlFor="country">Country</label>
        <input id="country" {...register("country")} />
        {errors.country && <span role="alert">{errors.country.message}</span>}
      </div>
    </fieldset>
  );
}

function PaymentStep() {
  const { register, formState: { errors } } = useFormContext<CheckoutFormValues>();

  return (
    <fieldset>
      <legend>Payment Details</legend>
      <div>
        <label htmlFor="cardNumber">Card Number</label>
        <input id="cardNumber" {...register("cardNumber")} />
        {errors.cardNumber && <span role="alert">{errors.cardNumber.message}</span>}
      </div>
      <div>
        <label htmlFor="expiryDate">Expiry Date</label>
        <input id="expiryDate" placeholder="MM/YY" {...register("expiryDate")} />
        {errors.expiryDate && <span role="alert">{errors.expiryDate.message}</span>}
      </div>
      <div>
        <label htmlFor="cvv">CVV</label>
        <input id="cvv" type="password" {...register("cvv")} />
        {errors.cvv && <span role="alert">{errors.cvv.message}</span>}
      </div>
      <div>
        <label htmlFor="nameOnCard">Name on Card</label>
        <input id="nameOnCard" {...register("nameOnCard")} />
        {errors.nameOnCard && <span role="alert">{errors.nameOnCard.message}</span>}
      </div>
    </fieldset>
  );
}
```

## File Upload Handling

### Single and Multiple File Uploads

```tsx
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useCallback, useState } from "react";

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const ACCEPTED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp", "image/gif"];

const uploadSchema = z.object({
  title: z.string().min(1, "Title is required"),
  avatar: z
    .instanceof(FileList)
    .refine((files) => files.length === 1, "Avatar is required")
    .refine((files) => files[0]?.size <= MAX_FILE_SIZE, "Max file size is 5MB")
    .refine(
      (files) => ACCEPTED_IMAGE_TYPES.includes(files[0]?.type),
      "Only .jpg, .png, .webp, and .gif are accepted"
    ),
  documents: z
    .instanceof(FileList)
    .refine((files) => files.length >= 1, "At least one document is required")
    .refine((files) => files.length <= 5, "Maximum 5 documents")
    .refine(
      (files) => Array.from(files).every((file) => file.size <= MAX_FILE_SIZE),
      "Each file must be under 5MB"
    ),
});

type UploadFormValues = z.infer<typeof uploadSchema>;

export function FileUploadForm() {
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
  } = useForm<UploadFormValues>({
    resolver: zodResolver(uploadSchema),
  });

  const avatarFile = watch("avatar");

  // Generate preview when avatar changes
  useEffect(() => {
    if (avatarFile?.length) {
      const url = URL.createObjectURL(avatarFile[0]);
      setAvatarPreview(url);
      return () => URL.revokeObjectURL(url);
    }
    setAvatarPreview(null);
  }, [avatarFile]);

  const onSubmit = async (data: UploadFormValues) => {
    const formData = new FormData();
    formData.append("title", data.title);
    formData.append("avatar", data.avatar[0]);
    Array.from(data.documents).forEach((file) => {
      formData.append("documents", file);
    });

    await fetch("/api/upload", { method: "POST", body: formData });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <label htmlFor="title">Title</label>
        <input id="title" {...register("title")} />
        {errors.title && <span role="alert">{errors.title.message}</span>}
      </div>

      <div>
        <label htmlFor="avatar">Avatar</label>
        <input
          id="avatar"
          type="file"
          accept={ACCEPTED_IMAGE_TYPES.join(",")}
          {...register("avatar")}
        />
        {avatarPreview && (
          <img src={avatarPreview} alt="Avatar preview" width={100} height={100} />
        )}
        {errors.avatar && <span role="alert">{errors.avatar.message}</span>}
      </div>

      <div>
        <label htmlFor="documents">Documents (up to 5)</label>
        <input
          id="documents"
          type="file"
          multiple
          {...register("documents")}
        />
        {errors.documents && <span role="alert">{errors.documents.message}</span>}
      </div>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Uploading..." : "Upload"}
      </button>
    </form>
  );
}
```

### Drag-and-Drop File Upload with Controller

```tsx
import { useForm, Controller } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useCallback, useState } from "react";

const dropzoneSchema = z.object({
  files: z
    .array(z.instanceof(File))
    .min(1, "At least one file is required")
    .max(10, "Maximum 10 files")
    .refine(
      (files) => files.every((f) => f.size <= 10 * 1024 * 1024),
      "Each file must be under 10MB"
    ),
});

type DropzoneFormValues = z.infer<typeof dropzoneSchema>;

export function DragDropUploadForm() {
  const { control, handleSubmit, formState: { errors } } = useForm<DropzoneFormValues>({
    resolver: zodResolver(dropzoneSchema),
    defaultValues: { files: [] },
  });

  return (
    <form onSubmit={handleSubmit((data) => console.log(data))}>
      <Controller
        name="files"
        control={control}
        render={({ field: { onChange, value } }) => (
          <DropZone files={value} onChange={onChange} />
        )}
      />
      {errors.files && <span role="alert">{errors.files.message}</span>}
      <button type="submit">Upload</button>
    </form>
  );
}

function DropZone({
  files,
  onChange,
}: {
  files: File[];
  onChange: (files: File[]) => void;
}) {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      const droppedFiles = Array.from(e.dataTransfer.files);
      onChange([...files, ...droppedFiles]);
    },
    [files, onChange]
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files) {
        onChange([...files, ...Array.from(e.target.files)]);
      }
    },
    [files, onChange]
  );

  const removeFile = useCallback(
    (index: number) => {
      onChange(files.filter((_, i) => i !== index));
    },
    [files, onChange]
  );

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragOver(true);
      }}
      onDragLeave={() => setIsDragOver(false)}
      onDrop={handleDrop}
      style={{
        border: `2px dashed ${isDragOver ? "#2196f3" : "#ccc"}`,
        padding: "2rem",
        textAlign: "center",
        borderRadius: "8px",
        backgroundColor: isDragOver ? "#e3f2fd" : "transparent",
      }}
    >
      <p>Drag files here or click to browse</p>
      <input type="file" multiple onChange={handleFileInput} style={{ display: "none" }} id="file-input" />
      <label htmlFor="file-input" style={{ cursor: "pointer", color: "#2196f3" }}>
        Browse Files
      </label>

      {files.length > 0 && (
        <ul>
          {files.map((file, index) => (
            <li key={`${file.name}-${index}`}>
              {file.name} ({(file.size / 1024).toFixed(1)} KB)
              <button type="button" onClick={() => removeFile(index)}>
                Remove
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

## Error Display Patterns

### Reusable Error Message Component

```tsx
import { type FieldError } from "react-hook-form";

interface FieldErrorMessageProps {
  error?: FieldError;
  id?: string;
}

export function FieldErrorMessage({ error, id }: FieldErrorMessageProps) {
  if (!error) return null;

  return (
    <p id={id} role="alert" className="field-error" aria-live="polite">
      {error.message}
    </p>
  );
}
```

### Form-Level Error Summary

```tsx
import { type FieldErrors } from "react-hook-form";

interface ErrorSummaryProps {
  errors: FieldErrors;
}

export function ErrorSummary({ errors }: ErrorSummaryProps) {
  const errorEntries = Object.entries(errors);
  if (errorEntries.length === 0) return null;

  return (
    <div role="alert" aria-label="Form errors" className="error-summary">
      <h4>Please fix the following errors:</h4>
      <ul>
        {errorEntries.map(([field, error]) => (
          <li key={field}>
            <a href={`#${field}`} onClick={() => document.getElementById(field)?.focus()}>
              {error?.message as string}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}

// Usage in a form
function MyForm() {
  const { register, handleSubmit, formState: { errors } } = useForm();

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <ErrorSummary errors={errors} />
      {/* ...fields */}
    </form>
  );
}
```

### Server-Side Error Integration

```tsx
import { useForm } from "react-hook-form";

interface ApiValidationError {
  field: string;
  message: string;
}

export function FormWithServerErrors() {
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<{ email: string; username: string }>();

  const onSubmit = async (data: { email: string; username: string }) => {
    try {
      const res = await fetch("/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!res.ok) {
        const { errors: serverErrors } = (await res.json()) as {
          errors: ApiValidationError[];
        };

        // Map server errors to form fields
        serverErrors.forEach(({ field, message }) => {
          setError(field as "email" | "username", {
            type: "server",
            message,
          });
        });

        // For non-field-specific errors, use root
        setError("root", {
          type: "server",
          message: "Registration failed. Please try again.",
        });
        return;
      }

      // Handle success
    } catch {
      setError("root", {
        type: "server",
        message: "Network error. Please check your connection.",
      });
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {errors.root && (
        <div role="alert" className="form-error">
          {errors.root.message}
        </div>
      )}

      <div>
        <input {...register("email")} />
        {errors.email && <span role="alert">{errors.email.message}</span>}
      </div>

      <div>
        <input {...register("username")} />
        {errors.username && <span role="alert">{errors.username.message}</span>}
      </div>

      <button type="submit">Register</button>
    </form>
  );
}
```

## TypeScript Integration

### Strongly Typed Form Hook

```tsx
import { useForm, type DefaultValues, type Path, type SubmitHandler } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { type ZodSchema, type z } from "zod";

// Generic form hook that wraps useForm with Zod
function useZodForm<T extends ZodSchema>(
  schema: T,
  defaultValues: DefaultValues<z.infer<T>>
) {
  return useForm<z.infer<T>>({
    resolver: zodResolver(schema),
    defaultValues,
  });
}

// Usage
const userSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
});

function UserForm() {
  const { register, handleSubmit } = useZodForm(userSchema, {
    name: "",
    email: "",
  });

  // data is fully typed as { name: string; email: string }
  const onSubmit: SubmitHandler<z.infer<typeof userSchema>> = (data) => {
    console.log(data.name, data.email);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register("name")} />
      <input {...register("email")} />
      <button type="submit">Submit</button>
    </form>
  );
}
```

### Typed Form Field Component

```tsx
import { type Control, type FieldValues, type Path, Controller } from "react-hook-form";

interface FormFieldProps<T extends FieldValues> {
  name: Path<T>;
  control: Control<T>;
  label: string;
  type?: "text" | "email" | "password" | "number" | "tel";
  placeholder?: string;
}

export function FormField<T extends FieldValues>({
  name,
  control,
  label,
  type = "text",
  placeholder,
}: FormFieldProps<T>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState: { error } }) => (
        <div>
          <label htmlFor={name}>{label}</label>
          <input
            {...field}
            id={name}
            type={type}
            placeholder={placeholder}
            aria-invalid={error ? "true" : "false"}
            aria-describedby={error ? `${name}-error` : undefined}
          />
          {error && (
            <span id={`${name}-error`} role="alert">
              {error.message}
            </span>
          )}
        </div>
      )}
    />
  );
}

// Usage -- field names are autocompleted and type-checked
function ProfileForm() {
  const { control, handleSubmit } = useForm<{
    name: string;
    email: string;
    age: number;
  }>();

  return (
    <form onSubmit={handleSubmit((data) => console.log(data))}>
      <FormField control={control} name="name" label="Name" />
      <FormField control={control} name="email" label="Email" type="email" />
      {/* TypeScript error: "invalid" is not a valid path */}
      {/* <FormField control={control} name="invalid" label="X" /> */}
      <button type="submit">Save</button>
    </form>
  );
}
```

### Type-Safe Form Submission with API Response

```tsx
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

// Shared schema between client and server
const createPostSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().min(10),
  tags: z.array(z.string()).optional(),
  published: z.boolean().default(false),
});

type CreatePostInput = z.infer<typeof createPostSchema>;

interface CreatePostResponse {
  id: string;
  title: string;
  content: string;
  slug: string;
  createdAt: string;
}

async function createPost(data: CreatePostInput): Promise<CreatePostResponse> {
  const res = await fetch("/api/posts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create post");
  return res.json();
}

function CreatePostForm({ onSuccess }: { onSuccess: (post: CreatePostResponse) => void }) {
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<CreatePostInput>({
    resolver: zodResolver(createPostSchema),
    defaultValues: { title: "", content: "", tags: [], published: false },
  });

  const onSubmit = async (data: CreatePostInput) => {
    try {
      const post = await createPost(data);
      onSuccess(post);
    } catch {
      setError("root", { message: "Failed to create post. Try again." });
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {errors.root && <div role="alert">{errors.root.message}</div>}
      <input {...register("title")} placeholder="Post title" />
      {errors.title && <span role="alert">{errors.title.message}</span>}
      <textarea {...register("content")} placeholder="Write your post..." />
      {errors.content && <span role="alert">{errors.content.message}</span>}
      <label>
        <input type="checkbox" {...register("published")} />
        Publish immediately
      </label>
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Creating..." : "Create Post"}
      </button>
    </form>
  );
}
```

## Performance Optimization

### Avoiding Re-Renders with Isolated Components

```tsx
import { useFormContext, useWatch } from "react-hook-form";

// BAD: Entire form re-renders when any watched value changes
function BadForm() {
  const { register, watch } = useForm();
  const allValues = watch(); // Re-renders on every field change
  return <form>{/* ... */}</form>;
}

// GOOD: Only the component that watches re-renders
function PriceDisplay() {
  // useWatch subscribes at the component level -- only this component re-renders
  const price = useWatch({ name: "price" });
  const quantity = useWatch({ name: "quantity" });

  return (
    <div>
      Total: ${((price || 0) * (quantity || 0)).toFixed(2)}
    </div>
  );
}

function GoodForm() {
  const { register, control, handleSubmit } = useForm({
    defaultValues: { price: 0, quantity: 1, notes: "" },
  });

  return (
    <form onSubmit={handleSubmit((data) => console.log(data))}>
      <input type="number" {...register("price")} />
      <input type="number" {...register("quantity")} />
      <input {...register("notes")} />
      {/* Only PriceDisplay re-renders when price or quantity change */}
      <PriceDisplay />
      <button type="submit">Submit</button>
    </form>
  );
}
```

### useWatch vs watch

```tsx
// watch: Triggers re-render of the component that calls it
// Best for: top-level forms, simple cases
const { watch } = useForm();
const name = watch("name"); // parent component re-renders

// useWatch: Triggers re-render only in the subscribing component
// Best for: deeply nested components, computed displays
function NamePreview({ control }: { control: Control }) {
  const name = useWatch({ control, name: "name" });
  return <span>Hello, {name}</span>; // only this re-renders
}
```

### Uncontrolled vs Controlled Performance

```tsx
// PREFER: register (uncontrolled) -- no re-renders on input change
<input {...register("name")} />

// USE WHEN NEEDED: Controller (controlled) -- re-renders on every change
// Required for: MUI, Radix, custom components that do not expose ref
<Controller
  name="name"
  control={control}
  render={({ field }) => <CustomInput {...field} />}
/>
```

### Form-Level Optimization Techniques

```tsx
import { useForm } from "react-hook-form";
import { memo } from "react";

// 1. Use mode: "onBlur" or "onSubmit" to reduce validation frequency
const { register } = useForm({
  mode: "onBlur", // validate on blur, not on every keystroke
});

// 2. Memoize expensive child components
const ExpensiveField = memo(function ExpensiveField({
  register,
  name,
}: {
  register: any;
  name: string;
}) {
  return <input {...register(name)} />;
});

// 3. Use shouldUnregister to clean up unmounted fields
const { register } = useForm({
  shouldUnregister: true, // fields removed from DOM are unregistered
});

// 4. Avoid spreading the entire formState -- destructure only what is needed
const {
  formState: { errors, isSubmitting }, // GOOD: only subscribes to errors and isSubmitting
} = useForm();

// BAD: subscribes to all formState changes
// const { formState } = useForm();
// console.log(formState.errors); // triggers re-render on any formState change
```

### DevTools for Debugging Performance

```tsx
import { DevTool } from "@hookform/devtools";
import { useForm } from "react-hook-form";

function DebugForm() {
  const { control, register, handleSubmit } = useForm();

  return (
    <>
      <form onSubmit={handleSubmit((data) => console.log(data))}>
        <input {...register("name")} />
        <button type="submit">Submit</button>
      </form>
      {/* Renders a floating panel showing form state, re-render counts, etc. */}
      {process.env.NODE_ENV === "development" && <DevTool control={control} />}
    </>
  );
}
```

## Additional Resources

- React Hook Form docs: https://react-hook-form.com/
- Zod docs: https://zod.dev/
- @hookform/resolvers: https://github.com/react-hook-form/resolvers
- React Hook Form DevTools: https://react-hook-form.com/dev-tools
