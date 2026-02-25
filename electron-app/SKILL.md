---
name: electron-app
description: Electron desktop application patterns covering main/renderer processes, IPC communication, native menus, auto-updates, packaging, and security hardening.
---

# Electron Desktop App

This skill should be used when building desktop applications with Electron. It covers main/renderer processes, IPC, native menus, auto-updates, packaging, and security.

## When to Use This Skill

Use this skill when you need to:

- Build cross-platform desktop applications
- Manage main and renderer process communication
- Create native menus and system tray apps
- Implement auto-updates with electron-updater
- Package and distribute desktop apps

## Project Structure

```
electron-app/
├── src/
│   ├── main/
│   │   ├── index.ts          # Main process entry
│   │   ├── ipc-handlers.ts   # IPC handler registration
│   │   └── menu.ts           # Application menu
│   ├── renderer/
│   │   ├── index.html
│   │   ├── App.tsx
│   │   └── preload.ts        # Preload script
│   └── shared/
│       └── types.ts           # Shared type definitions
├── electron-builder.yml
└── package.json
```

## Main Process

```typescript
// src/main/index.ts
import { app, BrowserWindow, ipcMain } from "electron";
import path from "path";

let mainWindow: BrowserWindow | null = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, "../renderer/preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  if (process.env.NODE_ENV === "development") {
    mainWindow.loadURL("http://localhost:5173");
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, "../renderer/index.html"));
  }

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
```

## Preload Script (Context Bridge)

```typescript
// src/renderer/preload.ts
import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld("electronAPI", {
  // File operations
  openFile: () => ipcRenderer.invoke("dialog:openFile"),
  saveFile: (content: string) => ipcRenderer.invoke("dialog:saveFile", content),

  // App info
  getVersion: () => ipcRenderer.invoke("app:getVersion"),

  // Events from main
  onUpdateAvailable: (callback: () => void) =>
    ipcRenderer.on("update-available", callback),

  // Notifications
  showNotification: (title: string, body: string) =>
    ipcRenderer.send("notification:show", title, body),
});
```

## IPC Handlers

```typescript
// src/main/ipc-handlers.ts
import { ipcMain, dialog, Notification, app } from "electron";
import fs from "fs/promises";

export function registerIpcHandlers() {
  ipcMain.handle("dialog:openFile", async () => {
    const result = await dialog.showOpenDialog({
      properties: ["openFile"],
      filters: [
        { name: "Text Files", extensions: ["txt", "md"] },
        { name: "All Files", extensions: ["*"] },
      ],
    });

    if (result.canceled || result.filePaths.length === 0) return null;

    const content = await fs.readFile(result.filePaths[0], "utf-8");
    return { path: result.filePaths[0], content };
  });

  ipcMain.handle("dialog:saveFile", async (_event, content: string) => {
    const result = await dialog.showSaveDialog({
      filters: [{ name: "Text Files", extensions: ["txt"] }],
    });

    if (result.canceled || !result.filePath) return false;

    await fs.writeFile(result.filePath, content, "utf-8");
    return true;
  });

  ipcMain.handle("app:getVersion", () => app.getVersion());

  ipcMain.on("notification:show", (_event, title: string, body: string) => {
    new Notification({ title, body }).show();
  });
}
```

## Application Menu

```typescript
// src/main/menu.ts
import { Menu, MenuItemConstructorOptions } from "electron";

export function createMenu() {
  const template: MenuItemConstructorOptions[] = [
    {
      label: "File",
      submenu: [
        { label: "Open", accelerator: "CmdOrCtrl+O", click: () => {} },
        { label: "Save", accelerator: "CmdOrCtrl+S", click: () => {} },
        { type: "separator" },
        { role: "quit" },
      ],
    },
    { label: "Edit", submenu: [{ role: "undo" }, { role: "redo" }, { type: "separator" }, { role: "cut" }, { role: "copy" }, { role: "paste" }] },
    { label: "View", submenu: [{ role: "reload" }, { role: "toggleDevTools" }, { type: "separator" }, { role: "zoomIn" }, { role: "zoomOut" }, { role: "resetZoom" }] },
  ];

  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}
```

## Auto-Updates

```typescript
import { autoUpdater } from "electron-updater";

autoUpdater.autoDownload = false;

autoUpdater.on("update-available", () => {
  mainWindow?.webContents.send("update-available");
});

autoUpdater.on("update-downloaded", () => {
  autoUpdater.quitAndInstall();
});

// Check for updates on app start
app.whenReady().then(() => {
  autoUpdater.checkForUpdates();
});
```

## Packaging

```yaml
# electron-builder.yml
appId: com.example.myapp
productName: MyApp
directories:
  output: dist
files:
  - "out/**/*"
mac:
  category: public.app-category.productivity
  target: [dmg, zip]
win:
  target: [nsis, portable]
linux:
  target: [AppImage, deb]
publish:
  provider: github
```

```json
{
  "scripts": {
    "dev": "electron-vite dev",
    "build": "electron-vite build",
    "package": "electron-builder --publish never",
    "publish": "electron-builder --publish always"
  }
}
```

## Additional Resources

- Electron Docs: https://www.electronjs.org/docs/latest/
- Electron Forge: https://www.electronforge.io/
- electron-builder: https://www.electron.build/
