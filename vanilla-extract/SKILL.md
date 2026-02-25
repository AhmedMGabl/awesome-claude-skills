---
name: vanilla-extract
description: vanilla-extract CSS-in-TypeScript covering type-safe styles, theme contracts, Sprinkles utility classes, recipes for component variants, responsive conditions, and build-time CSS extraction.
---

# vanilla-extract

This skill should be used when styling applications with vanilla-extract. It covers type-safe CSS, theme contracts, Sprinkles, recipes, and build-time extraction.

## When to Use This Skill

Use this skill when you need to:

- Write type-safe CSS in TypeScript
- Define theme contracts and design tokens
- Create utility-first CSS with Sprinkles
- Build component variants with recipes
- Generate CSS at build time with zero runtime

## Basic Styles

```typescript
// styles.css.ts
import { style, globalStyle } from "@vanilla-extract/css";

export const container = style({
  maxWidth: 1200,
  margin: "0 auto",
  padding: "0 1rem",
});

export const heading = style({
  fontSize: "2rem",
  fontWeight: 700,
  color: "#1a1a1a",
  marginBottom: "1rem",
  ":hover": {
    color: "#3b82f6",
  },
  "@media": {
    "(max-width: 768px)": {
      fontSize: "1.5rem",
    },
  },
});

export const card = style({
  backgroundColor: "white",
  borderRadius: 12,
  padding: 24,
  boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
  transition: "transform 0.2s, box-shadow 0.2s",
  ":hover": {
    transform: "translateY(-2px)",
    boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
  },
});

// Global styles
globalStyle("html, body", {
  margin: 0,
  fontFamily: "system-ui, sans-serif",
});
```

## Theme Contracts

```typescript
// theme.css.ts
import { createTheme, createThemeContract } from "@vanilla-extract/css";

const vars = createThemeContract({
  color: {
    brand: null,
    text: null,
    textSecondary: null,
    background: null,
    surface: null,
    border: null,
  },
  space: {
    sm: null,
    md: null,
    lg: null,
    xl: null,
  },
  radius: {
    sm: null,
    md: null,
    lg: null,
  },
});

export const lightTheme = createTheme(vars, {
  color: {
    brand: "#3b82f6",
    text: "#1a1a1a",
    textSecondary: "#6b7280",
    background: "#ffffff",
    surface: "#f9fafb",
    border: "#e5e7eb",
  },
  space: { sm: "0.5rem", md: "1rem", lg: "1.5rem", xl: "2rem" },
  radius: { sm: "4px", md: "8px", lg: "12px" },
});

export const darkTheme = createTheme(vars, {
  color: {
    brand: "#60a5fa",
    text: "#f9fafb",
    textSecondary: "#9ca3af",
    background: "#111827",
    surface: "#1f2937",
    border: "#374151",
  },
  space: { sm: "0.5rem", md: "1rem", lg: "1.5rem", xl: "2rem" },
  radius: { sm: "4px", md: "8px", lg: "12px" },
});

export { vars };
```

## Sprinkles (Utility Classes)

```typescript
// sprinkles.css.ts
import { defineProperties, createSprinkles } from "@vanilla-extract/sprinkles";
import { vars } from "./theme.css";

const responsiveProperties = defineProperties({
  conditions: {
    mobile: {},
    tablet: { "@media": "screen and (min-width: 768px)" },
    desktop: { "@media": "screen and (min-width: 1024px)" },
  },
  defaultCondition: "mobile",
  properties: {
    display: ["none", "flex", "block", "grid"],
    flexDirection: ["row", "column"],
    gap: vars.space,
    padding: vars.space,
    fontSize: { sm: "0.875rem", md: "1rem", lg: "1.25rem", xl: "1.5rem" },
  },
});

const colorProperties = defineProperties({
  conditions: { lightMode: {}, darkMode: { "@media": "(prefers-color-scheme: dark)" } },
  defaultCondition: "lightMode",
  properties: {
    color: vars.color,
    backgroundColor: vars.color,
  },
});

export const sprinkles = createSprinkles(responsiveProperties, colorProperties);
export type Sprinkles = Parameters<typeof sprinkles>[0];
```

## Recipes (Component Variants)

```typescript
// button.css.ts
import { recipe } from "@vanilla-extract/recipes";
import { vars } from "./theme.css";

export const button = recipe({
  base: {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    borderRadius: vars.radius.md,
    fontWeight: 600,
    cursor: "pointer",
    border: "none",
    transition: "all 0.2s",
  },
  variants: {
    variant: {
      primary: { backgroundColor: vars.color.brand, color: "white" },
      secondary: { backgroundColor: vars.color.surface, color: vars.color.text, border: `1px solid ${vars.color.border}` },
      ghost: { backgroundColor: "transparent", color: vars.color.brand },
    },
    size: {
      sm: { padding: "6px 12px", fontSize: "0.875rem" },
      md: { padding: "8px 16px", fontSize: "1rem" },
      lg: { padding: "12px 24px", fontSize: "1.125rem" },
    },
  },
  defaultVariants: { variant: "primary", size: "md" },
});

// Usage
import { button } from "./button.css";
<button className={button({ variant: "primary", size: "lg" })}>Click me</button>
```

## Additional Resources

- vanilla-extract docs: https://vanilla-extract.style/
- Sprinkles: https://vanilla-extract.style/documentation/packages/sprinkles/
- Recipes: https://vanilla-extract.style/documentation/packages/recipes/
