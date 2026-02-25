---
name: emotion-css
description: Emotion CSS-in-JS patterns covering the css prop, styled API, theming, keyframes, global styles, SSR, and TypeScript integration.
---

# Emotion CSS

This skill should be used when styling React components with Emotion. It covers the css prop, styled API, theming, keyframes, global styles, and SSR.

## When to Use This Skill

Use this skill when you need to:

- Style React components with Emotion's css prop
- Use the styled API for component styling
- Implement theming with Emotion
- Handle server-side rendering
- Combine object and string styles

## css Prop

```tsx
/** @jsxImportSource @emotion/react */
import { css } from "@emotion/react";

const buttonStyle = css`
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  background: #0066cc;
  color: white;
  cursor: pointer;

  &:hover {
    background: #0052a3;
  }
`;

// Object style
const cardStyle = css({
  padding: "1rem",
  borderRadius: 8,
  boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
});

function App() {
  return (
    <div css={cardStyle}>
      <button css={buttonStyle}>Click me</button>
    </div>
  );
}
```

## Styled API

```tsx
import styled from "@emotion/styled";

const Button = styled.button<{ variant?: "primary" | "outline" }>`
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;

  ${({ variant }) =>
    variant === "outline"
      ? css`
          background: transparent;
          border: 2px solid #0066cc;
          color: #0066cc;
        `
      : css`
          background: #0066cc;
          border: none;
          color: white;
        `}
`;

const Flex = styled.div<{ gap?: string; direction?: string }>(
  ({ gap = "1rem", direction = "row" }) => ({
    display: "flex",
    flexDirection: direction,
    gap,
    alignItems: "center",
  })
);
```

## Theming

```tsx
import { ThemeProvider } from "@emotion/react";

const theme = {
  colors: {
    primary: "#0066cc",
    text: "#1a1a1a",
    background: "#ffffff",
  },
  spacing: (n: number) => `${n * 0.25}rem`,
};

type Theme = typeof theme;

declare module "@emotion/react" {
  export interface Theme extends Theme {}
}

// Usage with css prop
const Heading = styled.h1`
  color: ${({ theme }) => theme.colors.primary};
  margin-bottom: ${({ theme }) => theme.spacing(4)};
`;

function App() {
  return (
    <ThemeProvider theme={theme}>
      <Heading>Hello</Heading>
    </ThemeProvider>
  );
}
```

## Global Styles

```tsx
import { Global, css } from "@emotion/react";

const globalStyles = css`
  * {
    box-sizing: border-box;
  }
  body {
    margin: 0;
    font-family: "Inter", system-ui, sans-serif;
    line-height: 1.6;
  }
`;

function App() {
  return (
    <>
      <Global styles={globalStyles} />
      {children}
    </>
  );
}
```

## Keyframes

```tsx
import { keyframes } from "@emotion/react";
import styled from "@emotion/styled";

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

const AnimatedCard = styled.div`
  animation: ${fadeIn} 0.3s ease-out;
`;
```

## Composition

```tsx
const base = css`
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-size: 1rem;
`;

const primary = css`
  ${base}
  background: #0066cc;
  color: white;
`;

const danger = css`
  ${base}
  background: #dc3545;
  color: white;
`;

<button css={primary}>Save</button>
<button css={danger}>Delete</button>
```

## Additional Resources

- Emotion: https://emotion.sh/docs/introduction
- styled: https://emotion.sh/docs/styled
- Theming: https://emotion.sh/docs/theming
