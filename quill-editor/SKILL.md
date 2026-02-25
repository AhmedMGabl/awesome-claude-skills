---
name: quill-editor
description: Quill editor patterns covering Delta document model, toolbar modules, custom formats/blots, content change events, clipboard handling, themes, and React integration.
---

# Quill Editor

This skill should be used when building rich text editors with Quill. It covers modules, custom formats, Delta model, clipboard handling, and React integration.

## When to Use This Skill

Use this skill when you need to:

- Build WYSIWYG rich text editors
- Work with the Delta document model
- Create custom formats and blots
- Handle clipboard paste operations
- Integrate Quill with React

## Setup

```bash
npm install quill
# For React:
npm install react-quill-new
```

## Basic React Integration

```tsx
import ReactQuill from "react-quill-new";
import "react-quill-new/dist/quill.snow.css";
import { useState, useMemo } from "react";

function RichTextEditor({ value, onChange }: {
  value: string;
  onChange: (html: string) => void;
}) {
  const modules = useMemo(() => ({
    toolbar: [
      [{ header: [1, 2, 3, false] }],
      ["bold", "italic", "underline", "strike"],
      [{ list: "ordered" }, { list: "bullet" }],
      ["blockquote", "code-block"],
      ["link", "image"],
      [{ color: [] }, { background: [] }],
      [{ align: [] }],
      ["clean"],
    ],
    clipboard: { matchVisual: false },
  }), []);

  const formats = [
    "header", "bold", "italic", "underline", "strike",
    "list", "blockquote", "code-block",
    "link", "image", "color", "background", "align",
  ];

  return (
    <ReactQuill
      value={value}
      onChange={onChange}
      modules={modules}
      formats={formats}
      theme="snow"
      placeholder="Start writing..."
    />
  );
}
```

## Vanilla JavaScript Setup

```ts
import Quill from "quill";
import "quill/dist/quill.snow.css";

const quill = new Quill("#editor", {
  theme: "snow",
  modules: {
    toolbar: [
      [{ header: [1, 2, 3, false] }],
      ["bold", "italic", "underline"],
      [{ list: "ordered" }, { list: "bullet" }],
      ["link", "image", "code-block"],
    ],
  },
  placeholder: "Start writing...",
});

// Listen for changes
quill.on("text-change", (delta, oldDelta, source) => {
  if (source === "user") {
    console.log("Delta:", delta);
    console.log("HTML:", quill.root.innerHTML);
    console.log("Text:", quill.getText());
  }
});
```

## Delta Operations

```ts
// Get content as Delta
const delta = quill.getContents();

// Set content from Delta
quill.setContents([
  { insert: "Hello ", attributes: { bold: true } },
  { insert: "World", attributes: { italic: true } },
  { insert: "\n", attributes: { header: 1 } },
  { insert: "This is a paragraph.\n" },
]);

// Insert text at position
quill.insertText(0, "Prefix: ", { bold: true });

// Format selection
quill.formatText(0, 5, { bold: true, color: "#ff0000" });

// Delete text
quill.deleteText(0, 5);
```

## Custom Blot (Format)

```ts
import Quill from "quill";
const BlockEmbed = Quill.import("blots/block/embed");

class DividerBlot extends BlockEmbed {
  static blotName = "divider";
  static tagName = "hr";

  static create() {
    const node = super.create() as HTMLElement;
    node.setAttribute("class", "editor-divider");
    return node;
  }
}

Quill.register(DividerBlot);

// Use it
quill.insertEmbed(quill.getLength() - 1, "divider", true);
```

## Image Upload Handler

```ts
const quill = new Quill("#editor", {
  modules: {
    toolbar: {
      container: [["image"]],
      handlers: {
        image: function () {
          const input = document.createElement("input");
          input.setAttribute("type", "file");
          input.setAttribute("accept", "image/*");
          input.click();

          input.onchange = async () => {
            const file = input.files?.[0];
            if (!file) return;

            const formData = new FormData();
            formData.append("image", file);

            const response = await fetch("/api/upload", { method: "POST", body: formData });
            const { url } = await response.json();

            const range = quill.getSelection(true);
            quill.insertEmbed(range.index, "image", url);
          };
        },
      },
    },
  },
});
```

## Additional Resources

- Quill: https://quilljs.com/
- Delta: https://quilljs.com/docs/delta
- Modules: https://quilljs.com/docs/modules
