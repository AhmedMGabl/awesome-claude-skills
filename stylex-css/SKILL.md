---
name: stylex-css
description: StyleX patterns covering atomic CSS-in-JS, conditional styles, themes, typed tokens, dynamic values, and build-time optimization for React applications.
---

# StyleX

This skill should be used when styling React components with Meta's StyleX. It covers atomic CSS-in-JS, conditional styles, themes, tokens, and build-time optimization.

## When to Use This Skill

Use this skill when you need to:

- Write type-safe, atomic CSS-in-JS styles
- Optimize CSS output at build time
- Implement theming with typed tokens
- Create conditional and dynamic styles
- Build performant design systems

## Basic Usage

```tsx
import * as stylex from "@stylexjs/stylex";

const styles = stylex.create({
  container: {
    padding: 16,
    borderRadius: 8,
    backgroundColor: "#ffffff",
    boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
  },
  title: {
    fontSize: 24,
    fontWeight: 700,
    marginBottom: 8,
  },
  button: {
    padding: "8px 16px",
    border: "none",
    borderRadius: 4,
    cursor: "pointer",
    fontWeight: 500,
  },
});

function Card({ title }: { title: string }) {
  return (
    <div {...stylex.props(styles.container)}>
      <h2 {...stylex.props(styles.title)}>{title}</h2>
      <button {...stylex.props(styles.button)}>Action</button>
    </div>
  );
}
```

## Conditional Styles

```tsx
const styles = stylex.create({
  base: {
    padding: "8px 16px",
    borderRadius: 4,
    fontWeight: 500,
    cursor: "pointer",
  },
  primary: {
    backgroundColor: "#0066cc",
    color: "white",
  },
  secondary: {
    backgroundColor: "transparent",
    color: "#0066cc",
    border: "2px solid #0066cc",
  },
  disabled: {
    opacity: 0.5,
    cursor: "not-allowed",
  },
  small: {
    padding: "4px 8px",
    fontSize: 14,
  },
  large: {
    padding: "12px 24px",
    fontSize: 18,
  },
});

type ButtonProps = {
  variant?: "primary" | "secondary";
  size?: "small" | "large";
  disabled?: boolean;
};

function Button({ variant = "primary", size, disabled, ...props }: ButtonProps) {
  return (
    <button
      {...stylex.props(
        styles.base,
        variant === "primary" && styles.primary,
        variant === "secondary" && styles.secondary,
        size === "small" && styles.small,
        size === "large" && styles.large,
        disabled && styles.disabled
      )}
      disabled={disabled}
      {...props}
    />
  );
}
```

## Theming with Tokens

```tsx
import * as stylex from "@stylexjs/stylex";

// Define tokens (variables)
export const tokens = stylex.defineVars({
  primaryColor: "#0066cc",
  textColor: "#1a1a1a",
  backgroundColor: "#ffffff",
  borderRadius: "4px",
  spacing: "8px",
});

// Create theme override
export const darkTheme = stylex.createTheme(tokens, {
  primaryColor: "#4da6ff",
  textColor: "#e0e0e0",
  backgroundColor: "#1a1a1a",
  borderRadius: "4px",
  spacing: "8px",
});

// Use tokens in styles
const styles = stylex.create({
  container: {
    backgroundColor: tokens.backgroundColor,
    color: tokens.textColor,
    padding: tokens.spacing,
    borderRadius: tokens.borderRadius,
  },
  link: {
    color: tokens.primaryColor,
  },
});

// Apply theme
function App() {
  return (
    <div {...stylex.props(darkTheme, styles.container)}>
      <a {...stylex.props(styles.link)}>Link</a>
    </div>
  );
}
```

## Dynamic Styles

```tsx
const styles = stylex.create({
  progress: (width: number) => ({
    width: `${width}%`,
    height: 8,
    backgroundColor: "#0066cc",
    borderRadius: 4,
    transition: "width 0.3s ease",
  }),
});

function ProgressBar({ value }: { value: number }) {
  return <div {...stylex.props(styles.progress(value))} />;
}
```

## Build Configuration

```javascript
// babel.config.js
module.exports = {
  plugins: [
    ["@stylexjs/babel-plugin", {
      dev: process.env.NODE_ENV !== "production",
      runtimeInjection: false,
      genConditionalClasses: true,
    }],
  ],
};

// next.config.js
const stylexPlugin = require("@stylexjs/nextjs-plugin");
module.exports = stylexPlugin({ rootDir: __dirname })({});
```

## Additional Resources

- StyleX: https://stylexjs.com/docs/learn/
- API: https://stylexjs.com/docs/api/
- Theming: https://stylexjs.com/docs/learn/theming/
