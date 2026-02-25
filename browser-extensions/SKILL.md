---
name: browser-extensions
description: Browser extension development covering Manifest V3, content scripts, background service workers, popup UI, storage API, message passing, context menus, Chrome and Firefox cross-browser compatibility, web request interception, and extension publishing patterns.
---

# Browser Extensions

This skill should be used when building browser extensions for Chrome, Firefox, or Edge. It covers Manifest V3, content scripts, background workers, messaging, storage, and publishing.

## When to Use This Skill

Use this skill when you need to:

- Build Chrome/Firefox/Edge extensions
- Inject content scripts into web pages
- Use background service workers for processing
- Implement popup or options page UI
- Store extension data with Chrome Storage API
- Publish extensions to browser stores

## Manifest V3

```json
{
  "manifest_version": 3,
  "name": "My Extension",
  "version": "1.0.0",
  "description": "A helpful browser extension",
  "permissions": ["storage", "activeTab", "contextMenus"],
  "host_permissions": ["https://*.example.com/*"],
  "background": {
    "service_worker": "background.js",
    "type": "module"
  },
  "content_scripts": [
    {
      "matches": ["https://*.example.com/*"],
      "js": ["content.js"],
      "css": ["content.css"],
      "run_at": "document_idle"
    }
  ],
  "action": {
    "default_popup": "popup.html",
    "default_icon": {
      "16": "icons/icon-16.png",
      "48": "icons/icon-48.png",
      "128": "icons/icon-128.png"
    }
  },
  "options_page": "options.html",
  "icons": {
    "16": "icons/icon-16.png",
    "48": "icons/icon-48.png",
    "128": "icons/icon-128.png"
  }
}
```

## Background Service Worker

```typescript
// background.ts
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === "install") {
    chrome.storage.local.set({ enabled: true, count: 0 });
  }

  // Context menu
  chrome.contextMenus.create({
    id: "myExtension",
    title: "Process with My Extension",
    contexts: ["selection"],
  });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "myExtension" && info.selectionText) {
    processSelection(info.selectionText, tab?.id);
  }
});

// Message handling from content scripts / popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "getData") {
    chrome.storage.local.get(["count", "enabled"]).then(sendResponse);
    return true; // Keep channel open for async response
  }

  if (message.type === "processPage") {
    handlePageProcessing(message.url, message.content)
      .then((result) => sendResponse({ success: true, data: result }))
      .catch((err) => sendResponse({ success: false, error: err.message }));
    return true;
  }
});

// Badge update
async function updateBadge(count: number) {
  await chrome.action.setBadgeText({ text: count > 0 ? String(count) : "" });
  await chrome.action.setBadgeBackgroundColor({ color: "#4F46E5" });
}
```

## Content Script

```typescript
// content.ts — Runs in the context of web pages
(function () {
  // Avoid double injection
  if (document.getElementById("my-extension-root")) return;

  // Inject UI element
  const container = document.createElement("div");
  container.id = "my-extension-root";
  container.style.cssText = "position:fixed;bottom:20px;right:20px;z-index:999999;";
  document.body.appendChild(container);

  // Extract page data
  function extractPageData() {
    return {
      title: document.title,
      url: window.location.href,
      text: document.body.innerText.slice(0, 5000),
    };
  }

  // Send data to background worker
  chrome.runtime.sendMessage(
    { type: "processPage", ...extractPageData() },
    (response) => {
      if (response?.success) {
        showNotification(response.data);
      }
    },
  );

  // Listen for messages from background/popup
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === "getPageContent") {
      sendResponse(extractPageData());
    }
    if (message.type === "highlightText") {
      highlightMatches(message.query);
      sendResponse({ done: true });
    }
  });

  function showNotification(data: any) {
    const toast = document.createElement("div");
    toast.textContent = data.message;
    toast.style.cssText = `
      position:fixed;top:20px;right:20px;z-index:999999;
      background:#4F46E5;color:white;padding:12px 20px;border-radius:8px;
      font-family:system-ui;font-size:14px;box-shadow:0 4px 12px rgba(0,0,0,0.15);
    `;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
  }
})();
```

## Popup UI

```html
<!-- popup.html -->
<!DOCTYPE html>
<html>
<head>
  <style>
    body { width: 320px; padding: 16px; font-family: system-ui; margin: 0; }
    .header { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; }
    .toggle { display: flex; align-items: center; justify-content: space-between; padding: 8px 0; }
    .stats { background: #f3f4f6; border-radius: 8px; padding: 12px; margin-top: 12px; }
    button { background: #4F46E5; color: white; border: none; padding: 8px 16px;
             border-radius: 6px; cursor: pointer; font-size: 14px; width: 100%; }
    button:hover { background: #4338CA; }
  </style>
</head>
<body>
  <div class="header">
    <img src="icons/icon-48.png" width="24" height="24" />
    <h3 style="margin:0">My Extension</h3>
  </div>
  <div class="toggle">
    <span>Enabled</span>
    <input type="checkbox" id="enabled" />
  </div>
  <div class="stats">
    <div>Pages processed: <strong id="count">0</strong></div>
  </div>
  <button id="processBtn" style="margin-top:12px">Process Current Page</button>
  <script src="popup.js"></script>
</body>
</html>
```

```typescript
// popup.ts
document.addEventListener("DOMContentLoaded", async () => {
  const data = await chrome.storage.local.get(["enabled", "count"]);
  (document.getElementById("enabled") as HTMLInputElement).checked = data.enabled ?? true;
  document.getElementById("count")!.textContent = String(data.count ?? 0);

  document.getElementById("enabled")!.addEventListener("change", async (e) => {
    const enabled = (e.target as HTMLInputElement).checked;
    await chrome.storage.local.set({ enabled });
  });

  document.getElementById("processBtn")!.addEventListener("click", async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab?.id) return;

    const response = await chrome.tabs.sendMessage(tab.id, { type: "getPageContent" });
    const result = await chrome.runtime.sendMessage({ type: "processPage", ...response });

    if (result.success) {
      const count = ((await chrome.storage.local.get("count")).count ?? 0) + 1;
      await chrome.storage.local.set({ count });
      document.getElementById("count")!.textContent = String(count);
    }
  });
});
```

## Storage API

```typescript
// Local storage (per-device)
await chrome.storage.local.set({ key: "value", settings: { theme: "dark" } });
const data = await chrome.storage.local.get(["key", "settings"]);

// Sync storage (synced across user's devices, 100KB limit)
await chrome.storage.sync.set({ preferences: { notifications: true } });

// Listen for storage changes
chrome.storage.onChanged.addListener((changes, area) => {
  if (area === "local" && changes.enabled) {
    console.log("Enabled changed:", changes.enabled.oldValue, "->", changes.enabled.newValue);
  }
});
```

## Additional Resources

- Chrome Extensions: https://developer.chrome.com/docs/extensions/
- Firefox Extensions: https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions
- WXT (framework): https://wxt.dev/
- Plasmo (React): https://docs.plasmo.com/
