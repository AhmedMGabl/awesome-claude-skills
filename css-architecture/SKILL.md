---
name: css-architecture
description: CSS architecture and methodology covering CSS Modules, CSS-in-JS patterns, BEM naming, CSS custom properties, cascade layers, CSS nesting, :has() selector, logical properties, color-scheme support, and scalable stylesheet organization strategies.
---

# CSS Architecture

This skill should be used when organizing CSS at scale, choosing CSS methodology, or implementing modern CSS features. It covers CSS Modules, custom properties, cascade layers, and scalable patterns.

## When to Use This Skill

Use this skill when you need to:

- Organize CSS for large applications
- Choose between CSS Modules, CSS-in-JS, or utility-first
- Implement design tokens with CSS custom properties
- Use modern CSS features (layers, nesting, :has)
- Avoid specificity conflicts and naming collisions

## CSS Modules

```css
/* components/Button.module.css */
.button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-weight: 500;
  transition: background-color 0.15s;
}

.primary {
  background-color: var(--color-primary);
  color: white;
}

.secondary {
  background-color: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.small { padding: 0.25rem 0.75rem; font-size: 0.875rem; }
.large { padding: 0.75rem 1.5rem; font-size: 1.125rem; }
```

```tsx
// components/Button.tsx
import styles from "./Button.module.css";
import clsx from "clsx";

type ButtonProps = {
  variant?: "primary" | "secondary";
  size?: "small" | "medium" | "large";
  children: React.ReactNode;
} & React.ButtonHTMLAttributes<HTMLButtonElement>;

export function Button({ variant = "primary", size = "medium", children, className, ...props }: ButtonProps) {
  return (
    <button
      className={clsx(styles.button, styles[variant], size !== "medium" && styles[size], className)}
      {...props}
    >
      {children}
    </button>
  );
}
```

## CSS Custom Properties (Design Tokens)

```css
/* tokens.css */
:root {
  /* Colors */
  --color-primary: oklch(0.55 0.2 260);
  --color-primary-hover: oklch(0.48 0.2 260);
  --color-surface: oklch(0.99 0 0);
  --color-text: oklch(0.15 0 0);
  --color-text-muted: oklch(0.45 0 0);
  --color-border: oklch(0.85 0 0);
  --color-error: oklch(0.55 0.2 25);
  --color-success: oklch(0.55 0.18 150);

  /* Spacing */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;

  /* Typography */
  --font-sans: system-ui, -apple-system, sans-serif;
  --font-mono: ui-monospace, "Cascadia Code", monospace;

  /* Shadows */
  --shadow-sm: 0 1px 2px oklch(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px oklch(0 0 0 / 0.07);

  /* Radii */
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-full: 9999px;
}

/* Dark mode tokens */
@media (prefers-color-scheme: dark) {
  :root {
    --color-surface: oklch(0.15 0 0);
    --color-text: oklch(0.92 0 0);
    --color-text-muted: oklch(0.65 0 0);
    --color-border: oklch(0.3 0 0);
  }
}
```

## Cascade Layers

```css
/* Order matters: lower layers have lower priority */
@layer reset, base, components, utilities;

@layer reset {
  *, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
  }
}

@layer base {
  body {
    font-family: var(--font-sans);
    color: var(--color-text);
    line-height: 1.6;
  }
  a { color: var(--color-primary); }
}

@layer components {
  .card {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: var(--space-6);
  }
}

@layer utilities {
  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
  }
  .truncate {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}
```

## Modern CSS Features

```css
/* Native nesting */
.card {
  padding: var(--space-4);
  border-radius: var(--radius-md);

  & .title {
    font-size: 1.25rem;
    font-weight: 600;
  }

  &:hover {
    box-shadow: var(--shadow-md);
  }

  @media (min-width: 768px) {
    padding: var(--space-6);
  }
}

/* :has() — parent selector */
.form-group:has(:invalid) {
  border-color: var(--color-error);
}

.card:has(img) {
  padding: 0;
}

label:has(+ input:required)::after {
  content: " *";
  color: var(--color-error);
}

/* Logical properties */
.sidebar {
  margin-inline-start: var(--space-4);   /* margin-left in LTR, margin-right in RTL */
  padding-block: var(--space-2);         /* padding-top + padding-bottom */
  border-inline-end: 1px solid var(--color-border);
  inline-size: 240px;                   /* width */
}
```

## File Organization

```
styles/
├── tokens.css          # CSS custom properties (design tokens)
├── reset.css           # CSS reset / normalize
├── base.css            # Base element styles
├── utilities.css       # Utility classes
└── layers.css          # @layer imports orchestrating order

components/
├── Button/
│   ├── Button.tsx
│   └── Button.module.css
├── Card/
│   ├── Card.tsx
│   └── Card.module.css

APPROACH COMPARISON:
  CSS Modules     → Scoped by default, no runtime, good DX
  Tailwind CSS    → Utility-first, fast prototyping, no CSS files
  CSS-in-JS       → Dynamic styles, colocation, runtime cost
  Vanilla CSS     → Modern features (layers, nesting) reduce need for tools
```

## Additional Resources

- CSS Cascade Layers: https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics/Cascade_layers
- CSS Nesting: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_nesting
- :has(): https://developer.mozilla.org/en-US/docs/Web/CSS/:has
- Open Props: https://open-props.style/
