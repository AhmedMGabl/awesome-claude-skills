---
name: service-workers
description: Service Workers and PWA patterns covering offline caching strategies, background sync, push notifications, workbox integration, precaching, runtime caching, and installable web app configuration.
---

# Service Workers & PWA

This skill should be used when building Progressive Web Apps with service workers. It covers caching strategies, offline support, push notifications, and Workbox integration.

## When to Use This Skill

Use this skill when you need to:

- Make web apps work offline
- Implement caching strategies for assets and API calls
- Add push notifications to web apps
- Build installable PWAs
- Use Workbox for production service workers

## Basic Service Worker

```typescript
// sw.ts
const CACHE_NAME = "app-v1";
const STATIC_ASSETS = ["/", "/index.html", "/styles.css", "/app.js"];

// Install - precache static assets
self.addEventListener("install", (event: ExtendableEvent) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS)),
  );
  (self as any).skipWaiting();
});

// Activate - clean old caches
self.addEventListener("activate", (event: ExtendableEvent) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)),
      ),
    ),
  );
  (self as any).clients.claim();
});

// Fetch - cache-first for assets, network-first for API
self.addEventListener("fetch", (event: FetchEvent) => {
  const url = new URL(event.request.url);

  if (url.pathname.startsWith("/api/")) {
    // Network first, fallback to cache
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          return response;
        })
        .catch(() => caches.match(event.request) as Promise<Response>),
    );
  } else {
    // Cache first, fallback to network
    event.respondWith(
      caches.match(event.request).then(
        (cached) => cached || fetch(event.request),
      ),
    );
  }
});
```

## Registration

```typescript
// main.ts
if ("serviceWorker" in navigator) {
  window.addEventListener("load", async () => {
    const registration = await navigator.serviceWorker.register("/sw.js");
    console.log("SW registered:", registration.scope);

    // Handle updates
    registration.addEventListener("updatefound", () => {
      const newWorker = registration.installing;
      newWorker?.addEventListener("statechange", () => {
        if (newWorker.state === "activated" && navigator.serviceWorker.controller) {
          // New version available
          showUpdateNotification();
        }
      });
    });
  });
}
```

## Workbox (Production)

```typescript
// sw.ts with Workbox
import { precacheAndRoute } from "workbox-precaching";
import { registerRoute } from "workbox-routing";
import {
  CacheFirst, NetworkFirst, StaleWhileRevalidate,
} from "workbox-strategies";
import { ExpirationPlugin } from "workbox-expiration";
import { CacheableResponsePlugin } from "workbox-cacheable-response";

// Precache build assets
precacheAndRoute(self.__WB_MANIFEST);

// Cache images
registerRoute(
  ({ request }) => request.destination === "image",
  new CacheFirst({
    cacheName: "images",
    plugins: [
      new ExpirationPlugin({ maxEntries: 100, maxAgeSeconds: 30 * 24 * 3600 }),
      new CacheableResponsePlugin({ statuses: [0, 200] }),
    ],
  }),
);

// API calls - network first
registerRoute(
  ({ url }) => url.pathname.startsWith("/api/"),
  new NetworkFirst({
    cacheName: "api",
    plugins: [new ExpirationPlugin({ maxEntries: 50, maxAgeSeconds: 300 })],
  }),
);

// Google Fonts - stale while revalidate
registerRoute(
  ({ url }) => url.origin === "https://fonts.googleapis.com",
  new StaleWhileRevalidate({ cacheName: "google-fonts" }),
);
```

## Push Notifications

```typescript
// Request permission and subscribe
async function subscribeToPush() {
  const registration = await navigator.serviceWorker.ready;
  const subscription = await registration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
  });

  // Send subscription to server
  await fetch("/api/push/subscribe", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(subscription),
  });
}

// Handle push in service worker
self.addEventListener("push", (event: PushEvent) => {
  const data = event.data?.json() ?? { title: "Notification", body: "" };
  event.waitUntil(
    (self as any).registration.showNotification(data.title, {
      body: data.body,
      icon: "/icon-192.png",
      badge: "/badge-72.png",
      data: { url: data.url },
    }),
  );
});

// Handle notification click
self.addEventListener("notificationclick", (event: NotificationEvent) => {
  event.notification.close();
  event.waitUntil(
    (self as any).clients.openWindow(event.notification.data.url || "/"),
  );
});
```

## Web App Manifest

```json
{
  "name": "My App",
  "short_name": "App",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#3b82f6",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

## Additional Resources

- MDN Service Workers: https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API
- Workbox: https://developer.chrome.com/docs/workbox/
- Web Push: https://web.dev/push-notifications-overview/
