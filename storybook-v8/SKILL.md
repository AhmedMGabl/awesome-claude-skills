---
name: storybook-v8
description: Storybook v8 patterns covering Component Story Format 3, args, decorators, play functions, interaction testing, visual regression, Autodocs, and framework integration for React, Vue, and Angular.
---

# Storybook v8

This skill should be used when building component libraries and design systems with Storybook v8. It covers CSF3, args, testing, Autodocs, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Document and develop UI components in isolation
- Write interaction tests with play functions
- Generate automatic documentation with Autodocs
- Visual regression test components
- Build and share design system component libraries

## Story Setup (CSF3)

```typescript
// Button.stories.ts
import type { Meta, StoryObj } from "@storybook/react";
import { Button } from "./Button";

const meta = {
  title: "Components/Button",
  component: Button,
  tags: ["autodocs"],
  argTypes: {
    variant: {
      control: "select",
      options: ["primary", "secondary", "danger"],
    },
    size: {
      control: "radio",
      options: ["sm", "md", "lg"],
    },
    onClick: { action: "clicked" },
  },
  args: {
    children: "Click me",
    variant: "primary",
    size: "md",
  },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Primary: Story = {
  args: {
    variant: "primary",
    children: "Primary Button",
  },
};

export const Secondary: Story = {
  args: {
    variant: "secondary",
    children: "Secondary Button",
  },
};

export const AllSizes: Story = {
  render: (args) => (
    <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
      <Button {...args} size="sm">Small</Button>
      <Button {...args} size="md">Medium</Button>
      <Button {...args} size="lg">Large</Button>
    </div>
  ),
};
```

## Decorators and Parameters

```typescript
// .storybook/preview.tsx
import type { Preview } from "@storybook/react";

const preview: Preview = {
  decorators: [
    (Story) => (
      <div style={{ padding: "1rem" }}>
        <Story />
      </div>
    ),
  ],
  parameters: {
    layout: "centered",
    backgrounds: {
      default: "light",
      values: [
        { name: "light", value: "#ffffff" },
        { name: "dark", value: "#1a1a1a" },
      ],
    },
  },
};

export default preview;

// Per-story decorators
export const WithTheme: Story = {
  decorators: [
    (Story) => (
      <ThemeProvider theme="dark">
        <Story />
      </ThemeProvider>
    ),
  ],
};
```

## Play Functions (Interaction Testing)

```typescript
import { expect, fn, userEvent, within } from "@storybook/test";

export const FilledForm: Story = {
  args: {
    onSubmit: fn(),
  },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);

    // Type into inputs
    await userEvent.type(canvas.getByLabelText("Email"), "test@example.com");
    await userEvent.type(canvas.getByLabelText("Password"), "secret123");

    // Click submit
    await userEvent.click(canvas.getByRole("button", { name: "Submit" }));

    // Assert
    await expect(args.onSubmit).toHaveBeenCalledWith({
      email: "test@example.com",
      password: "secret123",
    });
  },
};

export const ErrorState: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // Submit empty form
    await userEvent.click(canvas.getByRole("button", { name: "Submit" }));

    // Check error messages appear
    await expect(canvas.getByText("Email is required")).toBeVisible();
    await expect(canvas.getByText("Password is required")).toBeVisible();
  },
};
```

## Loaders and Async Data

```typescript
export const WithData: Story = {
  loaders: [
    async () => ({
      users: await fetch("/api/users").then((r) => r.json()),
    }),
  ],
  render: (args, { loaded: { users } }) => (
    <UserList users={users} {...args} />
  ),
};
```

## Autodocs

```typescript
/**
 * A versatile button component that supports multiple variants and sizes.
 *
 * ## Usage
 *
 * ```tsx
 * <Button variant="primary" size="md" onClick={handleClick}>
 *   Click me
 * </Button>
 * ```
 */
export function Button({
  /** The visual style variant */
  variant = "primary",
  /** The size of the button */
  size = "md",
  /** Button contents */
  children,
  /** Click handler */
  onClick,
}: ButtonProps) {
  // ...
}

// Enable autodocs in meta
const meta = {
  title: "Components/Button",
  component: Button,
  tags: ["autodocs"], // Generates docs page automatically
} satisfies Meta<typeof Button>;
```

## MDX Documentation

```mdx
{/* Button.mdx */}
import { Canvas, Meta, Story, Controls } from "@storybook/blocks";
import * as ButtonStories from "./Button.stories";

<Meta of={ButtonStories} />

# Button

A versatile button component.

<Canvas of={ButtonStories.Primary} />

## Props

<Controls />

## Variants

<Canvas>
  <Story of={ButtonStories.Primary} />
  <Story of={ButtonStories.Secondary} />
  <Story of={ButtonStories.Danger} />
</Canvas>
```

## Visual Testing

```typescript
// Install: npm i -D @storybook/test-runner chromatic

// In package.json
{
  "scripts": {
    "test-storybook": "test-storybook",
    "chromatic": "chromatic --project-token=<token>"
  }
}
```

## Additional Resources

- Storybook: https://storybook.js.org/
- Storybook testing: https://storybook.js.org/docs/writing-tests
- Autodocs: https://storybook.js.org/docs/writing-docs/autodocs
