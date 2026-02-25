---
name: expo-router
description: Expo Router covering file-based routing for React Native, navigation patterns, layouts, typed routes, deep linking, authentication flows, API routes, and universal app patterns for iOS, Android, and web.
---

# Expo Router

This skill should be used when building navigation in Expo/React Native apps with Expo Router. It covers file-based routing, layouts, deep linking, and authentication.

## When to Use This Skill

Use this skill when you need to:

- Implement file-based navigation in React Native
- Create tab bars, stacks, and drawer layouts
- Handle deep linking and universal links
- Build authentication flows with route protection
- Share routes across iOS, Android, and web

## File Structure

```
app/
├── _layout.tsx           # Root layout
├── index.tsx             # / (home)
├── about.tsx             # /about
├── (tabs)/               # Tab group
│   ├── _layout.tsx       # Tab navigator
│   ├── index.tsx         # Tab 1
│   ├── explore.tsx       # Tab 2
│   └── profile.tsx       # Tab 3
├── (auth)/               # Auth group
│   ├── _layout.tsx       # Auth layout (no tabs)
│   ├── login.tsx         # /login
│   └── register.tsx      # /register
├── posts/
│   ├── index.tsx         # /posts
│   └── [id].tsx          # /posts/:id
└── +not-found.tsx        # 404 page
```

## Root Layout

```tsx
// app/_layout.tsx
import { Stack } from "expo-router";
import { useColorScheme } from "react-native";

export default function RootLayout() {
  const colorScheme = useColorScheme();

  return (
    <Stack
      screenOptions={{
        headerStyle: { backgroundColor: colorScheme === "dark" ? "#000" : "#fff" },
        headerTintColor: colorScheme === "dark" ? "#fff" : "#000",
      }}
    >
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      <Stack.Screen name="(auth)" options={{ headerShown: false }} />
      <Stack.Screen name="posts/[id]" options={{ title: "Post" }} />
      <Stack.Screen name="+not-found" />
    </Stack>
  );
}
```

## Tab Layout

```tsx
// app/(tabs)/_layout.tsx
import { Tabs } from "expo-router";
import { Ionicons } from "@expo/vector-icons";

export default function TabLayout() {
  return (
    <Tabs screenOptions={{ tabBarActiveTintColor: "#007AFF" }}>
      <Tabs.Screen
        name="index"
        options={{
          title: "Home",
          tabBarIcon: ({ color, size }) => <Ionicons name="home" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="explore"
        options={{
          title: "Explore",
          tabBarIcon: ({ color, size }) => <Ionicons name="compass" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: "Profile",
          tabBarIcon: ({ color, size }) => <Ionicons name="person" size={size} color={color} />,
        }}
      />
    </Tabs>
  );
}
```

## Navigation

```tsx
import { Link, useRouter, useLocalSearchParams } from "expo-router";

function HomeScreen() {
  const router = useRouter();

  return (
    <View>
      {/* Declarative */}
      <Link href="/posts/123">View Post</Link>
      <Link href={{ pathname: "/posts/[id]", params: { id: "123" } }}>View Post</Link>

      {/* Imperative */}
      <Button title="Navigate" onPress={() => router.push("/posts/123")} />
      <Button title="Replace" onPress={() => router.replace("/login")} />
      <Button title="Back" onPress={() => router.back()} />
    </View>
  );
}

// Dynamic route
function PostScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  return <Text>Post {id}</Text>;
}
```

## Authentication Guard

```tsx
// app/_layout.tsx
import { useEffect } from "react";
import { useRouter, useSegments } from "expo-router";
import { useAuth } from "@/providers/auth";

function useProtectedRoute() {
  const { user, isLoading } = useAuth();
  const segments = useSegments();
  const router = useRouter();

  useEffect(() => {
    if (isLoading) return;

    const inAuthGroup = segments[0] === "(auth)";

    if (!user && !inAuthGroup) {
      router.replace("/login");
    } else if (user && inAuthGroup) {
      router.replace("/");
    }
  }, [user, segments, isLoading]);
}

export default function RootLayout() {
  useProtectedRoute();
  return <Stack />;
}
```

## Deep Linking

```json
// app.json
{
  "expo": {
    "scheme": "myapp",
    "plugins": [
      ["expo-router", {
        "origin": "https://myapp.com"
      }]
    ]
  }
}
```

## Additional Resources

- Expo Router docs: https://docs.expo.dev/router/introduction/
- Navigation: https://docs.expo.dev/router/navigating-pages/
- Authentication: https://docs.expo.dev/router/reference/authentication/
