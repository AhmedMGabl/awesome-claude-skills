---
name: ionic-framework
description: Ionic Framework covering cross-platform UI components, Capacitor native plugins, Angular/React/Vue integration, navigation patterns, theming, platform-specific styling, and app store deployment.
---

# Ionic Framework

This skill should be used when building cross-platform mobile and web applications with Ionic. It covers UI components, Capacitor plugins, framework integration, and native features.

## When to Use This Skill

Use this skill when you need to:

- Build cross-platform apps with web technologies
- Use pre-built mobile UI components
- Access native device features via Capacitor
- Deploy to iOS, Android, and web from one codebase
- Integrate with Angular, React, or Vue

## React Setup

```typescript
// App.tsx
import {
  IonApp, IonRouterOutlet, IonTabs, IonTabBar, IonTabButton,
  IonIcon, IonLabel, setupIonicReact,
} from "@ionic/react";
import { IonReactRouter } from "@ionic/react-router";
import { home, list, person } from "ionicons/icons";
import { Route, Redirect } from "react-router-dom";

import "@ionic/react/css/core.css";
import "@ionic/react/css/normalize.css";
import "@ionic/react/css/structure.css";
import "@ionic/react/css/typography.css";

setupIonicReact();

function App() {
  return (
    <IonApp>
      <IonReactRouter>
        <IonTabs>
          <IonRouterOutlet>
            <Route exact path="/home" component={HomePage} />
            <Route exact path="/list" component={ListPage} />
            <Route exact path="/profile" component={ProfilePage} />
            <Redirect exact from="/" to="/home" />
          </IonRouterOutlet>
          <IonTabBar slot="bottom">
            <IonTabButton tab="home" href="/home">
              <IonIcon icon={home} />
              <IonLabel>Home</IonLabel>
            </IonTabButton>
            <IonTabButton tab="list" href="/list">
              <IonIcon icon={list} />
              <IonLabel>List</IonLabel>
            </IonTabButton>
            <IonTabButton tab="profile" href="/profile">
              <IonIcon icon={person} />
              <IonLabel>Profile</IonLabel>
            </IonTabButton>
          </IonTabBar>
        </IonTabs>
      </IonReactRouter>
    </IonApp>
  );
}
```

## List with Actions

```tsx
import {
  IonPage, IonHeader, IonToolbar, IonTitle, IonContent,
  IonList, IonItem, IonLabel, IonItemSliding,
  IonItemOptions, IonItemOption, IonRefresher,
  IonRefresherContent, IonSearchbar,
} from "@ionic/react";

function ListPage() {
  const [items, setItems] = useState<Item[]>([]);
  const [search, setSearch] = useState("");

  const handleRefresh = async (event: CustomEvent) => {
    const data = await fetchItems();
    setItems(data);
    event.detail.complete();
  };

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonTitle>Items</IonTitle>
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
          {items.filter((i) => i.name.includes(search)).map((item) => (
            <IonItemSliding key={item.id}>
              <IonItem>
                <IonLabel>
                  <h2>{item.name}</h2>
                  <p>{item.description}</p>
                </IonLabel>
              </IonItem>
              <IonItemOptions side="end">
                <IonItemOption color="danger" onClick={() => deleteItem(item.id)}>
                  Delete
                </IonItemOption>
              </IonItemOptions>
            </IonItemSliding>
          ))}
        </IonList>
      </IonContent>
    </IonPage>
  );
}
```

## Capacitor Native Plugins

```typescript
import { Camera, CameraResultType, CameraSource } from "@capacitor/camera";
import { Geolocation } from "@capacitor/geolocation";
import { LocalNotifications } from "@capacitor/local-notifications";

// Camera
async function takePhoto() {
  const photo = await Camera.getPhoto({
    quality: 90,
    resultType: CameraResultType.Uri,
    source: CameraSource.Camera,
  });
  return photo.webPath;
}

// Geolocation
async function getCurrentPosition() {
  const position = await Geolocation.getCurrentPosition();
  return {
    lat: position.coords.latitude,
    lng: position.coords.longitude,
  };
}

// Local notifications
async function scheduleReminder(title: string, body: string) {
  await LocalNotifications.schedule({
    notifications: [
      {
        title,
        body,
        id: Date.now(),
        schedule: { at: new Date(Date.now() + 60000) },
      },
    ],
  });
}
```

## Theming

```css
/* variables.css */
:root {
  --ion-color-primary: #3880ff;
  --ion-color-primary-rgb: 56, 128, 255;
  --ion-color-primary-contrast: #ffffff;
  --ion-color-primary-shade: #3171e0;
  --ion-color-primary-tint: #4c8dff;
}

@media (prefers-color-scheme: dark) {
  body {
    --ion-background-color: #1e1e1e;
    --ion-text-color: #ffffff;
    --ion-card-background: #2a2a2a;
  }
}
```

## Additional Resources

- Ionic docs: https://ionicframework.com/docs
- Capacitor plugins: https://capacitorjs.com/docs/plugins
- Ionicons: https://ionic.io/ionicons
