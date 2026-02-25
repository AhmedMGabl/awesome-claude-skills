---
name: panda-css-patterns
description: Panda CSS patterns covering type-safe tokens, recipes, patterns, conditions, semantic tokens, CSS-in-JS at build time, and design system configuration.
---

# Panda CSS Patterns

This skill should be used when styling with Panda CSS. It covers type-safe tokens, recipes, patterns, conditions, semantic tokens, and build-time CSS generation.

## When to Use This Skill

Use this skill when you need to:

- Write type-safe CSS with design tokens
- Create component recipes with variants
- Use atomic CSS generated at build time
- Define semantic tokens for theming
- Build design system foundations

## Configuration

```typescript
// panda.config.ts
import { defineConfig } from "@pandacss/dev";

export default defineConfig({
  preflight: true,
  include: ["./src/**/*.{js,jsx,ts,tsx}"],
  exclude: [],
  theme: {
    extend: {
      tokens: {
        colors: {
          brand: {
            50: { value: "#eff6ff" },
            500: { value: "#0066cc" },
            700: { value: "#0052a3" },
          },
        },
      },
      semanticTokens: {
        colors: {
          primary: {
            value: { base: "{colors.brand.500}", _dark: "{colors.brand.50}" },
          },
          bg: {
            surface: {
              value: { base: "white", _dark: "{colors.gray.900}" },
            },
          },
        },
      },
    },
  },
  outdir: "styled-system",
});
```

## Style Functions

```tsx
import { css } from "../styled-system/css";

function Card() {
  return (
    <div className={css({
      padding: "4",
      borderRadius: "lg",
      bg: "bg.surface",
      boxShadow: "md",
      _hover: { boxShadow: "lg" },
      transition: "all 0.2s",
    })}>
      <h2 className={css({ fontSize: "xl", fontWeight: "bold", color: "primary" })}>
        Title
      </h2>
    </div>
  );
}
```

## Recipes (Component Variants)

```typescript
// button.recipe.ts
import { cva } from "../styled-system/css";

const button = cva({
  base: {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    borderRadius: "md",
    fontWeight: "medium",
    cursor: "pointer",
    transition: "all 0.2s",
  },
  variants: {
    variant: {
      primary: {
        bg: "brand.500",
        color: "white",
        _hover: { bg: "brand.700" },
      },
      outline: {
        border: "2px solid",
        borderColor: "brand.500",
        color: "brand.500",
        _hover: { bg: "brand.50" },
      },
      ghost: {
        color: "brand.500",
        _hover: { bg: "brand.50" },
      },
    },
    size: {
      sm: { px: "3", py: "1.5", fontSize: "sm" },
      md: { px: "4", py: "2", fontSize: "md" },
      lg: { px: "6", py: "3", fontSize: "lg" },
    },
  },
  defaultVariants: {
    variant: "primary",
    size: "md",
  },
});

// Usage
<button className={button({ variant: "outline", size: "lg" })}>
  Click me
</button>
```

## Patterns

```tsx
import { flex, grid, stack, center } from "../styled-system/patterns";

<div className={flex({ gap: "4", align: "center" })}>
  <span>Item 1</span>
  <span>Item 2</span>
</div>

<div className={grid({ columns: 3, gap: "4" })}>
  <div>Col 1</div>
  <div>Col 2</div>
  <div>Col 3</div>
</div>

<div className={stack({ direction: "column", gap: "2" })}>
  <p>Stacked item</p>
</div>

<div className={center({ h: "screen" })}>
  Centered content
</div>
```

## Conditions

```tsx
<div className={css({
  bg: "white",
  // Responsive
  md: { display: "grid", gridTemplateColumns: "2" },
  lg: { gridTemplateColumns: "3" },
  // Dark mode
  _dark: { bg: "gray.900", color: "gray.100" },
  // States
  _hover: { transform: "translateY(-2px)" },
  _focus: { ring: "2", ringColor: "brand.500" },
  // Selectors
  "& > p": { marginBottom: "2" },
})}>
```

## Additional Resources

- Panda CSS: https://panda-css.com/docs/
- Recipes: https://panda-css.com/docs/concepts/recipes
- Patterns: https://panda-css.com/docs/concepts/patterns
