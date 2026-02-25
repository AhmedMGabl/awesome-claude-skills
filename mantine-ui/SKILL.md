---
name: mantine-ui
description: Mantine UI patterns covering core components, form handling with useForm, notifications, modals manager, theme customization, CSS-in-JS with Mantine styles, hooks, and Next.js/Remix integration.
---

# Mantine UI

This skill should be used when building React applications with Mantine component library. It covers components, forms, notifications, theming, hooks, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Build React UIs with Mantine components
- Handle forms with @mantine/form
- Add notifications and modal managers
- Customize themes and styles
- Integrate with Next.js or Remix

## Setup

```bash
npm install @mantine/core @mantine/hooks @mantine/form @mantine/notifications
```

```tsx
// app/layout.tsx (Next.js)
import "@mantine/core/styles.css";
import "@mantine/notifications/styles.css";
import { MantineProvider, ColorSchemeScript } from "@mantine/core";
import { Notifications } from "@mantine/notifications";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <head>
        <ColorSchemeScript />
      </head>
      <body>
        <MantineProvider>
          <Notifications />
          {children}
        </MantineProvider>
      </body>
    </html>
  );
}
```

## Core Components

```tsx
import {
  Button, TextInput, Select, Checkbox, Switch,
  Card, Badge, Group, Stack, Text, Title,
  Tabs, Accordion, Modal, Drawer,
  Table, Pagination, LoadingOverlay,
} from "@mantine/core";

function Dashboard() {
  return (
    <Stack gap="md">
      <Title order={2}>Dashboard</Title>

      <Group>
        <Button variant="filled">Primary</Button>
        <Button variant="light">Light</Button>
        <Button variant="outline">Outline</Button>
        <Button loading>Loading</Button>
      </Group>

      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Group justify="space-between">
          <Text fw={500}>Project Status</Text>
          <Badge color="green">Active</Badge>
        </Group>
        <Text size="sm" c="dimmed" mt="sm">
          Last updated 2 hours ago
        </Text>
      </Card>

      <Tabs defaultValue="overview">
        <Tabs.List>
          <Tabs.Tab value="overview">Overview</Tabs.Tab>
          <Tabs.Tab value="analytics">Analytics</Tabs.Tab>
          <Tabs.Tab value="settings">Settings</Tabs.Tab>
        </Tabs.List>
        <Tabs.Panel value="overview" pt="xs">Overview content</Tabs.Panel>
        <Tabs.Panel value="analytics" pt="xs">Analytics content</Tabs.Panel>
        <Tabs.Panel value="settings" pt="xs">Settings content</Tabs.Panel>
      </Tabs>
    </Stack>
  );
}
```

## Forms with useForm

```tsx
import { useForm } from "@mantine/form";
import { TextInput, PasswordInput, Select, Button, Stack } from "@mantine/core";

function RegistrationForm() {
  const form = useForm({
    mode: "uncontrolled",
    initialValues: {
      name: "",
      email: "",
      password: "",
      role: "",
    },
    validate: {
      name: (value) => (value.length < 2 ? "Name must be at least 2 characters" : null),
      email: (value) => (/^\S+@\S+$/.test(value) ? null : "Invalid email"),
      password: (value) => (value.length < 8 ? "Password must be at least 8 characters" : null),
      role: (value) => (!value ? "Please select a role" : null),
    },
  });

  return (
    <form onSubmit={form.onSubmit((values) => console.log(values))}>
      <Stack gap="sm">
        <TextInput
          label="Name"
          placeholder="Your name"
          key={form.key("name")}
          {...form.getInputProps("name")}
        />
        <TextInput
          label="Email"
          placeholder="your@email.com"
          key={form.key("email")}
          {...form.getInputProps("email")}
        />
        <PasswordInput
          label="Password"
          placeholder="Password"
          key={form.key("password")}
          {...form.getInputProps("password")}
        />
        <Select
          label="Role"
          data={["Developer", "Designer", "Manager"]}
          key={form.key("role")}
          {...form.getInputProps("role")}
        />
        <Button type="submit">Register</Button>
      </Stack>
    </form>
  );
}
```

## Notifications

```tsx
import { notifications } from "@mantine/notifications";

// Show notifications
notifications.show({
  title: "Success",
  message: "Your changes have been saved",
  color: "green",
  autoClose: 3000,
});

notifications.show({
  title: "Error",
  message: "Failed to save changes",
  color: "red",
});

// Update notification
const id = notifications.show({
  loading: true,
  title: "Uploading",
  message: "Please wait...",
  autoClose: false,
});

// Later...
notifications.update({
  id,
  loading: false,
  title: "Upload Complete",
  message: "File uploaded successfully",
  color: "green",
  autoClose: 2000,
});
```

## Theme Customization

```tsx
import { createTheme, MantineProvider } from "@mantine/core";

const theme = createTheme({
  primaryColor: "violet",
  fontFamily: "Inter, sans-serif",
  headings: { fontFamily: "Inter, sans-serif" },
  defaultRadius: "md",
  colors: {
    brand: [
      "#f0e4ff", "#d9bfff", "#c299ff", "#ab73ff",
      "#944dff", "#7d26ff", "#6600ff", "#5200cc",
      "#3d0099", "#290066",
    ],
  },
  components: {
    Button: {
      defaultProps: { radius: "md" },
    },
    TextInput: {
      defaultProps: { radius: "md" },
    },
  },
});

function App() {
  return (
    <MantineProvider theme={theme}>
      {/* App content */}
    </MantineProvider>
  );
}
```

## Useful Hooks

```tsx
import {
  useDisclosure, useToggle, useDebouncedValue,
  useMediaQuery, useClipboard, useLocalStorage,
} from "@mantine/hooks";

function Component() {
  const [opened, { open, close, toggle }] = useDisclosure(false);
  const [value, toggleValue] = useToggle(["light", "dark"]);
  const [search, setSearch] = useState("");
  const [debounced] = useDebouncedValue(search, 300);
  const isMobile = useMediaQuery("(max-width: 768px)");
  const clipboard = useClipboard({ timeout: 2000 });
  const [theme, setTheme] = useLocalStorage({ key: "theme", defaultValue: "light" });
}
```

## Additional Resources

- Mantine: https://mantine.dev/
- Components: https://mantine.dev/core/
- Hooks: https://mantine.dev/hooks/
