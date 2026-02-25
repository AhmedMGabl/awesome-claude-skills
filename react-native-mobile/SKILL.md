---
name: react-native-mobile
description: This skill should be used when building cross-platform mobile applications with React Native. It covers Expo setup, core components, React Navigation (stack/tabs/drawer), responsive styling, platform-specific code, native modules, push notifications, AsyncStorage, Reanimated animations, and app store deployment.
---

# React Native Mobile Development

## Expo Project Setup

```bash
npx create-expo-app@latest my-app --template blank-typescript
cd my-app
npx expo install expo-router react-native-reanimated react-native-gesture-handler \
  react-native-screens react-native-safe-area-context \
  @react-native-async-storage/async-storage expo-notifications expo-device expo-constants
```

## Core Components (View, Text, FlatList, ScrollView)

```tsx
import { View, Text, FlatList, ScrollView, Pressable, StyleSheet, RefreshControl } from "react-native";
interface Item { id: string; title: string; subtitle: string }
function ItemList({ items, onPress }: { items: Item[]; onPress: (id: string) => void }) {
  const [refreshing, setRefreshing] = React.useState(false);
  const onRefresh = React.useCallback(async () => { setRefreshing(true); /* fetch */ setRefreshing(false); }, []);
  return (
    <FlatList
      data={items}
      keyExtractor={(item) => item.id}
      renderItem={({ item }) => (
        <Pressable onPress={() => onPress(item.id)} style={({ pressed }) => [styles.card, pressed && { opacity: 0.8 }]}>
          <Text style={styles.title}>{item.title}</Text>
          <Text style={styles.subtitle}>{item.subtitle}</Text>
        </Pressable>
      )}
      ListEmptyComponent={<Text style={styles.empty}>No items found</Text>}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      removeClippedSubviews maxToRenderPerBatch={10} windowSize={5}
    />
  );
}
```

## Navigation (React Navigation Stack, Tabs, Drawer)

```tsx
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { createDrawerNavigator } from "@react-navigation/drawer";
import { useNavigation } from "@react-navigation/native";
import type { NativeStackNavigationProp } from "@react-navigation/native-stack";
type HomeStackParams = { Home: undefined; Details: { itemId: string } };
type TabParams = { HomeTab: undefined; Profile: undefined; Settings: undefined };
const HomeStack = createNativeStackNavigator<HomeStackParams>();
const Tab = createBottomTabNavigator<TabParams>();
const Drawer = createDrawerNavigator();
function HomeNavigator() {
  return (
    <HomeStack.Navigator>
      <HomeStack.Screen name="Home" component={HomeScreen} />
      <HomeStack.Screen name="Details" component={DetailsScreen}
        options={({ route }) => ({ title: `Item ${route.params.itemId}` })} />
    </HomeStack.Navigator>
  );
}
function MainTabs() {
  return (
    <Tab.Navigator screenOptions={{ headerShown: false, tabBarActiveTintColor: "#2563eb" }}>
      <Tab.Screen name="HomeTab" component={HomeNavigator} options={{ tabBarLabel: "Home" }} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
      <Tab.Screen name="Settings" component={SettingsScreen} />
    </Tab.Navigator>
  );
}
// Type-safe navigation: useNavigation<NativeStackNavigationProp<HomeStackParams>>()
```

## Styling (StyleSheet + Responsive Design)

```tsx
import { StyleSheet, Platform, useWindowDimensions } from "react-native";

function useResponsive() {
  const { width } = useWindowDimensions();
  return { isTablet: width >= 768, columns: width >= 1024 ? 3 : width >= 768 ? 2 : 1 };
}
const styles = StyleSheet.create({
  card: {
    backgroundColor: "#fff", padding: 16, borderRadius: 10, marginVertical: 6, marginHorizontal: 16,
    ...Platform.select({
      ios: { shadowColor: "#000", shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 8 },
      android: { elevation: 4 },
    }),
  },
  title: { fontSize: 16, fontWeight: "600", color: "#1e293b" },
  subtitle: { fontSize: 14, color: "#64748b", marginTop: 4 },
  empty: { textAlign: "center", color: "#94a3b8", padding: 48 },
});
```

## Platform-Specific Code and Native Modules

```tsx
import { Platform, Linking, NativeModules } from "react-native";
// File-based splitting: Component.ios.tsx / Component.android.tsx resolved automatically
function openAppSettings() {
  Platform.OS === "ios" ? Linking.openURL("app-settings:") : Linking.openSettings();
}
const fontFamily = Platform.select({ ios: "System", android: "Roboto", default: "System" });
// Native module bridge (bare workflow)
interface DeviceModuleInterface { getDeviceId(): Promise<string>; getBatteryLevel(): Promise<number> }
const DeviceModule: DeviceModuleInterface = Platform.OS === "web"
  ? { getDeviceId: async () => "web", getBatteryLevel: async () => -1 }
  : NativeModules.DeviceModule;
```

## Push Notifications (Expo)

```tsx
import * as Notifications from "expo-notifications";
import * as Device from "expo-device";
import Constants from "expo-constants";

Notifications.setNotificationHandler({
  handleNotification: async () => ({ shouldShowAlert: true, shouldPlaySound: true, shouldSetBadge: true }),
});
async function registerForPush(): Promise<string | null> {
  if (!Device.isDevice) return null;
  const { status } = await Notifications.requestPermissionsAsync();
  if (status !== "granted") return null;
  if (Platform.OS === "android") {
    await Notifications.setNotificationChannelAsync("default", { name: "Default", importance: Notifications.AndroidImportance.MAX });
  }
  const { data } = await Notifications.getExpoPushTokenAsync({ projectId: Constants.expoConfig?.extra?.eas?.projectId });
  return data;
}
```

## AsyncStorage

```tsx
import AsyncStorage from "@react-native-async-storage/async-storage";

async function saveUser(user: { id: string; name: string }) {
  await AsyncStorage.setItem("@user", JSON.stringify(user));
}
async function loadUser(): Promise<{ id: string; name: string } | null> {
  const json = await AsyncStorage.getItem("@user");
  return json ? JSON.parse(json) : null;
}
async function clearAll() { await AsyncStorage.clear(); }
```

## Animations (React Native Reanimated)

```tsx
import Animated, { useSharedValue, useAnimatedStyle, withSpring, FadeInDown } from "react-native-reanimated";
import { Gesture, GestureDetector } from "react-native-gesture-handler";

function AnimatedCard({ title, onPress }: { title: string; onPress: () => void }) {
  const scale = useSharedValue(1);
  const tap = Gesture.Tap()
    .onBegin(() => { "worklet"; scale.value = withSpring(0.95, { damping: 15 }); })
    .onFinalize(() => { "worklet"; scale.value = withSpring(1, { damping: 15 }); })
    .onEnd(onPress);
  const animStyle = useAnimatedStyle(() => ({ transform: [{ scale: scale.value }] }));
  return (
    <GestureDetector gesture={tap}>
      <Animated.View entering={FadeInDown.springify()} style={[styles.card, animStyle]}>
        <Text style={styles.title}>{title}</Text>
      </Animated.View>
    </GestureDetector>
  );
}
```

## App Store Deployment (EAS Build + Submit)

```bash
npm install -g eas-cli && eas login && eas build:configure
eas build --profile production --platform ios       # Build iOS binary
eas build --profile production --platform android   # Build Android binary
eas submit --platform ios                           # Submit to App Store
eas submit --platform android                       # Submit to Google Play
eas update --branch production --message "Hotfix"   # OTA JS-only update
```

Configure `eas.json` with `build` profiles (development, production) and `submit` settings containing Apple ID / Google service account credentials for each platform.

## Additional Resources

- React Native docs: https://reactnative.dev/docs/getting-started
- Expo documentation: https://docs.expo.dev/
- React Navigation: https://reactnavigation.org/docs/getting-started
- React Native Reanimated: https://docs.swmansion.com/react-native-reanimated/
- EAS Build and Submit: https://docs.expo.dev/build/introduction/
- AsyncStorage: https://react-native-async-storage.github.io/async-storage/
- Expo Notifications: https://docs.expo.dev/push-notifications/overview/
