---
name: wxt-extensions
description: WXT browser extension patterns covering manifest configuration, background scripts, content scripts, popup and options pages, storage API, messaging, cross-browser support, and hot module replacement during development.
---

# WXT Browser Extensions

This skill should be used when building browser extensions with WXT framework. It covers manifest configuration, background/content scripts, storage, messaging, and cross-browser development.

## When to Use This Skill

Use this skill when you need to:

- Build cross-browser extensions (Chrome, Firefox, Safari)
- Configure manifest v3 with file-based conventions
- Create popups, options pages, and side panels
- Use content scripts and background service workers
- Manage extension storage and messaging

## Project Structure

```
my-extension/
├── wxt.config.ts
├── entrypoints/
│   ├── background.ts          # Service worker
│   ├── popup/                 # Popup page
│   │   ├── index.html
│   │   └── main.tsx
│   ├── options/               # Options page
│   │   ├── index.html
│   │   └── main.tsx
│   ├── content.ts             # Content script
│   └── injected.ts            # Injected script
├── public/
│   └── icon/
│       ├── 16.png
│       ├── 48.png
│       └── 128.png
├── assets/
│   └── styles.css
└── utils/
    └── storage.ts
```

## Configuration

```typescript
// wxt.config.ts
import { defineConfig } from "wxt";

export default defineConfig({
  modules: ["@wxt-dev/module-react"],
  manifest: {
    name: "My Extension",
    description: "A browser extension built with WXT",
    permissions: ["storage", "activeTab", "tabs"],
    host_permissions: ["https://*.example.com/*"],
  },
});
```

## Background Script

```typescript
// entrypoints/background.ts
export default defineBackground(() => {
  console.log("Background script loaded");

  // Listen for extension install
  browser.runtime.onInstalled.addListener(({ reason }) => {
    if (reason === "install") {
      browser.tabs.create({ url: browser.runtime.getURL("/options.html") });
    }
  });

  // Handle messages from content scripts
  browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === "GET_DATA") {
      fetchData(message.url).then(sendResponse);
      return true; // Keep channel open for async response
    }
  });

  // Context menu
  browser.contextMenus.create({
    id: "save-text",
    title: "Save selected text",
    contexts: ["selection"],
  });

  browser.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "save-text") {
      saveText(info.selectionText!);
    }
  });
});
```

## Content Script

```typescript
// entrypoints/content.ts
export default defineContentScript({
  matches: ["https://*.example.com/*"],
  runAt: "document_idle",

  main(ctx) {
    console.log("Content script loaded on", window.location.href);

    // Create UI with shadow DOM
    const ui = createIntegratedUi(ctx, {
      position: "inline",
      anchor: "body",
      onMount: (container) => {
        const app = document.createElement("div");
        app.textContent = "Extension UI";
        container.append(app);
      },
    });

    ui.mount();

    // Listen for messages
    browser.runtime.onMessage.addListener((message) => {
      if (message.type === "HIGHLIGHT") {
        highlightElements(message.selector);
      }
    });

    // Send message to background
    const response = await browser.runtime.sendMessage({
      type: "GET_DATA",
      url: window.location.href,
    });
  },
});
```

## Popup Page

```tsx
// entrypoints/popup/main.tsx
import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom/client";

function Popup() {
  const [count, setCount] = useState(0);
  const [currentTab, setCurrentTab] = useState<string>("");

  useEffect(() => {
    // Get current tab info
    browser.tabs.query({ active: true, currentWindow: true }).then(([tab]) => {
      setCurrentTab(tab.url || "");
    });

    // Load saved count
    storage.getItem<number>("local:count").then((val) => {
      if (val !== null) setCount(val);
    });
  }, []);

  const increment = async () => {
    const newCount = count + 1;
    setCount(newCount);
    await storage.setItem("local:count", newCount);
  };

  return (
    <div style={{ width: 300, padding: 16 }}>
      <h1>My Extension</h1>
      <p>Current tab: {currentTab}</p>
      <button onClick={increment}>Count: {count}</button>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(<Popup />);
```

## Storage

```typescript
// utils/storage.ts
import { storage } from "wxt/storage";

// Define typed storage items
export const settings = storage.defineItem<{
  theme: "light" | "dark";
  notifications: boolean;
  apiKey: string;
}>("local:settings", {
  fallback: {
    theme: "light",
    notifications: true,
    apiKey: "",
  },
});

// Usage
const currentSettings = await settings.getValue();
await settings.setValue({ ...currentSettings, theme: "dark" });

// Watch for changes
settings.watch((newValue) => {
  console.log("Settings changed:", newValue);
});

// Simple key-value
await storage.setItem("local:lastVisit", Date.now());
const lastVisit = await storage.getItem<number>("local:lastVisit");
```

## Messaging

```typescript
// Define typed messages
import { defineExtensionMessaging } from "@webext-core/messaging";

interface ProtocolMap {
  getTabData(data: { tabId: number }): { title: string; url: string };
  saveBookmark(data: { url: string; title: string }): boolean;
}

export const { sendMessage, onMessage } = defineExtensionMessaging<ProtocolMap>();

// In background
onMessage("getTabData", async ({ data }) => {
  const tab = await browser.tabs.get(data.tabId);
  return { title: tab.title!, url: tab.url! };
});

// In content script or popup
const tabData = await sendMessage("getTabData", { tabId: 123 });
```

## Additional Resources

- WXT: https://wxt.dev/
- WXT guide: https://wxt.dev/guide/installation.html
- Browser extension APIs: https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions
