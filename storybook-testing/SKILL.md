---
name: storybook-testing
description: Storybook component testing covering story definitions, controls, decorators, interaction tests, visual regression, accessibility audits, documentation with MDX, and CI integration.
---

# Storybook Testing

This skill should be used when developing and testing UI components with Storybook. It covers story definitions, interaction tests, visual regression, and documentation.

## When to Use This Skill

Use this skill when you need to:

- Develop UI components in isolation
- Write interaction tests for components
- Run visual regression tests
- Generate component documentation
- Test accessibility compliance

## Story Definition (CSF3)

```typescript
// Button.stories.tsx
import type { Meta, StoryObj } from "@storybook/react";
import { Button } from "./Button";

const meta = {
  title: "Components/Button",
  component: Button,
  tags: ["autodocs"],
  argTypes: {
    variant: { control: "select", options: ["primary", "secondary", "ghost"] },
    size: { control: "radio", options: ["sm", "md", "lg"] },
    disabled: { control: "boolean" },
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
  args: { variant: "primary" },
};

export const Secondary: Story = {
  args: { variant: "secondary" },
};

export const Small: Story = {
  args: { size: "sm" },
};

export const Disabled: Story = {
  args: { disabled: true },
};

export const Loading: Story = {
  args: { loading: true, children: "Saving..." },
};
```

## Interaction Tests

```typescript
import { expect, fn, userEvent, within } from "@storybook/test";

export const ClickTest: Story = {
  args: { onClick: fn() },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    const button = canvas.getByRole("button");

    await userEvent.click(button);
    await expect(args.onClick).toHaveBeenCalledOnce();
  },
};

export const FormSubmission: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    await userEvent.type(canvas.getByLabelText("Email"), "test@example.com");
    await userEvent.type(canvas.getByLabelText("Password"), "password123");
    await userEvent.click(canvas.getByRole("button", { name: "Sign In" }));

    await expect(canvas.getByText("Welcome!")).toBeInTheDocument();
  },
};
```

## Decorators

```typescript
// Global decorator in .storybook/preview.tsx
import type { Preview } from "@storybook/react";

const preview: Preview = {
  decorators: [
    (Story) => (
      <ThemeProvider theme={defaultTheme}>
        <Story />
      </ThemeProvider>
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

// Story-level decorator
export const WithSidebar: Story = {
  decorators: [
    (Story) => (
      <div style={{ display: "flex", gap: "1rem" }}>
        <nav style={{ width: 200 }}>Sidebar</nav>
        <main><Story /></main>
      </div>
    ),
  ],
};
```

## Accessibility Testing

```typescript
// .storybook/main.ts - add a11y addon
export default {
  addons: ["@storybook/addon-a11y"],
};

// Story with a11y parameters
export const AccessibleForm: Story = {
  parameters: {
    a11y: {
      config: {
        rules: [
          { id: "color-contrast", enabled: true },
          { id: "label", enabled: true },
        ],
      },
    },
  },
};
```

## Visual Regression with Chromatic

```bash
# Install
npm install -D chromatic

# Run visual tests
npx chromatic --project-token=<token>
```

```typescript
// Stories with visual test config
export const ResponsiveLayout: Story = {
  parameters: {
    chromatic: {
      viewports: [320, 768, 1200],
      delay: 300,
    },
  },
};
```

## MDX Documentation

```mdx
{/* Button.mdx */}
import { Meta, Story, Canvas, Controls, Source } from "@storybook/blocks";
import * as ButtonStories from "./Button.stories";

<Meta of={ButtonStories} />

# Button

A versatile button component with multiple variants and sizes.

<Canvas of={ButtonStories.Primary} />

## Props

<Controls />

## Usage

```tsx
<Button variant="primary" size="md" onClick={handleClick}>
  Click me
</Button>
```
```

## Additional Resources

- Storybook docs: https://storybook.js.org/docs
- Testing: https://storybook.js.org/docs/writing-tests
- Visual testing: https://storybook.js.org/docs/writing-tests/visual-testing
