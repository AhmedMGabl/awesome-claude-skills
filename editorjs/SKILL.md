---
name: editorjs
description: Editor.js patterns covering block-style editing, custom tool plugins, inline tools, output data parsing, server-side validation, image/embed tools, and React integration.
---

# Editor.js

This skill should be used when building block-style content editors with Editor.js. It covers tools, custom plugins, inline tools, data handling, and React integration.

## When to Use This Skill

Use this skill when you need to:

- Build block-style content editors
- Create custom block tool plugins
- Handle structured JSON output data
- Add image, embed, and media tools
- Integrate with React applications

## Setup

```bash
npm install @editorjs/editorjs
npm install @editorjs/header @editorjs/list @editorjs/code @editorjs/image
npm install @editorjs/embed @editorjs/quote @editorjs/marker @editorjs/delimiter
npm install @editorjs/inline-code @editorjs/table
```

## Basic Setup

```ts
import EditorJS from "@editorjs/editorjs";
import Header from "@editorjs/header";
import List from "@editorjs/list";
import Code from "@editorjs/code";
import ImageTool from "@editorjs/image";
import Quote from "@editorjs/quote";
import Delimiter from "@editorjs/delimiter";
import Table from "@editorjs/table";
import Marker from "@editorjs/marker";
import InlineCode from "@editorjs/inline-code";
import Embed from "@editorjs/embed";

const editor = new EditorJS({
  holder: "editorjs",
  placeholder: "Start writing...",
  tools: {
    header: { class: Header, config: { levels: [1, 2, 3, 4], defaultLevel: 2 } },
    list: { class: List, inlineToolbar: true, config: { defaultStyle: "unordered" } },
    code: Code,
    image: {
      class: ImageTool,
      config: {
        endpoints: { byFile: "/api/upload/image", byUrl: "/api/upload/url" },
        field: "image",
        types: "image/*",
      },
    },
    quote: { class: Quote, inlineToolbar: true },
    delimiter: Delimiter,
    table: { class: Table, inlineToolbar: true },
    marker: Marker,
    inlineCode: InlineCode,
    embed: { class: Embed, config: { services: { youtube: true, vimeo: true, codepen: true } } },
  },
  data: initialData,
  onChange: async (api) => {
    const data = await api.saver.save();
    console.log("Saved data:", data);
  },
});
```

## React Integration

```tsx
import { useEffect, useRef, useCallback } from "react";
import EditorJS from "@editorjs/editorjs";

function BlockEditor({ data, onChange }: {
  data?: any;
  onChange?: (data: any) => void;
}) {
  const editorRef = useRef<EditorJS | null>(null);
  const holderRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!holderRef.current) return;

    const editor = new EditorJS({
      holder: holderRef.current,
      tools: { /* ... */ },
      data,
      onChange: async (api) => {
        const savedData = await api.saver.save();
        onChange?.(savedData);
      },
    });

    editorRef.current = editor;
    return () => { editor.isReady.then(() => editor.destroy()); };
  }, []);

  return <div ref={holderRef} id="editorjs" />;
}
```

## Output Data Format

```json
{
  "time": 1706000000000,
  "blocks": [
    {
      "id": "abc123",
      "type": "header",
      "data": { "text": "My Article", "level": 1 }
    },
    {
      "id": "def456",
      "type": "paragraph",
      "data": { "text": "This is a <b>rich text</b> paragraph with <a href=\"/\">links</a>." }
    },
    {
      "id": "ghi789",
      "type": "list",
      "data": { "style": "unordered", "items": ["First item", "Second item", "Third item"] }
    },
    {
      "id": "jkl012",
      "type": "image",
      "data": {
        "file": { "url": "https://example.com/image.jpg" },
        "caption": "An example image",
        "withBorder": false,
        "stretched": true,
        "withBackground": false
      }
    }
  ],
  "version": "2.28.0"
}
```

## Custom Block Tool

```ts
class AlertTool {
  static get toolbox() {
    return { title: "Alert", icon: "<svg>...</svg>" };
  }

  static get isReadOnlySupported() { return true; }

  private data: { type: string; message: string };
  private wrapper: HTMLElement | null = null;

  constructor({ data }: { data: any }) {
    this.data = { type: data.type || "info", message: data.message || "" };
  }

  render() {
    this.wrapper = document.createElement("div");
    this.wrapper.className = `alert alert-${this.data.type}`;

    const select = document.createElement("select");
    ["info", "warning", "error", "success"].forEach((type) => {
      const option = document.createElement("option");
      option.value = type;
      option.textContent = type;
      option.selected = type === this.data.type;
      select.appendChild(option);
    });
    select.addEventListener("change", (e) => {
      this.data.type = (e.target as HTMLSelectElement).value;
      this.wrapper!.className = `alert alert-${this.data.type}`;
    });

    const content = document.createElement("div");
    content.contentEditable = "true";
    content.textContent = this.data.message;
    content.addEventListener("input", () => {
      this.data.message = content.textContent || "";
    });

    this.wrapper.append(select, content);
    return this.wrapper;
  }

  save() { return this.data; }

  validate(savedData: any) { return savedData.message.trim() !== ""; }
}
```

## Save and Render

```ts
// Save
async function saveContent() {
  const data = await editor.save();
  await fetch("/api/posts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content: data }),
  });
}

// Render blocks as HTML
function renderBlock(block: any): string {
  switch (block.type) {
    case "header": return `<h${block.data.level}>${block.data.text}</h${block.data.level}>`;
    case "paragraph": return `<p>${block.data.text}</p>`;
    case "list": {
      const tag = block.data.style === "ordered" ? "ol" : "ul";
      const items = block.data.items.map((i: string) => `<li>${i}</li>`).join("");
      return `<${tag}>${items}</${tag}>`;
    }
    default: return "";
  }
}
```

## Additional Resources

- Editor.js: https://editorjs.io/
- Tools: https://editorjs.io/creating-a-block-tool
- API: https://editorjs.io/api
