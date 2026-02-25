---
name: tauri-v2
description: Tauri v2 desktop and mobile application patterns covering window management, IPC commands, event system, file system access, system tray, auto-updater, plugins, multi-window apps, and Rust backend integration.
---

# Tauri v2

This skill should be used when building desktop and mobile applications with Tauri v2. It covers IPC, window management, plugins, system tray, and Rust backend integration.

## When to Use This Skill

Use this skill when you need to:

- Build cross-platform desktop apps with web frontend
- Communicate between frontend and Rust backend via IPC
- Access native features (filesystem, notifications, system tray)
- Create multi-window applications
- Configure auto-updates and app distribution

## IPC Commands

```rust
// src-tauri/src/lib.rs
use tauri::Manager;

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! Welcome to Tauri v2.", name)
}

#[tauri::command]
async fn read_file(path: String) -> Result<String, String> {
    std::fs::read_to_string(&path).map_err(|e| e.to_string())
}

#[tauri::command]
async fn save_settings(
    app: tauri::AppHandle,
    settings: serde_json::Value,
) -> Result<(), String> {
    let config_dir = app.path().app_config_dir().map_err(|e| e.to_string())?;
    std::fs::create_dir_all(&config_dir).map_err(|e| e.to_string())?;
    let path = config_dir.join("settings.json");
    std::fs::write(path, serde_json::to_string_pretty(&settings).unwrap())
        .map_err(|e| e.to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![greet, read_file, save_settings])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

## Frontend IPC Calls

```typescript
import { invoke } from "@tauri-apps/api/core";

// Call Rust commands
async function greetUser(name: string) {
  const message = await invoke<string>("greet", { name });
  console.log(message);
}

async function loadFile(path: string) {
  try {
    const content = await invoke<string>("read_file", { path });
    return content;
  } catch (error) {
    console.error("Failed to read file:", error);
  }
}

async function saveSettings(settings: Record<string, unknown>) {
  await invoke("save_settings", { settings });
}
```

## Event System

```typescript
import { listen, emit } from "@tauri-apps/api/event";

// Listen for events from Rust
const unlisten = await listen<{ progress: number }>("download-progress", (event) => {
  console.log(`Download: ${event.payload.progress}%`);
});

// Emit events to Rust
await emit("start-download", { url: "https://example.com/file.zip" });

// Clean up listener
unlisten();
```

```rust
// Emit events from Rust
use tauri::Emitter;

#[tauri::command]
async fn start_download(app: tauri::AppHandle, url: String) -> Result<(), String> {
    // Simulate download progress
    for i in 0..=100 {
        app.emit("download-progress", serde_json::json!({ "progress": i }))
            .map_err(|e| e.to_string())?;
        tokio::time::sleep(std::time::Duration::from_millis(50)).await;
    }
    Ok(())
}
```

## Window Management

```typescript
import { getCurrentWindow, Window } from "@tauri-apps/api/window";

// Get current window
const mainWindow = getCurrentWindow();

// Window operations
await mainWindow.setTitle("My App");
await mainWindow.setSize({ width: 800, height: 600 });
await mainWindow.center();
await mainWindow.setAlwaysOnTop(true);

// Create new window
const settingsWindow = new Window("settings", {
  url: "/settings",
  title: "Settings",
  width: 400,
  height: 300,
  resizable: false,
  center: true,
});

// Window events
await mainWindow.onCloseRequested(async (event) => {
  const confirmed = await confirm("Are you sure you want to quit?");
  if (!confirmed) event.preventDefault();
});
```

## System Tray

```rust
// src-tauri/src/lib.rs
use tauri::{
    menu::{Menu, MenuItem},
    tray::TrayIconBuilder,
    Manager,
};

pub fn run() {
    tauri::Builder::default()
        .setup(|app| {
            let quit = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>)?;
            let show = MenuItem::with_id(app, "show", "Show Window", true, None::<&str>)?;
            let menu = Menu::with_items(app, &[&show, &quit])?;

            TrayIconBuilder::new()
                .icon(app.default_window_icon().unwrap().clone())
                .menu(&menu)
                .on_menu_event(|app, event| match event.id.as_ref() {
                    "quit" => app.exit(0),
                    "show" => {
                        if let Some(window) = app.get_webview_window("main") {
                            window.show().unwrap();
                            window.set_focus().unwrap();
                        }
                    }
                    _ => {}
                })
                .build(app)?;

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

## Filesystem Plugin

```typescript
import {
  readTextFile,
  writeTextFile,
  exists,
  mkdir,
  BaseDirectory,
} from "@tauri-apps/plugin-fs";

// Read file from app data directory
const content = await readTextFile("config.json", {
  baseDir: BaseDirectory.AppData,
});

// Write file
await writeTextFile("config.json", JSON.stringify(config), {
  baseDir: BaseDirectory.AppData,
});

// Check if file exists
const fileExists = await exists("config.json", {
  baseDir: BaseDirectory.AppData,
});

// Create directory
await mkdir("data", { baseDir: BaseDirectory.AppData, recursive: true });
```

## Configuration

```json
// src-tauri/tauri.conf.json
{
  "productName": "My App",
  "version": "1.0.0",
  "identifier": "com.example.myapp",
  "build": {
    "frontendDist": "../dist"
  },
  "app": {
    "windows": [
      {
        "title": "My App",
        "width": 1024,
        "height": 768,
        "resizable": true,
        "fullscreen": false
      }
    ],
    "security": {
      "csp": "default-src 'self'; style-src 'self' 'unsafe-inline'"
    }
  },
  "plugins": {
    "fs": {
      "scope": { "allow": ["$APPDATA/**"], "deny": ["$APPDATA/secrets/**"] }
    }
  }
}
```

## Additional Resources

- Tauri v2 docs: https://v2.tauri.app/
- Plugins: https://v2.tauri.app/plugin/
- Rust API: https://docs.rs/tauri/latest/tauri/
