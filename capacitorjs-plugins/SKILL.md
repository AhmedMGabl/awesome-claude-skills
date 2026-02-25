---
name: capacitorjs-plugins
description: CapacitorJS patterns covering native plugin development, web-to-native bridge, camera, filesystem, push notifications, deep links, and app lifecycle hooks.
---

# CapacitorJS Plugins

This skill should be used when building hybrid mobile apps with CapacitorJS. It covers native plugins, web-to-native bridge, camera, filesystem, notifications, deep links, and lifecycle hooks.

## When to Use This Skill

Use this skill when you need to:

- Access native device features from a web app
- Create custom Capacitor plugins
- Use camera, filesystem, and push notifications
- Handle deep links and app URL schemes
- Manage app lifecycle (foreground/background)

## Setup

```bash
npm install @capacitor/core @capacitor/cli
npx cap init
npm install @capacitor/android @capacitor/ios
npx cap add android
npx cap add ios
```

## Capacitor Configuration

```typescript
// capacitor.config.ts
import { CapacitorConfig } from "@capacitor/cli";

const config: CapacitorConfig = {
  appId: "com.example.myapp",
  appName: "MyApp",
  webDir: "dist",
  server: {
    androidScheme: "https",
  },
  plugins: {
    PushNotifications: {
      presentationOptions: ["badge", "sound", "alert"],
    },
    SplashScreen: {
      launchAutoHide: true,
      androidSplashResourceName: "splash",
    },
  },
};

export default config;
```

## Camera

```typescript
import { Camera, CameraResultType, CameraSource } from "@capacitor/camera";

async function takePicture(): Promise<string | undefined> {
  const image = await Camera.getPhoto({
    quality: 90,
    allowEditing: true,
    resultType: CameraResultType.Base64,
    source: CameraSource.Camera,
  });

  return image.base64String;
}

async function pickFromGallery(): Promise<string | undefined> {
  const image = await Camera.getPhoto({
    quality: 90,
    resultType: CameraResultType.Uri,
    source: CameraSource.Photos,
  });

  return image.webPath;
}
```

## Filesystem

```typescript
import { Filesystem, Directory, Encoding } from "@capacitor/filesystem";

async function writeFile(filename: string, content: string) {
  await Filesystem.writeFile({
    path: filename,
    data: content,
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

async function listFiles(): Promise<string[]> {
  const result = await Filesystem.readdir({
    path: "",
    directory: Directory.Documents,
  });
  return result.files.map((f) => f.name);
}
```

## Push Notifications

```typescript
import { PushNotifications } from "@capacitor/push-notifications";

async function registerNotifications() {
  const permission = await PushNotifications.requestPermissions();
  if (permission.receive !== "granted") return;

  await PushNotifications.register();

  PushNotifications.addListener("registration", (token) => {
    console.log("Push token:", token.value);
    // Send token to backend
  });

  PushNotifications.addListener("pushNotificationReceived", (notification) => {
    console.log("Notification received:", notification);
  });

  PushNotifications.addListener("pushNotificationActionPerformed", (action) => {
    console.log("Action performed:", action.notification);
    // Navigate based on notification data
  });
}
```

## App Lifecycle

```typescript
import { App } from "@capacitor/app";

App.addListener("appStateChange", ({ isActive }) => {
  if (isActive) {
    console.log("App came to foreground");
    // Refresh data
  } else {
    console.log("App went to background");
    // Save state
  }
});

App.addListener("appUrlOpen", ({ url }) => {
  console.log("Deep link:", url);
  // Handle deep link routing
});

App.addListener("backButton", ({ canGoBack }) => {
  if (!canGoBack) {
    App.exitApp();
  } else {
    window.history.back();
  }
});
```

## Custom Plugin

```typescript
// definitions.ts
export interface EchoPlugin {
  echo(options: { value: string }): Promise<{ value: string }>;
}

// web.ts
import { WebPlugin } from "@capacitor/core";
import type { EchoPlugin } from "./definitions";

export class EchoWeb extends WebPlugin implements EchoPlugin {
  async echo(options: { value: string }): Promise<{ value: string }> {
    return options;
  }
}
```

```java
// android/src/main/java/com/example/EchoPlugin.java
@CapacitorPlugin(name = "Echo")
public class EchoPlugin extends Plugin {
    @PluginMethod
    public void echo(PluginCall call) {
        String value = call.getString("value");
        JSObject ret = new JSObject();
        ret.put("value", value);
        call.resolve(ret);
    }
}
```

## Build & Deploy

```bash
# Sync web assets to native projects
npx cap sync

# Open native IDE
npx cap open android
npx cap open ios

# Live reload during development
npx cap run android --livereload --external
```

## Additional Resources

- Capacitor Docs: https://capacitorjs.com/docs
- Official Plugins: https://capacitorjs.com/docs/apis
- Plugin Guide: https://capacitorjs.com/docs/plugins
