---
name: chakra-ui-v3
description: Chakra UI v3 patterns covering style props, responsive design, color mode, component recipes, slot recipes, tokens, semantic tokens, custom themes, and accessibility-first component composition.
---

# Chakra UI v3

This skill should be used when building React UIs with Chakra UI v3. It covers style props, recipes, tokens, color mode, responsive design, and accessible components.

## When to Use This Skill

Use this skill when you need to:

- Build accessible React UIs with style props
- Create component variants with recipes
- Implement dark mode with color mode system
- Define design tokens and semantic tokens
- Build responsive layouts with breakpoints

## Setup

```bash
npm install @chakra-ui/react
```

```tsx
// app/layout.tsx
import { ChakraProvider, defaultSystem } from "@chakra-ui/react";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html suppressHydrationWarning>
      <body>
        <ChakraProvider value={defaultSystem}>
          {children}
        </ChakraProvider>
      </body>
    </html>
  );
}
```

## Style Props

```tsx
import { Box, Flex, Text, Heading, Stack, HStack, VStack } from "@chakra-ui/react";

function Card() {
  return (
    <Box
      bg="white"
      _dark={{ bg: "gray.800" }}
      borderRadius="lg"
      p={6}
      shadow="md"
      _hover={{ shadow: "lg", transform: "translateY(-2px)" }}
      transition="all 0.2s"
    >
      <Heading size="md" mb={2}>Card Title</Heading>
      <Text color="gray.600" _dark={{ color: "gray.400" }}>
        Card description text
      </Text>
    </Box>
  );
}

function Layout() {
  return (
    <Flex direction={{ base: "column", md: "row" }} gap={4} p={4}>
      <Box flex={1}>Sidebar</Box>
      <Box flex={3}>Main Content</Box>
    </Flex>
  );
}
```

## Recipes (Component Variants)

```tsx
import { defineRecipe } from "@chakra-ui/react";

const buttonRecipe = defineRecipe({
  base: {
    fontWeight: "semibold",
    borderRadius: "md",
    cursor: "pointer",
  },
  variants: {
    variant: {
      solid: {
        bg: "blue.500",
        color: "white",
        _hover: { bg: "blue.600" },
      },
      outline: {
        border: "2px solid",
        borderColor: "blue.500",
        color: "blue.500",
        _hover: { bg: "blue.50" },
      },
      ghost: {
        color: "blue.500",
        _hover: { bg: "blue.50" },
      },
    },
    size: {
      sm: { px: 3, py: 1.5, fontSize: "sm" },
      md: { px: 4, py: 2, fontSize: "md" },
      lg: { px: 6, py: 3, fontSize: "lg" },
    },
  },
  defaultVariants: {
    variant: "solid",
    size: "md",
  },
});
```

## Slot Recipes (Multi-part Components)

```tsx
import { defineSlotRecipe } from "@chakra-ui/react";

const cardRecipe = defineSlotRecipe({
  slots: ["root", "header", "body", "footer"],
  base: {
    root: {
      borderRadius: "lg",
      overflow: "hidden",
      border: "1px solid",
      borderColor: "gray.200",
    },
    header: {
      p: 4,
      borderBottom: "1px solid",
      borderColor: "gray.200",
      fontWeight: "bold",
    },
    body: {
      p: 4,
    },
    footer: {
      p: 4,
      borderTop: "1px solid",
      borderColor: "gray.200",
    },
  },
  variants: {
    variant: {
      elevated: {
        root: { shadow: "md", border: "none" },
      },
      outline: {
        root: { shadow: "none" },
      },
    },
  },
});
```

## Tokens and Theme

```tsx
import { createSystem, defineConfig } from "@chakra-ui/react";

const config = defineConfig({
  theme: {
    tokens: {
      colors: {
        brand: {
          50: { value: "#f0e4ff" },
          100: { value: "#d1b3ff" },
          500: { value: "#7c3aed" },
          600: { value: "#6d28d9" },
          900: { value: "#3b0764" },
        },
      },
      fonts: {
        heading: { value: "Inter, sans-serif" },
        body: { value: "Inter, sans-serif" },
      },
    },
    semanticTokens: {
      colors: {
        "bg.surface": {
          value: { _light: "white", _dark: "gray.800" },
        },
        "text.primary": {
          value: { _light: "gray.900", _dark: "gray.100" },
        },
        "border.default": {
          value: { _light: "gray.200", _dark: "gray.700" },
        },
      },
    },
  },
});

export const system = createSystem(config);
```

## Color Mode

```tsx
import { useColorMode, ColorModeButton } from "@chakra-ui/react";

function ThemeToggle() {
  const { colorMode, toggleColorMode } = useColorMode();

  return (
    <button onClick={toggleColorMode}>
      {colorMode === "light" ? "Dark" : "Light"} Mode
    </button>
  );
}

// Or use the built-in button
function Header() {
  return (
    <Flex justify="space-between" p={4}>
      <Heading>My App</Heading>
      <ColorModeButton />
    </Flex>
  );
}
```

## Responsive Design

```tsx
<Box
  w={{ base: "100%", sm: "80%", md: "60%", lg: "40%" }}
  p={{ base: 4, md: 8 }}
  fontSize={{ base: "sm", md: "md", lg: "lg" }}
>
  Responsive content
</Box>

<Grid templateColumns={{ base: "1fr", md: "repeat(2, 1fr)", lg: "repeat(3, 1fr)" }} gap={4}>
  <GridItem>Item 1</GridItem>
  <GridItem>Item 2</GridItem>
  <GridItem>Item 3</GridItem>
</Grid>
```

## Additional Resources

- Chakra UI v3: https://www.chakra-ui.com/
- Style props: https://www.chakra-ui.com/docs/styling/style-props
- Recipes: https://www.chakra-ui.com/docs/styling/recipes
