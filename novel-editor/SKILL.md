---
name: novel-editor
description: Novel editor patterns covering Notion-style WYSIWYG editing, Tiptap-based architecture, slash commands, bubble menu, AI completions, image uploads, and Next.js integration.
---

# Novel Editor

This skill should be used when building Notion-style editors with Novel. It covers configuration, slash commands, bubble menu, AI completions, and Next.js integration.

## When to Use This Skill

Use this skill when you need to:

- Add a Notion-style editor to React/Next.js apps
- Configure slash commands and bubble menus
- Integrate AI-powered text completions
- Handle image uploads in the editor
- Customize editor extensions and styling

## Setup

```bash
npm install novel
```

## Basic Usage

```tsx
import { Editor } from "novel";

function ArticleEditor() {
  return (
    <Editor
      defaultValue={defaultContent}
      onUpdate={(editor) => {
        const json = editor?.getJSON();
        const html = editor?.getHTML();
        console.log("Content:", json);
      }}
      className="prose dark:prose-invert"
    />
  );
}

const defaultContent = {
  type: "doc",
  content: [
    {
      type: "heading",
      attrs: { level: 1 },
      content: [{ type: "text", text: "Welcome to Novel" }],
    },
    {
      type: "paragraph",
      content: [{ type: "text", text: "Start writing your article..." }],
    },
  ],
};
```

## Advanced Configuration

```tsx
import {
  EditorRoot, EditorContent, EditorCommand, EditorCommandItem,
  EditorCommandEmpty, EditorBubble,
} from "novel";
import { useState } from "react";

function AdvancedEditor() {
  const [content, setContent] = useState(defaultContent);
  const [openCommand, setOpenCommand] = useState(false);

  return (
    <EditorRoot>
      <EditorContent
        initialContent={content}
        onUpdate={({ editor }) => setContent(editor.getJSON())}
        extensions={[/* custom extensions */]}
        className="prose dark:prose-invert max-w-none"
      >
        {/* Slash command menu */}
        <EditorCommand
          open={openCommand}
          onOpenChange={setOpenCommand}
          className="command-menu"
        >
          <EditorCommandEmpty>No results</EditorCommandEmpty>
          <EditorCommandItem
            value="heading"
            onCommand={({ editor, range }) => {
              editor.chain().focus().deleteRange(range).setNode("heading", { level: 1 }).run();
            }}
          >
            Heading 1
          </EditorCommandItem>
          <EditorCommandItem
            value="bullet-list"
            onCommand={({ editor, range }) => {
              editor.chain().focus().deleteRange(range).toggleBulletList().run();
            }}
          >
            Bullet List
          </EditorCommandItem>
          <EditorCommandItem
            value="code"
            onCommand={({ editor, range }) => {
              editor.chain().focus().deleteRange(range).toggleCodeBlock().run();
            }}
          >
            Code Block
          </EditorCommandItem>
        </EditorCommand>

        {/* Bubble menu (floating toolbar) */}
        <EditorBubble className="bubble-menu">
          <button onClick={({ editor }) => editor.chain().focus().toggleBold().run()}>
            Bold
          </button>
          <button onClick={({ editor }) => editor.chain().focus().toggleItalic().run()}>
            Italic
          </button>
          <button onClick={({ editor }) => editor.chain().focus().toggleStrike().run()}>
            Strike
          </button>
        </EditorBubble>
      </EditorContent>
    </EditorRoot>
  );
}
```

## Image Upload

```tsx
import { handleImageUpload } from "novel/plugins";

const extensions = [
  // ... other extensions
  handleImageUpload({
    onUpload: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      const { url } = await response.json();
      return url;
    },
  }),
];
```

## Get/Set Content

```tsx
function EditorControls({ editor }: { editor: any }) {
  // Get content in different formats
  const getJSON = () => editor.getJSON();
  const getHTML = () => editor.getHTML();
  const getText = () => editor.getText();

  // Set content
  const setContent = (json: any) => {
    editor.commands.setContent(json);
  };

  // Clear content
  const clear = () => {
    editor.commands.clearContent();
  };

  return (
    <div>
      <button onClick={() => console.log(getJSON())}>Export JSON</button>
      <button onClick={() => console.log(getHTML())}>Export HTML</button>
      <button onClick={clear}>Clear</button>
    </div>
  );
}
```

## Additional Resources

- Novel: https://novel.sh/
- GitHub: https://github.com/steven-tey/novel
- Examples: https://novel.sh/docs
