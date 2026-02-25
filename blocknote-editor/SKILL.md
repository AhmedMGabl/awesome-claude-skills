---
name: blocknote-editor
description: BlockNote editor patterns covering block-based Notion-style editing, custom block types, slash menu, drag-and-drop, collaborative editing, theming, and React integration.
---

# BlockNote Editor

This skill should be used when building block-based Notion-style editors with BlockNote. It covers blocks, slash menu, custom types, collaboration, and React integration.

## When to Use This Skill

Use this skill when you need to:

- Build Notion-style block editors
- Add custom block types
- Implement slash commands and drag-and-drop
- Enable real-time collaborative editing
- Integrate with React applications

## Setup

```bash
npm install @blocknote/core @blocknote/react @blocknote/mantine
```

## Basic Editor

```tsx
import { BlockNoteEditor } from "@blocknote/core";
import { useCreateBlockNote } from "@blocknote/react";
import { BlockNoteView } from "@blocknote/mantine";
import "@blocknote/mantine/style.css";

function Editor() {
  const editor = useCreateBlockNote({
    initialContent: [
      { type: "heading", content: "Welcome", props: { level: 1 } },
      { type: "paragraph", content: "Start writing..." },
    ],
  });

  return (
    <BlockNoteView
      editor={editor}
      theme="light"
      onChange={() => {
        const blocks = editor.document;
        console.log("Blocks:", JSON.stringify(blocks));
      }}
    />
  );
}
```

## Custom Block Type

```tsx
import { createReactBlockSpec } from "@blocknote/react";
import { defaultBlockSpecs } from "@blocknote/core";

const AlertBlock = createReactBlockSpec(
  {
    type: "alert",
    propSchema: {
      type: { default: "info", values: ["info", "warning", "error", "success"] },
    },
    content: "inline",
  },
  {
    render: ({ block, contentRef }) => {
      const styles: Record<string, string> = {
        info: "bg-blue-50 border-blue-400",
        warning: "bg-yellow-50 border-yellow-400",
        error: "bg-red-50 border-red-400",
        success: "bg-green-50 border-green-400",
      };

      return (
        <div className={`p-4 border-l-4 rounded ${styles[block.props.type]}`}>
          <select
            value={block.props.type}
            onChange={(e) => {
              block.props.type = e.target.value as any;
            }}
          >
            <option value="info">Info</option>
            <option value="warning">Warning</option>
            <option value="error">Error</option>
            <option value="success">Success</option>
          </select>
          <div ref={contentRef} />
        </div>
      );
    },
  }
);

// Register custom blocks
const editor = useCreateBlockNote({
  blockSpecs: {
    ...defaultBlockSpecs,
    alert: AlertBlock,
  },
});
```

## Slash Menu Customization

```tsx
import { getDefaultReactSlashMenuItems } from "@blocknote/react";

const customSlashMenuItems = [
  ...getDefaultReactSlashMenuItems(editor),
  {
    title: "Alert",
    subtext: "Add an alert block",
    group: "Other",
    icon: <span>!</span>,
    aliases: ["alert", "callout", "warning"],
    onItemClick: () => {
      editor.insertBlocks(
        [{ type: "alert", props: { type: "info" } }],
        editor.getTextCursorPosition().block,
        "after"
      );
    },
  },
];
```

## Content Manipulation

```ts
// Insert blocks
editor.insertBlocks(
  [
    { type: "heading", content: "New Section", props: { level: 2 } },
    { type: "paragraph", content: "Some content here." },
  ],
  editor.document[editor.document.length - 1],
  "after"
);

// Update block
editor.updateBlock(editor.document[0], {
  type: "heading",
  props: { level: 1 },
  content: "Updated Title",
});

// Remove block
editor.removeBlocks([editor.document[1]]);

// Get Markdown
const markdown = await editor.blocksToMarkdownLossy(editor.document);

// Get HTML
const html = await editor.blocksToHTMLLossy(editor.document);

// From Markdown
const blocks = await editor.tryParseMarkdownToBlocks("# Hello\n\nWorld");
editor.replaceBlocks(editor.document, blocks);
```

## Collaborative Editing

```tsx
import * as Y from "yjs";
import { WebsocketProvider } from "y-websocket";

const ydoc = new Y.Doc();
const provider = new WebsocketProvider("wss://collab.example.com", "room-id", ydoc);

const editor = useCreateBlockNote({
  collaboration: {
    provider,
    fragment: ydoc.getXmlFragment("document-store"),
    user: { name: "Alice", color: "#ff0000" },
  },
});
```

## Additional Resources

- BlockNote: https://www.blocknotejs.org/
- Custom Blocks: https://www.blocknotejs.org/docs/custom-schemas/custom-blocks
- Collaboration: https://www.blocknotejs.org/docs/advanced/real-time-collaboration
