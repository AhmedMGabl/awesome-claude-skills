---
name: react-native-expo
description: React Native with Expo patterns covering managed workflow, file-based routing, native modules, EAS Build, push notifications, and over-the-air updates.
---

# React Native with Expo

This skill should be used when building mobile apps with React Native and Expo. It covers managed workflow, file-based routing, native modules, EAS Build, push notifications, and OTA updates.

## When to Use This Skill

Use this skill when you need to:

- Build cross-platform mobile apps with React Native and Expo
- Set up file-based routing with Expo Router
- Configure EAS Build and Submit
- Implement push notifications
- Use native modules and config plugins

## Project Setup

```bash
npx create-expo-app@latest my-app --template tabs
cd my-app
npx expo start
```

## App Configuration

```json
// app.json
{
  "expo": {
    "name": "MyApp",
    "slug": "my-app",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#ffffff"
    },
    "ios": {
      "supportsTablet": true,
      "bundleIdentifier": "com.example.myapp"
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#ffffff"
      },
      "package": "com.example.myapp"
    },
    "plugins": [
      "expo-router",
      ["expo-camera", { "cameraPermission": "Allow camera access" }]
    ]
  }
}
```

## Expo Router (File-Based Routing)

```typescript
// app/_layout.tsx
import { Stack } from "expo-router";

export default function RootLayout() {
  return (
    <Stack>
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      <Stack.Screen name="modal" options={{ presentation: "modal" }} />
    </Stack>
  );
}

// app/(tabs)/_layout.tsx
import { Tabs } from "expo-router";
import { Ionicons } from "@expo/vector-icons";

export default function TabLayout() {
  return (
    <Tabs screenOptions={{ tabBarActiveTintColor: "#0066cc" }}>
      <Tabs.Screen
        name="index"
        options={{
          title: "Home",
          tabBarIcon: ({ color }) => <Ionicons name="home" size={24} color={color} />,
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: "Profile",
          tabBarIcon: ({ color }) => <Ionicons name="person" size={24} color={color} />,
        }}
      />
    </Tabs>
  );
}

// app/(tabs)/index.tsx
import { View, Text, FlatList, Pressable } from "react-native";
import { Link } from "expo-router";

export default function HomeScreen() {
  return (
    <View style={{ flex: 1, padding: 16 }}>
      <Text style={{ fontSize: 24, fontWeight: "bold" }}>Home</Text>
      <Link href="/details/123" asChild>
        <Pressable>
          <Text>Go to Details</Text>
        </Pressable>
      </Link>
    </View>
  );
}

// app/details/[id].tsx
import { useLocalSearchParams } from "expo-router";
import { View, Text } from "react-native";

export default function DetailsScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  return (
    <View style={{ flex: 1, padding: 16 }}>
      <Text>Detail ID: {id}</Text>
    </View>
  );
}
```

## Custom Hooks

```typescript
// hooks/useApi.ts
import { useState, useCallback } from "react";

export function useApi<T>(fetcher: () => Promise<T>) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const execute = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetcher();
      setData(result);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [fetcher]);

  return { data, loading, error, execute };
}
```

## Push Notifications

```typescript
import * as Notifications from "expo-notifications";
import * as Device from "expo-device";
import { Platform } from "react-native";

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

async function registerForPushNotifications(): Promise<string | null> {
  if (!Device.isDevice) return null;

  const { status: existing } = await Notifications.getPermissionsAsync();
  let finalStatus = existing;

  if (existing !== "granted") {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== "granted") return null;

  if (Platform.OS === "android") {
    await Notifications.setNotificationChannelAsync("default", {
      name: "default",
      importance: Notifications.AndroidImportance.MAX,
    });
  }

  const token = await Notifications.getExpoPushTokenAsync();
  return token.data;
}
```

## EAS Build & Submit

```json
// eas.json
{
  "cli": { "version": ">= 5.0.0" },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "distribution": "internal"
    },
    "production": {}
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "user@example.com",
        "ascAppId": "1234567890"
      },
      "android": {
        "serviceAccountKeyPath": "./google-services.json"
      }
    }
  }
}
```

```bash
# Build commands
eas build --platform ios --profile production
eas build --platform android --profile production

# OTA updates
eas update --branch production --message "Bug fix"

# Submit to stores
eas submit --platform ios
eas submit --platform android
```

## Additional Resources

- Expo Docs: https://docs.expo.dev/
- Expo Router: https://docs.expo.dev/router/introduction/
- EAS Build: https://docs.expo.dev/build/introduction/
