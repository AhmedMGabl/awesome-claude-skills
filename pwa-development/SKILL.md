---
name: pwa-development
description: Progressive Web App development covering service workers, Web App Manifest, caching strategies (Cache First, Network First, Stale-While-Revalidate), offline support, push notifications, background sync, install prompts, and Workbox integration.
---

# PWA Development

This skill should be used when building Progressive Web Apps. It covers service workers, offline support, caching strategies, push notifications, and Workbox tooling.

## When to Use This Skill

Use this skill when you need to:

- Add offline support to a web application
- Implement service worker caching strategies
- Set up push notifications
- Create an installable web app
- Use Workbox for service worker management

## Web App Manifest

```json
{
  "name": "My Application",
  "short_name": "MyApp",
  "description": "A progressive web application",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#3b82f6",
  "icons": [
    { "src": "/icons/192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/icons/512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ],
  "screenshots": [
    { "src": "/screenshots/desktop.png", "sizes": "1280x720", "type": "image/png", "form_factor": "wide" },
    { "src": "/screenshots/mobile.png", "sizes": "640x1136", "type": "image/png", "form_factor": "narrow" }
  ]
}
```

## Service Worker with Workbox

```typescript
// sw.ts (compiled with workbox-cli or vite-plugin-pwa)
import { precacheAndRoute } from "workbox-precaching";
import { registerRoute } from "workbox-routing";
import { CacheFirst, NetworkFirst, StaleWhileRevalidate } from "workbox-strategies";
import { ExpirationPlugin } from "workbox-expiration";

// Precache app shell
precacheAndRoute(self.__WB_MANIFEST);

// Cache API responses — Network First
registerRoute(
  ({ url }) => url.pathname.startsWith("/api/"),
  new NetworkFirst({
    cacheName: "api-cache",
    plugins: [new ExpirationPlugin({ maxEntries: 50, maxAgeSeconds: 300 })],
  }),
);

// Cache images — Cache First
registerRoute(
  ({ request }) => request.destination === "image",
  new CacheFirst({
    cacheName: "images",
    plugins: [new ExpirationPlugin({ maxEntries: 100, maxAgeSeconds: 30 * 24 * 60 * 60 })],
  }),
);

// Cache fonts — Cache First (long-lived)
registerRoute(
  ({ request }) => request.destination === "font",
  new CacheFirst({
    cacheName: "fonts",
    plugins: [new ExpirationPlugin({ maxEntries: 10, maxAgeSeconds: 365 * 24 * 60 * 60 })],
  }),
);

// Cache pages — Stale While Revalidate
registerRoute(
  ({ request }) => request.mode === "navigate",
  new StaleWhileRevalidate({ cacheName: "pages" }),
);
```

## Service Worker Registration

```typescript
// register-sw.ts
export async function registerServiceWorker() {
  if (!("serviceWorker" in navigator)) return;

  try {
    const registration = await navigator.serviceWorker.register("/sw.js", { scope: "/" });

    // Handle updates
    registration.addEventListener("updatefound", () => {
      const newWorker = registration.installing;
      if (!newWorker) return;

      newWorker.addEventListener("statechange", () => {
        if (newWorker.state === "activated" && navigator.serviceWorker.controller) {
          // New version available — prompt user to refresh
          showUpdateBanner();
        }
      });
    });
  } catch (error) {
    console.error("SW registration failed:", error);
  }
}
```

## Push Notifications

```typescript
// Subscribe to push notifications
async function subscribeToPush() {
  const registration = await navigator.serviceWorker.ready;

  const subscription = await registration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY!),
  });

  // Send subscription to server
  await fetch("/api/push/subscribe", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(subscription),
  });
}

// In service worker: handle push event
self.addEventListener("push", (event: PushEvent) => {
  const data = event.data?.json() ?? { title: "Notification", body: "" };

  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: "/icons/192.png",
      badge: "/icons/badge.png",
      data: { url: data.url ?? "/" },
    }),
  );
});

// Handle notification click
self.addEventListener("notificationclick", (event: NotificationEvent) => {
  event.notification.close();
  const url = event.notification.data?.url ?? "/";
  event.waitUntil(clients.openWindow(url));
});
```

## Install Prompt

```typescript
// Capture the beforeinstallprompt event
let deferredPrompt: BeforeInstallPromptEvent | null = null;

window.addEventListener("beforeinstallprompt", (e) => {
  e.preventDefault();
  deferredPrompt = e;
  showInstallButton();
});

async function handleInstallClick() {
  if (!deferredPrompt) return;
  deferredPrompt.prompt();
  const { outcome } = await deferredPrompt.userChoice;
  console.log(`Install prompt outcome: ${outcome}`);
  deferredPrompt = null;
  hideInstallButton();
}
```

## Caching Strategy Reference

```
STRATEGY                  USE CASE                     BEHAVIOR
────────────────────────────────────────────────────────────────────
Cache First               Images, fonts, static assets  Cache → fallback to network
Network First             API data, dynamic content      Network → fallback to cache
Stale-While-Revalidate    Pages, semi-static content    Cache immediately, update in background
Network Only              Auth, payments                 Always network, no caching
Cache Only                Precached app shell            Always cache, never network
```

## Additional Resources

- Workbox: https://developer.chrome.com/docs/workbox
- Web App Manifest: https://developer.mozilla.org/en-US/docs/Web/Manifest
- PWA Builder: https://www.pwabuilder.com/
- Push API: https://developer.mozilla.org/en-US/docs/Web/API/Push_API
