---
name: tamagui
description: Tamagui patterns covering universal styling, responsive design tokens, themes, media queries, animations, form components, and cross-platform React Native and web component development.
---

# Tamagui

This skill should be used when building cross-platform React Native and web UIs with Tamagui. It covers styling, tokens, themes, animations, and responsive components.

## When to Use This Skill

Use this skill when you need to:

- Build cross-platform UI (React Native + web)
- Use design tokens for consistent styling
- Create responsive layouts with media queries
- Animate components with spring physics
- Share components between mobile and web

## Setup

```bash
npx expo install tamagui @tamagui/config
```

```tsx
// tamagui.config.ts
import { createTamagui } from "tamagui";
import { config } from "@tamagui/config/v3";

export const tamaguiConfig = createTamagui(config);
export type Conf = typeof tamaguiConfig;

declare module "tamagui" {
  interface TamaguiCustomConfig extends Conf {}
}
```

## Basic Components

```tsx
import { Stack, XStack, YStack, Text, Button, H1, Paragraph } from "tamagui";

function Card() {
  return (
    <YStack
      padding="$4"
      backgroundColor="$background"
      borderRadius="$4"
      borderWidth={1}
      borderColor="$borderColor"
      shadowColor="$shadowColor"
      shadowOffset={{ width: 0, height: 2 }}
      shadowOpacity={0.1}
      shadowRadius={4}
      gap="$3"
    >
      <H1 size="$6">Card Title</H1>
      <Paragraph color="$gray10">
        Card description text goes here.
      </Paragraph>
      <XStack gap="$2">
        <Button theme="active" size="$3">Primary</Button>
        <Button variant="outlined" size="$3">Secondary</Button>
      </XStack>
    </YStack>
  );
}
```

## Responsive Design

```tsx
import { Stack, Text, useMedia } from "tamagui";

function ResponsiveLayout() {
  const media = useMedia();

  return (
    <Stack
      flexDirection={media.sm ? "column" : "row"}
      padding={media.sm ? "$2" : "$4"}
      gap="$4"
    >
      <Stack flex={1}>
        <Text fontSize={media.sm ? "$4" : "$6"}>Responsive Content</Text>
      </Stack>
    </Stack>
  );
}

// Or use media prop shorthand
function ResponsiveCard() {
  return (
    <YStack
      padding="$4"
      $sm={{ padding: "$2" }}
      $lg={{ padding: "$6" }}
      width="100%"
      $md={{ width: "50%" }}
      $lg={{ width: "33%" }}
    >
      <Text>Responsive card</Text>
    </YStack>
  );
}
```

## Themes

```tsx
import { Theme, YStack, Text, Button } from "tamagui";

function ThemedSection() {
  return (
    <YStack gap="$4">
      <Theme name="light">
        <YStack padding="$4" backgroundColor="$background">
          <Text color="$color">Light theme</Text>
          <Button>Light Button</Button>
        </YStack>
      </Theme>

      <Theme name="dark">
        <YStack padding="$4" backgroundColor="$background">
          <Text color="$color">Dark theme</Text>
          <Button>Dark Button</Button>
        </YStack>
      </Theme>

      <Theme name="blue">
        <Button theme="active">Blue Active</Button>
      </Theme>
    </YStack>
  );
}
```

## Animations

```tsx
import { Stack, styled } from "tamagui";

const AnimatedBox = styled(Stack, {
  animation: "bouncy",
  backgroundColor: "$blue10",
  width: 100,
  height: 100,
  borderRadius: "$4",

  hoverStyle: {
    scale: 1.1,
    backgroundColor: "$blue9",
  },

  pressStyle: {
    scale: 0.95,
    backgroundColor: "$blue11",
  },

  variants: {
    visible: {
      true: {
        opacity: 1,
        y: 0,
      },
      false: {
        opacity: 0,
        y: 20,
      },
    },
  } as const,
});

function AnimatedComponent() {
  const [visible, setVisible] = useState(false);
  return <AnimatedBox visible={visible} onPress={() => setVisible(!visible)} />;
}
```

## Forms

```tsx
import { Input, TextArea, Label, XStack, YStack, Switch, Select } from "tamagui";

function ContactForm() {
  return (
    <YStack gap="$3" padding="$4">
      <YStack>
        <Label htmlFor="name">Name</Label>
        <Input id="name" placeholder="Enter your name" />
      </YStack>

      <YStack>
        <Label htmlFor="email">Email</Label>
        <Input id="email" placeholder="your@email.com" keyboardType="email-address" />
      </YStack>

      <YStack>
        <Label htmlFor="message">Message</Label>
        <TextArea id="message" placeholder="Your message..." numberOfLines={4} />
      </YStack>

      <XStack alignItems="center" gap="$2">
        <Switch id="newsletter" size="$3">
          <Switch.Thumb animation="quick" />
        </Switch>
        <Label htmlFor="newsletter">Subscribe to newsletter</Label>
      </XStack>

      <Button theme="active" size="$4">Submit</Button>
    </YStack>
  );
}
```

## Additional Resources

- Tamagui: https://tamagui.dev/
- Core concepts: https://tamagui.dev/docs/core/configuration
- Components: https://tamagui.dev/docs/components/stacks
