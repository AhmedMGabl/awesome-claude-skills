---
name: capacitor-mobile
description: Capacitor cross-platform mobile development covering project setup, native plugins (Camera, Filesystem, Push Notifications), custom native plugins, deep linking, app lifecycle, live reload, and deployment to iOS and Android app stores.
---

# Capacitor Mobile

This skill should be used when building cross-platform mobile apps with Capacitor. It covers native plugins, custom plugin creation, deep linking, and app store deployment.

## When to Use This Skill

Use this skill when you need to:

- Convert web apps to native iOS/Android apps
- Access native device features (camera, filesystem, push)
- Create custom native plugins
- Configure deep links and universal links
- Deploy to Apple App Store and Google Play

## Project Setup

```bash
npm install @capacitor/core @capacitor/cli
npx cap init "MyApp" "com.example.myapp"
npm install @capacitor/ios @capacitor/android
npx cap add ios
npx cap add android
```

## Capacitor Configuration

```typescript
// capacitor.config.ts
import type { CapacitorConfig } from "@capacitor/cli";

const config: CapacitorConfig = {
  appId: "com.example.myapp",
  appName: "MyApp",
  webDir: "dist",
  server: {
    androidScheme: "https",
    // Live reload in development
    ...(process.env.NODE_ENV === "development" && {
      url: "http://192.168.1.100:5173",
      cleartext: true,
    }),
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: "#ffffff",
    },
    PushNotifications: {
      presentationOptions: ["badge", "sound", "alert"],
    },
  },
};

export default config;
```

## Camera Plugin

```typescript
import { Camera, CameraResultType, CameraSource } from "@capacitor/camera";

async function takePhoto() {
  const image = await Camera.getPhoto({
    quality: 90,
    allowEditing: false,
    resultType: CameraResultType.Uri,
    source: CameraSource.Camera,
  });

  return image.webPath; // Use in <img src="">
}

async function pickFromGallery() {
  const images = await Camera.pickImages({
    quality: 80,
    limit: 5,
  });

  return images.photos.map((p) => p.webPath);
}
```

## Filesystem

```typescript
import { Filesystem, Directory, Encoding } from "@capacitor/filesystem";

async function writeFile(filename: string, data: string) {
  await Filesystem.writeFile({
    path: filename,
    data,
    directory: Directory.Documents,
    encoding: Encoding.UTF8,
  });
}

async function readFile(filename: string): Promise<string> {
  const result = await Filesystem.readFile({
    path: filename,
    directory: Directory.Documents,
    encoding: Encoding.UTF8,
  });
  return result.data as string;
}

async function listFiles(directory: string) {
  const result = await Filesystem.readdir({
    path: directory,
    directory: Directory.Documents,
  });
  return result.files;
}
```

## Push Notifications

```typescript
import { PushNotifications } from "@capacitor/push-notifications";

async function initPush() {
  const permission = await PushNotifications.requestPermissions();
  if (permission.receive !== "granted") return;

  await PushNotifications.register();

  PushNotifications.addListener("registration", (token) => {
    console.log("FCM Token:", token.value);
    // Send token to your backend
    api.registerDevice(token.value);
  });

  PushNotifications.addListener("pushNotificationReceived", (notification) => {
    console.log("Push received:", notification.title, notification.body);
  });

  PushNotifications.addListener("pushNotificationActionPerformed", (action) => {
    const data = action.notification.data;
    // Navigate based on notification data
    if (data.route) router.push(data.route);
  });
}
```

## App Lifecycle

```typescript
import { App } from "@capacitor/app";

// Handle back button (Android)
App.addListener("backButton", ({ canGoBack }) => {
  if (canGoBack) {
    window.history.back();
  } else {
    App.exitApp();
  }
});

// App state changes
App.addListener("appStateChange", ({ isActive }) => {
  if (isActive) {
    // App came to foreground — refresh data
    refreshData();
  }
});

// Deep link handling
App.addListener("appUrlOpen", ({ url }) => {
  const path = new URL(url).pathname;
  router.push(path);
});
```

## Build and Deploy

```bash
# Build web assets
npm run build

# Sync to native projects
npx cap sync

# Open in native IDE
npx cap open ios      # Opens Xcode
npx cap open android  # Opens Android Studio

# Live reload during development
npx cap run ios --livereload --external
npx cap run android --livereload --external
```

## Additional Resources

- Capacitor docs: https://capacitorjs.com/docs
- Capacitor plugins: https://capacitorjs.com/docs/plugins
