---
name: storybook-docs
description: Storybook component documentation and testing covering CSF3 story format with TypeScript, args/argTypes/controls, decorators and parameters, play functions for interaction testing, visual regression with Chromatic, accessibility/viewport/actions addons, MDX documentation pages, component composition, CI integration, and design system patterns.
---

# Storybook Documentation & Testing

This skill should be used when documenting, testing, or showcasing UI components with Storybook. It covers CSF3 story authoring, controls and arg types, interaction testing with play functions, visual regression via Chromatic, addon configuration, MDX documentation, and CI integration for component libraries and design systems.

## When to Use This Skill

- Write stories for React components using CSF3 and TypeScript
- Configure args, argTypes, and controls for interactive component exploration
- Apply decorators and parameters at global, component, or story level
- Author play functions for interaction testing
- Set up visual regression testing with Chromatic
- Configure addons (a11y, viewport, actions, backgrounds)
- Create MDX documentation pages alongside stories
- Compose complex components from smaller stories
- Integrate Storybook into CI/CD pipelines
- Build and maintain Storybook-driven design systems

---

## Project Setup

### Installation

```bash
# Initialize Storybook in an existing React project
npx storybook@latest init

# Start the dev server
npm run storybook

# Build a static Storybook site
npm run build-storybook
```

### Essential Addons

```bash
# Accessibility testing
npm install -D @storybook/addon-a11y

# Interaction testing
npm install -D @storybook/test @storybook/addon-interactions

# Visual regression (Chromatic)
npm install -D chromatic
```

### Directory Structure

```
.storybook/
  main.ts          # Addons, framework config, story globs
  preview.ts       # Global decorators, parameters, argTypes
  manager.ts       # UI customization (optional)
src/
  components/
    Button/
      Button.tsx
      Button.stories.tsx
      Button.mdx        # Optional MDX docs
      Button.test.tsx
```

---

## Story Writing (CSF3)

Component Story Format 3 (CSF3) is the current standard. Every story file exports a default `meta` object and named story exports.

### Basic Story File

```typescript
// Button.stories.tsx
import type { Meta, StoryObj } from "@storybook/react";
import { Button } from "./Button";

const meta = {
  title: "Components/Button",
  component: Button,
  tags: ["autodocs"],
  argTypes: {
    variant: {
      control: "select",
      options: ["primary", "secondary", "destructive"],
      description: "Visual style of the button",
      table: { defaultValue: { summary: "primary" } },
    },
    size: {
      control: "radio",
      options: ["sm", "md", "lg"],
      description: "Size of the button",
      table: { defaultValue: { summary: "md" } },
    },
    disabled: { control: "boolean" },
    onClick: { action: "clicked" },
  },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Primary: Story = {
  args: {
    variant: "primary",
    children: "Click me",
  },
};

export const Secondary: Story = {
  args: {
    variant: "secondary",
    children: "Secondary action",
  },
};

export const Disabled: Story = {
  args: {
    variant: "primary",
    children: "Disabled",
    disabled: true,
  },
};
```

### Custom Render Functions

Use `render` when the default single-component rendering is insufficient.

```typescript
export const AllVariants: Story = {
  render: () => (
    <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
      <Button variant="primary">Primary</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="destructive">Destructive</Button>
    </div>
  ),
};

export const WithIcon: Story = {
  render: (args) => (
    <Button {...args}>
      <PlusIcon className="mr-2 h-4 w-4" />
      Add item
    </Button>
  ),
  args: {
    variant: "primary",
    size: "md",
  },
};
```

### Responsive Story with Multiple Breakpoints

```typescript
export const ResponsiveSizes: Story = {
  render: () => (
    <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <Button size="sm">Small</Button>
      <Button size="md">Medium</Button>
      <Button size="lg">Large</Button>
    </div>
  ),
  parameters: {
    viewport: { defaultViewport: "mobile1" },
  },
};
```

---

## Args, ArgTypes, and Controls

Args are the inputs to a story. ArgTypes define metadata and control widgets. Controls generate the interactive panel in Storybook.

### ArgTypes Reference

```typescript
const meta = {
  component: Card,
  argTypes: {
    // Select dropdown
    variant: {
      control: "select",
      options: ["elevated", "outlined", "filled"],
      description: "Card visual variant",
      table: {
        type: { summary: "string" },
        defaultValue: { summary: "elevated" },
        category: "Appearance",
      },
    },
    // Boolean toggle
    hoverable: {
      control: "boolean",
      description: "Whether the card shows a hover effect",
      table: { category: "Behavior" },
    },
    // Number with range slider
    padding: {
      control: { type: "range", min: 0, max: 64, step: 4 },
      description: "Inner padding in pixels",
      table: { category: "Spacing" },
    },
    // Color picker
    borderColor: {
      control: "color",
      description: "Border color override",
      table: { category: "Appearance" },
    },
    // Text input
    title: {
      control: "text",
      description: "Card title text",
    },
    // Object control (for complex props)
    style: {
      control: "object",
      description: "Inline style override",
    },
    // Disable control for callback props
    onClick: {
      action: "card-clicked",
      table: { disable: true },
    },
    // Read-only display (no control)
    children: {
      control: false,
      description: "Card content",
    },
  },
} satisfies Meta<typeof Card>;
```

### Control Type Quick Reference

| Control Type | Prop Type | Example |
|---|---|---|
| `"text"` | `string` | Name, label, placeholder |
| `"boolean"` | `boolean` | Disabled, loading, checked |
| `"number"` | `number` | Count, index |
| `{ type: "range", min, max, step }` | `number` | Padding, opacity |
| `"color"` | `string` (hex) | Background, border color |
| `"date"` | `Date` | Created date, deadline |
| `"select"` | Enum / union | Variant, size |
| `"radio"` | Enum / union | Size (few options) |
| `"inline-radio"` | Enum / union | Compact option sets |
| `"check"` | `string[]` | Multi-select features |
| `"object"` | `object` | Config objects, style |
| `"file"` | File input | Image upload |
| `false` | Any | Disable control entirely |

### Mapping Values to Labels

```typescript
argTypes: {
  status: {
    control: "select",
    options: ["idle", "loading", "success", "error"],
    mapping: {
      idle: undefined,
      loading: "loading",
      success: "success",
      error: "error",
    },
    labels: {
      idle: "Idle (default)",
      loading: "Loading...",
      success: "Success",
      error: "Error state",
    },
  },
},
```

---

## Decorators and Parameters

Decorators wrap stories with additional rendering logic. Parameters configure addons and story behavior.

### Global Decorators (preview.ts)

```typescript
// .storybook/preview.ts
import type { Preview } from "@storybook/react";
import { ThemeProvider } from "../src/theme/ThemeProvider";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import "../src/styles/globals.css";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false, staleTime: Infinity } },
});

const preview: Preview = {
  decorators: [
    // Theme provider wrapper
    (Story, context) => {
      const theme = context.globals.theme || "light";
      return (
        <ThemeProvider theme={theme}>
          <Story />
        </ThemeProvider>
      );
    },
    // React Query provider
    (Story) => (
      <QueryClientProvider client={queryClient}>
        <Story />
      </QueryClientProvider>
    ),
    // Layout padding
    (Story) => (
      <div style={{ padding: "2rem" }}>
        <Story />
      </div>
    ),
  ],
  globalTypes: {
    theme: {
      description: "Global theme for components",
      toolbar: {
        title: "Theme",
        icon: "paintbrush",
        items: [
          { value: "light", title: "Light", icon: "sun" },
          { value: "dark", title: "Dark", icon: "moon" },
        ],
        dynamicTitle: true,
      },
    },
  },
  parameters: {
    actions: { argTypesRegex: "^on[A-Z].*" },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    layout: "centered",
    backgrounds: {
      default: "light",
      values: [
        { name: "light", value: "#ffffff" },
        { name: "dark", value: "#1a1a2e" },
        { name: "gray", value: "#f5f5f5" },
      ],
    },
  },
};

export default preview;
```

### Component-Level Decorators

```typescript
// Modal.stories.tsx
const meta = {
  title: "Components/Modal",
  component: Modal,
  decorators: [
    // Provide a container with relative positioning for portal-based modals
    (Story) => (
      <div style={{ minHeight: "500px", position: "relative" }}>
        <Story />
      </div>
    ),
  ],
  parameters: {
    layout: "fullscreen",
    // Disable Chromatic snapshots for animated modals
    chromatic: { disableSnapshot: false, delay: 500 },
  },
} satisfies Meta<typeof Modal>;
```

### Story-Level Decorators and Parameters

```typescript
export const InSidebar: Story = {
  decorators: [
    (Story) => (
      <aside style={{ width: "280px", background: "#f9fafb", padding: "1rem" }}>
        <Story />
      </aside>
    ),
  ],
  parameters: {
    layout: "padded",
    viewport: { defaultViewport: "mobile1" },
  },
};
```

### Router Decorator

```typescript
import { MemoryRouter, Route, Routes } from "react-router-dom";

const meta = {
  title: "Pages/UserProfile",
  component: UserProfile,
  decorators: [
    (Story) => (
      <MemoryRouter initialEntries={["/users/42"]}>
        <Routes>
          <Route path="/users/:id" element={<Story />} />
        </Routes>
      </MemoryRouter>
    ),
  ],
} satisfies Meta<typeof UserProfile>;
```

---

## Play Functions for Interaction Testing

Play functions run after a story renders, enabling automated interaction testing directly in Storybook. They use Testing Library utilities under the hood.

### Basic Interaction Test

```typescript
import { within, userEvent, expect, fn } from "@storybook/test";

const meta = {
  title: "Components/LoginForm",
  component: LoginForm,
} satisfies Meta<typeof LoginForm>;

export default meta;
type Story = StoryObj<typeof meta>;

export const SuccessfulLogin: Story = {
  args: {
    onSubmit: fn(),
  },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);

    // Fill in the form
    await userEvent.type(canvas.getByLabelText("Email"), "user@example.com");
    await userEvent.type(canvas.getByLabelText("Password"), "s3cure-p@ss!");

    // Submit the form
    await userEvent.click(canvas.getByRole("button", { name: "Sign in" }));

    // Assert the callback was called with form data
    await expect(args.onSubmit).toHaveBeenCalledWith({
      email: "user@example.com",
      password: "s3cure-p@ss!",
    });
  },
};
```

### Validation Error Testing

```typescript
export const ValidationErrors: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // Submit without filling any fields
    await userEvent.click(canvas.getByRole("button", { name: "Sign in" }));

    // Assert error messages appear
    await expect(canvas.getByText("Email is required")).toBeVisible();
    await expect(canvas.getByText("Password is required")).toBeVisible();
  },
};

export const InvalidEmailFormat: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    await userEvent.type(canvas.getByLabelText("Email"), "not-an-email");
    await userEvent.tab(); // Move focus to trigger blur validation

    await expect(canvas.getByText("Please enter a valid email")).toBeVisible();
  },
};
```

### Multi-Step Interaction

```typescript
export const AddAndRemoveItem: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // Step 1: Add item
    await userEvent.type(canvas.getByPlaceholderText("Add a task..."), "Buy groceries");
    await userEvent.click(canvas.getByRole("button", { name: "Add" }));

    // Step 2: Verify item appears
    await expect(canvas.getByText("Buy groceries")).toBeVisible();

    // Step 3: Remove item
    await userEvent.click(canvas.getByRole("button", { name: "Delete Buy groceries" }));

    // Step 4: Verify item is gone
    await expect(canvas.queryByText("Buy groceries")).not.toBeInTheDocument();
  },
};
```

### Keyboard Navigation Testing

```typescript
export const KeyboardNavigation: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // Focus the first menu item
    await userEvent.tab();
    await expect(canvas.getByRole("menuitem", { name: "Home" })).toHaveFocus();

    // Navigate with arrow keys
    await userEvent.keyboard("{ArrowDown}");
    await expect(canvas.getByRole("menuitem", { name: "About" })).toHaveFocus();

    await userEvent.keyboard("{ArrowDown}");
    await expect(canvas.getByRole("menuitem", { name: "Contact" })).toHaveFocus();

    // Select with Enter
    await userEvent.keyboard("{Enter}");
    await expect(canvas.getByText("Contact page loaded")).toBeVisible();
  },
};
```

### Waiting for Async Results

```typescript
import { within, userEvent, expect, waitFor } from "@storybook/test";

export const AsyncSearch: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    await userEvent.type(canvas.getByRole("searchbox"), "react");

    // Wait for loading to complete and results to appear
    await waitFor(
      () => {
        expect(canvas.getByText("3 results found")).toBeVisible();
      },
      { timeout: 3000 },
    );

    await expect(canvas.getAllByRole("listitem")).toHaveLength(3);
  },
};
```

---

## Visual Regression Testing with Chromatic

Chromatic captures screenshots of every story and compares them against a baseline to detect unintended visual changes.

### Setup

```bash
# Install Chromatic
npm install -D chromatic

# Run the first build (establishes baseline)
npx chromatic --project-token=<token>
```

### Chromatic Parameters

```typescript
// Customize per-story
export const AnimatedCard: Story = {
  parameters: {
    chromatic: {
      // Wait for animations to settle
      delay: 800,
      // Capture at multiple viewports
      viewports: [320, 768, 1200],
      // Diff threshold (0 = pixel-perfect, 1 = ignore all changes)
      diffThreshold: 0.063,
      // Disable snapshot for this story
      // disableSnapshot: true,
    },
  },
};

// Responsive story with multi-viewport snapshots
export const ResponsiveNavbar: Story = {
  parameters: {
    chromatic: {
      viewports: [375, 768, 1440],
    },
    layout: "fullscreen",
  },
};
```

### Modes for Theme and Locale Testing

```typescript
// .storybook/preview.ts
const preview: Preview = {
  parameters: {
    chromatic: {
      modes: {
        light: { theme: "light" },
        dark: { theme: "dark" },
      },
    },
  },
};
```

```typescript
// Individual story override
export const ThemeAware: Story = {
  parameters: {
    chromatic: {
      modes: {
        "light-mobile": { theme: "light", viewport: 375 },
        "light-desktop": { theme: "light", viewport: 1440 },
        "dark-mobile": { theme: "dark", viewport: 375 },
        "dark-desktop": { theme: "dark", viewport: 1440 },
      },
    },
  },
};
```

### Ignoring Flaky Stories

```typescript
// Skip snapshot for stories with random data or animations
export const RandomAvatar: Story = {
  parameters: {
    chromatic: { disableSnapshot: true },
  },
};
```

---

## Storybook Addons

### Accessibility Addon (@storybook/addon-a11y)

Runs axe-core accessibility checks against every story.

```typescript
// .storybook/main.ts
import type { StorybookConfig } from "@storybook/react-vite";

const config: StorybookConfig = {
  stories: ["../src/**/*.mdx", "../src/**/*.stories.@(js|jsx|mjs|ts|tsx)"],
  addons: [
    "@storybook/addon-essentials",
    "@storybook/addon-a11y",
    "@storybook/addon-interactions",
  ],
  framework: {
    name: "@storybook/react-vite",
    options: {},
  },
};

export default config;
```

Configure a11y rules at the story level:

```typescript
export const CustomA11y: Story = {
  parameters: {
    a11y: {
      config: {
        rules: [
          // Disable specific rule for this story
          { id: "color-contrast", enabled: false },
          // Override rule to warning level
          { id: "landmark-one-main", reviewOnFail: true },
        ],
      },
      // Run against a specific DOM element instead of the whole canvas
      element: "#storybook-root",
    },
  },
};
```

Programmatic a11y assertion in play functions:

```typescript
import { within, expect } from "@storybook/test";

export const AccessibleForm: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // Verify form labels are present
    await expect(canvas.getByLabelText("Email address")).toBeVisible();
    await expect(canvas.getByLabelText("Password")).toBeVisible();

    // Verify required fields are announced
    const emailInput = canvas.getByLabelText("Email address");
    await expect(emailInput).toHaveAttribute("aria-required", "true");
  },
};
```

### Viewport Addon

Simulate different device sizes.

```typescript
// .storybook/preview.ts
const preview: Preview = {
  parameters: {
    viewport: {
      viewports: {
        mobile: { name: "Mobile", styles: { width: "375px", height: "667px" } },
        tablet: { name: "Tablet", styles: { width: "768px", height: "1024px" } },
        desktop: { name: "Desktop", styles: { width: "1440px", height: "900px" } },
      },
      defaultViewport: "desktop",
    },
  },
};
```

Per-story viewport:

```typescript
export const MobileLayout: Story = {
  parameters: {
    viewport: { defaultViewport: "mobile" },
    layout: "fullscreen",
  },
};
```

### Actions Addon

Log and spy on event handler callbacks.

```typescript
import { fn } from "@storybook/test";

const meta = {
  title: "Components/SearchInput",
  component: SearchInput,
  args: {
    onSearch: fn(),
    onClear: fn(),
    onChange: fn(),
  },
} satisfies Meta<typeof SearchInput>;

export const TypeAndSearch: Story = {
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);

    await userEvent.type(canvas.getByRole("searchbox"), "storybook");
    await userEvent.click(canvas.getByRole("button", { name: "Search" }));

    await expect(args.onSearch).toHaveBeenCalledWith("storybook");
    await expect(args.onChange).toHaveBeenCalledTimes(9); // One per character
  },
};
```

---

## MDX Documentation

MDX files combine Markdown with JSX to create rich documentation pages alongside or instead of autodocs.

### Component Documentation Page

```mdx
{/* Button.mdx */}
import { Meta, Story, Canvas, Controls, ArgTypes } from "@storybook/blocks";
import * as ButtonStories from "./Button.stories";

<Meta of={ButtonStories} />

# Button

The Button component is the primary interactive element in the design system.
It supports multiple variants, sizes, and states.

## Usage Guidelines

- Use **Primary** for the main call-to-action on a page
- Use **Secondary** for less prominent actions
- Use **Destructive** only for irreversible operations (delete, remove)
- Limit one Primary button per visible section

## Interactive Playground

<Canvas of={ButtonStories.Primary} />

<Controls of={ButtonStories.Primary} />

## Variants

<Canvas>
  <Story of={ButtonStories.Primary} />
  <Story of={ButtonStories.Secondary} />
  <Story of={ButtonStories.Disabled} />
</Canvas>

## All Props

<ArgTypes of={ButtonStories} />

## Accessibility

- Buttons use native `<button>` elements for full keyboard and screen reader support
- Disabled buttons retain `aria-disabled` and remove `tabindex` focus
- Icon-only buttons require an `aria-label` prop

## Do's and Don'ts

| Do | Don't |
|---|---|
| Use clear, action-oriented labels ("Save changes") | Use vague labels ("Click here") |
| Provide loading state for async actions | Leave the user without feedback |
| Use destructive variant for delete operations | Use primary variant for destructive actions |
```

### Standalone Documentation Page

```mdx
{/* docs/GettingStarted.mdx */}
import { Meta } from "@storybook/blocks";

<Meta title="Getting Started/Installation" />

# Getting Started

Install the component library in a consuming project:

\`\`\`bash
npm install @acme/ui
\`\`\`

Import and use components:

\`\`\`tsx
import { Button, Card, Input } from "@acme/ui";

function App() {
  return (
    <Card>
      <Input label="Name" />
      <Button variant="primary">Submit</Button>
    </Card>
  );
}
\`\`\`
```

---

## Component Composition in Stories

Show how components work together in realistic scenarios.

### Form Composition

```typescript
// ContactForm.stories.tsx
import type { Meta, StoryObj } from "@storybook/react";
import { within, userEvent, expect, fn } from "@storybook/test";
import { Button } from "../Button/Button";
import { Input } from "../Input/Input";
import { Select } from "../Select/Select";
import { Textarea } from "../Textarea/Textarea";

function ContactForm({ onSubmit }: { onSubmit: (data: Record<string, string>) => void }) {
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        const formData = new FormData(e.currentTarget);
        onSubmit(Object.fromEntries(formData) as Record<string, string>);
      }}
      style={{ display: "flex", flexDirection: "column", gap: "1rem", maxWidth: "400px" }}
    >
      <Input label="Full Name" name="name" required />
      <Input label="Email" name="email" type="email" required />
      <Select
        label="Subject"
        name="subject"
        options={[
          { value: "general", label: "General inquiry" },
          { value: "support", label: "Technical support" },
          { value: "billing", label: "Billing question" },
        ]}
      />
      <Textarea label="Message" name="message" rows={4} required />
      <Button type="submit" variant="primary">
        Send message
      </Button>
    </form>
  );
}

const meta = {
  title: "Patterns/ContactForm",
  component: ContactForm,
  parameters: { layout: "centered" },
} satisfies Meta<typeof ContactForm>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: { onSubmit: fn() },
};

export const FilledAndSubmitted: Story = {
  args: { onSubmit: fn() },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);

    await userEvent.type(canvas.getByLabelText("Full Name"), "Alice Johnson");
    await userEvent.type(canvas.getByLabelText("Email"), "alice@example.com");
    await userEvent.selectOptions(canvas.getByLabelText("Subject"), "support");
    await userEvent.type(canvas.getByLabelText("Message"), "I need help with my account settings.");
    await userEvent.click(canvas.getByRole("button", { name: "Send message" }));

    await expect(args.onSubmit).toHaveBeenCalledWith({
      name: "Alice Johnson",
      email: "alice@example.com",
      subject: "support",
      message: "I need help with my account settings.",
    });
  },
};
```

### Page-Level Composition

```typescript
// DashboardPage.stories.tsx
import type { Meta, StoryObj } from "@storybook/react";
import { Header } from "../Header/Header";
import { Sidebar } from "../Sidebar/Sidebar";
import { StatsCard } from "../StatsCard/StatsCard";
import { DataTable } from "../DataTable/DataTable";

function DashboardPage() {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "250px 1fr", gridTemplateRows: "64px 1fr", height: "100vh" }}>
      <Header style={{ gridColumn: "1 / -1" }} />
      <Sidebar />
      <main style={{ padding: "1.5rem", display: "flex", flexDirection: "column", gap: "1.5rem" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem" }}>
          <StatsCard title="Revenue" value="$12,450" change={+8.2} />
          <StatsCard title="Users" value="1,234" change={+3.1} />
          <StatsCard title="Orders" value="342" change={-1.4} />
        </div>
        <DataTable
          columns={["Name", "Email", "Plan", "Status"]}
          rows={[
            ["Alice Johnson", "alice@example.com", "Pro", "Active"],
            ["Bob Smith", "bob@example.com", "Free", "Inactive"],
          ]}
        />
      </main>
    </div>
  );
}

const meta = {
  title: "Pages/Dashboard",
  component: DashboardPage,
  parameters: {
    layout: "fullscreen",
    chromatic: { viewports: [1440] },
  },
} satisfies Meta<typeof DashboardPage>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
```

---

## Mocking Data and Network Requests

### MSW (Mock Service Worker) Integration

```typescript
// .storybook/preview.ts
import { initialize, mswLoader } from "msw-storybook-addon";

initialize();

const preview: Preview = {
  loaders: [mswLoader],
};
```

```typescript
// UserProfile.stories.tsx
import { http, HttpResponse } from "msw";

export const WithUserData: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get("/api/users/42", () =>
          HttpResponse.json({
            id: 42,
            name: "Alice Johnson",
            email: "alice@example.com",
            avatar: "https://i.pravatar.cc/150?u=alice",
            role: "admin",
          }),
        ),
        http.get("/api/users/42/activity", () =>
          HttpResponse.json([
            { id: 1, action: "Logged in", timestamp: "2025-12-01T10:00:00Z" },
            { id: 2, action: "Updated profile", timestamp: "2025-12-01T10:15:00Z" },
          ]),
        ),
      ],
    },
  },
};

export const NetworkError: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get("/api/users/42", () =>
          HttpResponse.error(),
        ),
      ],
    },
  },
};

export const SlowLoading: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get("/api/users/42", async () => {
          await new Promise((resolve) => setTimeout(resolve, 3000));
          return HttpResponse.json({ id: 42, name: "Alice Johnson" });
        }),
      ],
    },
  },
};
```

---

## CI Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/storybook.yml
name: Storybook CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  storybook-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - run: npm ci

      # Build Storybook
      - run: npm run build-storybook -- --quiet

      # Run interaction tests via test-runner
      - name: Install Playwright browsers
        run: npx playwright install --with-deps chromium

      - name: Run Storybook tests
        run: |
          npx concurrently -k -s first -n "SB,TEST" -c "magenta,blue" \
            "npx http-server storybook-static --port 6006 --silent" \
            "npx wait-on tcp:127.0.0.1:6006 && npx test-storybook --url http://127.0.0.1:6006"

  chromatic:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Required for Chromatic to detect changes

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - run: npm ci

      - name: Publish to Chromatic
        uses: chromaui/action@latest
        with:
          projectToken: ${{ secrets.CHROMATIC_PROJECT_TOKEN }}
          exitZeroOnChanges: true  # Do not fail the build on visual changes
          onlyChanged: true        # Only snapshot stories affected by code changes
          externals: |
            - "src/**/*.css"
            - "src/**/*.scss"

  # Deploy Storybook as a static site
  deploy-storybook:
    if: github.ref == 'refs/heads/main'
    needs: [storybook-tests]
    runs-on: ubuntu-latest
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - run: npm ci
      - run: npm run build-storybook

      - uses: actions/upload-pages-artifact@v3
        with:
          path: storybook-static

      - id: deployment
        uses: actions/deploy-pages@v4
```

### Storybook Test Runner Configuration

```typescript
// .storybook/test-runner.ts
import type { TestRunnerConfig } from "@storybook/test-runner";
import { checkA11y, injectAxe } from "axe-playwright";

const config: TestRunnerConfig = {
  async preVisit(page) {
    // Inject axe-core for a11y testing
    await injectAxe(page);
  },
  async postVisit(page) {
    // Run a11y checks on every story
    await checkA11y(page, "#storybook-root", {
      detailedReport: true,
      detailedReportOptions: {
        html: true,
      },
    });
  },
};

export default config;
```

---

## Storybook for Design Systems

### Token Documentation

```typescript
// tokens/Colors.stories.tsx
import type { Meta, StoryObj } from "@storybook/react";
import { tokens } from "../tokens";

function ColorPalette() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
      {Object.entries(tokens.colors).map(([name, shades]) => (
        <div key={name}>
          <h3 style={{ marginBottom: "0.5rem", textTransform: "capitalize" }}>{name}</h3>
          <div style={{ display: "flex", gap: "0.25rem" }}>
            {Object.entries(shades).map(([shade, value]) => (
              <div key={shade} style={{ textAlign: "center" }}>
                <div
                  style={{
                    width: "80px",
                    height: "48px",
                    backgroundColor: value,
                    borderRadius: "4px",
                    border: "1px solid #e5e5e5",
                  }}
                />
                <span style={{ fontSize: "0.75rem" }}>{shade}</span>
                <br />
                <code style={{ fontSize: "0.625rem" }}>{value}</code>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

const meta: Meta = {
  title: "Design Tokens/Colors",
  component: ColorPalette,
  parameters: {
    layout: "padded",
    chromatic: { disableSnapshot: false },
  },
};
export default meta;

type Story = StoryObj;

export const Default: Story = {};
```

### Spacing and Typography Tokens

```typescript
// tokens/Typography.stories.tsx
function TypographyShowcase() {
  const samples = [
    { name: "xs", className: "text-xs" },
    { name: "sm", className: "text-sm" },
    { name: "base", className: "text-base" },
    { name: "lg", className: "text-lg" },
    { name: "xl", className: "text-xl" },
    { name: "2xl", className: "text-2xl" },
    { name: "3xl", className: "text-3xl" },
  ];

  return (
    <table style={{ borderCollapse: "collapse", width: "100%" }}>
      <thead>
        <tr>
          <th style={{ textAlign: "left", padding: "0.5rem" }}>Token</th>
          <th style={{ textAlign: "left", padding: "0.5rem" }}>Sample</th>
        </tr>
      </thead>
      <tbody>
        {samples.map(({ name, className }) => (
          <tr key={name}>
            <td style={{ padding: "0.5rem" }}>
              <code>{name}</code>
            </td>
            <td style={{ padding: "0.5rem" }}>
              <span className={className}>The quick brown fox jumps over the lazy dog</span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

const meta: Meta = {
  title: "Design Tokens/Typography",
  component: TypographyShowcase,
  parameters: { layout: "padded" },
};
export default meta;
```

### Icon Gallery

```typescript
// icons/IconGallery.stories.tsx
import * as Icons from "../icons";

function IconGallery() {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fill, minmax(120px, 1fr))",
        gap: "1rem",
      }}
    >
      {Object.entries(Icons).map(([name, Icon]) => (
        <div
          key={name}
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "0.5rem",
            padding: "1rem",
            border: "1px solid #e5e5e5",
            borderRadius: "8px",
          }}
        >
          <Icon style={{ width: "24px", height: "24px" }} />
          <code style={{ fontSize: "0.7rem" }}>{name}</code>
        </div>
      ))}
    </div>
  );
}

const meta: Meta = {
  title: "Design Tokens/Icons",
  component: IconGallery,
  parameters: { layout: "padded" },
};
export default meta;
```

### Component Status Documentation

```mdx
{/* docs/ComponentStatus.mdx */}
import { Meta } from "@storybook/blocks";

<Meta title="Overview/Component Status" />

# Component Status

Track the maturity and availability of each component.

| Component | Status | Accessibility | Tests | Docs |
|---|---|---|---|---|
| Button | Stable | WCAG AA | Yes | Yes |
| Input | Stable | WCAG AA | Yes | Yes |
| Select | Stable | WCAG AA | Yes | Yes |
| Modal | Beta | WCAG AA | Yes | Partial |
| DataTable | Beta | In progress | Yes | Partial |
| DatePicker | Alpha | Not started | No | No |
| Combobox | Alpha | In progress | No | No |

### Status Definitions

- **Stable** -- Production-ready, full test coverage, complete documentation
- **Beta** -- Usable but API may change, partial documentation
- **Alpha** -- Early development, not recommended for production
```

---

## Storybook Configuration Reference

### main.ts Full Example

```typescript
// .storybook/main.ts
import type { StorybookConfig } from "@storybook/react-vite";

const config: StorybookConfig = {
  stories: [
    "../src/**/*.mdx",
    "../src/**/*.stories.@(js|jsx|mjs|ts|tsx)",
  ],
  addons: [
    "@storybook/addon-essentials",    // Controls, actions, viewport, backgrounds, docs
    "@storybook/addon-a11y",          // Accessibility panel
    "@storybook/addon-interactions",  // Interaction testing panel
    "@storybook/addon-links",         // Link between stories
  ],
  framework: {
    name: "@storybook/react-vite",
    options: {},
  },
  docs: {
    autodocs: "tag",  // Generate docs for stories tagged with "autodocs"
  },
  staticDirs: ["../public"],
  typescript: {
    reactDocgen: "react-docgen-typescript",
    reactDocgenTypescriptOptions: {
      shouldExtractLiteralValuesFromEnum: true,
      shouldRemoveUndefinedFromOptional: true,
      propFilter: (prop) =>
        prop.parent ? !/node_modules/.test(prop.parent.fileName) : true,
    },
  },
};

export default config;
```

---

## Additional Resources

- Storybook docs: https://storybook.js.org/docs
- CSF3 format: https://storybook.js.org/docs/api/csf
- Interaction testing: https://storybook.js.org/docs/writing-tests/interaction-testing
- Visual testing: https://storybook.js.org/docs/writing-tests/visual-testing
- Chromatic: https://www.chromatic.com/docs
- Storybook test-runner: https://storybook.js.org/docs/writing-tests/test-runner
- MSW addon: https://storybook.js.org/addons/msw-storybook-addon
- Addon a11y: https://storybook.js.org/addons/@storybook/addon-a11y
