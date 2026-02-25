---
name: tanstack-form
description: TanStack Form patterns covering type-safe form state, field validation with Zod/Valibot, async validators, field arrays, form composition, side effects, and framework-agnostic React/Vue/Solid integration.
---

# TanStack Form

This skill should be used when building type-safe forms with TanStack Form. It covers field management, validation, arrays, composition, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Build type-safe forms with first-class TypeScript
- Validate fields with Zod, Valibot, or custom validators
- Manage dynamic field arrays
- Handle async validation (e.g., unique email check)
- Use forms across React, Vue, or Solid

## Basic Form

```tsx
import { useForm } from "@tanstack/react-form";
import { zodValidator } from "@tanstack/zod-form-adapter";
import { z } from "zod";

function ContactForm() {
  const form = useForm({
    defaultValues: {
      name: "",
      email: "",
      message: "",
    },
    onSubmit: async ({ value }) => {
      await submitForm(value);
    },
    validatorAdapter: zodValidator(),
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        form.handleSubmit();
      }}
    >
      <form.Field
        name="name"
        validators={{ onChange: z.string().min(1, "Name is required") }}
        children={(field) => (
          <div>
            <label>Name</label>
            <input
              value={field.state.value}
              onChange={(e) => field.handleChange(e.target.value)}
              onBlur={field.handleBlur}
            />
            {field.state.meta.errors.map((err) => (
              <p key={err} className="error">{err}</p>
            ))}
          </div>
        )}
      />

      <form.Field
        name="email"
        validators={{
          onChange: z.string().email("Invalid email"),
          onChangeAsyncDebounceMs: 500,
          onChangeAsync: async ({ value }) => {
            const exists = await checkEmailExists(value);
            return exists ? "Email already taken" : undefined;
          },
        }}
        children={(field) => (
          <div>
            <label>Email</label>
            <input
              value={field.state.value}
              onChange={(e) => field.handleChange(e.target.value)}
              onBlur={field.handleBlur}
            />
            {field.state.meta.isValidating && <span>Checking...</span>}
            {field.state.meta.errors.map((err) => (
              <p key={err} className="error">{err}</p>
            ))}
          </div>
        )}
      />

      <form.Field
        name="message"
        validators={{ onChange: z.string().min(10, "At least 10 characters") }}
        children={(field) => (
          <div>
            <label>Message</label>
            <textarea
              value={field.state.value}
              onChange={(e) => field.handleChange(e.target.value)}
            />
          </div>
        )}
      />

      <form.Subscribe
        selector={(state) => [state.canSubmit, state.isSubmitting]}
        children={([canSubmit, isSubmitting]) => (
          <button type="submit" disabled={!canSubmit}>
            {isSubmitting ? "Submitting..." : "Submit"}
          </button>
        )}
      />
    </form>
  );
}
```

## Field Arrays

```tsx
function OrderForm() {
  const form = useForm({
    defaultValues: {
      items: [{ name: "", quantity: 1, price: 0 }],
    },
    onSubmit: async ({ value }) => {
      await placeOrder(value);
    },
  });

  return (
    <form onSubmit={(e) => { e.preventDefault(); form.handleSubmit(); }}>
      <form.Field name="items" mode="array">
        {(field) => (
          <div>
            {field.state.value.map((_, index) => (
              <div key={index} className="item-row">
                <form.Field name={`items[${index}].name`}>
                  {(subField) => (
                    <input
                      value={subField.state.value}
                      onChange={(e) => subField.handleChange(e.target.value)}
                      placeholder="Item name"
                    />
                  )}
                </form.Field>
                <form.Field name={`items[${index}].quantity`}>
                  {(subField) => (
                    <input
                      type="number"
                      value={subField.state.value}
                      onChange={(e) => subField.handleChange(Number(e.target.value))}
                    />
                  )}
                </form.Field>
                <button type="button" onClick={() => field.removeValue(index)}>
                  Remove
                </button>
              </div>
            ))}
            <button
              type="button"
              onClick={() => field.pushValue({ name: "", quantity: 1, price: 0 })}
            >
              Add Item
            </button>
          </div>
        )}
      </form.Field>
    </form>
  );
}
```

## Form State Subscription

```tsx
function FormStatus() {
  const form = useForm({ /* ... */ });

  return (
    <div>
      <form.Subscribe
        selector={(state) => ({
          isDirty: state.isDirty,
          isValid: state.isValid,
          isSubmitting: state.isSubmitting,
          submitCount: state.submissionAttempts,
          errors: state.errors,
        })}
      >
        {({ isDirty, isValid, isSubmitting, submitCount }) => (
          <div className="form-status">
            {isDirty && <span>Unsaved changes</span>}
            {!isValid && <span>Fix errors before submitting</span>}
            {isSubmitting && <span>Saving...</span>}
            <span>Attempts: {submitCount}</span>
          </div>
        )}
      </form.Subscribe>
    </div>
  );
}
```

## Additional Resources

- TanStack Form: https://tanstack.com/form
- Validation: https://tanstack.com/form/latest/docs/framework/react/guides/validation
- Field arrays: https://tanstack.com/form/latest/docs/framework/react/guides/arrays
