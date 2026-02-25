---
name: css-modules-patterns
description: CSS Modules patterns covering scoped class names, composition, global styles, theming with CSS variables, responsive patterns, TypeScript integration, and Next.js/Vite configuration.
---

# CSS Modules Patterns

This skill should be used when styling with CSS Modules. It covers scoped styles, composition, theming, TypeScript support, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Write locally scoped CSS without naming conflicts
- Compose styles from multiple modules
- Build themeable component libraries
- Integrate CSS Modules with TypeScript
- Configure CSS Modules in Next.js or Vite

## Basic Usage

```css
/* Button.module.css */
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.primary {
  background-color: var(--color-primary, #3b82f6);
  color: white;
}

.primary:hover {
  background-color: var(--color-primary-hover, #2563eb);
}

.secondary {
  background-color: transparent;
  border: 1px solid var(--color-border, #e5e7eb);
  color: var(--color-text, #1f2937);
}

.small { padding: 4px 8px; font-size: 0.875rem; }
.medium { padding: 8px 16px; font-size: 1rem; }
.large { padding: 12px 24px; font-size: 1.125rem; }
```

```tsx
import styles from "./Button.module.css";
import clsx from "clsx";

interface ButtonProps {
  variant?: "primary" | "secondary";
  size?: "small" | "medium" | "large";
  children: React.ReactNode;
}

function Button({ variant = "primary", size = "medium", children }: ButtonProps) {
  return (
    <button className={clsx(styles.button, styles[variant], styles[size])}>
      {children}
    </button>
  );
}
```

## Composition

```css
/* base.module.css */
.flex {
  display: flex;
}

.flexCenter {
  composes: flex;
  align-items: center;
  justify-content: center;
}

/* Card.module.css */
.card {
  composes: flexCenter from "./base.module.css";
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
```

## Global Styles

```css
/* Component.module.css */
.wrapper :global(.external-class) {
  /* Style third-party elements */
  color: red;
}

:global(.dark-mode) .card {
  background-color: #1f2937;
  color: white;
}
```

## Theming with CSS Variables

```css
/* theme.css (global) */
:root {
  --color-primary: #3b82f6;
  --color-primary-hover: #2563eb;
  --color-text: #1f2937;
  --color-text-secondary: #6b7280;
  --color-bg: #ffffff;
  --color-surface: #f9fafb;
  --color-border: #e5e7eb;
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
}

[data-theme="dark"] {
  --color-primary: #60a5fa;
  --color-text: #f9fafb;
  --color-text-secondary: #9ca3af;
  --color-bg: #111827;
  --color-surface: #1f2937;
  --color-border: #374151;
}

/* Card.module.css - uses theme variables */
.card {
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
}
```

## TypeScript Support

```typescript
// css-modules.d.ts
declare module "*.module.css" {
  const classes: { [key: string]: string };
  export default classes;
}

// For typed CSS Modules (with typed-css-modules)
// Run: npx tcm src --watch
// Generates Button.module.css.d.ts:
// export const button: string;
// export const primary: string;
```

## Responsive Patterns

```css
/* Layout.module.css */
.grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;
}

@media (min-width: 768px) {
  .grid { grid-template-columns: repeat(2, 1fr); }
}

@media (min-width: 1024px) {
  .grid { grid-template-columns: repeat(3, 1fr); }
}

.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

@media (min-width: 768px) {
  .container { padding: 0 2rem; }
}
```

## Next.js Configuration

```javascript
// next.config.mjs - CSS Modules work out of the box in Next.js
// Custom config if needed:
export default {
  cssModules: {
    localIdentName: "[name]__[local]--[hash:base64:5]",
  },
};
```

## Additional Resources

- CSS Modules spec: https://github.com/css-modules/css-modules
- Next.js CSS Modules: https://nextjs.org/docs/app/building-your-application/styling/css-modules
- Vite CSS Modules: https://vite.dev/guide/features.html#css-modules
