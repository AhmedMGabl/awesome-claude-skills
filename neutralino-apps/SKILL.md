---
name: neutralino-apps
description: Neutralinojs patterns covering lightweight desktop apps, native OS API access, file system operations, system info, window management, tray menus, process spawning, and cross-platform distribution without bundled browser.
---

# Neutralinojs

This skill should be used when building lightweight desktop applications with Neutralinojs. It covers native APIs, file system operations, window management, and distribution.

## When to Use This Skill

Use this skill when you need to:

- Build lightweight desktop apps without bundled Chromium
- Access native OS APIs (filesystem, OS info, clipboard)
- Create system tray apps and multi-window applications
- Distribute small-footprint desktop apps
- Spawn processes and run system commands

## Setup

```bash
npm install -g @neutralinojs/neu
neu create my-app
cd my-app
neu run
```

## Configuration

```json
// neutralino.config.json
{
  "applicationId": "com.myapp.desktop",
  "defaultMode": "window",
  "url": "/",
  "enableServer": true,
  "modes": {
    "window": {
      "title": "My App",
      "width": 1024,
      "height": 768,
      "minWidth": 600,
      "minHeight": 400,
      "center": true,
      "resizable": true,
      "maximize": false,
      "icon": "/resources/icons/appIcon.png"
    }
  },
  "cli": {
    "binaryName": "myapp",
    "resourcesPath": "/resources/",
    "clientLibrary": "/resources/js/neutralino.js"
  }
}
```

## File System Operations

```ts
import { filesystem } from "@neutralinojs/lib";

// Read file
async function readTextFile(path: string): Promise<string> {
  return filesystem.readFile(path);
}

// Write file
async function writeTextFile(path: string, content: string): Promise<void> {
  await filesystem.writeFile(path, content);
}

// Read binary file
async function readBinaryFile(path: string): Promise<ArrayBuffer> {
  return filesystem.readBinaryFile(path);
}

// List directory contents
async function listDirectory(path: string) {
  const entries = await filesystem.readDirectory(path);
  return entries.map((entry) => ({
    name: entry.entry,
    type: entry.type, // "FILE" or "DIRECTORY"
  }));
}

// Create directory
async function createDir(path: string): Promise<void> {
  await filesystem.createDirectory(path);
}

// Copy and move
async function copyFile(src: string, dest: string): Promise<void> {
  await filesystem.copyFile(src, dest);
}

// Watch directory for changes
async function watchDirectory(path: string) {
  await filesystem.watcher.watch(path);

  Neutralino.events.on("watchFile", (event) => {
    console.log("File changed:", event.detail.action, event.detail.filename);
  });
}
```

## Dialogs

```ts
import { os } from "@neutralinojs/lib";

// Open file dialog
async function openFileDialog(): Promise<string | null> {
  const entries = await os.showOpenDialog("Select a File", {
    filters: [
      { name: "Documents", extensions: ["txt", "md", "json"] },
      { name: "All Files", extensions: ["*"] },
    ],
  });
  return entries.length > 0 ? entries[0] : null;
}

// Save file dialog
async function saveFileDialog(): Promise<string | null> {
  return os.showSaveDialog("Save File", {
    filters: [{ name: "Text", extensions: ["txt"] }],
  });
}

// Message box
async function showMessage(title: string, content: string) {
  await os.showMessageBox(title, content, "OK", "INFO");
}

// Confirmation dialog
async function confirm(title: string, message: string): Promise<boolean> {
  const result = await os.showMessageBox(title, message, "YES_NO", "QUESTION");
  return result === "YES";
}
```

## System Tray

```ts
import { os } from "@neutralinojs/lib";

async function createTray() {
  await os.setTray({
    icon: "/resources/icons/trayIcon.png",
    menuItems: [
      { id: "show", text: "Show App" },
      { id: "hide", text: "Hide App" },
      { text: "-" }, // Separator
      { id: "about", text: "About" },
      { id: "quit", text: "Quit" },
    ],
  });

  Neutralino.events.on("trayMenuItemClicked", (event) => {
    switch (event.detail.id) {
      case "show":
        Neutralino.window.show();
        break;
      case "hide":
        Neutralino.window.hide();
        break;
      case "about":
        showAboutDialog();
        break;
      case "quit":
        Neutralino.app.exit();
        break;
    }
  });
}
```

## Window Management

```ts
import { window as nWindow } from "@neutralinojs/lib";

// Set window properties
await nWindow.setTitle("My App - Document.txt");
await nWindow.setSize({ width: 1200, height: 800 });
await nWindow.center();

// Fullscreen toggle
let isFullscreen = false;
async function toggleFullscreen() {
  isFullscreen = !isFullscreen;
  if (isFullscreen) {
    await nWindow.setFullScreen();
  } else {
    await nWindow.exitFullScreen();
  }
}

// Create new window
async function openSecondaryWindow() {
  await nWindow.create("/settings.html", {
    title: "Settings",
    width: 600,
    height: 400,
    resizable: false,
    center: true,
  });
}
```

## Process Execution

```ts
import { os } from "@neutralinojs/lib";

// Run a command
async function runCommand(command: string): Promise<string> {
  const result = await os.execCommand(command);
  return result.stdOut;
}

// Spawn long-running process
async function spawnProcess(command: string) {
  const process = await os.spawnProcess(command);

  Neutralino.events.on("spawnedProcess", (event) => {
    if (event.detail.id === process.id) {
      if (event.detail.action === "stdOut") {
        console.log("Output:", event.detail.data);
      } else if (event.detail.action === "exit") {
        console.log("Process exited with code:", event.detail.data);
      }
    }
  });

  return process.id;
}

// Open URL in default browser
async function openExternal(url: string) {
  await os.open(url);
}
```

## Build and Distribute

```bash
# Build for all platforms
neu build

# Build output is in dist/
# Binary sizes: ~2-5 MB (no bundled browser)

# Release configuration in neutralino.config.json
# Supports: linux/x64, win/x64, mac/x64, mac/arm64
```

## Additional Resources

- Neutralinojs: https://neutralino.js.org/
- API Reference: https://neutralino.js.org/docs/api/overview
- Configuration: https://neutralino.js.org/docs/configuration/neutralino.config.json
