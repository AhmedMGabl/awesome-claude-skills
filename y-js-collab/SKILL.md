---
name: y-js-collab
description: Yjs collaborative editing patterns covering CRDTs, shared types, awareness protocol, WebSocket/WebRTC providers, ProseMirror/CodeMirror bindings, undo manager, and offline-first sync.
---

# Yjs Collaborative Editing

This skill should be used when building real-time collaborative applications with Yjs. It covers shared types, providers, editor bindings, awareness, and offline sync.

## When to Use This Skill

Use this skill when you need to:

- Build real-time collaborative editors
- Implement CRDT-based conflict resolution
- Add presence and cursor awareness
- Sync state via WebSocket or WebRTC
- Support offline-first editing with sync

## Setup

```bash
npm install yjs y-websocket y-prosemirror
# or for CodeMirror:
npm install yjs y-websocket y-codemirror.next
```

## Core Concepts

```ts
import * as Y from "yjs";

// Create a Yjs document
const ydoc = new Y.Doc();

// Shared types
const ytext = ydoc.getText("editor");          // Collaborative text
const yarray = ydoc.getArray("items");         // Collaborative array
const ymap = ydoc.getMap("settings");          // Collaborative map
const yxmlFragment = ydoc.getXmlFragment("prosemirror"); // For ProseMirror

// Text operations
ytext.insert(0, "Hello ");
ytext.insert(6, "World");
ytext.delete(0, 6); // Delete "Hello "
ytext.applyDelta([
  { retain: 5 },
  { insert: "!", attributes: { bold: true } },
]);

// Array operations
yarray.push(["item1"]);
yarray.insert(0, ["first"]);
yarray.delete(1, 1);

// Map operations
ymap.set("theme", "dark");
ymap.set("fontSize", 14);
ymap.delete("fontSize");

// Nested types
const nestedMap = new Y.Map();
nestedMap.set("name", "Alice");
yarray.push([nestedMap]);
```

## WebSocket Provider

```ts
import { WebsocketProvider } from "y-websocket";

const provider = new WebsocketProvider(
  "wss://your-server.com",
  "room-name",
  ydoc
);

// Connection status
provider.on("status", (event: { status: string }) => {
  console.log("Connection:", event.status); // "connecting", "connected", "disconnected"
});

// Sync status
provider.on("sync", (synced: boolean) => {
  console.log("Synced:", synced);
});

// Awareness (presence)
const awareness = provider.awareness;

// Set local user state
awareness.setLocalStateField("user", {
  name: "Alice",
  color: "#ff0000",
  cursor: null,
});

// Listen for awareness changes
awareness.on("change", () => {
  const states = awareness.getStates();
  states.forEach((state, clientId) => {
    console.log(`User ${state.user?.name} is online`);
  });
});

// Disconnect
provider.disconnect();
provider.connect(); // Reconnect
```

## ProseMirror Binding

```ts
import { ySyncPlugin, yCursorPlugin, yUndoPlugin } from "y-prosemirror";
import { EditorState } from "prosemirror-state";
import { EditorView } from "prosemirror-view";
import { schema } from "prosemirror-schema-basic";

const yxmlFragment = ydoc.getXmlFragment("prosemirror");

const state = EditorState.create({
  schema,
  plugins: [
    ySyncPlugin(yxmlFragment),
    yCursorPlugin(provider.awareness),
    yUndoPlugin(),
  ],
});

const view = new EditorView(document.querySelector("#editor")!, { state });
```

## CodeMirror Binding

```ts
import { yCollab } from "y-codemirror.next";
import { EditorView, basicSetup } from "codemirror";
import { EditorState } from "@codemirror/state";

const ytext = ydoc.getText("codemirror");

const state = EditorState.create({
  doc: ytext.toString(),
  extensions: [
    basicSetup,
    yCollab(ytext, provider.awareness),
  ],
});

const view = new EditorView({ state, parent: document.querySelector("#editor")! });
```

## Undo Manager

```ts
const undoManager = new Y.UndoManager(ytext, {
  trackedOrigins: new Set([ydoc.clientID]),
  captureTimeout: 500,
});

undoManager.on("stack-item-added", (event) => {
  console.log("Can undo:", undoManager.canUndo());
  console.log("Can redo:", undoManager.canRedo());
});

// Undo/Redo
undoManager.undo();
undoManager.redo();
```

## Observing Changes

```ts
// Observe text changes
ytext.observe((event) => {
  console.log("Delta:", event.delta);
  console.log("Full text:", ytext.toString());
});

// Observe map changes
ymap.observe((event) => {
  event.keysChanged.forEach((key) => {
    const change = event.changes.keys.get(key);
    console.log(`Key "${key}": ${change?.action}`); // "add", "update", "delete"
  });
});

// Deep observe (nested changes)
yarray.observeDeep((events) => {
  events.forEach((event) => {
    console.log("Path:", event.path);
    console.log("Changes:", event.changes);
  });
});
```

## Additional Resources

- Yjs: https://docs.yjs.dev/
- y-websocket: https://github.com/yjs/y-websocket
- y-prosemirror: https://github.com/yjs/y-prosemirror
