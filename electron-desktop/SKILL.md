---
name: electron-desktop
description: Electron desktop application development covering main/renderer process architecture, IPC communication, BrowserWindow management, Electron Forge tooling, auto-updates, system tray, native menus, file system access, notification API, code signing, and cross-platform packaging for Windows, macOS, and Linux.
---

# Electron Desktop Apps

This skill should be used when building cross-platform desktop applications with Electron. It covers main/renderer process architecture, IPC, packaging, auto-updates, and native OS integration.

## When to Use This Skill

Use this skill when you need to:

- Build cross-platform desktop applications
- Wrap web apps as native desktop apps
- Access native OS features (file system, tray, menus)
- Implement auto-update functionality
- Package and distribute desktop applications

## Main Process

```typescript
// src/main.ts
import { app, BrowserWindow, ipcMain, Menu, Tray, nativeImage } from "electron";
import path from "path";

let mainWindow: BrowserWindow | null = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
    titleBarStyle: "hiddenInset",  // macOS frameless
    show: false,
  });

  // Show when ready to avoid white flash
  mainWindow.once("ready-to-show", () => mainWindow?.show());

  if (process.env.NODE_ENV === "development") {
    mainWindow.loadURL("http://localhost:5173");
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, "../renderer/index.html"));
  }
}

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
```

## Preload Script (Secure Bridge)

```typescript
// src/preload.ts — runs in renderer but has access to Node APIs
import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld("electronAPI", {
  // File operations
  openFile: () => ipcRenderer.invoke("dialog:openFile"),
  saveFile: (content: string) => ipcRenderer.invoke("dialog:saveFile", content),
  readFile: (path: string) => ipcRenderer.invoke("fs:readFile", path),

  // App info
  getVersion: () => ipcRenderer.invoke("app:version"),

  // Events
  onMenuAction: (callback: (action: string) => void) => {
    const handler = (_: any, action: string) => callback(action);
    ipcRenderer.on("menu:action", handler);
    return () => ipcRenderer.removeListener("menu:action", handler);
  },

  // Notifications
  showNotification: (title: string, body: string) =>
    ipcRenderer.invoke("notification:show", title, body),
});
```

## IPC Handlers

```typescript
// src/main.ts — IPC handlers in main process
import { dialog, Notification } from "electron";
import fs from "fs/promises";

ipcMain.handle("dialog:openFile", async () => {
  const result = await dialog.showOpenDialog(mainWindow!, {
    properties: ["openFile"],
    filters: [
      { name: "Documents", extensions: ["txt", "md", "json"] },
      { name: "All Files", extensions: ["*"] },
    ],
  });
  if (result.canceled || !result.filePaths[0]) return null;

  const content = await fs.readFile(result.filePaths[0], "utf-8");
  return { path: result.filePaths[0], content };
});

ipcMain.handle("dialog:saveFile", async (_, content: string) => {
  const result = await dialog.showSaveDialog(mainWindow!, {
    filters: [{ name: "Text Files", extensions: ["txt"] }],
  });
  if (result.canceled || !result.filePath) return false;

  await fs.writeFile(result.filePath, content, "utf-8");
  return true;
});

ipcMain.handle("fs:readFile", async (_, filePath: string) => {
  return fs.readFile(filePath, "utf-8");
});

ipcMain.handle("app:version", () => app.getVersion());

ipcMain.handle("notification:show", (_, title: string, body: string) => {
  new Notification({ title, body }).show();
});
```

## Renderer (React)

```tsx
// src/renderer/App.tsx — Uses exposed API from preload
function App() {
  const [content, setContent] = useState("");
  const [filePath, setFilePath] = useState<string | null>(null);

  const openFile = async () => {
    const result = await window.electronAPI.openFile();
    if (result) {
      setContent(result.content);
      setFilePath(result.path);
    }
  };

  const saveFile = async () => {
    await window.electronAPI.saveFile(content);
    window.electronAPI.showNotification("Saved", "File saved successfully");
  };

  useEffect(() => {
    const cleanup = window.electronAPI.onMenuAction((action) => {
      if (action === "open") openFile();
      if (action === "save") saveFile();
    });
    return cleanup;
  }, [content]);

  return (
    <div className="h-screen flex flex-col">
      <header className="drag-region h-10 flex items-center px-4 bg-gray-100">
        <span className="text-sm text-gray-600">{filePath ?? "Untitled"}</span>
      </header>
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        className="flex-1 p-4 resize-none outline-none font-mono"
      />
    </div>
  );
}
```

## Auto-Updates

```typescript
import { autoUpdater } from "electron-updater";

autoUpdater.autoDownload = true;
autoUpdater.autoInstallOnAppQuit = true;

autoUpdater.on("update-available", (info) => {
  mainWindow?.webContents.send("update:available", info.version);
});

autoUpdater.on("update-downloaded", () => {
  mainWindow?.webContents.send("update:ready");
});

// Check for updates on app ready
app.whenReady().then(() => {
  autoUpdater.checkForUpdatesAndNotify();
});
```

## Packaging with Electron Forge

```json
{
  "scripts": {
    "start": "electron-forge start",
    "package": "electron-forge package",
    "make": "electron-forge make"
  }
}
```

```javascript
// forge.config.js
module.exports = {
  packagerConfig: {
    icon: "./assets/icon",
    appBundleId: "com.example.myapp",
    osxSign: {},
    osxNotarize: { appleId: process.env.APPLE_ID, appleIdPassword: process.env.APPLE_PASSWORD },
  },
  makers: [
    { name: "@electron-forge/maker-squirrel", config: {} },      // Windows
    { name: "@electron-forge/maker-dmg", config: {} },            // macOS
    { name: "@electron-forge/maker-deb", config: {} },            // Linux .deb
    { name: "@electron-forge/maker-rpm", config: {} },            // Linux .rpm
  ],
};
```

## Additional Resources

- Electron docs: https://www.electronjs.org/docs
- Electron Forge: https://www.electronforge.io/
- electron-updater: https://www.electron.build/auto-update
- Tauri (Rust alternative): https://tauri.app/
