---
name: styled-components-patterns
description: styled-components patterns covering theming, dynamic props, CSS animations, global styles, SSR, component variants, and TypeScript integration.
---

# styled-components Patterns

This skill should be used when styling React components with styled-components. It covers theming, dynamic props, animations, SSR, variants, and TypeScript typing.

## When to Use This Skill

Use this skill when you need to:

- Style React components with CSS-in-JS
- Implement theming with ThemeProvider
- Create dynamic styles based on props
- Handle SSR with styled-components
- Type styled components with TypeScript

## Basic Usage

```typescript
import styled from "styled-components";

const Button = styled.button<{ $variant?: "primary" | "secondary" }>`
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;

  background: ${({ $variant, theme }) =>
    $variant === "secondary" ? theme.colors.secondary : theme.colors.primary};
  color: white;

  &:hover {
    opacity: 0.9;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const Card = styled.div`
  padding: ${({ theme }) => theme.spacing.md};
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`;

const Title = styled.h2`
  font-size: 1.5rem;
  margin-bottom: ${({ theme }) => theme.spacing.sm};
`;
```

## Theming

```typescript
// theme.ts
const theme = {
  colors: {
    primary: "#0066cc",
    secondary: "#6c757d",
    background: "#ffffff",
    text: "#1a1a1a",
  },
  spacing: {
    xs: "0.25rem",
    sm: "0.5rem",
    md: "1rem",
    lg: "1.5rem",
    xl: "2rem",
  },
  breakpoints: {
    sm: "576px",
    md: "768px",
    lg: "992px",
  },
} as const;

type Theme = typeof theme;

declare module "styled-components" {
  export interface DefaultTheme extends Theme {}
}

// App.tsx
import { ThemeProvider } from "styled-components";

function App() {
  return (
    <ThemeProvider theme={theme}>
      <GlobalStyles />
      {children}
    </ThemeProvider>
  );
}
```

## Global Styles

```typescript
import { createGlobalStyle } from "styled-components";

const GlobalStyles = createGlobalStyle`
  *, *::before, *::after {
    box-sizing: border-box;
  }

  body {
    margin: 0;
    font-family: "Inter", system-ui, sans-serif;
    background: ${({ theme }) => theme.colors.background};
    color: ${({ theme }) => theme.colors.text};
  }
`;
```

## Animations

```typescript
import styled, { keyframes, css } from "styled-components";

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

const spin = keyframes`
  to { transform: rotate(360deg); }
`;

const FadeInDiv = styled.div<{ $delay?: number }>`
  animation: ${fadeIn} 0.3s ease-out;
  animation-delay: ${({ $delay }) => $delay || 0}ms;
  animation-fill-mode: both;
`;

const Spinner = styled.div`
  width: 24px;
  height: 24px;
  border: 3px solid ${({ theme }) => theme.colors.primary};
  border-top-color: transparent;
  border-radius: 50%;
  animation: ${spin} 0.8s linear infinite;
`;
```

## Extending and Composition

```typescript
const BaseInput = styled.input`
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;

  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 0 0 2px ${({ theme }) => theme.colors.primary}33;
  }
`;

const SearchInput = styled(BaseInput)`
  padding-left: 2.5rem;
  background-image: url("/icons/search.svg");
  background-repeat: no-repeat;
  background-position: 0.75rem center;
`;

// Polymorphic "as" prop
<Button as="a" href="/link">Link Button</Button>
```

## Responsive Helpers

```typescript
const media = {
  sm: `@media (min-width: 576px)`,
  md: `@media (min-width: 768px)`,
  lg: `@media (min-width: 992px)`,
};

const Grid = styled.div`
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;

  ${media.md} {
    grid-template-columns: repeat(2, 1fr);
  }

  ${media.lg} {
    grid-template-columns: repeat(3, 1fr);
  }
`;
```

## Additional Resources

- styled-components: https://styled-components.com/docs
- API Reference: https://styled-components.com/docs/api
- Best Practices: https://styled-components.com/docs/faqs
