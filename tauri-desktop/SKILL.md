---
name: tauri-desktop
description: Tauri desktop application development covering Rust backend commands, JavaScript frontend integration, window management, system tray, file system access, IPC communication, auto-updates, app bundling, and cross-platform builds for Windows, macOS, and Linux.
---

# Tauri Desktop

This skill should be used when building cross-platform desktop apps with Tauri. It covers Rust commands, frontend integration, IPC, system tray, auto-updates, and packaging.

## When to Use This Skill

Use this skill when you need to:

- Build lightweight desktop apps with web technologies
- Use Rust for native backend functionality
- Implement system tray and native menus
- Package apps for Windows, macOS, Linux
- Bridge frontend JavaScript with Rust commands

## Tauri Commands (Rust Backend)

```rust
// src-tauri/src/lib.rs
use tauri::Manager;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
struct AppSettings {
    theme: String,
    language: String,
    notifications: bool,
}

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! Welcome to Tauri.", name)
}

#[tauri::command]
async fn fetch_data(url: String) -> Result<String, String> {
    reqwest::get(&url)
        .await
        .map_err(|e| e.to_string())?
        .text()
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
fn save_settings(settings: AppSettings) -> Result<(), String> {
    let path = dirs::config_dir()
        .ok_or("Could not find config dir")?
        .join("my-app/settings.json");

    std::fs::create_dir_all(path.parent().unwrap()).map_err(|e| e.to_string())?;
    let json = serde_json::to_string_pretty(&settings).map_err(|e| e.to_string())?;
    std::fs::write(path, json).map_err(|e| e.to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![greet, fetch_data, save_settings])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

## Frontend Integration (TypeScript)

```typescript
import { invoke } from "@tauri-apps/api/core";
import { open, save } from "@tauri-apps/plugin-dialog";
import { readTextFile, writeTextFile } from "@tauri-apps/plugin-fs";

// Call Rust commands
async function greeting() {
  const message = await invoke<string>("greet", { name: "World" });
  console.log(message);
}

// File dialog
async function openFile() {
  const path = await open({
    filters: [{ name: "Text", extensions: ["txt", "md"] }],
  });
  if (path) {
    const content = await readTextFile(path);
    return content;
  }
}

async function saveFile(content: string) {
  const path = await save({
    filters: [{ name: "Text", extensions: ["txt"] }],
  });
  if (path) {
    await writeTextFile(path, content);
  }
}
```

## Configuration

```json
// src-tauri/tauri.conf.json
{
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
  "bundle": {
    "active": true,
    "targets": "all",
    "identifier": "com.myapp.desktop",
    "icon": ["icons/32x32.png", "icons/128x128.png", "icons/icon.icns", "icons/icon.ico"]
  }
}
```

## Tauri vs Electron

```
FEATURE           TAURI              ELECTRON
──────────────────────────────────────────────
Bundle size       ~3-10 MB           ~150+ MB
Memory usage      ~30-50 MB          ~100-300 MB
Backend           Rust               Node.js
Renderer          System WebView     Chromium
Startup time      Fast               Slower
NPM ecosystem     Via frontend       Full Node.js
Learning curve    Higher (Rust)      Lower (JS)
```

## Additional Resources

- Tauri docs: https://v2.tauri.app/
- Tauri plugins: https://v2.tauri.app/plugin/
- Tauri vs Electron: https://v2.tauri.app/concept/
