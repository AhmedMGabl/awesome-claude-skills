---
name: electron-forge
description: Electron Forge patterns covering desktop app scaffolding, IPC communication, BrowserWindow management, auto-updates, tray icons, native menus, system integration, and packaging for Windows/macOS/Linux.
---

# Electron Forge

This skill should be used when building cross-platform desktop applications with Electron Forge. It covers IPC communication, window management, auto-updates, system integration, and packaging.

## When to Use This Skill

Use this skill when you need to:

- Build cross-platform desktop apps with web technologies
- Handle IPC between main and renderer processes
- Manage multiple BrowserWindows
- Add auto-updates, tray icons, and native menus
- Package and distribute for Windows, macOS, and Linux

## Setup

```bash
npm init electron-app@latest my-app -- --template=webpack-typescript
cd my-app
npm start
```

## Main Process

```ts
// src/main.ts
import { app, BrowserWindow, ipcMain, Menu, Tray, nativeImage } from "electron";
import path from "node:path";

let mainWindow: BrowserWindow | null = null;
let tray: Tray | null = null;

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
    titleBarStyle: "hiddenInset",
    show: false,
  });

  mainWindow.loadFile(path.join(__dirname, "index.html"));

  mainWindow.once("ready-to-show", () => {
    mainWindow?.show();
  });

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  createWindow();
  createTray();
  registerIpcHandlers();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
```

## Preload Script (Context Bridge)

```ts
// src/preload.ts
import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld("electronAPI", {
  // Invoke main process handlers
  readFile: (path: string) => ipcRenderer.invoke("file:read", path),
  saveFile: (path: string, content: string) =>
    ipcRenderer.invoke("file:save", path, content),
  showOpenDialog: () => ipcRenderer.invoke("dialog:open"),

  // Listen for events from main process
  onMenuAction: (callback: (action: string) => void) => {
    const listener = (_event: any, action: string) => callback(action);
    ipcRenderer.on("menu:action", listener);
    return () => ipcRenderer.removeListener("menu:action", listener);
  },

  onUpdateAvailable: (callback: (info: any) => void) => {
    const listener = (_event: any, info: any) => callback(info);
    ipcRenderer.on("update:available", listener);
    return () => ipcRenderer.removeListener("update:available", listener);
  },
});
```

## IPC Handlers

```ts
// src/ipc-handlers.ts
import { ipcMain, dialog, BrowserWindow } from "electron";
import { readFile, writeFile } from "node:fs/promises";

export function registerIpcHandlers() {
  ipcMain.handle("file:read", async (_event, filePath: string) => {
    return readFile(filePath, "utf-8");
  });

  ipcMain.handle("file:save", async (_event, filePath: string, content: string) => {
    await writeFile(filePath, content, "utf-8");
    return { success: true };
  });

  ipcMain.handle("dialog:open", async (event) => {
    const window = BrowserWindow.fromWebContents(event.sender);
    const result = await dialog.showOpenDialog(window!, {
      properties: ["openFile"],
      filters: [
        { name: "Text Files", extensions: ["txt", "md", "json"] },
        { name: "All Files", extensions: ["*"] },
      ],
    });
    return result.canceled ? null : result.filePaths[0];
  });
}
```

## System Tray

```ts
function createTray() {
  const icon = nativeImage.createFromPath(path.join(__dirname, "icon.png"));
  tray = new Tray(icon.resize({ width: 16, height: 16 }));

  const contextMenu = Menu.buildFromTemplate([
    { label: "Show App", click: () => mainWindow?.show() },
    { label: "Hide App", click: () => mainWindow?.hide() },
    { type: "separator" },
    { label: "Quit", click: () => app.quit() },
  ]);

  tray.setToolTip("My App");
  tray.setContextMenu(contextMenu);

  tray.on("double-click", () => {
    mainWindow?.show();
  });
}
```

## Auto Updates

```ts
import { autoUpdater } from "electron-updater";

export function setupAutoUpdater(window: BrowserWindow) {
  autoUpdater.autoDownload = false;

  autoUpdater.on("update-available", (info) => {
    window.webContents.send("update:available", info);
  });

  autoUpdater.on("download-progress", (progress) => {
    window.webContents.send("update:progress", progress.percent);
  });

  autoUpdater.on("update-downloaded", () => {
    window.webContents.send("update:ready");
  });

  ipcMain.handle("update:download", () => autoUpdater.downloadUpdate());
  ipcMain.handle("update:install", () => autoUpdater.quitAndInstall());

  autoUpdater.checkForUpdates();
}
```

## Packaging

```ts
// forge.config.ts
import type { ForgeConfig } from "@electron-forge/shared-types";

const config: ForgeConfig = {
  packagerConfig: {
    asar: true,
    icon: "./assets/icon",
    appBundleId: "com.myapp.desktop",
  },
  makers: [
    { name: "@electron-forge/maker-squirrel", config: { name: "MyApp" } },
    { name: "@electron-forge/maker-dmg", config: {} },
    { name: "@electron-forge/maker-deb", config: {} },
    { name: "@electron-forge/maker-rpm", config: {} },
  ],
};

export default config;
```

```bash
# Package for current platform
npm run package

# Create distributable
npm run make
```

## Additional Resources

- Electron Forge: https://www.electronforge.io/
- Electron: https://www.electronjs.org/docs/latest/
- IPC: https://www.electronjs.org/docs/latest/tutorial/ipc
