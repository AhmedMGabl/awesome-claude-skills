---
name: ckeditor5
description: CKEditor 5 patterns covering modular editor builds, plugin architecture, custom plugins, toolbar configuration, image upload adapters, content conversion, and React integration.
---

# CKEditor 5

This skill should be used when building rich text editors with CKEditor 5. It covers builds, plugins, toolbar, image upload, content conversion, and React integration.

## When to Use This Skill

Use this skill when you need to:

- Add enterprise-grade WYSIWYG editors to web apps
- Configure modular editor builds with specific plugins
- Create custom plugins and converters
- Handle image and file uploads
- Integrate CKEditor with React

## Setup

```bash
npm install ckeditor5
# For React:
npm install @ckeditor/ckeditor5-react
```

## React Integration

```tsx
import { CKEditor } from "@ckeditor/ckeditor5-react";
import {
  ClassicEditor, Bold, Italic, Essentials, Paragraph,
  Heading, Link, List, Image, ImageUpload, Table,
  BlockQuote, CodeBlock, MediaEmbed,
} from "ckeditor5";
import "ckeditor5/ckeditor5.css";

function RichTextEditor({ value, onChange }: {
  value: string;
  onChange: (html: string) => void;
}) {
  return (
    <CKEditor
      editor={ClassicEditor}
      config={{
        plugins: [
          Essentials, Bold, Italic, Paragraph, Heading,
          Link, List, Image, ImageUpload, Table,
          BlockQuote, CodeBlock, MediaEmbed,
        ],
        toolbar: [
          "heading", "|",
          "bold", "italic", "link", "|",
          "bulletedList", "numberedList", "|",
          "blockQuote", "codeBlock", "|",
          "insertTable", "imageUpload", "mediaEmbed", "|",
          "undo", "redo",
        ],
      }}
      data={value}
      onChange={(event, editor) => {
        onChange(editor.getData());
      }}
    />
  );
}
```

## Vanilla JavaScript

```ts
import {
  ClassicEditor, Bold, Italic, Essentials,
  Paragraph, Heading, Link, List,
} from "ckeditor5";
import "ckeditor5/ckeditor5.css";

ClassicEditor.create(document.querySelector("#editor")!, {
  plugins: [Essentials, Bold, Italic, Paragraph, Heading, Link, List],
  toolbar: ["heading", "|", "bold", "italic", "link", "|", "bulletedList", "numberedList"],
}).then((editor) => {
  // Get content
  const html = editor.getData();

  // Set content
  editor.setData("<h2>New Content</h2><p>Hello world.</p>");

  // Listen for changes
  editor.model.document.on("change:data", () => {
    console.log("Content changed:", editor.getData());
  });
});
```

## Image Upload Adapter

```ts
import { FileLoader, UploadAdapter } from "ckeditor5";

class CustomUploadAdapter implements UploadAdapter {
  private loader: FileLoader;

  constructor(loader: FileLoader) {
    this.loader = loader;
  }

  async upload(): Promise<{ default: string }> {
    const file = await this.loader.file;
    if (!file) throw new Error("No file");

    const formData = new FormData();
    formData.append("upload", file);

    const response = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    });

    const { url } = await response.json();
    return { default: url };
  }

  abort(): void {}
}

function CustomUploadAdapterPlugin(editor: any) {
  editor.plugins.get("FileRepository").createUploadAdapter = (loader: FileLoader) => {
    return new CustomUploadAdapter(loader);
  };
}

// Use in config
const config = {
  extraPlugins: [CustomUploadAdapterPlugin],
};
```

## Custom Plugin

```ts
import { Plugin, ButtonView } from "ckeditor5";

class HighlightPlugin extends Plugin {
  static get pluginName() {
    return "Highlight" as const;
  }

  init() {
    const editor = this.editor;

    editor.model.schema.extend("$text", { allowAttributes: "highlight" });

    editor.conversion.attributeToElement({
      model: "highlight",
      view: {
        name: "mark",
        classes: "highlight",
      },
    });

    editor.ui.componentFactory.add("highlight", (locale) => {
      const button = new ButtonView(locale);
      button.set({ label: "Highlight", withText: true, tooltip: true });

      button.on("execute", () => {
        editor.model.change((writer) => {
          const selection = editor.model.document.selection;
          if (selection.hasAttribute("highlight")) {
            writer.removeSelectionAttribute("highlight");
          } else {
            writer.setSelectionAttribute("highlight", true);
          }
        });
      });

      return button;
    });
  }
}
```

## Additional Resources

- CKEditor 5: https://ckeditor.com/docs/ckeditor5/latest/
- Plugins: https://ckeditor.com/docs/ckeditor5/latest/framework/plugins/creating-simple-plugin.html
- React: https://ckeditor.com/docs/ckeditor5/latest/getting-started/integrations/react.html
