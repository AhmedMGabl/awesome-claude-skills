---
name: panda-css
description: Panda CSS covering type-safe styling, design tokens, recipes, patterns, conditional styles, responsive design, dark mode, and zero-runtime CSS-in-JS with build-time extraction.
---

# Panda CSS

This skill should be used when styling applications with Panda CSS. It covers design tokens, recipes, patterns, responsive styles, and zero-runtime CSS generation.

## When to Use This Skill

Use this skill when you need to:

- Write type-safe CSS-in-JS with zero runtime
- Define design tokens and reusable recipes
- Build responsive, theme-aware styles
- Create variant-based component styles
- Generate optimized CSS at build time

## Setup

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
            500: { value: "#3b82f6" },
            900: { value: "#1e3a5f" },
          },
        },
        spacing: {
          gutter: { value: "1.5rem" },
        },
      },
      semanticTokens: {
        colors: {
          text: {
            primary: { value: { base: "{colors.gray.900}", _dark: "{colors.gray.100}" } },
            secondary: { value: { base: "{colors.gray.600}", _dark: "{colors.gray.400}" } },
          },
          bg: {
            surface: { value: { base: "white", _dark: "{colors.gray.900}" } },
          },
        },
      },
    },
  },
  outdir: "styled-system",
});
```

## Basic Styling

```tsx
import { css } from "../styled-system/css";

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div
      className={css({
        bg: "bg.surface",
        borderRadius: "lg",
        padding: "6",
        boxShadow: "md",
        transition: "all 0.2s",
        _hover: { boxShadow: "lg", transform: "translateY(-2px)" },
      })}
    >
      <h2 className={css({ fontSize: "xl", fontWeight: "bold", color: "text.primary" })}>
        {title}
      </h2>
      <div className={css({ mt: "3", color: "text.secondary" })}>{children}</div>
    </div>
  );
}
```

## Recipes (Variant Styles)

```typescript
// button.recipe.ts
import { cva } from "../styled-system/css";

export const button = cva({
  base: {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    borderRadius: "md",
    fontWeight: "semibold",
    cursor: "pointer",
    transition: "all 0.2s",
  },
  variants: {
    variant: {
      solid: {
        bg: "brand.500",
        color: "white",
        _hover: { bg: "brand.600" },
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
    variant: "solid",
    size: "md",
  },
});

// Usage
function Button({ variant, size, children }) {
  return <button className={button({ variant, size })}>{children}</button>;
}
```

## Responsive Styles

```tsx
<div
  className={css({
    display: "grid",
    gridTemplateColumns: { base: "1fr", md: "1fr 1fr", lg: "repeat(3, 1fr)" },
    gap: { base: "4", md: "6" },
    padding: { base: "4", md: "8" },
  })}
>
  {items.map((item) => (
    <Card key={item.id} title={item.title}>
      {item.description}
    </Card>
  ))}
</div>
```

## Patterns

```tsx
import { flex, grid, stack, center } from "../styled-system/patterns";

// Flex layout
<div className={flex({ gap: "4", align: "center", justify: "between" })}>
  <Logo />
  <Nav />
</div>

// Stack (vertical)
<div className={stack({ gap: "3", direction: "column" })}>
  <Input />
  <Input />
  <Button>Submit</Button>
</div>

// Center
<div className={center({ h: "screen" })}>
  <Spinner />
</div>

// Grid
<div className={grid({ columns: 3, gap: "6" })}>
  {cards.map((c) => <Card key={c.id} {...c} />)}
</div>
```

## Conditional Styles

```tsx
<div
  className={css({
    color: "text.primary",
    _hover: { color: "brand.500" },
    _focus: { outline: "2px solid", outlineColor: "brand.500" },
    _dark: { bg: "gray.800" },
    _disabled: { opacity: 0.5, cursor: "not-allowed" },
    _first: { mt: "0" },
    _even: { bg: "gray.50" },
  })}
/>
```

## Additional Resources

- Panda CSS docs: https://panda-css.com/docs
- Playground: https://play.panda-css.com/
- Recipes: https://panda-css.com/docs/concepts/recipes
