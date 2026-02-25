---
name: storybook-docs
description: Storybook component documentation covering story writing (CSF3), args and controls, autodocs, interaction testing with play functions, visual regression testing, accessibility addon, mock data patterns, and Storybook deployment.
---

# Storybook Documentation

This skill should be used when documenting and testing UI components with Storybook. It covers CSF3 stories, controls, interaction testing, and visual regression.

## When to Use This Skill

Use this skill when you need to:

- Document React components with Storybook
- Write interactive stories with controls
- Test component interactions with play functions
- Set up visual regression testing
- Generate component documentation

## Story Writing (CSF3)

```typescript
// Button.stories.tsx
import type { Meta, StoryObj } from "@storybook/react";
import { Button } from "./Button";

const meta = {
  title: "Components/Button",
  component: Button,
  tags: ["autodocs"],
  argTypes: {
    variant: { control: "select", options: ["primary", "secondary", "destructive"] },
    size: { control: "radio", options: ["sm", "md", "lg"] },
    disabled: { control: "boolean" },
  },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Primary: Story = {
  args: { variant: "primary", children: "Click me" },
};

export const Secondary: Story = {
  args: { variant: "secondary", children: "Secondary" },
};

export const Disabled: Story = {
  args: { variant: "primary", children: "Disabled", disabled: true },
};

export const AllVariants: Story = {
  render: () => (
    <div style={{ display: "flex", gap: "1rem" }}>
      <Button variant="primary">Primary</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="destructive">Destructive</Button>
    </div>
  ),
};
```

## Interaction Testing

```typescript
import { within, userEvent, expect } from "@storybook/test";

export const FormSubmission: Story = {
  args: { onSubmit: fn() },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);

    await userEvent.type(canvas.getByLabelText("Email"), "test@example.com");
    await userEvent.type(canvas.getByLabelText("Password"), "password123");
    await userEvent.click(canvas.getByRole("button", { name: "Sign In" }));

    await expect(args.onSubmit).toHaveBeenCalledWith({
      email: "test@example.com",
      password: "password123",
    });
  },
};

export const ValidationError: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // Submit without filling fields
    await userEvent.click(canvas.getByRole("button", { name: "Sign In" }));

    await expect(canvas.getByText("Email is required")).toBeVisible();
  },
};
```

## Decorators and Context

```typescript
// .storybook/preview.tsx
import type { Preview } from "@storybook/react";
import { ThemeProvider } from "../src/theme";

const preview: Preview = {
  decorators: [
    (Story) => (
      <ThemeProvider>
        <div style={{ padding: "1rem" }}>
          <Story />
        </div>
      </ThemeProvider>
    ),
  ],
  parameters: {
    backgrounds: {
      default: "light",
      values: [
        { name: "light", value: "#ffffff" },
        { name: "dark", value: "#1a1a2e" },
      ],
    },
  },
};

export default preview;
```

## Additional Resources

- Storybook docs: https://storybook.js.org/docs
- Visual testing: https://storybook.js.org/docs/writing-tests/visual-testing
- Interaction testing: https://storybook.js.org/docs/writing-tests/interaction-testing
