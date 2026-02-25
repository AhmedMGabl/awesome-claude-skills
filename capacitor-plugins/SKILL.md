---
name: capacitor-plugins
description: Capacitor native plugin patterns covering Camera, Filesystem, Geolocation, Push Notifications, Haptics, App Launcher, Biometrics, Share, local notifications, and custom native plugin creation for iOS and Android.
---

# Capacitor Plugins

This skill should be used when accessing native device features with Capacitor plugins. It covers camera, filesystem, geolocation, push notifications, biometrics, and custom plugin creation.

## When to Use This Skill

Use this skill when you need to:

- Access camera, photos, and file system on mobile
- Implement push notifications and local notifications
- Use geolocation, haptics, and device sensors
- Add biometric authentication (Face ID, fingerprint)
- Create custom native plugins for iOS and Android

## Camera

```typescript
import { Camera, CameraResultType, CameraSource } from "@capacitor/camera";

async function takePhoto() {
  const image = await Camera.getPhoto({
    quality: 90,
    resultType: CameraResultType.Uri,
    source: CameraSource.Camera,
    allowEditing: false,
    width: 1024,
    height: 1024,
  });

  return image.webPath; // Displayable in <img src="">
}

async function pickFromGallery() {
  const images = await Camera.pickImages({
    quality: 80,
    limit: 5,
  });

  return images.photos.map((p) => p.webPath);
}

// Check and request permissions
async function checkCameraPermission() {
  const status = await Camera.checkPermissions();
  if (status.camera !== "granted") {
    const request = await Camera.requestPermissions({ permissions: ["camera"] });
    return request.camera === "granted";
  }
  return true;
}
```

## Filesystem

```typescript
import { Filesystem, Directory, Encoding } from "@capacitor/filesystem";

// Write file
async function writeFile(filename: string, data: string) {
  await Filesystem.writeFile({
    path: filename,
    data,
    directory: Directory.Documents,
    encoding: Encoding.UTF8,
  });
}

// Read file
async function readFile(filename: string) {
  const result = await Filesystem.readFile({
    path: filename,
    directory: Directory.Documents,
    encoding: Encoding.UTF8,
  });
  return result.data as string;
}

// List directory
async function listFiles(path: string = "") {
  const result = await Filesystem.readdir({
    path,
    directory: Directory.Documents,
  });
  return result.files;
}

// Download file
async function downloadFile(url: string, filename: string) {
  const response = await fetch(url);
  const blob = await response.blob();
  const base64 = await blobToBase64(blob);

  await Filesystem.writeFile({
    path: `downloads/${filename}`,
    data: base64,
    directory: Directory.Documents,
  });
}

// Delete file
async function deleteFile(filename: string) {
  await Filesystem.deleteFile({
    path: filename,
    directory: Directory.Documents,
  });
}
```

## Geolocation

```typescript
import { Geolocation } from "@capacitor/geolocation";

// Get current position
async function getCurrentPosition() {
  const position = await Geolocation.getCurrentPosition({
    enableHighAccuracy: true,
    timeout: 10000,
  });

  return {
    lat: position.coords.latitude,
    lng: position.coords.longitude,
    accuracy: position.coords.accuracy,
  };
}

// Watch position
function watchPosition(callback: (lat: number, lng: number) => void) {
  const watchId = Geolocation.watchPosition(
    { enableHighAccuracy: true },
    (position, err) => {
      if (err) {
        console.error(err);
        return;
      }
      if (position) {
        callback(position.coords.latitude, position.coords.longitude);
      }
    },
  );

  // Return cleanup function
  return () => Geolocation.clearWatch({ id: watchId });
}
```

## Push Notifications

```typescript
import { PushNotifications } from "@capacitor/push-notifications";

async function initPushNotifications() {
  // Request permission
  const permission = await PushNotifications.requestPermissions();
  if (permission.receive !== "granted") return;

  // Register with APNS/FCM
  await PushNotifications.register();

  // Get device token
  PushNotifications.addListener("registration", (token) => {
    console.log("Push token:", token.value);
    // Send token to your server
    sendTokenToServer(token.value);
  });

  PushNotifications.addListener("registrationError", (error) => {
    console.error("Registration error:", error.error);
  });

  // Handle received notification
  PushNotifications.addListener("pushNotificationReceived", (notification) => {
    console.log("Notification received:", notification);
    // Show in-app notification
  });

  // Handle notification tap
  PushNotifications.addListener("pushNotificationActionPerformed", (action) => {
    const data = action.notification.data;
    // Navigate to relevant screen
    router.push(data.deepLink);
  });
}
```

## Local Notifications

```typescript
import { LocalNotifications } from "@capacitor/local-notifications";

async function scheduleNotification(title: string, body: string, delayMs: number) {
  await LocalNotifications.schedule({
    notifications: [
      {
        id: Date.now(),
        title,
        body,
        schedule: { at: new Date(Date.now() + delayMs) },
        extra: { route: "/reminders" },
      },
    ],
  });
}

// Repeating notification
async function scheduleDailyReminder() {
  await LocalNotifications.schedule({
    notifications: [
      {
        id: 1001,
        title: "Daily Reminder",
        body: "Don't forget to check your tasks!",
        schedule: {
          on: { hour: 9, minute: 0 },
          repeats: true,
        },
      },
    ],
  });
}

// Handle notification tap
LocalNotifications.addListener("localNotificationActionPerformed", (action) => {
  const route = action.notification.extra?.route;
  if (route) router.push(route);
});
```

## Haptics

```typescript
import { Haptics, ImpactStyle, NotificationType } from "@capacitor/haptics";

// Impact feedback
async function lightImpact() {
  await Haptics.impact({ style: ImpactStyle.Light });
}

async function heavyImpact() {
  await Haptics.impact({ style: ImpactStyle.Heavy });
}

// Notification feedback
async function successHaptic() {
  await Haptics.notification({ type: NotificationType.Success });
}

async function errorHaptic() {
  await Haptics.notification({ type: NotificationType.Error });
}

// Selection feedback (for scrolling/picking)
async function selectionHaptic() {
  await Haptics.selectionStart();
  // During selection changes:
  await Haptics.selectionChanged();
  // When selection ends:
  await Haptics.selectionEnd();
}
```

## Share and App

```typescript
import { Share } from "@capacitor/share";
import { App } from "@capacitor/app";
import { Browser } from "@capacitor/browser";

// Share content
async function shareContent(title: string, text: string, url?: string) {
  await Share.share({ title, text, url, dialogTitle: "Share with..." });
}

// Listen for app state changes
App.addListener("appStateChange", ({ isActive }) => {
  if (isActive) {
    // App came to foreground — refresh data
    refreshData();
  }
});

// Handle deep links
App.addListener("appUrlOpen", (event) => {
  const path = new URL(event.url).pathname;
  router.push(path);
});

// Open external link in in-app browser
async function openLink(url: string) {
  await Browser.open({ url, presentationStyle: "popover" });
}
```

## Additional Resources

- Capacitor docs: https://capacitorjs.com/docs
- Official plugins: https://capacitorjs.com/docs/apis
- Community plugins: https://github.com/capacitor-community
