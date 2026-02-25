---
name: react-native-mobile
description: React Native mobile development covering Expo, React Navigation, native modules, platform-specific code, animations with Reanimated, state management, push notifications, app store deployment, and cross-platform patterns.
---

# React Native Mobile Development

This skill provides comprehensive guidance for building production-quality React Native mobile applications. It covers the full development lifecycle from project initialization through app store deployment, with emphasis on modern tooling and cross-platform best practices.

---

## 1. Project Setup

### Expo vs Bare Workflow

For most projects, start with Expo (managed workflow) unless native module customization is required from day one.

```bash
# Create a new Expo project with the latest SDK
npx create-expo-app@latest my-app --template blank-typescript

# Or with the navigation template for a head start
npx create-expo-app@latest my-app --template tabs

# For bare workflow (when native code access is needed immediately)
npx react-native@latest init MyApp --template react-native-template-typescript
```

### Recommended Project Structure

```
src/
├── app/                    # App entry, providers, global config
│   ├── App.tsx
│   └── Providers.tsx
├── components/             # Shared UI components
│   ├── ui/                 # Primitives (Button, Input, Card)
│   └── forms/              # Form-specific components
├── features/               # Feature-based modules
│   ├── auth/
│   │   ├── screens/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api.ts
│   │   └── store.ts
│   └── home/
├── navigation/             # Navigation configuration
│   ├── RootNavigator.tsx
│   ├── AuthNavigator.tsx
│   └── MainTabNavigator.tsx
├── hooks/                  # Global custom hooks
├── services/               # API client, storage, analytics
├── stores/                 # Global state (Zustand stores)
├── theme/                  # Colors, typography, spacing
│   ├── colors.ts
│   ├── typography.ts
│   └── spacing.ts
├── utils/                  # Pure utility functions
└── types/                  # Shared TypeScript types
```

### EAS Build Configuration

```json
// eas.json
{
  "cli": { "version": ">= 5.0.0" },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": { "simulator": true },
      "env": { "API_URL": "https://dev-api.example.com" }
    },
    "preview": {
      "distribution": "internal",
      "ios": { "resourceClass": "m-medium" },
      "env": { "API_URL": "https://staging-api.example.com" }
    },
    "production": {
      "ios": { "resourceClass": "m-medium" },
      "env": { "API_URL": "https://api.example.com" }
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "developer@example.com",
        "ascAppId": "1234567890",
        "appleTeamId": "ABCDE12345"
      },
      "android": {
        "serviceAccountKeyPath": "./google-services-key.json",
        "track": "internal"
      }
    }
  }
}
```

```bash
# Build for development
eas build --profile development --platform ios

# Build for production
eas build --profile production --platform all

# Submit to app stores
eas submit --profile production --platform ios
```

---

## 2. Core Components

### Foundational Layout and Interaction Patterns

```tsx
import React, { useCallback, useState } from "react";
import {
  View,
  Text,
  ScrollView,
  FlatList,
  Pressable,
  StyleSheet,
  RefreshControl,
  ActivityIndicator,
} from "react-native";

// --- Reusable Button Component ---
interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: "primary" | "secondary" | "ghost";
  disabled?: boolean;
  loading?: boolean;
}

function Button({
  title,
  onPress,
  variant = "primary",
  disabled = false,
  loading = false,
}: ButtonProps) {
  return (
    <Pressable
      onPress={onPress}
      disabled={disabled || loading}
      style={({ pressed }) => [
        styles.button,
        styles[],
        pressed && styles.buttonPressed,
        disabled && styles.buttonDisabled,
      ]}
    >
      {loading ? (
        <ActivityIndicator color="#fff" size="small" testID="activity-indicator" />
      ) : (
        <Text style={[styles.buttonText, styles[]]}>
          {title}
        </Text>
      )}
    </Pressable>
  );
}

// --- Optimized FlatList with Pull-to-Refresh ---
interface ListItem {
  id: string;
  title: string;
  subtitle: string;
}

function ItemCard({ item, onPress }: { item: ListItem; onPress: (id: string) => void }) {
  return (
    <Pressable
      onPress={() => onPress(item.id)}
      style={({ pressed }) => [styles.card, pressed && styles.cardPressed]}
    >
      <Text style={styles.cardTitle}>{item.title}</Text>
      <Text style={styles.cardSubtitle}>{item.subtitle}</Text>
    </Pressable>
  );
}

function ItemListScreen() {
  const [refreshing, setRefreshing] = useState(false);
  const [items] = useState<ListItem[]>([
    { id: "1", title: "First Item", subtitle: "Description here" },
    { id: "2", title: "Second Item", subtitle: "Another description" },
  ]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    // Fetch fresh data here
    setRefreshing(false);
  }, []);

  const handlePress = useCallback((id: string) => {
    console.log("Pressed item:", id);
  }, []);

  const renderItem = useCallback(
    ({ item }: { item: ListItem }) => (
      <ItemCard item={item} onPress={handlePress} />
    ),
    [handlePress],
  );

  const keyExtractor = useCallback((item: ListItem) => item.id, []);

  return (
    <FlatList
      data={items}
      renderItem={renderItem}
      keyExtractor={keyExtractor}
      contentContainerStyle={styles.listContent}
      ItemSeparatorComponent={() => <View style={styles.separator} />}
      ListEmptyComponent={
        <View style={styles.emptyState}>
          <Text style={styles.emptyText}>No items found</Text>
        </View>
      }
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
      // Performance optimizations
      removeClippedSubviews
      maxToRenderPerBatch={10}
      windowSize={5}
      initialNumToRender={8}
      getItemLayout={(_, index) => ({
        length: 80,
        offset: 80 * index,
        index,
      })}
    />
  );
}

const styles = StyleSheet.create({
  button: {
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
    minHeight: 48,
  },
  button_primary: { backgroundColor: "#2563eb" },
  button_secondary: { backgroundColor: "#e2e8f0" },
  button_ghost: { backgroundColor: "transparent" },
  buttonPressed: { opacity: 0.85 },
  buttonDisabled: { opacity: 0.5 },
  buttonText: { fontSize: 16, fontWeight: "600" },
  buttonText_primary: { color: "#ffffff" },
  buttonText_secondary: { color: "#1e293b" },
  buttonText_ghost: { color: "#2563eb" },
  listContent: { padding: 16 },
  card: {
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 10,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 2,
  },
  cardPressed: { backgroundColor: "#f8fafc" },
  cardTitle: { fontSize: 16, fontWeight: "600", color: "#1e293b" },
  cardSubtitle: { fontSize: 14, color: "#64748b", marginTop: 4 },
  separator: { height: 12 },
  emptyState: { alignItems: "center", paddingVertical: 48 },
  emptyText: { fontSize: 16, color: "#94a3b8" },
});
```

---

## 3. Navigation

### Full Navigation Setup with React Navigation

```tsx
// navigation/types.ts
export type RootStackParamList = {
  Auth: undefined;
  Main: undefined;
};

export type AuthStackParamList = {
  Login: undefined;
  Register: undefined;
  ForgotPassword: { email?: string };
};

export type MainTabParamList = {
  HomeTab: undefined;
  SearchTab: undefined;
  ProfileTab: undefined;
};

export type HomeStackParamList = {
  Home: undefined;
  Details: { itemId: string; title: string };
  Settings: undefined;
};
```

```tsx
// navigation/RootNavigator.tsx
import React from "react";
import { NavigationContainer, LinkingOptions } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { createDrawerNavigator } from "@react-navigation/drawer";
import * as Linking from "expo-linking";
import type {
  RootStackParamList,
  AuthStackParamList,
  MainTabParamList,
  HomeStackParamList,
} from "./types";

// Screens (imported from feature directories)
import LoginScreen from "../features/auth/screens/LoginScreen";
import RegisterScreen from "../features/auth/screens/RegisterScreen";
import HomeScreen from "../features/home/screens/HomeScreen";
import DetailsScreen from "../features/home/screens/DetailsScreen";
import SearchScreen from "../features/search/screens/SearchScreen";
import ProfileScreen from "../features/profile/screens/ProfileScreen";
import SettingsScreen from "../features/settings/screens/SettingsScreen";

const RootStack = createNativeStackNavigator<RootStackParamList>();
const AuthStack = createNativeStackNavigator<AuthStackParamList>();
const HomeStack = createNativeStackNavigator<HomeStackParamList>();
const MainTab = createBottomTabNavigator<MainTabParamList>();
const Drawer = createDrawerNavigator();

// --- Deep Linking Configuration ---
const prefix = Linking.createURL("/");

const linking: LinkingOptions<RootStackParamList> = {
  prefixes: [prefix, "https://myapp.example.com"],
  config: {
    screens: {
      Main: {
        screens: {
          HomeTab: {
            screens: {
              Home: "home",
              Details: "item/:itemId",
            },
          },
          ProfileTab: "profile",
        },
      },
      Auth: {
        screens: {
          Login: "login",
          Register: "register",
        },
      },
    },
  },
};

// --- Navigator Definitions ---
function AuthNavigator() {
  return (
    <AuthStack.Navigator screenOptions={{ headerShown: false }}>
      <AuthStack.Screen name="Login" component={LoginScreen} />
      <AuthStack.Screen name="Register" component={RegisterScreen} />
    </AuthStack.Navigator>
  );
}

function HomeNavigator() {
  return (
    <HomeStack.Navigator>
      <HomeStack.Screen name="Home" component={HomeScreen} />
      <HomeStack.Screen
        name="Details"
        component={DetailsScreen}
        options={({ route }) => ({ title: route.params.title })}
      />
      <HomeStack.Screen name="Settings" component={SettingsScreen} />
    </HomeStack.Navigator>
  );
}

function MainTabNavigator() {
  return (
    <MainTab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: "#2563eb",
        tabBarInactiveTintColor: "#94a3b8",
        tabBarStyle: { paddingBottom: 4, height: 56 },
      }}
    >
      <MainTab.Screen
        name="HomeTab"
        component={HomeNavigator}
        options={{ tabBarLabel: "Home" }}
      />
      <MainTab.Screen
        name="SearchTab"
        component={SearchScreen}
        options={{ tabBarLabel: "Search" }}
      />
      <MainTab.Screen
        name="ProfileTab"
        component={ProfileScreen}
        options={{ tabBarLabel: "Profile" }}
      />
    </MainTab.Navigator>
  );
}

// --- Root Navigator with Auth Gate ---
export default function RootNavigator() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  return (
    <NavigationContainer linking={linking}>
      <RootStack.Navigator screenOptions={{ headerShown: false }}>
        {isAuthenticated ? (
          <RootStack.Screen name="Main" component={MainTabNavigator} />
        ) : (
          <RootStack.Screen name="Auth" component={AuthNavigator} />
        )}
      </RootStack.Navigator>
    </NavigationContainer>
  );
}
```

### Type-Safe Navigation Hook

```tsx
// hooks/useAppNavigation.ts
import { useNavigation } from "@react-navigation/native";
import type { NativeStackNavigationProp } from "@react-navigation/native-stack";
import type { HomeStackParamList } from "../navigation/types";

export function useHomeNavigation() {
  return useNavigation<NativeStackNavigationProp<HomeStackParamList>>();
}

// Usage in a component:
// const navigation = useHomeNavigation();
// navigation.navigate("Details", { itemId: "123", title: "Item Title" });
```

---

## 4. Styling

### Theme System with Responsive Design

```tsx
// theme/colors.ts
export const colors = {
  primary: "#2563eb",
  primaryDark: "#1d4ed8",
  secondary: "#7c3aed",
  background: "#f8fafc",
  surface: "#ffffff",
  text: "#1e293b",
  textSecondary: "#64748b",
  textTertiary: "#94a3b8",
  border: "#e2e8f0",
  error: "#ef4444",
  success: "#22c55e",
  warning: "#f59e0b",
} as const;

// theme/spacing.ts
export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
} as const;

// theme/typography.ts
import { Platform, TextStyle } from "react-native";

const fontFamily = Platform.select({
  ios: "System",
  android: "Roboto",
  default: "System",
});

export const typography: Record<string, TextStyle> = {
  h1: { fontSize: 32, fontWeight: "700", lineHeight: 40, fontFamily },
  h2: { fontSize: 24, fontWeight: "600", lineHeight: 32, fontFamily },
  h3: { fontSize: 20, fontWeight: "600", lineHeight: 28, fontFamily },
  body: { fontSize: 16, fontWeight: "400", lineHeight: 24, fontFamily },
  bodySmall: { fontSize: 14, fontWeight: "400", lineHeight: 20, fontFamily },
  caption: { fontSize: 12, fontWeight: "400", lineHeight: 16, fontFamily },
  button: { fontSize: 16, fontWeight: "600", lineHeight: 24, fontFamily },
};
```

### Responsive Design Utilities

```tsx
// hooks/useResponsive.ts
import { useWindowDimensions } from "react-native";

type Breakpoint = "sm" | "md" | "lg";

const breakpoints = { sm: 0, md: 768, lg: 1024 };

export function useResponsive() {
  const { width, height } = useWindowDimensions();

  const breakpoint: Breakpoint =
    width >= breakpoints.lg ? "lg" : width >= breakpoints.md ? "md" : "sm";

  const isTablet = width >= breakpoints.md;

  function select<T>(options: Partial<Record<Breakpoint, T>> & { sm: T }): T {
    if (breakpoint === "lg" && options.lg \!== undefined) return options.lg;
    if (breakpoint \!== "sm" && options.md \!== undefined) return options.md;
    return options.sm;
  }

  return { width, height, breakpoint, isTablet, select };
}

// Usage:
// const { select, isTablet } = useResponsive();
// const columns = select({ sm: 1, md: 2, lg: 3 });
```

### Platform-Specific Styling

```tsx
import { Platform, StyleSheet } from "react-native";

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 16,
    ...Platform.select({
      ios: {
        shadowColor: "#000",
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
      },
      android: {
        elevation: 4,
      },
    }),
  },
  safeText: {
    fontFamily: Platform.OS === "ios" ? "SF Pro Display" : "Roboto",
  },
});
```

---

## 5. State Management

### Zustand Store with Persistence

```tsx
// stores/authStore.ts
import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import AsyncStorage from "@react-native-async-storage/async-storage";

interface User {
  id: string;
  email: string;
  name: string;
  avatarUrl?: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  setAuth: (user: User, token: string) => void;
  logout: () => void;
  updateUser: (updates: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      setAuth: (user, token) =>
        set({ user, token, isAuthenticated: true }),

      logout: () =>
        set({ user: null, token: null, isAuthenticated: false }),

      updateUser: (updates) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...updates } : null,
        })),
    }),
    {
      name: "auth-storage",
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    },
  ),
);
```

### TanStack Query (React Query) for Server State

```tsx
// services/api.ts
const BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? "https://api.example.com";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const token = useAuthStore.getState().token;

  const res = await fetch(, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization:  } : {}),
      ...options?.headers,
    },
  });

  if (!res.ok) {
    if (res.status === 401) useAuthStore.getState().logout();
    throw new ApiError(res.status, await res.text());
  }

  return res.json();
}

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

// --- Feature API Module ---
// features/home/api.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

interface Item {
  id: string;
  title: string;
  description: string;
  createdAt: string;
}

export function useItems() {
  return useQuery({
    queryKey: ["items"],
    queryFn: () => apiFetch<Item[]>("/items"),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useItem(id: string) {
  return useQuery({
    queryKey: ["items", id],
    queryFn: () => apiFetch<Item>(),
    enabled: !!id,
  });
}

export function useCreateItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { title: string; description: string }) =>
      apiFetch<Item>("/items", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["items"] });
    },
  });
}

// --- Query Provider Setup ---
// app/Providers.tsx
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 30_000,
      gcTime: 5 * 60 * 1000,
    },
  },
});

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
```

---

## 6. Animations

### React Native Reanimated with Gesture Handler

```tsx
// components/AnimatedCard.tsx
import React from "react";
import { StyleSheet, Text, View } from "react-native";
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
  interpolate,
  Extrapolation,
  FadeInDown,
  Layout,
} from "react-native-reanimated";
import {
  Gesture,
  GestureDetector,
  GestureHandlerRootView,
} from "react-native-gesture-handler";

// --- Spring-Animated Pressable Card ---
function AnimatedCard({ title, onPress }: { title: string; onPress: () => void }) {
  const scale = useSharedValue(1);
  const pressed = useSharedValue(false);

  const tapGesture = Gesture.Tap()
    .onBegin(() => {
      "worklet";
      scale.value = withSpring(0.96, { damping: 15 });
      pressed.value = true;
    })
    .onFinalize(() => {
      "worklet";
      scale.value = withSpring(1, { damping: 15 });
      pressed.value = false;
    })
    .onEnd(() => {
      onPress();
    });

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    shadowOpacity: interpolate(
      scale.value,
      [0.96, 1],
      [0.05, 0.15],
      Extrapolation.CLAMP,
    ),
  }));

  return (
    <GestureDetector gesture={tapGesture}>
      <Animated.View
        entering={FadeInDown.springify().damping(18)}
        layout={Layout.springify()}
        style={[animStyles.card, animatedStyle]}
      >
        <Text style={animStyles.cardTitle}>{title}</Text>
      </Animated.View>
    </GestureDetector>
  );
}

// --- Swipe-to-Dismiss Row ---
function SwipeToDelete({
  children,
  onDelete,
}: {
  children: React.ReactNode;
  onDelete: () => void;
}) {
  const translateX = useSharedValue(0);
  const itemHeight = useSharedValue(70);
  const DELETE_THRESHOLD = -120;

  const panGesture = Gesture.Pan()
    .activeOffsetX([-10, 10])
    .onUpdate((event) => {
      "worklet";
      translateX.value = Math.min(0, event.translationX);
    })
    .onEnd(() => {
      "worklet";
      if (translateX.value < DELETE_THRESHOLD) {
        translateX.value = withTiming(-500, { duration: 250 });
        itemHeight.value = withTiming(0, { duration: 300 }, () => {
          onDelete();
        });
      } else {
        translateX.value = withSpring(0, { damping: 20 });
      }
    });

  const rowStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: translateX.value }],
  }));

  const containerStyle = useAnimatedStyle(() => ({
    height: itemHeight.value,
    overflow: "hidden" as const,
  }));

  const deleteIndicatorStyle = useAnimatedStyle(() => ({
    opacity: interpolate(
      translateX.value,
      [DELETE_THRESHOLD, 0],
      [1, 0],
      Extrapolation.CLAMP,
    ),
  }));

  return (
    <Animated.View style={containerStyle}>
      <Animated.View style={[animStyles.deleteBackground, deleteIndicatorStyle]}>
        <Text style={animStyles.deleteText}>Delete</Text>
      </Animated.View>
      <GestureDetector gesture={panGesture}>
        <Animated.View style={[animStyles.swipeRow, rowStyle]}>
          {children}
        </Animated.View>
      </GestureDetector>
    </Animated.View>
  );
}

// --- Skeleton Loading Placeholder ---
function SkeletonLoader({ width, height }: { width: number | string; height: number }) {
  const opacity = useSharedValue(0.3);

  React.useEffect(() => {
    function pulse() {
      opacity.value = withTiming(1, { duration: 800 }, () => {
        opacity.value = withTiming(0.3, { duration: 800 });
      });
    }
    pulse();
  }, [opacity]);

  const animatedStyle = useAnimatedStyle(() => ({
    opacity: opacity.value,
  }));

  return (
    <Animated.View
      style={[
        { width: width as number, height, backgroundColor: "#e2e8f0", borderRadius: 8 },
        animatedStyle,
      ]}
    />
  );
}

const animStyles = StyleSheet.create({
  card: {
    backgroundColor: "#fff",
    padding: 20,
    borderRadius: 12,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 12,
    elevation: 4,
    marginVertical: 6,
    marginHorizontal: 16,
  },
  cardTitle: { fontSize: 17, fontWeight: "600", color: "#1e293b" },
  deleteBackground: {
    position: "absolute",
    right: 0,
    top: 0,
    bottom: 0,
    width: 120,
    backgroundColor: "#ef4444",
    justifyContent: "center",
    alignItems: "center",
    borderRadius: 8,
  },
  deleteText: { color: "#fff", fontWeight: "700", fontSize: 15 },
  swipeRow: {
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 8,
  },
});
```

---

## 7. Native Modules and Platform-Specific Code

### Platform Branching Patterns

```tsx
import { Platform, NativeModules, Alert, Linking } from "react-native";

// --- Platform-specific file imports ---
// Create two files: CameraButton.ios.tsx and CameraButton.android.tsx
// React Native automatically resolves the correct file:
// import CameraButton from "./CameraButton";

// --- Runtime platform branching ---
function openAppSettings() {
  if (Platform.OS === "ios") {
    Linking.openURL("app-settings:");
  } else {
    Linking.openSettings();
  }
}

// --- Platform-specific component behavior ---
function getHapticFeedback() {
  if (Platform.OS === "ios") {
    const Haptics = require("expo-haptics");
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
  }
  // Android haptics are handled through Vibration API or expo-haptics
}

// --- Platform version checks ---
function supportsBlurView(): boolean {
  if (Platform.OS === "ios") return true;
  if (Platform.OS === "android" && Platform.Version >= 31) return true;
  return false;
}
```

### Expo Modules (Config Plugins)

```typescript
// app.config.ts - Dynamic Expo config with platform-specific plugins
import { ExpoConfig, ConfigContext } from "expo/config";

export default ({ config }: ConfigContext): ExpoConfig => ({
  ...config,
  name: "My App",
  slug: "my-app",
  version: "1.2.0",
  ios: {
    bundleIdentifier: "com.example.myapp",
    supportsTablet: true,
    infoPlist: {
      NSCameraUsageDescription: "To scan documents and take photos.",
      NSPhotoLibraryUsageDescription: "To select images from the gallery.",
    },
    config: {
      usesNonExemptEncryption: false,
    },
  },
  android: {
    package: "com.example.myapp",
    adaptiveIcon: {
      foregroundImage: "./assets/adaptive-icon.png",
      backgroundColor: "#2563eb",
    },
    permissions: [
      "CAMERA",
      "READ_EXTERNAL_STORAGE",
      "WRITE_EXTERNAL_STORAGE",
    ],
  },
  plugins: [
    "expo-router",
    "expo-secure-store",
    [
      "expo-camera",
      { cameraPermission: "Allow access to the camera for document scanning." },
    ],
    [
      "expo-notifications",
      {
        icon: "./assets/notification-icon.png",
        color: "#2563eb",
        sounds: ["./assets/notification.wav"],
      },
    ],
  ],
});
```

### Creating a Native Module Bridge (Bare Workflow)

```tsx
// When Expo modules do not cover a requirement, create a native bridge.
// This pattern applies to the bare React Native workflow.

// NativeHelloModule.ts
import { NativeModules, Platform } from "react-native";

const { HelloModule } = NativeModules;

interface HelloModuleInterface {
  greet(name: string): Promise<string>;
  getDeviceInfo(): Promise<{ model: string; osVersion: string }>;
}

// Provide a fallback for platforms that do not have the native module
const NativeHello: HelloModuleInterface =
  Platform.OS === "web"
    ? {
        greet: async (name: string) => ,
        getDeviceInfo: async () => ({ model: "web", osVersion: "n/a" }),
      }
    : HelloModule;

export default NativeHello;
```

---

## 8. Push Notifications

### Expo Notifications Full Setup

```tsx
// services/notifications.ts
import * as Notifications from "expo-notifications";
import * as Device from "expo-device";
import { Platform } from "react-native";
import Constants from "expo-constants";

// Configure default notification behavior
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export async function registerForPushNotifications(): Promise<string | null> {
  if (\!Device.isDevice) {
    console.warn("Push notifications require a physical device.");
    return null;
  }

  // Check existing permissions
  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  // Request permissions if not granted
  if (existingStatus \!== "granted") {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus \!== "granted") {
    console.warn("Push notification permission denied.");
    return null;
  }

  // Android notification channel setup
  if (Platform.OS === "android") {
    await Notifications.setNotificationChannelAsync("default", {
      name: "Default",
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: "#2563eb",
    });

    await Notifications.setNotificationChannelAsync("reminders", {
      name: "Reminders",
      importance: Notifications.AndroidImportance.HIGH,
      sound: "notification.wav",
    });
  }

  // Get the Expo push token
  const projectId = Constants.expoConfig?.extra?.eas?.projectId;
  const tokenData = await Notifications.getExpoPushTokenAsync({ projectId });
  return tokenData.data;
}

export async function sendTokenToServer(token: string): Promise<void> {
  await fetch("https://api.example.com/push-tokens", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, platform: Platform.OS }),
  });
}

export async function scheduleLocalNotification(
  title: string,
  body: string,
  delaySeconds: number,
): Promise<string> {
  const id = await Notifications.scheduleNotificationAsync({
    content: {
      title,
      body,
      sound: true,
      data: { screen: "Home" },
    },
    trigger: { seconds: delaySeconds },
  });
  return id;
}
```

### Notification Listener Hook

```tsx
// hooks/useNotifications.ts
import { useEffect, useRef } from "react";
import * as Notifications from "expo-notifications";

export function useNotificationListeners(
  onNotificationReceived?: (notification: Notifications.Notification) => void,
  onNotificationResponse?: (response: Notifications.NotificationResponse) => void,
) {
  const receivedListener = useRef<Notifications.Subscription>();
  const responseListener = useRef<Notifications.Subscription>();

  useEffect(() => {
    receivedListener.current = Notifications.addNotificationReceivedListener(
      (notification) => {
        onNotificationReceived?.(notification);
      },
    );

    responseListener.current = Notifications.addNotificationResponseReceivedListener(
      (response) => {
        const screen = response.notification.request.content.data?.screen;
        if (screen) {
          // Navigate to the appropriate screen based on notification data
          // navigation.navigate(screen);
        }
        onNotificationResponse?.(response);
      },
    );

    return () => {
      receivedListener.current?.remove();
      responseListener.current?.remove();
    };
  }, [onNotificationReceived, onNotificationResponse]);
}
```

---

## 9. App Store Preparation

### app.json Production Configuration

```json
{
  "expo": {
    "name": "My App",
    "slug": "my-app",
    "version": "1.2.0",
    "runtimeVersion": {
      "policy": "appVersion"
    },
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#2563eb"
    },
    "userInterfaceStyle": "automatic",
    "scheme": "myapp",
    "updates": {
      "url": "https://u.expo.dev/your-project-id"
    },
    "ios": {
      "bundleIdentifier": "com.example.myapp",
      "buildNumber": "42",
      "supportsTablet": true,
      "config": {
        "usesNonExemptEncryption": false
      },
      "infoPlist": {
        "ITSAppUsesNonExemptEncryption": false,
        "LSApplicationQueriesSchemes": ["mailto", "tel"],
        "UIBackgroundModes": ["remote-notification"]
      },
      "associatedDomains": ["applinks:myapp.example.com"],
      "privacyManifests": {
        "NSPrivacyAccessedAPITypes": [
          {
            "NSPrivacyAccessedAPIType": "NSPrivacyAccessedAPICategoryUserDefaults",
            "NSPrivacyAccessedAPITypeReasons": ["CA92.1"]
          }
        ]
      }
    },
    "android": {
      "package": "com.example.myapp",
      "versionCode": 42,
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundImage": "./assets/adaptive-icon-bg.png"
      },
      "intentFilters": [
        {
          "action": "VIEW",
          "autoVerify": true,
          "data": [
            {
              "scheme": "https",
              "host": "myapp.example.com",
              "pathPrefix": "/item"
            }
          ],
          "category": ["BROWSABLE", "DEFAULT"]
        }
      ]
    }
  }
}
```

### Asset Preparation Checklist

```
Required assets and their dimensions:

iOS App Icon:
  icon.png              - 1024x1024 px (no transparency, no rounded corners)

Android Adaptive Icon:
  adaptive-icon.png     - 1024x1024 px (foreground, centered in safe zone)
  adaptive-icon-bg.png  - 1024x1024 px (background layer, or use backgroundColor)

Splash Screen:
  splash.png            - 1284x2778 px (iPhone 14 Pro Max size, content centered)

Notification Icon (Android):
  notification-icon.png - 96x96 px (white on transparent, used in status bar)

App Store Screenshots (capture with eas submit or manually):
  iPhone 6.7"           - 1290x2796 px
  iPhone 6.5"           - 1284x2778 px
  iPad 12.9"            - 2048x2732 px
  Android Phone         - 1080x1920 px (minimum)
```

### Over-the-Air Updates with EAS Update

```bash
# Publish an update to the preview channel
eas update --branch preview --message "Fix login button alignment"

# Publish an update to production
eas update --branch production --message "Hotfix: correct price display"
```

---

## 10. Testing

### Unit and Component Testing with Jest and RNTL

```tsx
// __tests__/components/Button.test.tsx
import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react-native";
import { Button } from "../../src/components/ui/Button";

describe("Button", () => {
  it("renders the title text", () => {
    render(<Button title="Submit" onPress={() => {}} />);
    expect(screen.getByText("Submit")).toBeTruthy();
  });

  it("calls onPress when tapped", () => {
    const onPress = jest.fn();
    render(<Button title="Submit" onPress={onPress} />);

    fireEvent.press(screen.getByText("Submit"));
    expect(onPress).toHaveBeenCalledTimes(1);
  });

  it("does not call onPress when disabled", () => {
    const onPress = jest.fn();
    render(<Button title="Submit" onPress={onPress} disabled />);

    fireEvent.press(screen.getByText("Submit"));
    expect(onPress).not.toHaveBeenCalled();
  });

  it("shows a loading indicator when loading", () => {
    render(<Button title="Submit" onPress={() => {}} loading />);
    expect(screen.queryByText("Submit")).toBeNull();
    expect(screen.getByTestId("activity-indicator")).toBeTruthy();
  });
});
```

### Screen Testing with Mocked API

```tsx
// __tests__/features/home/HomeScreen.test.tsx
import React from "react";
import { render, screen, waitFor } from "@testing-library/react-native";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import HomeScreen from "../../../src/features/home/screens/HomeScreen";

jest.mock("../../../src/features/home/api", () => ({
  useItems: jest.fn(),
}));

import { useItems } from "../../../src/features/home/api";

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>,
  );
}

describe("HomeScreen", () => {
  it("displays loading state initially", () => {
    (useItems as jest.Mock).mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    });

    renderWithProviders(<HomeScreen />);
    expect(screen.getByTestId("loading-skeleton")).toBeTruthy();
  });

  it("renders the list of items after loading", async () => {
    (useItems as jest.Mock).mockReturnValue({
      data: [
        { id: "1", title: "First", description: "Description 1" },
        { id: "2", title: "Second", description: "Description 2" },
      ],
      isLoading: false,
      error: null,
    });

    renderWithProviders(<HomeScreen />);

    await waitFor(() => {
      expect(screen.getByText("First")).toBeTruthy();
      expect(screen.getByText("Second")).toBeTruthy();
    });
  });

  it("displays an error message on failure", () => {
    (useItems as jest.Mock).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error("Network error"),
    });

    renderWithProviders(<HomeScreen />);
    expect(screen.getByText(/something went wrong/i)).toBeTruthy();
  });
});
```

### Store Testing

```tsx
// __tests__/stores/authStore.test.ts
import { useAuthStore } from "../../src/stores/authStore";
import { act } from "@testing-library/react-native";

describe("authStore", () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: null,
      token: null,
      isAuthenticated: false,
    });
  });

  it("sets authentication state correctly", () => {
    act(() => {
      useAuthStore.getState().setAuth(
        { id: "1", email: "test@example.com", name: "Test User" },
        "mock-jwt-token",
      );
    });

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(true);
    expect(state.user?.email).toBe("test@example.com");
    expect(state.token).toBe("mock-jwt-token");
  });

  it("clears state on logout", () => {
    act(() => {
      useAuthStore.getState().setAuth(
        { id: "1", email: "test@example.com", name: "Test User" },
        "token",
      );
      useAuthStore.getState().logout();
    });

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.user).toBeNull();
    expect(state.token).toBeNull();
  });
});
```

### End-to-End Testing with Detox

```tsx
// e2e/login.e2e.ts
import { device, element, by, expect, waitFor } from "detox";

describe("Login Flow", () => {
  beforeAll(async () => {
    await device.launchApp({ newInstance: true });
  });

  beforeEach(async () => {
    await device.reloadReactNative();
  });

  it("should show the login screen on launch", async () => {
    await expect(element(by.id("login-screen"))).toBeVisible();
    await expect(element(by.id("email-input"))).toBeVisible();
    await expect(element(by.id("password-input"))).toBeVisible();
  });

  it("should display validation errors for empty fields", async () => {
    await element(by.id("login-button")).tap();

    await waitFor(element(by.text("Email is required")))
      .toBeVisible()
      .withTimeout(2000);
  });

  it("should log in successfully with valid credentials", async () => {
    await element(by.id("email-input")).typeText("test@example.com");
    await element(by.id("password-input")).typeText("password123");
    await element(by.id("login-button")).tap();

    await waitFor(element(by.id("home-screen")))
      .toBeVisible()
      .withTimeout(5000);
  });

  it("should navigate through tabs after login", async () => {
    await element(by.id("email-input")).typeText("test@example.com");
    await element(by.id("password-input")).typeText("password123");
    await element(by.id("login-button")).tap();

    await waitFor(element(by.id("home-screen")))
      .toBeVisible()
      .withTimeout(5000);

    await element(by.id("tab-profile")).tap();
    await expect(element(by.id("profile-screen"))).toBeVisible();

    await element(by.id("tab-search")).tap();
    await expect(element(by.id("search-screen"))).toBeVisible();
  });
});
```

### Detox Configuration

```javascript
// .detoxrc.js
/** @type {Detox.DetoxConfig} */
module.exports = {
  testRunner: {
    args: {
      /usr/bin/bash: "jest",
      config: "e2e/jest.config.js",
    },
    jest: {
      setupTimeout: 120000,
    },
  },
  apps: {
    "ios.debug": {
      type: "ios.app",
      binaryPath: "ios/build/Build/Products/Debug-iphonesimulator/MyApp.app",
      build:
        "xcodebuild -workspace ios/MyApp.xcworkspace -scheme MyApp -configuration Debug -sdk iphonesimulator -derivedDataPath ios/build",
    },
    "android.debug": {
      type: "android.apk",
      binaryPath: "android/app/build/outputs/apk/debug/app-debug.apk",
      build:
        "cd android && ./gradlew assembleDebug assembleAndroidTest -DtestBuildType=debug",
      reversePorts: [8081],
    },
  },
  devices: {
    simulator: {
      type: "ios.simulator",
      device: { type: "iPhone 15" },
    },
    emulator: {
      type: "android.emulator",
      device: { avdName: "Pixel_7_API_34" },
    },
  },
  configurations: {
    "ios.sim.debug": {
      device: "simulator",
      app: "ios.debug",
    },
    "android.emu.debug": {
      device: "emulator",
      app: "android.debug",
    },
  },
};
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Start dev server | `npx expo start` |
| Run on iOS simulator | `npx expo run:ios` |
| Run on Android emulator | `npx expo run:android` |
| Install a library | `npx expo install <package>` |
| Build (dev) | `eas build --profile development` |
| Build (prod) | `eas build --profile production` |
| OTA update | `eas update --branch production` |
| Submit to stores | `eas submit --platform all` |
| Run unit tests | `npx jest` |
| Run E2E tests | `npx detox test --configuration ios.sim.debug` |
| Check for issues | `npx expo-doctor` |
| Upgrade Expo SDK | `npx expo install expo@latest --fix` |
