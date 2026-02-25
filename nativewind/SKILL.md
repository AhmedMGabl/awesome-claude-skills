---
name: nativewind
description: NativeWind (Tailwind CSS for React Native) covering setup, utility classes, responsive design, dark mode, platform-specific styling, animations, custom themes, and integration with Expo and React Navigation.
---

# NativeWind

This skill should be used when styling React Native apps with NativeWind (Tailwind CSS). It covers utility classes, responsive design, dark mode, and platform styling.

## When to Use This Skill

Use this skill when you need to:

- Use Tailwind CSS utility classes in React Native
- Build responsive layouts for mobile and tablet
- Implement dark mode with system preference support
- Apply platform-specific styles (iOS vs Android)
- Create custom themes with Tailwind configuration

## Setup

```bash
npm install nativewind tailwindcss react-native-reanimated
npx tailwindcss init
```

```javascript
// tailwind.config.js
module.exports = {
  content: ["./app/**/*.{js,jsx,ts,tsx}", "./components/**/*.{js,jsx,ts,tsx}"],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: "#007AFF", dark: "#0A84FF" },
      },
    },
  },
  plugins: [],
};
```

```css
/* global.css */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

## Basic Usage

```tsx
import { View, Text, Pressable } from "react-native";
import "../global.css";

export default function HomeScreen() {
  return (
    <View className="flex-1 items-center justify-center bg-white dark:bg-gray-900 p-4">
      <Text className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
        Hello NativeWind
      </Text>
      <Pressable className="bg-primary px-6 py-3 rounded-xl active:opacity-80">
        <Text className="text-white font-semibold text-base">Get Started</Text>
      </Pressable>
    </View>
  );
}
```

## Responsive Design

```tsx
function ResponsiveCard() {
  return (
    <View className="p-4 sm:p-6 md:p-8">
      <View className="flex-col sm:flex-row gap-4">
        <Image
          source={{ uri: imageUrl }}
          className="w-full sm:w-32 h-48 sm:h-32 rounded-lg"
        />
        <View className="flex-1">
          <Text className="text-lg sm:text-xl font-bold">{title}</Text>
          <Text className="text-sm text-gray-500 mt-1">{description}</Text>
        </View>
      </View>
    </View>
  );
}
```

## Dark Mode

```tsx
import { useColorScheme } from "nativewind";

function ThemeToggle() {
  const { colorScheme, toggleColorScheme } = useColorScheme();

  return (
    <Pressable onPress={toggleColorScheme} className="p-2">
      <Text className="text-gray-900 dark:text-white">
        {colorScheme === "dark" ? "Light Mode" : "Dark Mode"}
      </Text>
    </Pressable>
  );
}

// Automatic dark mode support via className
function Card() {
  return (
    <View className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm dark:shadow-none border border-gray-200 dark:border-gray-700">
      <Text className="text-gray-900 dark:text-gray-100 font-semibold">Card Title</Text>
      <Text className="text-gray-500 dark:text-gray-400 mt-1">Description</Text>
    </View>
  );
}
```

## Platform-Specific Styles

```tsx
function PlatformComponent() {
  return (
    <View className="ios:pt-12 android:pt-4">
      <Text className="ios:font-['-apple-system'] android:font-['Roboto'] text-base">
        Platform text
      </Text>
      <View className="ios:shadow-sm android:elevation-2 bg-white rounded-lg p-4">
        <Text>Platform card</Text>
      </View>
    </View>
  );
}
```

## Animations (with Reanimated)

```tsx
import Animated, { FadeIn, SlideInRight } from "react-native-reanimated";

function AnimatedList({ items }: { items: Item[] }) {
  return (
    <View className="gap-3">
      {items.map((item, index) => (
        <Animated.View
          key={item.id}
          entering={SlideInRight.delay(index * 100)}
          className="bg-white dark:bg-gray-800 rounded-xl p-4"
        >
          <Text className="font-semibold dark:text-white">{item.title}</Text>
        </Animated.View>
      ))}
    </View>
  );
}
```

## Additional Resources

- NativeWind docs: https://www.nativewind.dev/
- Tailwind CSS: https://tailwindcss.com/docs
- Expo setup: https://www.nativewind.dev/getting-started/expo-router
