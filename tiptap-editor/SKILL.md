---
name: tiptap-editor
description: Tiptap editor patterns covering ProseMirror-based rich text, extensions, custom nodes/marks, collaborative editing, bubble/floating menus, slash commands, and React/Vue integration.
---

# Tiptap Editor

This skill should be used when building rich text editors with Tiptap. It covers extensions, custom nodes, collaborative editing, menus, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Build rich text editors with ProseMirror
- Create custom block types and marks
- Add bubble menus and slash commands
- Enable real-time collaborative editing
- Integrate with React or Vue

## Setup

```bash
npm install @tiptap/react @tiptap/starter-kit @tiptap/extension-placeholder
npm install @tiptap/extension-link @tiptap/extension-image @tiptap/extension-code-block-lowlight
```

## Basic React Editor

```tsx
import { useEditor, EditorContent, BubbleMenu } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Placeholder from "@tiptap/extension-placeholder";
import Link from "@tiptap/extension-link";
import Image from "@tiptap/extension-image";

function RichTextEditor({ content, onChange }: {
  content: string;
  onChange: (html: string) => void;
}) {
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: { levels: [1, 2, 3] },
        codeBlock: false,
      }),
      Placeholder.configure({ placeholder: "Start writing..." }),
      Link.configure({ openOnClick: false }),
      Image.configure({ inline: false, allowBase64: true }),
    ],
    content,
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML());
    },
  });

  if (!editor) return null;

  return (
    <div className="editor-wrapper">
      <Toolbar editor={editor} />
      <BubbleMenu editor={editor} className="bubble-menu">
        <button
          onClick={() => editor.chain().focus().toggleBold().run()}
          className={editor.isActive("bold") ? "active" : ""}
        >
          Bold
        </button>
        <button
          onClick={() => editor.chain().focus().toggleItalic().run()}
          className={editor.isActive("italic") ? "active" : ""}
        >
          Italic
        </button>
        <button onClick={() => {
          const url = prompt("Enter URL");
          if (url) editor.chain().focus().setLink({ href: url }).run();
        }}>
          Link
        </button>
      </BubbleMenu>
      <EditorContent editor={editor} className="prose" />
    </div>
  );
}
```

## Toolbar Component

```tsx
function Toolbar({ editor }: { editor: Editor }) {
  return (
    <div className="toolbar">
      <button
        onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
        className={editor.isActive("heading", { level: 1 }) ? "active" : ""}
      >
        H1
      </button>
      <button
        onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
        className={editor.isActive("heading", { level: 2 }) ? "active" : ""}
      >
        H2
      </button>
      <button
        onClick={() => editor.chain().focus().toggleBulletList().run()}
        className={editor.isActive("bulletList") ? "active" : ""}
      >
        Bullet List
      </button>
      <button
        onClick={() => editor.chain().focus().toggleOrderedList().run()}
        className={editor.isActive("orderedList") ? "active" : ""}
      >
        Ordered List
      </button>
      <button
        onClick={() => editor.chain().focus().toggleCodeBlock().run()}
        className={editor.isActive("codeBlock") ? "active" : ""}
      >
        Code
      </button>
      <button
        onClick={() => editor.chain().focus().toggleBlockquote().run()}
        className={editor.isActive("blockquote") ? "active" : ""}
      >
        Quote
      </button>
      <button onClick={() => editor.chain().focus().undo().run()} disabled={!editor.can().undo()}>
        Undo
      </button>
      <button onClick={() => editor.chain().focus().redo().run()} disabled={!editor.can().redo()}>
        Redo
      </button>
    </div>
  );
}
```

## Custom Extension

```ts
import { Node, mergeAttributes } from "@tiptap/core";

const Callout = Node.create({
  name: "callout",
  group: "block",
  content: "block+",
  defining: true,

  addAttributes() {
    return {
      type: { default: "info", parseHTML: (el) => el.getAttribute("data-type") || "info" },
    };
  },

  parseHTML() {
    return [{ tag: "div[data-callout]" }];
  },

  renderHTML({ HTMLAttributes }) {
    return ["div", mergeAttributes(HTMLAttributes, { "data-callout": "", class: `callout callout-${HTMLAttributes.type}` }), 0];
  },

  addCommands() {
    return {
      setCallout: (attrs) => ({ commands }) => commands.wrapIn(this.name, attrs),
      toggleCallout: (attrs) => ({ commands }) => commands.toggleWrap(this.name, attrs),
    };
  },
});
```

## Collaborative Editing

```tsx
import { Collaboration } from "@tiptap/extension-collaboration";
import { CollaborationCursor } from "@tiptap/extension-collaboration-cursor";
import * as Y from "yjs";
import { WebsocketProvider } from "y-websocket";

const ydoc = new Y.Doc();
const provider = new WebsocketProvider("wss://collab.example.com", "doc-room", ydoc);

const editor = useEditor({
  extensions: [
    StarterKit.configure({ history: false }),
    Collaboration.configure({ document: ydoc }),
    CollaborationCursor.configure({
      provider,
      user: { name: "Alice", color: "#f783ac" },
    }),
  ],
});
```

## Get/Set Content

```ts
// Get content
const html = editor.getHTML();
const json = editor.getJSON();
const text = editor.getText();

// Set content
editor.commands.setContent("<h1>Hello</h1><p>World</p>");
editor.commands.setContent({ type: "doc", content: [/* ... */] });

// Insert content at cursor
editor.commands.insertContent("<p>Inserted paragraph</p>");
editor.chain().focus().insertContent("text").run();
```

## Additional Resources

- Tiptap: https://tiptap.dev/
- Extensions: https://tiptap.dev/docs/editor/extensions
- Collaboration: https://tiptap.dev/docs/editor/extensions/collaboration
