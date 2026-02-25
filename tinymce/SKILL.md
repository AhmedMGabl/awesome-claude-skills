---
name: tinymce
description: TinyMCE patterns covering WYSIWYG configuration, plugin ecosystem, custom toolbar buttons, content formatting, image upload, templates, and React/Vue integration.
---

# TinyMCE

This skill should be used when integrating WYSIWYG editing with TinyMCE. It covers configuration, plugins, custom buttons, image uploads, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Add full-featured WYSIWYG editors to web apps
- Configure toolbar and plugin combinations
- Handle image and file uploads
- Create custom toolbar buttons and dialogs
- Integrate TinyMCE with React or Vue

## Setup

```bash
npm install tinymce @tinymce/tinymce-react
```

## React Integration

```tsx
import { Editor } from "@tinymce/tinymce-react";
import { useRef } from "react";

function RichTextEditor({ value, onChange }: {
  value: string;
  onChange: (html: string) => void;
}) {
  const editorRef = useRef<any>(null);

  return (
    <Editor
      apiKey={process.env.NEXT_PUBLIC_TINYMCE_API_KEY}
      onInit={(evt, editor) => { editorRef.current = editor; }}
      value={value}
      onEditorChange={onChange}
      init={{
        height: 500,
        menubar: true,
        plugins: [
          "advlist", "autolink", "lists", "link", "image", "charmap",
          "preview", "anchor", "searchreplace", "visualblocks", "code",
          "fullscreen", "insertdatetime", "media", "table", "help",
          "wordcount", "codesample",
        ],
        toolbar:
          "undo redo | blocks | bold italic forecolor | " +
          "alignleft aligncenter alignright alignjustify | " +
          "bullist numlist outdent indent | removeformat | " +
          "link image codesample | help",
        content_style: "body { font-family: -apple-system, sans-serif; font-size: 16px; }",
        codesample_languages: [
          { text: "TypeScript", value: "typescript" },
          { text: "JavaScript", value: "javascript" },
          { text: "Python", value: "python" },
          { text: "HTML", value: "markup" },
          { text: "CSS", value: "css" },
        ],
      }}
    />
  );
}
```

## Image Upload

```tsx
<Editor
  init={{
    images_upload_handler: async (blobInfo) => {
      const formData = new FormData();
      formData.append("file", blobInfo.blob(), blobInfo.filename());

      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Upload failed");
      const { url } = await response.json();
      return url;
    },
    automatic_uploads: true,
    file_picker_types: "image",
  }}
/>
```

## Custom Toolbar Button

```tsx
<Editor
  init={{
    setup: (editor) => {
      // Toggle button
      editor.ui.registry.addToggleButton("customHighlight", {
        text: "Highlight",
        onAction: () => editor.execCommand("HiliteColor", false, "#ffff00"),
        onSetup: (api) => {
          editor.on("NodeChange", () => {
            api.setActive(editor.queryCommandState("HiliteColor"));
          });
        },
      });

      // Menu button with dropdown
      editor.ui.registry.addMenuButton("insertBlock", {
        text: "Insert",
        fetch: (callback) => {
          callback([
            { type: "menuitem", text: "Alert Box", onAction: () => {
              editor.insertContent('<div class="alert alert-info">Alert content</div>');
            }},
            { type: "menuitem", text: "Divider", onAction: () => {
              editor.insertContent("<hr />");
            }},
          ]);
        },
      });

      // Keyboard shortcut
      editor.addShortcut("meta+shift+h", "Highlight text", () => {
        editor.execCommand("HiliteColor", false, "#ffff00");
      });
    },
    toolbar: "undo redo | bold italic | customHighlight insertBlock",
  }}
/>
```

## Templates

```tsx
<Editor
  init={{
    plugins: ["template"],
    templates: [
      {
        title: "Blog Post",
        description: "Standard blog post template",
        content: `
          <h1>Post Title</h1>
          <p><em>Published on {$date}</em></p>
          <p>Introduction paragraph...</p>
          <h2>Section 1</h2>
          <p>Content...</p>
        `,
      },
      {
        title: "Product Card",
        description: "E-commerce product card",
        content: `
          <div class="product-card">
            <h3>Product Name</h3>
            <p class="price">$0.00</p>
            <p>Description...</p>
          </div>
        `,
      },
    ],
  }}
/>
```

## Get/Set Content

```ts
// Get content
const html = editorRef.current.getContent();
const text = editorRef.current.getContent({ format: "text" });

// Set content
editorRef.current.setContent("<h1>New Content</h1><p>Hello World</p>");

// Insert content at cursor
editorRef.current.insertContent("<p>Inserted paragraph</p>");

// Reset
editorRef.current.resetContent();
```

## Additional Resources

- TinyMCE: https://www.tiny.cloud/docs/tinymce/latest/
- Plugins: https://www.tiny.cloud/docs/tinymce/latest/plugins/
- React: https://www.tiny.cloud/docs/tinymce/latest/react-cloud/
