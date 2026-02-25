---
name: unistyles
description: React Native Unistyles patterns covering createStyleSheet, useStyles hook, breakpoints, themes, runtime theming, media queries, dynamic values, and cross-platform styling with StyleSheet-like API.
---

# React Native Unistyles

This skill should be used when styling React Native apps with Unistyles. It covers stylesheets, breakpoints, themes, runtime theming, and responsive patterns.

## When to Use This Skill

Use this skill when you need to:

- Style React Native apps with breakpoints
- Create theme-aware stylesheets
- Use responsive design with media queries
- Build cross-platform styling systems
- Replace StyleSheet with reactive styles

## Setup

```bash
npm install react-native-unistyles
```

```typescript
// unistyles.ts
import { UnistylesRegistry } from "react-native-unistyles";

const lightTheme = {
  colors: {
    background: "#ffffff",
    text: "#1a1a1a",
    primary: "#3b82f6",
    secondary: "#6b7280",
    border: "#e5e7eb",
    error: "#ef4444",
    success: "#22c55e",
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
  },
  borderRadius: {
    sm: 4,
    md: 8,
    lg: 16,
    full: 9999,
  },
};

const darkTheme = {
  ...lightTheme,
  colors: {
    background: "#1a1a1a",
    text: "#f5f5f5",
    primary: "#60a5fa",
    secondary: "#9ca3af",
    border: "#374151",
    error: "#f87171",
    success: "#4ade80",
  },
};

const breakpoints = {
  xs: 0,
  sm: 576,
  md: 768,
  lg: 992,
  xl: 1200,
};

type AppBreakpoints = typeof breakpoints;
type AppThemes = { light: typeof lightTheme; dark: typeof darkTheme };

declare module "react-native-unistyles" {
  export interface UnistylesBreakpoints extends AppBreakpoints {}
  export interface UnistylesThemes extends AppThemes {}
}

UnistylesRegistry
  .addBreakpoints(breakpoints)
  .addThemes({ light: lightTheme, dark: darkTheme })
  .addConfig({ adaptiveThemes: true });
```

## Basic Styling

```tsx
import { createStyleSheet, useStyles } from "react-native-unistyles";

function Card({ title, description }: CardProps) {
  const { styles } = useStyles(stylesheet);

  return (
    <View style={styles.card}>
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.description}>{description}</Text>
    </View>
  );
}

const stylesheet = createStyleSheet((theme) => ({
  card: {
    backgroundColor: theme.colors.background,
    borderRadius: theme.borderRadius.lg,
    borderWidth: 1,
    borderColor: theme.colors.border,
    padding: theme.spacing.lg,
    gap: theme.spacing.sm,
  },
  title: {
    color: theme.colors.text,
    fontSize: 18,
    fontWeight: "600",
  },
  description: {
    color: theme.colors.secondary,
    fontSize: 14,
    lineHeight: 20,
  },
}));
```

## Responsive Breakpoints

```tsx
const stylesheet = createStyleSheet((theme) => ({
  container: {
    padding: theme.spacing.md,
    flexDirection: {
      xs: "column",
      md: "row",
    },
    gap: {
      xs: theme.spacing.sm,
      md: theme.spacing.lg,
    },
  },
  sidebar: {
    width: {
      xs: "100%",
      md: 280,
      lg: 320,
    },
  },
  content: {
    flex: 1,
  },
  heading: {
    fontSize: {
      xs: 20,
      sm: 24,
      md: 28,
      lg: 32,
    },
    color: theme.colors.text,
  },
}));
```

## Dynamic Styles

```tsx
const stylesheet = createStyleSheet((theme) => ({
  button: (variant: "primary" | "secondary" | "danger") => ({
    backgroundColor:
      variant === "primary" ? theme.colors.primary :
      variant === "danger" ? theme.colors.error :
      "transparent",
    borderWidth: variant === "secondary" ? 1 : 0,
    borderColor: theme.colors.border,
    paddingVertical: theme.spacing.sm,
    paddingHorizontal: theme.spacing.lg,
    borderRadius: theme.borderRadius.md,
    alignItems: "center" as const,
  }),
  buttonText: (variant: "primary" | "secondary" | "danger") => ({
    color: variant === "secondary" ? theme.colors.text : "#ffffff",
    fontWeight: "600" as const,
  }),
}));

function MyButton({ variant = "primary", title, onPress }: ButtonProps) {
  const { styles } = useStyles(stylesheet);

  return (
    <TouchableOpacity style={styles.button(variant)} onPress={onPress}>
      <Text style={styles.buttonText(variant)}>{title}</Text>
    </TouchableOpacity>
  );
}
```

## Theme Switching

```tsx
import { UnistylesRuntime } from "react-native-unistyles";

function ThemeToggle() {
  const toggleTheme = () => {
    UnistylesRuntime.setTheme(
      UnistylesRuntime.themeName === "light" ? "dark" : "light"
    );
  };

  return (
    <TouchableOpacity onPress={toggleTheme}>
      <Text>Switch to {UnistylesRuntime.themeName === "light" ? "Dark" : "Light"}</Text>
    </TouchableOpacity>
  );
}
```

## Additional Resources

- Unistyles: https://reactnativeunistyles.vercel.app/
- Breakpoints: https://reactnativeunistyles.vercel.app/reference/breakpoints/
- Themes: https://reactnativeunistyles.vercel.app/reference/theming/
