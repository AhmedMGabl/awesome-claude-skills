---
name: ionic-capacitor
description: Ionic Capacitor patterns covering cross-platform mobile apps, native device APIs, Ionic React/Angular/Vue components, navigation with IonRouter, native plugins, app lifecycle, and iOS/Android deployment.
---

# Ionic Capacitor

This skill should be used when building cross-platform mobile apps with Ionic Framework and Capacitor. It covers components, native APIs, navigation, plugins, and deployment.

## When to Use This Skill

Use this skill when you need to:

- Build cross-platform mobile apps with web technologies
- Access native device APIs (camera, filesystem, push notifications)
- Use Ionic UI components for mobile-optimized UX
- Deploy to iOS, Android, and web from one codebase
- Integrate native Capacitor plugins

## Setup

```bash
npm install @ionic/react @ionic/react-router
npm install @capacitor/core @capacitor/cli
npx cap init
npx cap add ios
npx cap add android
```

## Navigation with Tabs

```tsx
import {
  IonApp, IonRouterOutlet, IonTabs, IonTabBar, IonTabButton,
  IonIcon, IonLabel, setupIonicReact,
} from "@ionic/react";
import { IonReactRouter } from "@ionic/react-router";
import { Route, Redirect } from "react-router-dom";
import { home, person, settings } from "ionicons/icons";

setupIonicReact();

function App() {
  return (
    <IonApp>
      <IonReactRouter>
        <IonTabs>
          <IonRouterOutlet>
            <Route exact path="/home" component={HomePage} />
            <Route exact path="/profile" component={ProfilePage} />
            <Route exact path="/settings" component={SettingsPage} />
            <Route exact path="/">
              <Redirect to="/home" />
            </Route>
          </IonRouterOutlet>
          <IonTabBar slot="bottom">
            <IonTabButton tab="home" href="/home">
              <IonIcon icon={home} />
              <IonLabel>Home</IonLabel>
            </IonTabButton>
            <IonTabButton tab="profile" href="/profile">
              <IonIcon icon={person} />
              <IonLabel>Profile</IonLabel>
            </IonTabButton>
            <IonTabButton tab="settings" href="/settings">
              <IonIcon icon={settings} />
              <IonLabel>Settings</IonLabel>
            </IonTabButton>
          </IonTabBar>
        </IonTabs>
      </IonReactRouter>
    </IonApp>
  );
}
```

## List Page with Pull-to-Refresh

```tsx
import {
  IonPage, IonHeader, IonToolbar, IonTitle, IonContent,
  IonList, IonItem, IonLabel, IonAvatar, IonRefresher,
  IonRefresherContent, IonSearchbar, IonInfiniteScroll,
  IonInfiniteScrollContent,
} from "@ionic/react";
import { useState } from "react";

function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [search, setSearch] = useState("");

  async function handleRefresh(event: CustomEvent) {
    const data = await fetchUsers();
    setUsers(data);
    event.detail.complete();
  }

  async function loadMore(event: CustomEvent) {
    const moreUsers = await fetchUsers({ offset: users.length });
    setUsers((prev) => [...prev, ...moreUsers]);
    (event.target as HTMLIonInfiniteScrollElement).complete();
  }

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonTitle>Users</IonTitle>
        </IonToolbar>
        <IonToolbar>
          <IonSearchbar value={search} onIonInput={(e) => setSearch(e.detail.value!)} />
        </IonToolbar>
      </IonHeader>
      <IonContent>
        <IonRefresher slot="fixed" onIonRefresh={handleRefresh}>
          <IonRefresherContent />
        </IonRefresher>

        <IonList>
          {users.map((user) => (
            <IonItem key={user.id} routerLink={`/users/${user.id}`}>
              <IonAvatar slot="start">
                <img src={user.avatar} alt={user.name} />
              </IonAvatar>
              <IonLabel>
                <h2>{user.name}</h2>
                <p>{user.email}</p>
              </IonLabel>
            </IonItem>
          ))}
        </IonList>

        <IonInfiniteScroll onIonInfinite={loadMore}>
          <IonInfiniteScrollContent loadingText="Loading more..." />
        </IonInfiniteScroll>
      </IonContent>
    </IonPage>
  );
}
```

## Camera Plugin

```tsx
import { Camera, CameraResultType, CameraSource } from "@capacitor/camera";

async function takePhoto() {
  const image = await Camera.getPhoto({
    quality: 90,
    allowEditing: true,
    resultType: CameraResultType.Uri,
    source: CameraSource.Camera,
  });

  return image.webPath;
}

async function pickFromGallery() {
  const image = await Camera.getPhoto({
    quality: 90,
    resultType: CameraResultType.Base64,
    source: CameraSource.Photos,
  });

  return `data:image/jpeg;base64,${image.base64String}`;
}
```

## Push Notifications

```tsx
import { PushNotifications } from "@capacitor/push-notifications";

async function initPushNotifications() {
  const permission = await PushNotifications.requestPermissions();
  if (permission.receive !== "granted") return;

  await PushNotifications.register();

  PushNotifications.addListener("registration", (token) => {
    sendTokenToServer(token.value);
  });

  PushNotifications.addListener("pushNotificationReceived", (notification) => {
    console.log("Push received:", notification.title, notification.body);
  });

  PushNotifications.addListener("pushNotificationActionPerformed", (action) => {
    const data = action.notification.data;
    navigateTo(data.route);
  });
}
```

## Action Sheet and Alerts

```tsx
import { useIonActionSheet, useIonAlert } from "@ionic/react";

function ItemActions() {
  const [presentActionSheet] = useIonActionSheet();
  const [presentAlert] = useIonAlert();

  function showActions() {
    presentActionSheet({
      header: "Actions",
      buttons: [
        { text: "Share", handler: () => shareItem() },
        { text: "Edit", handler: () => editItem() },
        { text: "Delete", role: "destructive", handler: () => confirmDelete() },
        { text: "Cancel", role: "cancel" },
      ],
    });
  }

  function confirmDelete() {
    presentAlert({
      header: "Delete Item",
      message: "This action cannot be undone.",
      buttons: [
        { text: "Cancel", role: "cancel" },
        { text: "Delete", role: "destructive", handler: () => deleteItem() },
      ],
    });
  }
}
```

## Build and Deploy

```bash
# Build web assets
ionic build

# Sync to native projects
npx cap sync

# Open in IDE
npx cap open ios
npx cap open android

# Live reload during development
ionic cap run ios --livereload --external
ionic cap run android --livereload --external
```

## Additional Resources

- Ionic: https://ionicframework.com/docs
- Capacitor: https://capacitorjs.com/docs
- Capacitor Plugins: https://capacitorjs.com/docs/plugins
