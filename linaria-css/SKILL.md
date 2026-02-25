---
name: linaria-css
description: Linaria zero-runtime CSS-in-JS patterns covering tagged template literals, styled API, theming, dynamic values, atomic mode, and build-time extraction.
---

# Linaria CSS

This skill should be used when styling components with Linaria. It covers zero-runtime CSS-in-JS, styled API, theming, dynamic values, and build-time extraction.

## When to Use This Skill

Use this skill when you need to:

- Write CSS-in-JS with zero runtime overhead
- Extract styles at build time to static CSS
- Use tagged template literals for type-safe styles
- Implement theming with CSS custom properties
- Create dynamic styles with CSS variables

## Basic Usage

```tsx
import { css } from "@linaria/core";
import { styled } from "@linaria/react";

const container = css`
  padding: 1rem;
  border-radius: 8px;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`;

const title = css`
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a1a1a;
`;

function Card() {
  return (
    <div className={container}>
      <h2 className={title}>Hello Linaria</h2>
    </div>
  );
}
```

## Styled Components

```tsx
import { styled } from "@linaria/react";

const Button = styled.button<{ variant?: "primary" | "outline" }>`
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  border: ${(props) =>
    props.variant === "outline" ? "2px solid #0066cc" : "none"};
  background: ${(props) =>
    props.variant === "outline" ? "transparent" : "#0066cc"};
  color: ${(props) =>
    props.variant === "outline" ? "#0066cc" : "white"};

  &:hover {
    opacity: 0.9;
  }
`;

const Flex = styled.div<{ gap?: string }>`
  display: flex;
  gap: ${(props) => props.gap || "1rem"};
  align-items: center;
`;
```

## Theming with CSS Variables

```tsx
import { css } from "@linaria/core";

// Theme as CSS variables
const lightTheme = css`
  :global() {
    --color-primary: #0066cc;
    --color-text: #1a1a1a;
    --color-bg: #ffffff;
    --spacing: 8px;
  }
`;

const darkTheme = css`
  :global() {
    --color-primary: #4da6ff;
    --color-text: #e0e0e0;
    --color-bg: #1a1a1a;
  }
`;

const card = css`
  background: var(--color-bg);
  color: var(--color-text);
  padding: calc(var(--spacing) * 2);
`;
```

## Build Configuration

```javascript
// vite.config.ts
import linaria from "@linaria/vite";

export default defineConfig({
  plugins: [linaria()],
});

// webpack.config.js
module.exports = {
  module: {
    rules: [
      {
        test: /\.(js|tsx?)$/,
        use: [
          { loader: "@linaria/webpack-loader", options: { sourceMap: true } },
        ],
      },
    ],
  },
};
```

## Additional Resources

- Linaria: https://linaria.dev/
- API: https://github.com/callstack/linaria/blob/master/docs/API.md
- How it works: https://github.com/callstack/linaria/blob/master/docs/HOW_IT_WORKS.md
